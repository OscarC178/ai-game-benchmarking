#!/usr/bin/env python3
"""
Game review dashboard server.

Usage:
    python3 review/server.py
    Then open http://localhost:5757 in your browser.

Ratings auto-save to review/ratings.json on every submission.
"""
import http.server
import json
import socketserver
import sys
from pathlib import Path
from urllib.parse import urlparse

PORT = 5757
HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent
RATINGS_FILE = HERE / "ratings.json"

# Game roots and how to read their folder structure.
# V1: games/<run-long-name>/<game>/<builder>/index.html
# V2: games-v2/builds/<run-short-name>/<game>/<builder>/index.html
GAME_ROOTS = [
    {"version": "v1", "root": WORKSPACE / "games", "url_key": "v1"},
    {"version": "v2", "root": WORKSPACE / "games-v2" / "builds", "url_key": "v2"},
]


def discover_games():
    games = []
    for cfg in GAME_ROOTS:
        root = cfg["root"]
        if not root.exists():
            continue
        for html in sorted(root.rglob("index.html")):
            rel = html.relative_to(root)
            parts = list(rel.parts[:-1])  # drop 'index.html'
            if len(parts) < 3:
                continue
            run, game, builder = parts[0], parts[1], parts[2]
            # Skip backup folders
            if ".bak" in builder or builder.startswith("."):
                continue
            game_id = f"{cfg['url_key']}/{run}/{game}/{builder}"
            games.append({
                "id": game_id,
                "version": cfg["version"],
                "run": run,
                "game": game,
                "builder": builder,
            })
    return games


def load_ratings():
    if RATINGS_FILE.exists():
        try:
            return json.loads(RATINGS_FILE.read_text())
        except json.JSONDecodeError:
            print("Warning: ratings.json is malformed, starting fresh", file=sys.stderr)
            return {}
    return {}


def save_ratings(data):
    RATINGS_FILE.write_text(json.dumps(data, indent=2, sort_keys=True))


def resolve_game_path(game_id):
    """Map 'v2/r1-opus/breakout/bench-sonnet' -> full path to index.html."""
    parts = game_id.strip("/").split("/")
    if len(parts) < 4:
        return None
    url_key = parts[0]
    for cfg in GAME_ROOTS:
        if cfg["url_key"] == url_key:
            full = cfg["root"].joinpath(*parts[1:]) / "index.html"
            return full if full.exists() else None
    return None


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            return self._serve_file(HERE / "index.html", "text/html; charset=utf-8")
        if path == "/api/games":
            games = discover_games()
            ratings = load_ratings()
            for g in games:
                g["rated"] = g["id"] in ratings
                g["rating"] = ratings.get(g["id"])
            return self._json(games)
        if path.startswith("/game/"):
            game_id = path[len("/game/"):].rstrip("/")
            full = resolve_game_path(game_id)
            if full is None:
                return self._404()
            return self._serve_file(full, "text/html; charset=utf-8")
        return self._404()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/rate":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return
            game_id = data.pop("game_id", None)
            if not game_id:
                self.send_response(400)
                self.end_headers()
                return
            ratings = load_ratings()
            ratings[game_id] = data
            save_ratings(ratings)
            return self._json({"ok": True})
        if parsed.path == "/api/delete":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            ratings = load_ratings()
            ratings.pop(data.get("game_id"), None)
            save_ratings(ratings)
            return self._json({"ok": True})
        return self._404()

    def _serve_file(self, path, content_type):
        if not path.exists():
            return self._404()
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _404(self):
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass  # keep terminal clean


if __name__ == "__main__":
    games = discover_games()
    rated = sum(1 for g in games if g["id"] in load_ratings())
    print(f"Review dashboard: http://localhost:{PORT}")
    print(f"Games discovered: {len(games)}   |   Already rated: {rated}")
    print(f"Ratings file: {RATINGS_FILE}")
    print("Press Ctrl-C to stop.")
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
