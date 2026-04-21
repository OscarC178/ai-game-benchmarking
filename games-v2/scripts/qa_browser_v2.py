#!/usr/bin/env python3
"""
Quick Browser QA for V2 builds.
Tests game files directly via Playwright, checks for JS errors and basic functionality.
Compatible with V2 build structure: builds/<run>/<game>/<builder>/index.html
"""

import asyncio, json, os, sys, time, random, string
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

BUILD_DIR = Path("/Users/oscar/.openclaw/workspace/games-v2/builds")
QA_DIR = Path("/Users/oscar/.openclaw/workspace/games-v2/qa/browser")
QA_DIR.mkdir(parents=True, exist_ok=True)

RUNS = ["r1-opus", "r2-gpt54", "r3-gemini-pro", "r4-glm5", "r5-control"]
GAMES = ["pong", "snake", "breakout", "space-invaders", "tetris", "asteroids", "galaga", "frogger", "pac-man", "donkey-kong"]
BUILDERS = ["bench-opus", "bench-sonnet", "bench-haiku", "bench-gpt54", "bench-gpt54mini", "bench-gemini-pro", "bench-gemini-flash", "bench-glm5"]

PORT = 0  # auto-assign

async def start_server(port=0):
    import http.server, socketserver, threading
    os.chdir(BUILD_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    actual_port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, actual_port

async def test_game(run_id, game_slug, builder_id, actual_port):
    """Test one game build. Returns (ok, errors, notes)."""
    game_url = f"http://localhost:{actual_port}/{run_id}/{game_slug}/{builder_id}/index.html"
    errors = []
    bugs = []
    notes = ""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Capture console errors
        def handle_console(msg):
            if msg.type == "error":
                errors.append(f"console_error: {msg.text[:200]}")
        page.on("console", handle_console)

        def handle_page_error(err):
            errors.append(f"page_error: {str(err)[:200]}")
        page.on("pageerror", handle_page_error)

        try:
            await page.goto(game_url, timeout=15000)
            await page.wait_for_timeout(2000)

            # Check game loaded (canvas element)
            canvas = await page.query_selector("canvas")
            if not canvas:
                bugs.append("no_canvas")

            # Check title
            title = await page.title()
            notes = f"title={title[:30]}"

            # Try pressing a key (Start/Enter)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1000)

            # Check no crash
            if not errors:
                pass  # ok

        except PWTimeout:
            bugs.append("timeout")
        except Exception as e:
            errors.append(f"load_error: {str(e)[:100]}")
        finally:
            await browser.close()

    return bool(canvas), errors, bugs, notes


async def run_qa(run_filter=None, game_filter=None, builder_filter=None):
    httpd, actual_port = await start_server(PORT)
    print(f"Server running on port {actual_port}")

    total = 0
    tested = 0
    buggy = 0

    for run_id in RUNS:
        if run_filter and run_id != run_filter:
            continue
        for game_slug in GAMES:
            if game_filter and game_slug != game_filter:
                continue
            for builder_id in (builder_filter if builder_filter else BUILDERS):
                build_path = BUILD_DIR / run_id / game_slug / builder_id / "index.html"
                dnf_path = BUILD_DIR / run_id / game_slug / builder_id / "dnf.txt"
                qa_report = QA_DIR / run_id / game_slug / builder_id / "report.json"

                if dnf_path.exists():
                    continue
                if not build_path.exists():
                    continue
                if qa_report.exists():
                    # Already done
                    tested += 1
                    continue

                total += 1
                ok, errors, bugs, notes = await test_game(run_id, game_slug, builder_id, actual_port)

                result = {
                    "run": run_id,
                    "game": game_slug,
                    "builder": builder_id,
                    "ok": ok,
                    "errors": errors,
                    "bugs": bugs,
                    "notes": notes,
                }

                qa_report.parent.mkdir(parents=True, exist_ok=True)
                with open(qa_report, "w") as f:
                    json.dump(result, f, indent=2)

                status = "✅" if (ok and not bugs) else "❌"
                print(f"{status} {run_id}/{game_slug}/{builder_id} — {notes or errors[:1]}")

                if bugs or errors:
                    buggy += 1
                tested += 1

                await asyncio.sleep(0.5)  # small delay between tests

    httpd.shutdown()
    print(f"\n=== QA complete — {tested} tested, {buggy} with bugs ===")
    return buggy


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default=None)
    parser.add_argument("--game", default=None)
    parser.add_argument("--builders", default=None, help="Comma-separated builder IDs (e.g. bench-sonnet)")
    args = parser.parse_args()

    # Allow builder filter to override default BUILDERS list
    if args.builders:
        builder_filter = [b.strip() for b in args.builders.split(",")]
    else:
        builder_filter = None

    n_bugs = asyncio.run(run_qa(run_filter=args.run, game_filter=args.game, builder_filter=builder_filter))
    sys.exit(0)
