#!/usr/bin/env bash
# 02_build_games.sh — Phase 2: Build all games
# Sequential only — no parallel (parallel caused timeouts in V1).
# 3 attempts per build then DNF.
# Session context cleared between every build via unique --session-id.
# Crash-safe: skips already-verified builds on restart.
# Telegram heartbeat every 30 min.
#
# Usage: ./02_build_games.sh [--run r1-opus] [--game pong] [--builder bench-sonnet]

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V2_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SPECS_DIR="$V2_DIR/specs"
BUILDS_DIR="$V2_DIR/builds"
LOG_FILE="$V2_DIR/build-log.txt"
NOTIFY="$SCRIPT_DIR/lib/telegram_notify.sh"
VERIFY="$SCRIPT_DIR/lib/verify_build.py"

notify() { bash "$NOTIFY" "$1" 2>/dev/null || true; }
log()    { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_FILE"; }

FILTER_RUN=""
FILTER_GAME=""
FILTER_BUILDER=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run)     FILTER_RUN="$2";     shift 2 ;;
    --game)    FILTER_GAME="$2";    shift 2 ;;
    --builder) FILTER_BUILDER="$2"; shift 2 ;;
    *) shift ;;
  esac
done

RUNS=(r1-opus r2-gpt54 r3-gemini-pro r4-glm5 r5-control)

GAMES=(
  "pong:Pong"
  "snake:Snake"
  "breakout:Breakout"
  "space-invaders:Space Invaders"
  "tetris:Tetris"
  "asteroids:Asteroids"
  "galaga:Galaga"
  "frogger:Frogger"
  "pac-man:Pac-Man"
  "donkey-kong:Donkey Kong"
)

get_model_id() {
  case "$1" in
    bench-opus)         echo "anthropic/claude-opus-4.6" ;;
    bench-sonnet)       echo "anthropic/claude-sonnet-4.6" ;;
    bench-haiku)        echo "anthropic/claude-haiku-4.5" ;;
    bench-gpt54)        echo "openai/gpt-5.4" ;;
    bench-gpt54mini)    echo "openai/gpt-5.4-mini" ;;
    bench-gemini-pro)   echo "google/gemini-3-pro-preview" ;;
    bench-gemini-flash) echo "google/gemini-3-flash-preview" ;;
    bench-glm5)         echo "z-ai/glm-5" ;;
    *) echo "unknown" ;;
  esac
}

BUILDER_ORDER=(bench-opus bench-sonnet bench-haiku bench-gpt54 bench-gpt54mini bench-gemini-pro bench-gemini-flash bench-glm5)

MAX_ATTEMPTS=3
BUILD_TIMEOUT=900     # 15 min per attempt
HEARTBEAT_SECS=1800   # Telegram update every 30 min

total=0
built=0
dnf=0
skipped=0
last_heartbeat=$(date +%s)

mkdir -p "$BUILDS_DIR"
touch "$LOG_FILE"

notify "🔨 V2 Build phase starting — 400 builds, sequential"
log "BUILD START"

