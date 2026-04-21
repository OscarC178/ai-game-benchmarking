#!/bin/bash
# run-game-build.sh
# Runs 5 builders in parallel for a single game, then spawns QA
# Usage: run-game-build.sh <run> <game> <game-number> <total-games> <game-display-name>
# Example: run-game-build.sh run1-opus-plan pong 1 10 "Pong"

set -e
RUN=$1
GAME=$2
GAME_NUM=$3
TOTAL=$4
GAME_NAME=$5

BASE="/Users/oscar/.openclaw/workspace/games/$RUN/$GAME"
SCRIPTS="/Users/oscar/.openclaw/workspace/games/scripts"
LOG="/Users/oscar/.openclaw/workspace/games/run-log.md"
PLANNER="anthropic/claude-opus-4.6"
[[ "$RUN" == *"gpt"* ]] && PLANNER="openai/gpt-5.4"

echo "=========================================="
echo "BUILDING: $GAME_NAME (Game $GAME_NUM/$TOTAL)"
echo "Run: $RUN"
echo "=========================================="

# Model configs
declare -A AGENTS=(
  ["sonnet"]="bench-sonnet"
  ["opus"]="bench-opus"  
  ["haiku"]="bench-haiku"
  ["gpt-5-4"]="bench-gpt54"
  ["o3-mini"]="bench-o3mini"
)

declare -A MODEL_IDS=(
  ["sonnet"]="anthropic/claude-sonnet-4-6"
  ["opus"]="anthropic/claude-opus-4-6"
  ["haiku"]="anthropic/claude-haiku-4-5"
  ["gpt-5-4"]="openai/gpt-5.4"
  ["o3-mini"]="openai/o3-mini"
)

SPEC="$BASE/spec.md"

# Build task for agent
build_task() {
  local MODEL_SLUG=$1
  local MODEL_ID=$2
  local OUT="$BASE/$MODEL_SLUG/index.html"
  
  cat << BUILDTASK
You are an expert HTML5/JS game developer participating in a model benchmark.

Your job: Build a complete, playable vintage game as a single self-contained HTML file.

SPEC FILE: Read $SPEC

OUTPUT FILE: $OUT

## BUILD RULES
1. Single file. All CSS and JS inline. Zero external dependencies. No CDN links.
2. HTML5 Canvas for all rendering.
3. Follow the spec EXACTLY — especially the Build Task Checklist (Section 12).

## HOW TO BUILD
Work through the spec's Section 12 task checklist IN ORDER:
- Complete T01 first. Verify it works. Then T02. Then T03. And so on.
- Do NOT skip ahead. Do NOT write the whole game at once and hope it works.
- After each task is complete, verify the code for that section before proceeding.
- If a task fails after 2 attempts, mark it failed and move to the next task.
- Max 5 total debug iterations across the whole build.

## OUTPUT FORMAT
When done, write the file. Then output this JSON on its own line starting with JSON_RESULT:

JSON_RESULT:{"model_id":"$MODEL_ID","game":"$GAME","run":"$RUN","status":"complete","wall_clock_seconds":0,"tokens_input":0,"tokens_output":0,"estimated_cost_usd":0.00,"iterations":0,"errors_found":0,"errors_fixed":0,"task_checklist":{"T01":"complete","T02":"complete","T03":"complete","T04":"complete","T05":"complete","T06":"complete","T07":"complete","T08":"complete","T09":"complete","T10":"complete","T11":"complete","T12":"complete"},"last_completed_task":"T12","first_failed_task":null}

## MANDATORY COMMENT HEADER
The VERY FIRST lines of $OUT must be:

<!--
  GAME:           $GAME_NAME
  RUN:            $RUN
  BUILDER:        $MODEL_ID
  PLANNER:        $PLANNER
  BUILD TIME:     {seconds} seconds
  TOKENS IN:      {count}
  TOKENS OUT:     {count}
  ESTIMATED COST: \${amount}
  ITERATIONS:     {count}
  TOOLS USED:     write, read
  STATUS:         complete
  TIMESTAMP:      $(date -u +"%Y-%m-%dT%H:%M:%SZ")
  TASKS DONE:     T01,T02,...
  FIRST FAILURE:  none
-->

## PRICING
- claude-sonnet-4.6: \$3/M in, \$15/M out
- claude-opus-4.6: \$15/M in, \$75/M out
- claude-haiku-4.5: \$0.80/M in, \$4/M out
- gpt-5.4: \$2.50/M in, \$15/M out
- o3-mini: \$1.10/M in, \$4.40/M out
BUILDTASK
}

# Launch all 5 builders in parallel
echo "Launching 5 builders in parallel..."
START_TIME=$(date +%s)

declare -A PIDS
for SLUG in sonnet opus haiku gpt-5-4 o3-mini; do
  MODEL_ID="${MODEL_IDS[$SLUG]}"
  AGENT="${AGENTS[$SLUG]}"
  SESSION_ID="$RUN-$GAME-$SLUG"
  OUTPUT_LOG="$BASE/$SLUG/build-output.txt"
  mkdir -p "$BASE/$SLUG"
  
  TASK=$(build_task "$SLUG" "$MODEL_ID")
  openclaw agent --agent "$AGENT" --session-id "$SESSION_ID" --message "$TASK" --timeout 600 \
    > "$OUTPUT_LOG" 2>&1 &
  PIDS[$SLUG]=$!
  echo "  [$SLUG] Started (PID ${PIDS[$SLUG]})"
done

# Wait for all to complete
echo "Waiting for all 5 builders..."
declare -A STATUS
for SLUG in sonnet opus haiku gpt-5-4 o3-mini; do
  PID=${PIDS[$SLUG]}
  if wait $PID; then
    STATUS[$SLUG]="done"
    echo "  [$SLUG] ✅ Complete"
  else
    STATUS[$SLUG]="error"
    echo "  [$SLUG] ❌ Error (exit code $?)"
  fi
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo "All builders finished in ${ELAPSED}s"

# Update results.json for each builder
echo "Updating results.json..."
for SLUG in sonnet opus haiku gpt-5-4 o3-mini; do
  OUTPUT_LOG="$BASE/$SLUG/build-output.txt"
  if [ -f "$OUTPUT_LOG" ]; then
    python3 "$SCRIPTS/update-results.py" "$RUN" "$GAME" "$SLUG" "$OUTPUT_LOG" 2>&1
  else
    echo "No output log for $SLUG"
  fi
done

echo "Build phase complete for $GAME"
