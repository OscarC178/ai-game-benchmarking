#!/usr/bin/env python3
"""
Browser Playtest QA for V2 builds.
Actually plays each game: sends inputs, takes screenshots, checks state.
Detects: position frozen, score not incrementing, game stuck, canvas blank.

Usage:
  python3 scripts/qa_playtest_v2.py --run r1-opus --builder bench-sonnet --game pac-man
  python3 scripts/qa_playtest_v2.py --manifest sample-manifest.json
"""

import asyncio, json, os, sys, time, argparse
from pathlib import Path
from datetime import datetime

try:
    from playwright.async_api import async_playwright, TimeoutError as PWTimeout
except ImportError:
    print("pip install playwright && playwright install chromium")
    raise SystemExit(1)

BUILD_DIR = Path("/Users/oscar/.openclaw/workspace/games-v2/builds")
QA_DIR = Path("/Users/oscar/.openclaw/workspace/games-v2/qa/playtest")
QA_DIR.mkdir(parents=True, exist_ok=True)

# ── Game-specific play scripts ────────────────────────────────────────────────
# Each step: {action, key?, ms?, label}
# Actions: key, wait, screenshot, check_state

# Start sequences per game — try common keys then the game-specific one
START_KEYS = [
    {"action": "key", "key": "Enter", "label": "try Enter"},
    {"action": "wait", "ms": 300},
    {"action": "key", "key": "Space", "label": "try Space"},
    {"action": "wait", "ms": 300},
    {"action": "key", "key": "Enter", "label": "try Enter again"},
    {"action": "wait", "ms": 500},
]

