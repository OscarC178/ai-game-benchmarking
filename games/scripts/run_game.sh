#!/usr/bin/env bash
# Single game build + QA script
# Usage: run_game.sh <agent_id> <session_id> <game> <game_name> <run> <model_slug> <model_id> <planner> <run_dir>

set -euo pipefail

AGENT_ID="$1"
SESSION_ID="$2"
GAME="$3"
GAME_NAME="$4"
RUN="$5"
MODEL_SLUG="$6"
MODEL_ID="$7"
PLANNER="$8"
RUN_DIR="$9"

OUTPUT_PATH="$RUN_DIR/$GAME/$MODEL_SLUG/index.html"
SPEC_PATH="$RUN_DIR/$GAME/spec.md"
RESULTS_JSON="$RUN_DIR/$GAME/results.json"
BUILD_OUTPUT="$RUN_DIR/$GAME/$MODEL_SLUG/build-output.txt"

BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
CHAT_ID="${TELEGRAM_CHAT_ID:-}"
LOG_FILE="/Users/oscar/.openclaw/workspace/games/run-log.md"

mkdir -p "$(dirname "$OUTPUT_PATH")"

send_telegram() {
  curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    --data-urlencode "text=$1" > /dev/null 2>&1 || true
}

build_task_msg() {
cat << ENDMSG
You are an expert HTML5/JS game developer in a model benchmark.

Build a complete, playable vintage game as a single self-contained HTML file.

SPEC: Read $SPEC_PATH

OUTPUT: Write the complete game to $OUTPUT_PATH

BUILD RULES:
1. Single file. All CSS and JS inline. Zero external dependencies. No CDN links.
2. HTML5 Canvas for rendering.
3. Follow the spec's Build Task Checklist IN ORDER (T01, T02, T03...).
4. Verify each task before moving to the next.
5. Max 5 debug iterations total.
6. Do NOT write the whole game at once — build task by task.

MANDATORY COMMENT HEADER (first lines of the HTML file):
<!--
  GAME:           $GAME_NAME
  RUN:            $RUN
  BUILDER:        $MODEL_ID
  PLANNER:        $PLANNER
  TIMESTAMP:      (current ISO-8601)
  TASKS DONE:     T01,T02,...
  FIRST FAILURE:  none
-->

When complete, output this exact line:
JSON_RESULT:{"model_id":"$MODEL_ID","game":"$GAME","run":"$RUN","status":"complete","iterations":1,"last_completed_task":"T12","first_failed_task":null}
ENDMSG
}

update_status() {
  local status="$1"
  python3 -c "
import json, sys
try:
    with open('$RESULTS_JSON') as f:
        d = json.load(f)
    if '$MODEL_SLUG' in d.get('builds', {}):
        d['builds']['$MODEL_SLUG']['status'] = '$status'
    with open('$RESULTS_JSON', 'w') as f:
        json.dump(d, f, indent=2)
except Exception as e:
    print(f'results.json update failed: {e}', file=sys.stderr)
" || true
}

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] START $RUN/$GAME/$MODEL_SLUG session=$SESSION_ID"

# Build
MSG=$(build_task_msg)
openclaw agent --agent "$AGENT_ID" --session-id "$SESSION_ID" --message "$MSG" --timeout 900 > "$BUILD_OUTPUT" 2>&1 || true

# Check result
if [ ! -f "$OUTPUT_PATH" ]; then
  echo "RETRY: $RUN/$GAME/$MODEL_SLUG"
  openclaw agent --agent "$AGENT_ID" --session-id "${SESSION_ID}-retry" --message "$MSG" --timeout 900 >> "$BUILD_OUTPUT" 2>&1 || true
fi

if [ ! -f "$OUTPUT_PATH" ]; then
  echo "DNF: $RUN/$GAME/$MODEL_SLUG"
  update_status "dnf"
  send_telegram "❌ $RUN/$GAME/$MODEL_SLUG DNF"
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "[$TS] $RUN/$GAME/$MODEL_SLUG → dnf score=N/A" >> "$LOG_FILE"
  echo "RESULT:dnf:N/A"
  exit 0
fi

update_status "complete"

# QA
QA_MSG="Read $OUTPUT_PATH and $SPEC_PATH. Score this HTML5 game build 0-10 on: functionality (30%), keyboard_controls (20%), visual_fidelity (20%), playability (20%), error_free (10%). Compute final_score = (functionality*0.30)+(keyboard_controls*0.20)+(visual_fidelity*0.20)+(playability*0.20)+(error_free*0.10). Update the file $RESULTS_JSON — set builds.$MODEL_SLUG.qa_scores with all 5 dimensions plus final_score. Output: QA_DONE:$GAME $MODEL_SLUG score=X"

QA_OUTPUT=$(openclaw agent --agent bench-sonnet --session-id "qa-${RUN}-${GAME}-${MODEL_SLUG}" --message "$QA_MSG" --timeout 300 2>&1) || true

SCORE=$(echo "$QA_OUTPUT" | grep -oP 'score=\K[\d.]+' | tail -1) || SCORE="N/A"

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "[$TS] $RUN/$GAME/$MODEL_SLUG → complete score=$SCORE" >> "$LOG_FILE"

echo "RESULT:complete:$SCORE"
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] DONE $RUN/$GAME/$MODEL_SLUG score=$SCORE"
