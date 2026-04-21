#!/usr/bin/env bash
# 04_browser_qa.sh — Phase 4: Browser agent QA (Playwright)
# Patches window.__qa state bridge into each build, then plays the game
# and checks for: position frozen, score never increments, state never transitions, JS errors
#
# Usage: ./04_browser_qa.sh [--run r1-opus] [--game pong]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V2_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILDS_DIR="$V2_DIR/builds"
QA_DIR="$V2_DIR/qa/browser"
NOTIFY="$SCRIPT_DIR/lib/telegram_notify.sh"
PATCH_SCRIPT="$SCRIPT_DIR/lib/patch_qa_bridge.py"
BROWSER_AGENT="$SCRIPT_DIR/lib/browser_qa_agent.py"

notify() { bash "$NOTIFY" "$1" 2>/dev/null || true; }
log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

FILTER_RUN=""
FILTER_GAME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) FILTER_RUN="$2"; shift 2 ;;
    --game) FILTER_GAME="$2"; shift 2 ;;
    *) shift ;;
  esac
done

RUNS=(r1-opus r2-gpt54 r3-gemini-pro r4-glm5 r5-control)
GAMES=(pong snake breakout space-invaders tetris asteroids galaga frogger pac-man donkey-kong)
BUILDERS=(bench-opus bench-sonnet bench-haiku bench-gpt54 bench-gpt54mini bench-gemini-pro bench-gemini-flash bench-glm5)

mkdir -p "$QA_DIR"

total=0
done_count=0
bugs_found=0

notify "🎮 V2 Browser QA starting — Playwright gameplay testing"

for run_id in "${RUNS[@]}"; do
  [[ -n "$FILTER_RUN" && "$run_id" != "$FILTER_RUN" ]] && continue

  for game_slug in "${GAMES[@]}"; do
    [[ -n "$FILTER_GAME" && "$game_slug" != "$FILTER_GAME" ]] && continue

    for agent_id in "${BUILDERS[@]}"; do
      build_file="$BUILDS_DIR/$run_id/$game_slug/$agent_id/index.html"
      qa_out_dir="$QA_DIR/$run_id/$game_slug/$agent_id"
      report_file="$qa_out_dir/report.json"

      [[ -f "$BUILDS_DIR/$run_id/$game_slug/$agent_id/dnf.txt" ]] && continue
      [[ ! -f "$build_file" ]] && continue
      [[ -f "$report_file" ]] && { ((done_count++)) || true; continue; }

      mkdir -p "$qa_out_dir"
      ((total++)) || true

      log "BROWSER QA $run_id/$game_slug/$agent_id"

      # Patch QA bridge
      patched_file="$qa_out_dir/index-patched.html"
      python3 "$PATCH_SCRIPT" "$build_file" "$patched_file" 2>/dev/null || cp "$build_file" "$patched_file"

      # Run browser agent
      python3 "$BROWSER_AGENT" \
        --file "$patched_file" \
        --game "$game_slug" \
        --report "$report_file" \
        --screenshot-dir "$qa_out_dir" \
        --timeout 30 2>/dev/null || true

      if [[ -f "$report_file" ]]; then
        bugs=$(python3 -c "import json; d=json.load(open('$report_file')); print(len(d.get('bugs',[])) + len(d.get('errors',[])))" 2>/dev/null || echo "?")
        log "OK BROWSER $run_id/$game_slug/$agent_id — ${bugs} issues"
        [[ "$bugs" != "0" && "$bugs" != "?" ]] && ((bugs_found++)) || true
        ((done_count++)) || true
      else
        echo '{"error":"agent_failed"}' > "$report_file"
        log "FAIL BROWSER $run_id/$game_slug/$agent_id"
      fi

    done
  done
done

echo ""
echo "============================================"
echo "Browser QA complete — ${done_count} tested, ${bugs_found} with bugs"
echo "============================================"
echo "NEXT STEP: python3 05_generate_report.py"

notify "✅ Browser QA done — ${done_count} tested, ${bugs_found} builds with bugs. Generating report next."