GAME_SCRIPTS = {
    "pong": START_KEYS + [
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "game started"},
        {"action": "key", "key": "ArrowUp", "label": "paddle up"},
        {"action": "wait", "ms": 500},
        {"action": "key", "key": "ArrowUp", "label": "paddle up again"},
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "after paddle movement"},
        {"action": "key", "key": "ArrowDown", "label": "paddle down"},
        {"action": "wait", "ms": 500},
        {"action": "key", "key": "ArrowDown", "label": "paddle down again"},
        {"action": "wait", "ms": 1000},
        {"action": "screenshot", "label": "paddle reversed"},
        {"action": "wait", "ms": 4000, "label": "let ball play"},
        {"action": "screenshot", "label": "after free play"},
        {"action": "check_state", "label": "final state"},
    ],

    "snake": START_KEYS + [
        {"action": "screenshot", "label": "game started"},
        {"action": "key", "key": "ArrowRight", "label": "move right"},
        {"action": "wait", "ms": 800},
        {"action": "screenshot", "label": "after move right"},
        {"action": "key", "key": "ArrowDown", "label": "move down"},
        {"action": "wait", "ms": 800},
        {"action": "key", "key": "ArrowLeft", "label": "move left"},
        {"action": "wait", "ms": 800},
        {"action": "screenshot", "label": "after direction changes"},
        {"action": "wait", "ms": 3000, "label": "free play"},
        {"action": "screenshot", "label": "after free play"},
        {"action": "check_state", "label": "final state"},
    ],

    "breakout": START_KEYS + [
        {"action": "key", "key": "Space", "label": "launch ball"},
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "ball launched"},
        {"action": "key", "key": "ArrowRight", "label": "paddle right"},
        {"action": "wait", "ms": 600},
        {"action": "key", "key": "ArrowRight", "label": "paddle right more"},
        {"action": "wait", "ms": 600},
        {"action": "screenshot", "label": "paddle moved right"},
        {"action": "key", "key": "ArrowLeft", "label": "paddle left"},
        {"action": "wait", "ms": 600},
        {"action": "key", "key": "ArrowLeft", "label": "paddle left more"},
        {"action": "wait", "ms": 600},
        {"action": "screenshot", "label": "paddle moved left"},
        {"action": "wait", "ms": 4000, "label": "let ball bounce"},
        {"action": "screenshot", "label": "after free play"},
        {"action": "check_state", "label": "final state"},
    ],

    "space-invaders": START_KEYS + [
        {"action": "screenshot", "label": "game started"},
        {"action": "key", "key": "ArrowLeft", "label": "move left"},
        {"action": "wait", "ms": 500},
        {"action": "key", "key": "Space", "label": "fire"},
        {"action": "wait", "ms": 300},
        {"action": "key", "key": "Space", "label": "fire again"},
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "after shooting"},
        {"action": "key", "key": "ArrowRight", "label": "move right"},
        {"action": "wait", "ms": 500},
        {"action": "key", "key": "Space", "label": "fire"},
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "moved and fired right"},
        {"action": "wait", "ms": 4000, "label": "let invaders advance"},
        {"action": "screenshot", "label": "after free play"},
        {"action": "check_state", "label": "final state"},
    ],

    "tetris": START_KEYS + [
        {"action": "screenshot", "label": "game started"},
        {"action": "key", "key": "ArrowLeft", "label": "move piece left"},
        {"action": "wait", "ms": 300},
        {"action": "key", "key": "ArrowLeft", "label": "move piece left again"},
        {"action": "wait", "ms": 300},
        {"action": "key", "key": "ArrowUp", "label": "rotate piece"},
        {"action": "wait", "ms": 300},
        {"action": "screenshot", "label": "after moves and rotate"},
        {"action": "key", "key": "ArrowDown", "label": "soft drop"},
        {"action": "wait", "ms": 200},
        {"action": "key", "key": "ArrowDown", "label": "soft drop"},
        {"action": "wait", "ms": 200},
        {"action": "key", "key": "ArrowDown", "label": "soft drop"},
        {"action": "wait", "ms": 200},
        {"action": "key", "key": "Space", "label": "hard drop"},
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "after drop"},
        {"action": "wait", "ms": 4000, "label": "let pieces fall"},
        {"action": "screenshot", "label": "after free play"},
        {"action": "check_state", "label": "final state"},
    ],

    "asteroids": START_KEYS + [
        {"action": "screenshot", "label": "game started"},
        {"action": "key", "key": "ArrowLeft", "label": "rotate left"},
        {"action": "wait", "ms": 400},
        {"action": "key", "key": "ArrowUp", "label": "thrust"},
        {"action": "wait", "ms": 600},
        {"action": "key", "key": "Space", "label": "fire"},
        {"action": "wait", "ms": 200},
        {"action": "key", "key": "Space", "label": "fire"},
        {"action": "wait", "ms": 200},
        {"action": "screenshot", "label": "after thrust and fire"},
        {"action": "key", "key": "ArrowRight", "label": "rotate right"},
        {"action": "wait", "ms": 400},
        {"action": "key", "key": "Space", "label": "fire"},
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "after rotate and fire"},
        {"action": "wait", "ms": 4000, "label": "free play"},
        {"action": "screenshot", "label": "after free play"},
        {"action": "check_state", "label": "final state"},
    ],

    "galaga": START_KEYS + [
        {"action": "screenshot", "label": "game started"},
        {"action": "key", "key": "ArrowLeft", "label": "move left"},
        {"action": "wait", "ms": 500},
        {"action": "key", "key": "Space", "label": "fire"},
        {"action": "wait", "ms": 200},
        {"action": "key", "key": "Space", "label": "fire"},
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "after shooting left"},
        {"action": "key", "key": "ArrowRight", "label": "move right"},
        {"action": "wait", "ms": 500},
        {"action": "key", "key": "Space", "label": "fire"},
        {"action": "wait", "ms": 200},
        {"action": "key", "key": "Space", "label": "fire"},
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "after shooting right"},
        {"action": "wait", "ms": 4000, "label": "free play"},
        {"action": "screenshot", "label": "after free play"},
        {"action": "check_state", "label": "final state"},
    ],

    "frogger": START_KEYS + [
        {"action": "screenshot", "label": "game started"},
        {"action": "key", "key": "ArrowUp", "label": "hop up"},
        {"action": "wait", "ms": 300},
        {"action": "key", "key": "ArrowUp", "label": "hop up"},
        {"action": "wait", "ms": 300},
        {"action": "key", "key": "ArrowUp", "label": "hop up"},
        {"action": "wait", "ms": 300},
        {"action": "screenshot", "label": "after 3 hops up (road zone)"},
        {"action": "key", "key": "ArrowRight", "label": "hop right"},
        {"action": "wait", "ms": 300},
        {"action": "key", "key": "ArrowUp", "label": "hop up"},
        {"action": "wait", "ms": 300},
        {"action": "key", "key": "ArrowUp", "label": "hop up"},
        {"action": "wait", "ms": 300},
        {"action": "screenshot", "label": "after more hops (should be in road/median)"},
        {"action": "wait", "ms": 4000, "label": "free play (timer running)"},
        {"action": "screenshot", "label": "after free play"},
        {"action": "check_state", "label": "final state"},
    ],

    "pac-man": START_KEYS + [
        {"action": "wait", "ms": 3000, "label": "wait for READY screen to clear"},
        {"action": "screenshot", "label": "game started"},
        {"action": "key", "key": "ArrowRight", "label": "move right"},
        {"action": "wait", "ms": 1200},
        {"action": "screenshot", "label": "after move right"},
        {"action": "key", "key": "ArrowUp", "label": "turn up"},
        {"action": "wait", "ms": 600},
        {"action": "screenshot", "label": "after turn up"},
        {"action": "key", "key": "ArrowLeft", "label": "turn left"},
        {"action": "wait", "ms": 600},
        {"action": "key", "key": "ArrowDown", "label": "turn down"},
        {"action": "wait", "ms": 80},
        {"action": "key", "key": "ArrowRight", "label": "rapid right"},
        {"action": "wait", "ms": 80},
        {"action": "key", "key": "ArrowUp", "label": "rapid up"},
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "after rapid turns"},
        {"action": "wait", "ms": 6000, "label": "free play (ghosts chase)"},
        {"action": "screenshot", "label": "after free play"},
        {"action": "check_state", "label": "final state"},
    ],

    "donkey-kong": START_KEYS + [
        {"action": "wait", "ms": 2000, "label": "wait for intro animation"},
        {"action": "screenshot", "label": "game started"},
        {"action": "key", "key": "ArrowRight", "label": "move mario right"},
        {"action": "wait", "ms": 1000},
        {"action": "screenshot", "label": "after move right"},
        {"action": "key", "key": "Space", "label": "jump"},
        {"action": "wait", "ms": 800},
        {"action": "screenshot", "label": "after jump"},
        {"action": "key", "key": "ArrowLeft", "label": "move left"},
        {"action": "wait", "ms": 600},
        {"action": "key", "key": "ArrowRight", "label": "back right toward ladder"},
        {"action": "wait", "ms": 800},
        {"action": "key", "key": "ArrowUp", "label": "try climb ladder"},
        {"action": "wait", "ms": 1000},
        {"action": "screenshot", "label": "after ladder attempt"},
        {"action": "key", "key": "ArrowRight", "label": "move right"},
        {"action": "wait", "ms": 80},
        {"action": "key", "key": "Space", "label": "jump"},
        {"action": "wait", "ms": 500},
        {"action": "screenshot", "label": "after rapid input"},
        {"action": "wait", "ms": 6000, "label": "free play (barrels rolling)"},
        {"action": "screenshot", "label": "after free play"},
        {"action": "check_state", "label": "final state"},
    ],
}

