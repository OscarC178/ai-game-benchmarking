#!/usr/bin/env python3
"""
Browser QA Agent — plays HTML5 games via Playwright and reports bugs.

Usage:
  python3 scripts/browser_qa_agent.py --game pac-man --model sonnet --run run1-opus-plan
  python3 scripts/browser_qa_agent.py --game pac-man --model sonnet --run run1-opus-plan --port 7890

Requires: pip install playwright && playwright install chromium
"""

import argparse
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime

try:
    from playwright.async_api import async_playwright, TimeoutError as PWTimeout
except ImportError:
    print("❌  Playwright not installed. Run:")
    print("    pip install playwright && playwright install chromium")
    raise SystemExit(1)

ROOT = Path("/Users/oscar/.openclaw/workspace/games")
REPORTS_DIR = Path("/Users/oscar/.openclaw/workspace/scripts/qa-browser-reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Key sequences per game ────────────────────────────────────────────────────

GAME_SCRIPTS = {
    "donkey-kong": [
        # Phase 1: start the game (Enter or Space)
        {"action": "key",        "key": "Enter",       "label": "start game"},
        {"action": "wait",       "ms": 1500,            "label": "wait for game to begin"},
        {"action": "check_state","label": "confirm PLAYING state (stateNum should be 1)"},

        # Phase 2: move right — mario should run toward ladder
        {"action": "key",        "key": "ArrowRight",  "label": "move mario right"},
        {"action": "wait",       "ms": 1000},
        {"action": "screenshot", "label": "mario should be moving right from spawn"},

        # Phase 3: jump — Space bar jumps over barrels (main mechanic)
        {"action": "key",        "key": "Space",        "label": "jump — key mechanic"},
        {"action": "wait",       "ms": 800},
        {"action": "screenshot", "label": "after jump — mario should have moved/scored"},

        # Phase 4: move left
        {"action": "key",        "key": "ArrowLeft",   "label": "reverse direction"},
        {"action": "wait",       "ms": 600},
        {"action": "screenshot", "label": "moving left — direction changed?"},

        # Phase 5: try to climb a ladder (ArrowUp)
        {"action": "key",        "key": "ArrowRight",  "label": "back right toward ladder"},
        {"action": "wait",       "ms": 800},
        {"action": "key",        "key": "ArrowUp",     "label": "attempt ladder climb"},
        {"action": "wait",       "ms": 1000},
        {"action": "screenshot", "label": "after ladder attempt — mario higher up?"},

        # Phase 6: rapid keys — stress test
        {"action": "key",        "key": "ArrowRight",  "label": "rapid: right"},
        {"action": "wait",       "ms": 80},
        {"action": "key",        "key": "Space",        "label": "rapid: jump"},
        {"action": "wait",       "ms": 80},
        {"action": "key",        "key": "ArrowLeft",   "label": "rapid: left"},
        {"action": "wait",       "ms": 500},
        {"action": "screenshot", "label": "after rapid inputs — frozen or moving?"},

        # Phase 7: free play 6s — let barrels spawn and roll
        {"action": "wait",       "ms": 6000,            "label": "free play 6s"},
        {"action": "screenshot", "label": "end of free play — score, lives, position"},

        # Phase 8: final state
        {"action": "check_state","label": "final game state read"},
    ],

    "pac-man": [
        # Phase 1: start the game, wait for READY → PLAYING transition (~3.5s)
        {"action": "key",        "key": "Enter",      "label": "start game"},
        {"action": "wait",       "ms": 4000,           "label": "wait for READY screen to clear (needs ~3.5s)"},
        {"action": "check_state","label": "confirm PLAYING state (stateNum should be 2)"},

        # Phase 2: move right, collect dots in the bottom corridor
        {"action": "key",        "key": "ArrowRight",  "label": "move right"},
        {"action": "wait",       "ms": 1200},
        {"action": "screenshot", "label": "moving right — Pac-Man should be east of start"},

        # Phase 3: turn up — the trapped-turn bug fires here (buffered at non-centre position)
        {"action": "key",        "key": "ArrowUp",     "label": "request turn up (trap bug candidate)"},
        {"action": "wait",       "ms": 600},
        {"action": "screenshot", "label": "after turn up — moving north or stuck?"},

        # Phase 4: turn left mid-corridor
        {"action": "key",        "key": "ArrowLeft",   "label": "request turn left"},
        {"action": "wait",       "ms": 600},
        {"action": "screenshot", "label": "after turn left — direction changed?"},

        # Phase 5: rapid direction changes — stress-test the 4px buffer window
        {"action": "key",        "key": "ArrowDown",   "label": "rapid: down"},
        {"action": "wait",       "ms": 80},
        {"action": "key",        "key": "ArrowRight",  "label": "rapid: right"},
        {"action": "wait",       "ms": 80},
        {"action": "key",        "key": "ArrowUp",     "label": "rapid: up"},
        {"action": "wait",       "ms": 500},
        {"action": "screenshot", "label": "after rapid turns — frozen or moving?"},

        # Phase 6: free play — 6s, let ghosts chase
        {"action": "wait",       "ms": 6000,           "label": "free play 6s"},
        {"action": "screenshot", "label": "end of free play — score, lives, position"},

        # Phase 7: final state read
        {"action": "check_state","label": "final game state read"},
    ],
}

# ── JS state inspector — reads internals from the game ────────────────────────

STATE_JS = "window.__qa || {}"

# ── Main agent ────────────────────────────────────────────────────────────────

async def run_qa(game: str, model: str, run: str, port: int) -> dict:
    url = f"http://localhost:{port}/{run}/{game}/{model}/index.html"
    script = GAME_SCRIPTS.get(game)
    if not script:
        return {"error": f"No QA script defined for game '{game}'"}

    report = {
        "game": game,
        "model": model,
        "run": run,
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "steps": [],
        "bugs": [],
        "console_errors": [],
        "screenshots": [],
        "final_state": None,
    }

    console_errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False so we can watch
        ctx = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await ctx.new_page()

        # Capture console errors
        page.on("console", lambda msg: (
            console_errors.append({"type": msg.type, "text": msg.text})
            if msg.type in ("error", "warning") else None
        ))
        page.on("pageerror", lambda err: console_errors.append({"type": "pageerror", "text": str(err)}))

        print(f"\n🎮  Opening {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(300)

        # Inject state-bridge into MAIN world via script tag (bypasses isolated context)
        await page.add_script_tag(content="""
            window.__qaState = {};
            window.__qaErrors = [];
            (function poll() {
                try {
                    window.__qaState = {
                        stateNum:  typeof state !== 'undefined' ? state       : null,
                        pacX:      typeof pac   !== 'undefined' ? pac.x       : null,
                        pacY:      typeof pac   !== 'undefined' ? pac.y       : null,
                        pacDx:     typeof pac   !== 'undefined' ? pac.dx      : null,
                        pacDy:     typeof pac   !== 'undefined' ? pac.dy      : null,
                        pacNextDx: typeof pac   !== 'undefined' ? pac.nextDx  : null,
                        pacNextDy: typeof pac   !== 'undefined' ? pac.nextDy  : null,
                        score:     typeof score !== 'undefined' ? score       : null,
                        lives:     typeof lives !== 'undefined' ? lives       : null,
                        dotsLeft:  typeof dots  !== 'undefined'
                                     ? (Array.isArray(dots) ? dots.filter(d=>!d.eaten).length : null)
                                     : null,
                        ts: Date.now(),
                    };
                } catch(e) { window.__qaErrors.push(String(e)); }
                setTimeout(poll, 100);
            })();
        """)
        await page.wait_for_timeout(200)

        # Click canvas to focus keyboard events
        try:
            canvas = page.locator("canvas")
            if await canvas.count():
                await canvas.first.click()
        except Exception:
            await page.click("body")

        step_num = 0
        prev_state = None

        for step in script:
            step_num += 1
            action = step["action"]
            label  = step.get("label", f"step {step_num}")
            print(f"  [{step_num:02d}] {action:12s} — {label}")

            result = {"step": step_num, "action": action, "label": label}

            if action == "key":
                await page.keyboard.press(step["key"])
                result["key"] = step["key"]

            elif action == "wait":
                await page.wait_for_timeout(step["ms"])
                result["ms"] = step["ms"]

            elif action == "screenshot":
                ts = int(time.time() * 1000)
                fname = f"{run}_{game}_{model}_step{step_num:02d}_{ts}.png"
                fpath = REPORTS_DIR / fname
                await page.screenshot(path=str(fpath), full_page=False)
                result["screenshot"] = str(fpath)
                report["screenshots"].append({"step": step_num, "label": label, "path": str(fpath)})
                print(f"         📸  saved → {fname}")

                # Read game state via injected bridge
                js_state = await page.evaluate(STATE_JS)
                result["js_state"] = js_state

                # Pretty-print depending on game
                if js_state:
                    if game == "donkey-kong" and js_state.get("marioX") is not None:
                        print(f"         📊  state={js_state.get('stateNum')}  mario=({js_state.get('marioX'):.1f},{js_state.get('marioY'):.1f})  score={js_state.get('score')}  lives={js_state.get('lives')}")
                    elif js_state.get("pacX") is not None:
                        print(f"         📊  state={js_state.get('stateNum')}  pos=({js_state.get('pacX'):.1f},{js_state.get('pacY'):.1f})  dir=({js_state.get('pacDx')},{js_state.get('pacDy')})  next=({js_state.get('pacNextDx')},{js_state.get('pacNextDy')})  score={js_state.get('score')}")
                    else:
                        print(f"         📊  {js_state}")

                # Bug detection: player position unchanged between screenshots
                # For pac-man: uses pacX/pacY; for donkey-kong: uses marioX/marioY
                px_key = "marioX" if game == "donkey-kong" else "pacX"
                py_key = "marioY" if game == "donkey-kong" else "pacY"
                # PLAYING state: DK uses 1, pac-man uses 2
                playing_state = 1 if game == "donkey-kong" else 2

                if prev_state and js_state and js_state.get(px_key) is not None:
                    dx_moved = abs((js_state.get(px_key) or 0) - (prev_state.get(px_key) or 0))
                    dy_moved = abs((js_state.get(py_key) or 0) - (prev_state.get(py_key) or 0))
                    is_playing = js_state.get("stateNum") == playing_state

                    if dx_moved < 1 and dy_moved < 1 and is_playing:
                        entity = "Mario" if game == "donkey-kong" else "Pac-Man"
                        bug = {
                            "type": "POSITION_FROZEN",
                            "step": step_num,
                            "label": label,
                            "detail": f"{entity} position unchanged from step {step_num-3}: ({js_state[px_key]:.1f}, {js_state[py_key]:.1f})",
                            "state": js_state,
                        }
                        report["bugs"].append(bug)
                        print(f"         🐛  BUG: position frozen at ({js_state[px_key]:.1f}, {js_state[py_key]:.1f})")

                    # Turn-buffering check (pac-man only)
                    if game == "pac-man":
                        prev_next = (prev_state.get("pacNextDx"), prev_state.get("pacNextDy"))
                        curr_dir  = (js_state.get("pacDx"),     js_state.get("pacDy"))
                        curr_next = (js_state.get("pacNextDx"), js_state.get("pacNextDy"))
                        if (prev_next != (0, 0) and prev_next != curr_dir and
                                curr_next == prev_next and is_playing):
                            result["note"] = (
                                f"Turn buffer still pending: intended={prev_next} "
                                f"actual_dir={curr_dir} — possible turn-trap"
                            )
                            print(f"         ⚠️   Turn still buffered: wanted {prev_next} but moving {curr_dir}")

                prev_state = js_state

            elif action == "check_state":
                js_state = await page.evaluate(STATE_JS)
                # Also grab any bridge errors
                bridge_errors = await page.evaluate("window.__qaErrors || []")
                result["js_state"] = js_state
                result["bridge_errors"] = bridge_errors
                report["final_state"] = js_state
                print(f"         📊  state={js_state.get('stateNum')} score={js_state.get('score')} lives={js_state.get('lives')} dots_left={js_state.get('dotsLeft')}")

                # Final checks — state expectations differ by game
                playing_state_final = 1 if game == "donkey-kong" else 2
                paused_state_final  = 2 if game == "donkey-kong" else 3
                allowed_states = (None, playing_state_final, paused_state_final)

                if js_state.get("stateNum") not in allowed_states:
                    report["bugs"].append({
                        "type": "UNEXPECTED_GAME_STATE",
                        "detail": f"Game ended unexpectedly — state is {js_state.get('stateNum')} (expected {playing_state_final}=PLAYING or {paused_state_final}=PAUSED)",
                    })

                if js_state.get("score") == 0 and js_state.get("stateNum") == playing_state_final:
                    entity = "Mario" if game == "donkey-kong" else "Pac-Man"
                    report["bugs"].append({
                        "type": "SCORE_NOT_INCREMENTING",
                        "detail": f"Score is 0 after full play session — {entity} may not be moving or scoring",
                    })

                if js_state.get("lives") is not None and int(js_state["lives"] or 3) < 3:
                    report["bugs"].append({
                        "type": "LIFE_LOST_DURING_QA",
                        "detail": f"Lives remaining: {js_state['lives']} (started with 3) — ghost collision during test",
                    })

            report["steps"].append(result)

        report["console_errors"] = console_errors
        if console_errors:
            print(f"\n  ⚠️   Console errors: {len(console_errors)}")
            for e in console_errors:
                print(f"       [{e['type']}] {e['text'][:120]}")

        await browser.close()

    return report


def print_report(report: dict):
    print("\n" + "═" * 60)
    print(f"  QA REPORT — {report['game'].upper()} / {report['model']} / {report['run']}")
    print("═" * 60)
    print(f"  URL:       {report['url']}")
    print(f"  Timestamp: {report['timestamp']}")
    print(f"  Steps run: {len(report['steps'])}")
    print(f"  Screenshots: {len(report['screenshots'])}")

    print(f"\n  FINAL STATE:")
    if report.get("final_state"):
        fs = report["final_state"]
        for k, v in fs.items():
            print(f"    {k:15s} = {v}")

    if report["bugs"]:
        print(f"\n  🐛  BUGS FOUND: {len(report['bugs'])}")
        for i, bug in enumerate(report["bugs"], 1):
            print(f"    {i}. [{bug['type']}] {bug.get('detail', '')}")
            if "step" in bug:
                print(f"       At step {bug['step']}: {bug.get('label', '')}")
    else:
        print(f"\n  ✅  No bugs detected by automated checks")

    if report["console_errors"]:
        print(f"\n  ⚠️   JS CONSOLE ERRORS: {len(report['console_errors'])}")
        for e in report["console_errors"][:5]:
            print(f"    [{e['type']}] {e['text'][:100]}")
    else:
        print(f"\n  ✅  No JS console errors")

    print("\n  SCREENSHOTS:")
    for s in report["screenshots"]:
        print(f"    [{s['step']:02d}] {s['label']}")
        print(f"         {s['path']}")

    print("═" * 60 + "\n")


async def main():
    parser = argparse.ArgumentParser(description="Browser QA agent for benchmark games")
    parser.add_argument("--game",  default="pac-man",          help="Game slug")
    parser.add_argument("--model", default="sonnet",           help="Model slug")
    parser.add_argument("--run",   default="run1-opus-plan",   help="Run dir name")
    parser.add_argument("--port",  type=int, default=7890,     help="Local server port")
    parser.add_argument("--save",  action="store_true",        help="Save JSON report")
    args = parser.parse_args()

    report = await run_qa(args.game, args.model, args.run, args.port)
    print_report(report)

    if args.save:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        out = REPORTS_DIR / f"report_{args.run}_{args.game}_{args.model}_{ts}.json"
        out.write_text(json.dumps(report, indent=2))
        print(f"  📄  Report saved → {out}\n")

    return report


if __name__ == "__main__":
    asyncio.run(main())
