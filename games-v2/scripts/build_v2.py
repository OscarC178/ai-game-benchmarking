#!/usr/bin/env python3
"""
build_v2.py — V2 Benchmark Build Orchestrator
Runs all builds sequentially using 'openclaw agent' CLI.
Uses subprocess with proper string handling to avoid bash interpolation issues.

Usage:
    python3 build_v2.py                          # Run all
    python3 build_v2.py --run r1-opus --game pong # Single combo
    python3 build_v2.py --run r1-opus             # Single run
"""
import subprocess, json, os, sys, time, pathlib, argparse, hashlib

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
V2_DIR = SCRIPT_DIR.parent
SPECS_DIR = V2_DIR / "specs"
BUILDS_DIR = V2_DIR / "builds"
VERIFY = SCRIPT_DIR / "lib" / "verify_build.py"
LOG_FILE = V2_DIR / "build-log.txt"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

MAX_ATTEMPTS = 3
BUILD_TIMEOUT = 900  # 15 min
HEARTBEAT_SECS = 1800  # 30 min

RUNS = ["r1-opus", "r2-gpt54", "r3-gemini-pro", "r4-glm5", "r5-control", "r6-mini"]

GAMES = [
    ("pong", "Pong"),
    ("snake", "Snake"),
    ("breakout", "Breakout"),
    ("space-invaders", "Space Invaders"),
    ("tetris", "Tetris"),
    ("asteroids", "Asteroids"),
    ("galaga", "Galaga"),
    ("frogger", "Frogger"),
    ("pac-man", "Pac-Man"),
    ("donkey-kong", "Donkey Kong"),
]

BUILDERS = [
    "bench-opus",
    "bench-sonnet",
    "bench-haiku",
    "bench-gpt54",
    "bench-gpt54mini",
    "bench-gemini-pro",
    "bench-gemini-flash",
    "bench-glm5",
]

MODEL_IDS = {
    "bench-opus": "anthropic/claude-opus-4.6",
    "bench-sonnet": "anthropic/claude-sonnet-4.6",
    "bench-haiku": "anthropic/claude-haiku-4.5",
    "bench-gpt54": "openai/gpt-5.4",
    "bench-gpt54mini": "palebluedot/openai/gpt-5.4-mini",
    "bench-gemini-pro": "google/gemini-3-pro-preview",
    "bench-gemini-flash": "google/gemini-3-flash-preview",
    "bench-glm5": "z-ai/glm-5",
}


def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def notify(msg):
    try:
        subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            "-d", f"chat_id={TELEGRAM_CHAT_ID}",
            "--data-urlencode", f"text={msg}",
        ], capture_output=True, timeout=10)
    except:
        pass