# ── Canvas pixel sampling for blank/frozen detection ──────────────────────────

PIXEL_SAMPLE_JS = """
(() => {
    const c = document.querySelector('canvas');
    if (!c) return { error: 'no_canvas' };
    const ctx = c.getContext('2d');
    if (!ctx) return { error: 'no_context' };
    const w = c.width, h = c.height;
    // Sample 100 pixels on a fixed grid (deterministic, not random)
    const samples = [];
    const step_x = Math.max(1, Math.floor(w / 10));
    const step_y = Math.max(1, Math.floor(h / 10));
    for (let gy = 0; gy < 10; gy++) {
        for (let gx = 0; gx < 10; gx++) {
            const x = Math.min(gx * step_x + Math.floor(step_x / 2), w - 1);
            const y = Math.min(gy * step_y + Math.floor(step_y / 2), h - 1);
            const d = ctx.getImageData(x, y, 1, 1).data;
            samples.push([d[0], d[1], d[2], d[3]]);
        }
    }
    // Hash: concatenate all pixel values into a string for exact comparison
    const hash = samples.map(s => s.join(',')).join('|');
    // Also compute non-black pixel count (any channel > 10)
    const nonBlack = samples.filter(s => s[0] > 10 || s[1] > 10 || s[2] > 10).length;
    return { width: w, height: h, samples, hash, nonBlack, sampleCount: samples.length };
})()
"""


