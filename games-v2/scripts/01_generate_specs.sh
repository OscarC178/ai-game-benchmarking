#!/usr/bin/env bash
# 01_generate_specs.sh — Phase 1: Generate specs from all planners
# Each planner gets a blank brief per game. No structure imposed.
# Run once; review all 40 specs before proceeding to builds.
#
# Usage: ./01_generate_specs.sh
# Output: games-v2/specs/{r1-opus,r2-gpt54,r3-gemini-pro,r4-glm5,r6-mini}/GAME/spec.md
#         games-v2/specs/r5-control/GAME/spec.md (control — game name only)

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V2_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SPECS_DIR="$V2_DIR/specs"
NOTIFY="$SCRIPT_DIR/lib/telegram_notify.sh"

notify() { bash "$NOTIFY" "$1" 2>/dev/null || true; }
log()    { echo "[$(date +%H:%M:%S)] $*"; }

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

get_agent() {
  case "$1" in
    r1-opus)       echo "bench-opus" ;;
    r2-gpt54)      echo "bench-gpt54" ;;
    r3-gemini-pro) echo "bench-gemini-pro" ;;
    r4-glm5)       echo "bench-glm5" ;;
    r6-mini)       echo "bench-gpt54mini" ;;
    *) echo "" ;;
  esac
}

mkdir -p "$SPECS_DIR"

total_ok=0
total_fail=0

notify "🚀 V2 Spec generation starting — 4 planners × 10 games = 40 specs"

for run_id in r1-opus r2-gpt54 r3-gemini-pro r4-glm5 r6-mini; do
  agent_id="$(get_agent "$run_id")"
  log "=== Planner run: $run_id (agent: $agent_id) ==="

  for game_entry in "${GAMES[@]}"; do
    game_slug="${game_entry%%:*}"
    game_name="${game_entry##*:}"

    spec_dir="$SPECS_DIR/$run_id/$game_slug"
    spec_file="$spec_dir/spec.md"
    mkdir -p "$spec_dir"

    # Skip if already done (crash recovery)
    if [[ -f "$spec_file" ]] && [[ $(wc -c < "$spec_file") -gt 200 ]]; then
      log "SKIP $run_id/$game_slug — already exists"
      ((total_ok++)) || true
      continue
    fi

    log "PLAN $run_id/$game_slug ..."

    prompt="You are writing a game specification for a skilled developer who will implement ${game_name} as a single self-contained HTML5 Canvas file with no external dependencies.

The developer is skilled but has never played this game. Write them a spec that gives them everything they need to build a complete, playable version.

No format is required. Write the spec however you think will best serve the developer. Be as detailed as you think necessary.

IMPORTANT: Write the spec to the file: ${spec_file}
Use the write tool. Do not output the spec as text. Write it directly to that path."

    session_id="v2-spec-${run_id}-${game_slug}-$$"

    # Run planner — no --json, embedded mode handles tools directly
    openclaw agent \
      --agent "$agent_id" \
      --session-id "$session_id" \
      --message "$prompt" \
      --timeout 600 \
      > /dev/null 2>&1 || true

    # Check if file was written
    spec_content=""
    if [[ -f "$spec_file" ]]; then
      spec_content=$(cat "$spec_file")
    fi

    if [[ -z "$spec_content" ]] || [[ ${#spec_content} -lt 200 ]]; then
      log "FAIL $run_id/$game_slug — output too short (${#spec_content} chars)"
      echo "GENERATION_FAILED: output too short" > "$spec_file"
      ((total_fail++)) || true
    else
      log "OK   $run_id/$game_slug — ${#spec_content} chars"
      ((total_ok++)) || true
    fi

    sleep 3  # Brief pause between API calls
  done

  notify "📝 Planner $run_id done — ${total_ok} OK so far"
done

# Control condition — no spec, just the game name
log "Writing control specs (r5-control)..."
for game_entry in "${GAMES[@]}"; do
  game_slug="${game_entry%%:*}"
  game_name="${game_entry##*:}"
  mkdir -p "$SPECS_DIR/r5-control/$game_slug"
  printf "# %s\n\nCONTROL CONDITION: No planner spec. Builder receives only the game name above.\n" "$game_name" \
    > "$SPECS_DIR/r5-control/$game_slug/spec.md"
done
log "Control specs written."

echo ""
echo "============================================"
echo "Spec generation complete — ${total_ok} OK, ${total_fail} failed"
echo "Specs at: $SPECS_DIR"
echo "============================================"
echo "NEXT STEP: Review all 40 specs, then run 02_build_games.sh"

notify "✅ Spec generation done — ${total_ok} OK, ${total_fail} failed. Oscar: please review specs before approving builds."
