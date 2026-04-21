#!/usr/bin/env python3
"""
Interactive guide server.

Serves:
  /                  → guide dashboard
  /api/data          → aggregated guide data (from data.json)
  /api/rate          → POST new/updated human rating
  /api/delete        → POST remove human rating
  /game/{build_id}/  → iframe-embedded game build
  /spec/{build_id}   → planner spec for a build (markdown)
  /paper             → the academic paper
  /beginners-guide   → the prose beginners guide

Usage:
    python3 guide/server.py
    Open http://localhost:5858 in your browser.

Ratings are shared with review/ — both tools write to review/ratings.json.
"""
import http.server
import json
import socketserver
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

PORT = 5858
HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent
DATA_FILE = HERE / "data.json"
RATINGS_FILE = WORKSPACE / "review" / "ratings.json"

GAME_ROOTS = {
    "v1": WORKSPACE / "games",
    "v2": WORKSPACE / "games-v2" / "builds",
}


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_ratings(data):
    RATINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RATINGS_FILE.write_text(json.dumps(data, indent=2, sort_keys=True))


def resolve_game_html(build_id):
    """Map 'v2/r1-opus/breakout/bench-sonnet' -> Path to index.html."""
    parts = build_id.strip("/").split("/")
    if len(parts) < 4:
        return None
    root = GAME_ROOTS.get(parts[0])
    if root is None:
        return None
    full = root.joinpath(*parts[1:]) / "index.html"
    return full if full.exists() else None


def resolve_spec(spec_path):
    """Map a 3- or 4-part path to the spec.md file.
       Accepts 'v2/r1-opus/breakout' or 'v2/r1-opus/breakout/bench-sonnet' (4th part ignored)."""
    parts = spec_path.strip("/").split("/")
    if len(parts) < 3:
        return None
    dataset, run, game = parts[0], parts[1], parts[2]
    if dataset == "v1":
        p = WORKSPACE / "games" / run / game / "spec.md"
    else:
        p = WORKSPACE / "games-v2" / "specs" / run / game / "spec.md"
    return p if p.exists() else None


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path in ("/", "/index.html"):
            return self._serve_file(HERE / "index.html", "text/html; charset=utf-8")
        if path == "/api/data":
            return self._reload_and_serve_data()
        if path == "/paper" or path == "/paper/":
            return self._serve_file(WORKSPACE / "paper" / "index.html", "text/html; charset=utf-8")
        if path == "/beginners-guide" or path == "/beginners-guide/":
            return self._serve_file(HERE / "beginners-guide.html", "text/html; charset=utf-8")
        if path.startswith("/game/"):
            build_id = path[len("/game/"):].rstrip("/")
            full = resolve_game_html(build_id)
            if full is None:
                return self._404()
            return self._serve_file(full, "text/html; charset=utf-8")
        if path.startswith("/spec/"):
            build_id = path[len("/spec/"):].rstrip("/")
            full = resolve_spec(build_id)
            if full is None:
                return self._404()
            return self._serve_file(full, "text/markdown; charset=utf-8")
        return self._404()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self.send_response(400); self.end_headers(); return

        if path == "/api/rate":
            game_id = body.pop("game_id", None)
            if not game_id:
                self.send_response(400); self.end_headers(); return
            ratings = load_json(RATINGS_FILE)
            ratings[game_id] = body
            save_ratings(ratings)
            return self._json({"ok": True})

        if path == "/api/delete":
            ratings = load_json(RATINGS_FILE)
            ratings.pop(body.get("game_id"), None)
            save_ratings(ratings)
            return self._json({"ok": True})

        if path == "/api/reaggregate":
            # Re-run the aggregator to pick up new ratings or updated scores
            result = subprocess.run(
                [sys.executable, str(HERE / "aggregate.py")],
                capture_output=True, text=True,
            )
            return self._json({
                "ok": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            })

        return self._404()

    def _reload_and_serve_data(self):
        """Re-read data.json each time — cheap and ensures fresh ratings."""
        return self._serve_file(DATA_FILE, "application/json")

    def _serve_file(self, path, content_type):
        if not path.exists():
            return self._404()
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
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
        pass  # quieter terminal


if __name__ == "__main__":
    if not DATA_FILE.exists():
        print("data.json missing — running aggregator first.")
        subprocess.run([sys.executable, str(HERE / "aggregate.py")], check=True)

    meta = load_json(DATA_FILE).get("meta", {})
    print(f"Guide dashboard:  http://localhost:{PORT}")
    print(f"Paper:            http://localhost:{PORT}/paper")
    print(f"Beginners guide:  http://localhost:{PORT}/beginners-guide")
    print(f"Builds loaded:    {meta.get('total_builds', '?')}")
    print(f"Human ratings:    {meta.get('human_ratings_count', '?')}")
    print("Press Ctrl-C to stop.")
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