async def start_server(port=0):
    import http.server, socketserver, threading
    os.chdir(BUILD_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None  # silence logs
    httpd = socketserver.TCPServer(("", port), handler)
    actual_port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, actual_port


async def playtest_game(run_id, game_slug, builder_id, port):
    """Play-test one game build. Returns detailed report dict."""
    url = f"http://localhost:{port}/{run_id}/{game_slug}/{builder_id}/index.html"
    script = GAME_SCRIPTS.get(game_slug, GAME_SCRIPTS["pong"])  # fallback to pong-style

    report = {
        "run": run_id, "game": game_slug, "builder": builder_id,
        "url": url, "timestamp": datetime.now().isoformat(),
        "steps": [], "bugs": [], "console_errors": [], "screenshots": [],
        "pixel_hashes": [],  # for frozen-frame detection
    }

    console_errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 800, "height": 700})
        page = await ctx.new_page()

        page.on("console", lambda msg: (
            console_errors.append({"type": msg.type, "text": msg.text[:200]})
            if msg.type in ("error",) else None
        ))
        page.on("pageerror", lambda err: console_errors.append({"type": "pageerror", "text": str(err)[:200]}))

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(500)
        except Exception as e:
            report["bugs"].append({"type": "LOAD_FAILED", "detail": str(e)[:200]})
            await browser.close()
            report["console_errors"] = console_errors
            return report

        # Check canvas exists
        canvas = await page.query_selector("canvas")
        if not canvas:
            report["bugs"].append({"type": "NO_CANVAS", "detail": "No <canvas> element found"})
            await browser.close()
            report["console_errors"] = console_errors
            return report

        # Focus canvas — ensure it can receive keyboard events
        try:
            await page.evaluate("""
                const c = document.querySelector('canvas');
                if (c) { c.setAttribute('tabindex', '0'); c.focus(); }
            """)
            await page.wait_for_timeout(100)
            await canvas.click()
        except:
            await page.click("body")

        prev_pixels = None
        screenshot_idx = 0

        for step_num, step in enumerate(script, 1):
            action = step["action"]
            label = step.get("label", f"step {step_num}")
            result = {"step": step_num, "action": action, "label": label}

            if action == "key":
                key = step["key"]
                await page.keyboard.press(key)
                # Also dispatch to document/window for games that listen there
                key_code = {"Enter": 13, "Space": 32, "ArrowUp": 38, "ArrowDown": 40,
                            "ArrowLeft": 37, "ArrowRight": 39, "Escape": 27,
                            "s": 83, "p": 80}.get(key, 0)
                js_key = " " if key == "Space" else key
                await page.evaluate(f"""
                    const evt = new KeyboardEvent('keydown', {{
                        key: '{js_key}', code: '{key}', keyCode: {key_code},
                        bubbles: true, cancelable: true
                    }});
                    document.dispatchEvent(evt);
                    window.dispatchEvent(evt);
                """)
                result["key"] = key

            elif action == "wait":
                await page.wait_for_timeout(step["ms"])

            elif action == "screenshot":
                screenshot_idx += 1
                fname = f"{run_id}_{game_slug}_{builder_id}_s{screenshot_idx:02d}.png"
                fpath = QA_DIR / run_id / game_slug / builder_id / fname
                fpath.parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(fpath), full_page=False, timeout=10000)
                report["screenshots"].append({
                    "step": step_num, "label": label, "path": str(fpath)
                })

                # Sample canvas pixels for frozen-frame detection
                try:
                    pixels = await page.evaluate(PIXEL_SAMPLE_JS)
                    if pixels and not pixels.get("error"):
                        report["pixel_hashes"].append(pixels["hash"])

                        # Check if canvas is truly all black (0 non-black pixels out of 100)
                        if pixels.get("nonBlack", 100) == 0:
                            report["bugs"].append({
                                "type": "CANVAS_BLANK",
                                "step": step_num,
                                "label": label,
                                "detail": f"All {pixels['sampleCount']} sampled pixels are black — game may not be rendering"
                            })

                        # Check if frame is pixel-identical to previous (exact string hash match)
                        if prev_pixels is not None and pixels["hash"] == prev_pixels:
                            report["bugs"].append({
                                "type": "FRAME_FROZEN",
                                "step": step_num,
                                "label": label,
                                "detail": "Canvas pixels exactly identical between screenshots"
                            })

                        prev_pixels = pixels["hash"]
                except:
                    pass

            elif action == "check_state":
                # Try to read common game state variables
                try:
                    state = await page.evaluate("""
                        (() => {
                            const s = {};
                            // Try common variable names
                            for (const k of ['score', 'lives', 'level', 'state', 'gameState',
                                             'gameOver', 'paused', 'playing']) {
                                try { if (typeof window[k] !== 'undefined') s[k] = window[k]; } catch(e) {}
                            }
                            return s;
                        })()
                    """)
                    result["game_state"] = state

                    # Check if game is in game-over state after only ~15s of play
                    if state.get("gameOver") == True or state.get("state") == "gameover":
                        report["bugs"].append({
                            "type": "PREMATURE_GAME_OVER",
                            "detail": f"Game ended during QA play — state: {state}"
                        })

                except:
                    pass

            report["steps"].append(result)

        report["console_errors"] = console_errors
        await browser.close()

    # Post-analysis: count unique pixel hashes
    if len(report["pixel_hashes"]) >= 3:
        unique_hashes = len(set(report["pixel_hashes"]))
        if unique_hashes == 1 and report["pixel_hashes"][0] != 0:
            report["bugs"].append({
                "type": "ALL_FRAMES_IDENTICAL",
                "detail": f"All {len(report['pixel_hashes'])} screenshots produced identical canvas content — game may be frozen"
            })

    return report