build_one() {
  local run_id="$1" game_slug="$2" game_name="$3" agent_id="$4"
  local model_id="$(get_model_id "$agent_id")"
  local spec_file="$SPECS_DIR/$run_id/$game_slug/spec.md"
  local out_dir="$BUILDS_DIR/$run_id/$game_slug/$agent_id"
  local out_file="$out_dir/index.html"
  local raw_log="$out_dir/raw-output.txt"

  mkdir -p "$out_dir"

  # Already done?
  if [[ -f "$out_file" ]]; then
    local check
    check=$(python3 "$VERIFY" "$out_file" 2>/dev/null || echo "error")
    if [[ "$check" == "ok" ]]; then
      log "SKIP $run_id/$game_slug/$agent_id"
      ((skipped++)) || true
      return 0
    fi
  fi

  # Spec missing?
  if [[ ! -f "$spec_file" ]]; then
    log "SKIP $run_id/$game_slug/$agent_id — no spec"
    ((skipped++)) || true
    return 0
  fi

  # Build prompt via python to avoid bash interpolation mangling spec content
  local prompt_file="/tmp/v2-build-prompt-$$.txt"
  python3 -c "
import sys
spec = open('$spec_file').read()
prompt = '''You are an expert HTML5/JavaScript game developer.

Your task: Build a complete, playable $game_name as a single self-contained HTML file.

SPEC:
---
''' + spec + '''
---

ABSOLUTE RULES:
1. You MUST use the write tool to save the file to: $out_file
2. DO NOT output the HTML as text. Use the write tool ONLY.
3. Single file only — all CSS and JS must be inline. Zero external dependencies.
4. Use HTML5 Canvas for all rendering.
5. Include this comment block at the very top of the file:
<!--
  GAME:      $game_name
  RUN:       $run_id
  BUILDER:   $model_id
-->
6. Do not ask questions. Build the game.
7. Max 3 tool calls. Plan the full game in your head first, then write the complete file in ONE write call.

After writing the file, say exactly: BUILD_COMPLETE'''
open('$prompt_file', 'w').write(prompt)
" || { log "FAIL $run_id/$game_slug/$agent_id — prompt gen failed"; return 1; }

  local attempt=0
  local success=false

  while [[ $attempt -lt $MAX_ATTEMPTS ]]; do
    ((attempt++)) || true
    local session_id="v2-build-${run_id}-${game_slug}-${agent_id}-a${attempt}-$$"

    log "BUILD $run_id/$game_slug/$agent_id attempt ${attempt}/${MAX_ATTEMPTS}"

    # Read prompt from file to avoid bash mangling
    openclaw agent \
      --agent "$agent_id" \
      --session-id "$session_id" \
      --message "$(cat "$prompt_file")" \
      --timeout "$BUILD_TIMEOUT" \
      > "$raw_log" 2>&1 || true

    # Verify artefact — never trust model self-report
    local check
    check=$(python3 "$VERIFY" "$out_file" 2>/dev/null || echo "error")
    if [[ "$check" == "ok" ]]; then
      log "OK    $run_id/$game_slug/$agent_id (attempt ${attempt})"
      success=true
      break
    else
      log "FAIL  $run_id/$game_slug/$agent_id attempt ${attempt} — ${check}"
      sleep 5
    fi
  done

  if [[ "$success" == "true" ]]; then
    ((built++)) || true
  else
    log "DNF   $run_id/$game_slug/$agent_id — all ${MAX_ATTEMPTS} attempts failed"
    echo "DNF" > "$out_dir/dnf.txt"
    ((dnf++)) || true
  fi
}

for run_id in "${RUNS[@]}"; do
  [[ -n "$FILTER_RUN" && "$run_id" != "$FILTER_RUN" ]] && continue
  log "=== RUN: $run_id ==="
  notify "📦 Starting planner run: $run_id"

  for game_entry in "${GAMES[@]}"; do
    game_slug="${game_entry%%:*}"
    game_name="${game_entry##*:}"
    [[ -n "$FILTER_GAME" && "$game_slug" != "$FILTER_GAME" ]] && continue
    log "--- $game_slug ---"

    for agent_id in "${BUILDER_ORDER[@]}"; do
      [[ -n "$FILTER_BUILDER" && "$agent_id" != "$FILTER_BUILDER" ]] && continue
      ((total++)) || true
      build_one "$run_id" "$game_slug" "$game_name" "$agent_id"

      now=$(date +%s)
      if (( now - last_heartbeat > HEARTBEAT_SECS )); then
        notify "💓 V2 builds: ${built} done, ${dnf} DNF, ${skipped} skipped (${total} attempted)"
        last_heartbeat=$now
      fi
    done
  done

  notify "✅ Run $run_id complete — ${built} built, ${dnf} DNF so far"
done

log "BUILD COMPLETE — ${built} OK / ${dnf} DNF / ${skipped} skipped"
notify "🏁 All builds done — ${built} OK, ${dnf} DNF. Run 03_static_qa.sh next."
