#!/usr/bin/env python3
"""
Targeted test: GPT-5.4 Mini as builder against GLM-5 specs.
Reuses specs from r4-glm5, builds with bench-gpt54mini only.
"""
import os, subprocess, json, pathlib, time
from generate_lib import (
    LOG_FILE, MAX_ATTEMPTS, BUILD_TIMEOUT,
    log, BUILD_DIR, GAME_INSTRUCTIONS
)

RUN_ID = "r4-glm5-mini"
GAMES = ["pong", "snake", "breakout", "space-invaders", "tetris",
         "asteroids", "galaga", "frogger", "pac-man", "donkey-kong"]
BUILDER = "bench-gpt54mini"
SPEC_SOURCE_RUN = "r4-glm5"  # specs from here

BUILD_DIR = pathlib.Path(__file__).parent.parent / "builds"
LOG_FILE = pathlib.Path(__file__).parent.parent / "build-log-mini-glm5.txt"
RESULTS_FILE = pathlib.Path(__file__).parent.parent / "reports" / "results-mini-glm5.json"

SYSTEM_PROMPT = """You are a game builder. Write the complete HTML5 game code.

Rules:
1. Write a complete, self-contained index.html — single file, no external deps
2. Canvas-based rendering at 800x600
3. Include window.__qa bridge for testing:
   window.__qa = { gameReady(), gameState, playerPos, score, gameStatus }
4. On game start: window.__qa.gameState = "PLAYING"
5. Store player position as window.__qa.playerPos = {x, y}
6. Handle errors gracefully — wrap draw/update loops in try/catch
7. Min console.error noise — game should run without errors
8. Include game-specific QA hooks from GAME_INSTRUCTIONS below

After writing, say exactly: BUILD_COMPLETE"""

results = []

for game in GAMES:
    slug = game.replace("-", "_")
    spec_path = pathlib.Path(__file__).parent.parent / "specs" / SPEC_SOURCE_RUN / game / "spec.md"
    
    if not spec_path.exists():
        log(f"SKIP {RUN_ID}/{game}/{BUILDER} — no spec")
        results.append({"run": RUN_ID, "game": game, "builder": BUILDER, "status": "missing", "final_score": None, "browser_bugs": 0})
        continue

    spec_content = spec_path.read_text()
    instructions = GAME_INSTRUCTIONS.get(game, "")
    prompt = f"""{SYSTEM_PROMPT}

GAME_INSTRUCTIONS:
{instructions}

SPEC:
{spec_content}

After writing the file, say exactly: BUILD_COMPLETE"""

    game_build_dir = BUILD_DIR / RUN_ID / game / BUILDER
    game_build_dir.mkdir(parents=True, exist_ok=True)
    (game_build_dir / "spec.md").write_text(spec_content)

    success = False
    attempt = 1
    raw_output = ""

    while attempt <= MAX_ATTEMPTS and not success:
        session_id = f"v2-{RUN_ID}-{slug}-{BUILDER}-a{attempt}"
        log(f"BUILD {RUN_ID}/{slug}/{BUILDER} attempt {attempt}/{MAX_ATTEMPTS}")

        try:
            clean_env = {k: v for k, v in os.environ.items() if k != "OPENROUTER_API_KEY"}
            result = subprocess.run(
                ["openclaw", "agent", "--local", "--agent", BUILDER,
                 "--session-id", session_id, "--message", prompt,
                 "--timeout", str(BUILD_TIMEOUT)],
                capture_output=True, text=True, timeout=BUILD_TIMEOUT + 60,
                env=clean_env,
            )
            raw_output = result.stdout + "\n---STDERR---\n" + result.stderr
            (game_build_dir / f"raw_output_a{attempt}.txt").write_text(raw_output)

            if "BUILD_COMPLETE" in raw_output:
                success = True
                log(f"OK {RUN_ID}/{slug}/{BUILDER} attempt {attempt}")
            else:
                log(f"RETRY {RUN_ID}/{slug}/{BUILDER} attempt {attempt} — no BUILD_COMPLETE")
                attempt += 1
        except subprocess.TimeoutExpired:
            log(f"TIMEOUT {RUN_ID}/{slug}/{BUILDER} attempt {attempt}")
            attempt += 1
        except Exception as e:
            log(f"ERROR {RUN_ID}/{slug}/{BUILDER} attempt {attempt} — {e}")
            attempt += 1
        time.sleep(1)

    if success:
        # Find the index.html in raw output
        import re
        html_matches = re.findall(r'```html\n(.*?)```', raw_output, re.DOTALL)
        if not html_matches:
            html_matches = re.findall(r'<html.*?</html>', raw_output, re.DOTALL | re.IGNORECASE)
        
        if html_matches:
            html = html_matches[-1]
            index_path = game_build_dir / "index.html"
            index_path.write_text(html)
            log(f"WROTE {RUN_ID}/{slug}/{BUILDER} ({len(html)} chars)")
            results.append({"run": RUN_ID, "game": game, "builder": BUILDER, "status": "complete", "final_score": None, "browser_bugs": 0})
        else:
            log(f"FAIL {RUN_ID}/{slug}/{BUILDER} — no HTML found")
            results.append({"run": RUN_ID, "game": game, "builder": BUILDER, "status": "DNF", "final_score": None, "browser_bugs": 0})
    else:
        (game_build_dir / "dnf.txt").write_text("No BUILD_COMPLETE after 3 attempts\n" + raw_output[-2000:])
        log(f"DNF {RUN_ID}/{slug}/{BUILDER}")
        results.append({"run": RUN_ID, "game": game, "builder": BUILDER, "status": "DNF", "final_score": None, "browser_bugs": 0})

print("\n=== RESULTS ===")
for r in results:
    print(f"  {r['game']}: {r['status']}")

# Save results
with open(RESULTS_FILE, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {RESULTS_FILE}")