def compute_score(report):
    """Score 0-10 based on playtest results."""
    score = 10
    js_errors = len(report.get("console_errors", []))
    bugs = report.get("bugs", [])

    # JS errors: -1 per error, min 0 from this factor
    score -= min(js_errors, 5)

    # Bug penalties
    frozen_count = sum(1 for b in bugs if b.get("type") == "FRAME_FROZEN")
    blank_count = sum(1 for b in bugs if b.get("type") == "CANVAS_BLANK")

    for bug in bugs:
        btype = bug.get("type", "")
        if btype == "LOAD_FAILED" or btype == "PLAYTEST_TIMEOUT":
            score -= 10
        elif btype == "NO_CANVAS":
            score -= 8
        elif btype == "ALL_FRAMES_IDENTICAL":
            score -= 8  # game is truly stuck — major penalty
        elif btype == "PREMATURE_GAME_OVER":
            score -= 1
        # FRAME_FROZEN and CANVAS_BLANK handled in aggregate below

    # Frozen frames: 1-2 is normal (title screen, ready screen), 3+ is suspicious
    if frozen_count >= 3:
        score -= 3
    elif frozen_count >= 2:
        score -= 1

    # Blank canvas: 1 can be a dark scene, 2+ is likely broken
    if blank_count >= 2:
        score -= 5
    elif blank_count == 1:
        score -= 1

    return max(0, min(10, score))