def verify_build(path):
    try:
        result = subprocess.run(
            ["python3", str(VERIFY), str(path)],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except:
        return "error"


def build_one(run_id, game_slug, game_name, agent_id):
    model_id = MODEL_IDS.get(agent_id, "unknown")
    spec_file = SPECS_DIR / run_id / game_slug / "spec.md"
    out_dir = BUILDS_DIR / run_id / game_slug / agent_id
    out_file = out_dir / "index.html"
    raw_log = out_dir / "raw-output.txt"

    out_dir.mkdir(parents=True, exist_ok=True)

    # Already done?
    if out_file.exists():
        check = verify_build(out_file)
        if check == "ok":
            log(f"SKIP {run_id}/{game_slug}/{agent_id}")
            return "skip"

    # Spec missing?
    if not spec_file.exists():
        log(f"SKIP {run_id}/{game_slug}/{agent_id} — no spec")
        return "skip"

    spec_content = spec_file.read_text()

    # Build the prompt — pure Python, no bash interpolation
    prompt = f"""You are an expert HTML5/JavaScript game developer.

Your task: Build a complete, playable {game_name} as a single self-contained HTML file.

SPEC:
---
{spec_content}
---

ABSOLUTE RULES:
1. You MUST use the write tool to save the file to: {out_file}
2. DO NOT output the HTML as text. Use the write tool ONLY.
3. Single file only — all CSS and JS must be inline. Zero external dependencies.
4. Use HTML5 Canvas for all rendering.
5. Include this comment block at the very top of the file:
<!--
  GAME:      {game_name}
  RUN:       {run_id}
  BUILDER:   {model_id}
-->
6. Do not ask questions. Build the game.
7. Max 3 tool calls. Plan the full game in your head first, then write the complete file in ONE write call.

After writing the file, say exactly: BUILD_COMPLETE"""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        # Unique session ID per attempt
        session_id = f"v2-{run_id}-{game_slug}-{agent_id}-a{attempt}-{os.getpid()}"

        log(f"BUILD {run_id}/{game_slug}/{agent_id} attempt {attempt}/{MAX_ATTEMPTS}")

        try:
            # Strip OPENROUTER_API_KEY so model resolver doesn't auto-discover OpenRouter
            clean_env = {k: v for k, v in os.environ.items() if k != "OPENROUTER_API_KEY"}
            result = subprocess.run(
                [
                    "openclaw", "agent",
                    "--local",
                    "--agent", agent_id,
                    "--session-id", session_id,
                    "--message", prompt,
                    "--timeout", str(BUILD_TIMEOUT),
                ],
                capture_output=True, text=True,
                timeout=BUILD_TIMEOUT + 60,  # extra buffer
                env=clean_env,
            )
            # Save raw output
            raw_log.write_text(result.stdout + "\n---STDERR---\n" + result.stderr)
        except subprocess.TimeoutExpired:
            log(f"TIMEOUT {run_id}/{game_slug}/{agent_id} attempt {attempt}")
            continue
        except Exception as e:
            log(f"ERROR {run_id}/{game_slug}/{agent_id} attempt {attempt} — {e}")
            continue

        # Verify artefact
        check = verify_build(out_file)
        if check == "ok":
            log(f"OK    {run_id}/{game_slug}/{agent_id} (attempt {attempt})")
            return "ok"
        else:
            log(f"FAIL  {run_id}/{game_slug}/{agent_id} attempt {attempt} — {check}")

    # All attempts exhausted
    log(f"DNF   {run_id}/{game_slug}/{agent_id} — all {MAX_ATTEMPTS} attempts failed")
    (out_dir / "dnf.txt").write_text("DNF")
    return "dnf"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", help="Filter to specific run (e.g. r1-opus)")
    parser.add_argument("--game", help="Filter to specific game (e.g. pong)")
    parser.add_argument("--builder", help="Filter to specific builder (e.g. bench-sonnet)")
    parser.add_argument("--skip-builder", action="append", default=[], help="Skip builder(s) (repeatable, e.g. --skip-builder bench-sonnet)")
    args = parser.parse_args()

    notify("🔨 V2 Build phase starting")
    log("BUILD START")

    stats = {"ok": 0, "skip": 0, "dnf": 0, "total": 0}
    last_heartbeat = time.time()

    for run_id in RUNS:
        if args.run and run_id != args.run:
            continue

        log(f"=== RUN: {run_id} ===")

        for game_slug, game_name in GAMES:
            if args.game and game_slug != args.game:
                continue

            log(f"--- {game_slug} ---")

            for agent_id in BUILDERS:
                if args.builder and agent_id != args.builder:
                    continue
                if agent_id in args.skip_builder:
                    continue

                stats["total"] += 1
                result = build_one(run_id, game_slug, game_name, agent_id)
                stats[result] = stats.get(result, 0) + 1

                # Heartbeat
                now = time.time()
                if now - last_heartbeat > HEARTBEAT_SECS:
                    msg = f"🔨 V2 Build progress: {stats['ok']} OK, {stats['skip']} skip, {stats['dnf']} DNF / {stats['total']} total"
                    notify(msg)
                    last_heartbeat = now

    log(f"BUILD COMPLETE — {stats['ok']} OK, {stats['skip']} skip, {stats['dnf']} DNF / {stats['total']} total")
    notify(f"✅ V2 Build phase complete — {stats['ok']} OK, {stats['skip']} skip, {stats['dnf']} DNF / {stats['total']} total")


if __name__ == "__main__":
    main()