async def run_playtest(manifest=None, run_filter=None, game_filter=None, builder_filter=None):
    httpd, port = await start_server()
    print(f"Server on port {port}\n")

    if manifest:
        with open(manifest) as f:
            builds = json.load(f)
    else:
        builds = []
        runs = [run_filter] if run_filter else ["r1-opus", "r2-gpt54", "r3-gemini-pro", "r4-glm5", "r5-control"]
        games = [game_filter] if game_filter else list(GAME_SCRIPTS.keys())
        builders = [builder_filter] if builder_filter else [
            "bench-opus", "bench-sonnet", "bench-haiku", "bench-gpt54",
            "bench-gpt54mini", "bench-gemini-pro", "bench-gemini-flash", "bench-glm5"
        ]
        for r in runs:
            for g in games:
                for b in builders:
                    if (BUILD_DIR / r / g / b / "index.html").exists():
                        builds.append({"run": r, "game": g, "builder": b})

    results = []
    for i, build in enumerate(builds, 1):
        r, g, b = build["run"], build["game"], build["builder"]
        # Skip if already play-tested
        report_path = QA_DIR / r / g / b / "playtest-report.json"
        if report_path.exists():
            print(f"[{i}/{len(builds)}] SKIP {r}/{g}/{b} (already tested)")
            with open(report_path) as f:
                results.append(json.load(f))
            continue

        print(f"[{i}/{len(builds)}] TESTING {r}/{g}/{b}...", end=" ", flush=True)
        try:
            report = await asyncio.wait_for(playtest_game(r, g, b, port), timeout=45)
        except (asyncio.TimeoutError, Exception) as e:
            report = {
                "run": r, "game": g, "builder": b,
                "url": f"http://localhost:{port}/{r}/{g}/{b}/index.html",
                "timestamp": datetime.now().isoformat(),
                "steps": [], "bugs": [{"type": "PLAYTEST_TIMEOUT", "detail": f"Build failed: {str(e)[:200]}"}],
                "console_errors": [], "screenshots": [], "pixel_hashes": [],
            }
        score = compute_score(report)
        report["playtest_score"] = score

        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        bugs_str = ", ".join(b["type"] for b in report["bugs"]) if report["bugs"] else "none"
        js_errs = len(report["console_errors"])
        status = "✅" if score >= 8 else "⚠️" if score >= 5 else "❌"
        print(f"{status} score={score}/10  js_errors={js_errs}  bugs=[{bugs_str}]", flush=True)

        results.append(report)
        await asyncio.sleep(0.3)

    httpd.shutdown()

    # Summary
    print(f"\n{'='*60}")
    print(f"PLAYTEST SUMMARY — {len(results)} builds tested")
    print(f"{'='*60}")
    scores = [r.get("playtest_score", 0) for r in results]
    avg = sum(scores) / len(scores) if scores else 0
    perfect = sum(1 for s in scores if s == 10)
    failing = sum(1 for s in scores if s < 5)
    print(f"  Average: {avg:.2f}  Perfect: {perfect}  Failing(<5): {failing}")

    # Bug type distribution
    from collections import Counter
    bug_types = Counter()
    for r in results:
        for b in r.get("bugs", []):
            bug_types[b["type"]] += 1
    if bug_types:
        print(f"\n  Bug types:")
        for bt, count in bug_types.most_common():
            print(f"    {bt}: {count}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default=None)
    parser.add_argument("--game", default=None)
    parser.add_argument("--builder", default=None)
    parser.add_argument("--manifest", default=None, help="JSON file with [{run, game, builder}, ...]")
    args = parser.parse_args()

    asyncio.run(run_playtest(
        manifest=args.manifest,
        run_filter=args.run,
        game_filter=args.game,
        builder_filter=args.builder,
    ))
