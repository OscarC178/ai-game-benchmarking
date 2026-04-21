#!/usr/bin/env bash
# Vintage Games Benchmark Orchestrator
# Runs Opus Isolated (R3/R4) + Gemini Pro + Gemini Flash in parallel

set -euo pipefail

WORKSPACE="/Users/oscar/.openclaw/workspace/games"
BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
CHAT_ID="${TELEGRAM_CHAT_ID:-}"
LOG_FILE="$WORKSPACE/run-log.md"

send_telegram() {
  local msg="$1"
  curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${CHAT_ID}" \
    --data-urlencode "text=${msg}" > /dev/null 2>&1 || true
}

# Build a single game
build_game() {
  local agent_id="$1"
  local session_id="$2"
  local game="$3"
  local game_name="$4"
  local run="$5"
  local model_slug="$6"
  local model_id="$7"
  local planner="$8"
  local output_path="$9"
  local spec_path="${10}"

  local output_dir
  output_dir=$(dirname "$output_path")
  mkdir -p "$output_dir"

  local build_output="$output_dir/build-output.txt"

  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Building $run/$game/$model_slug (session: $session_id)" >&2

  local task_msg="You are an expert HTML5/JS game developer in a model benchmark.

Build a complete, playable vintage game as a single self-contained HTML file.

SPEC: Read $spec_path

OUTPUT: Write the complete game to $output_path

BUILD RULES:
1. Single file. All CSS and JS inline. Zero external dependencies. No CDN links.
2. HTML5 Canvas for rendering.
3. Follow the spec's Build Task Checklist IN ORDER (T01, T02, T03...).
4. Verify each task before moving to the next.
5. Max 5 debug iterations total.
6. Do NOT write the whole game at once — build task by task.

MANDATORY COMMENT HEADER (first lines of the HTML file):
<!--
  GAME:           $game_name
  RUN:            $run
  BUILDER:        $model_id
  PLANNER:        $planner
  TIMESTAMP:      (current ISO-8601)
  TASKS DONE:     T01,T02,...
  FIRST FAILURE:  none
-->

When complete, output this exact line:
JSON_RESULT:{\"model_id\":\"$model_id\",\"game\":\"$game\",\"run\":\"$run\",\"status\":\"complete\",\"iterations\":1,\"last_completed_task\":\"T12\",\"first_failed_task\":null}"

  openclaw agent --agent "$agent_id" --session-id "$session_id" --message "$task_msg" --timeout 900 > "$build_output" 2>&1 || true

  # Verify output
  if [ -f "$output_path" ]; then
    echo "BUILD_OK: $run/$game/$model_slug" >&2
    return 0
  else
    echo "BUILD_MISSING: $run/$game/$model_slug - retrying..." >&2
    local retry_session="${session_id}-retry"
    openclaw agent --agent "$agent_id" --session-id "$retry_session" --message "$task_msg" --timeout 900 >> "$build_output" 2>&1 || true
    if [ -f "$output_path" ]; then
      echo "BUILD_OK_RETRY: $run/$game/$model_slug" >&2
      return 0
    else
      echo "BUILD_DNF: $run/$game/$model_slug" >&2
      return 1
    fi
  fi
}

qa_game() {
  local run="$1"
  local game="$2"
  local model_slug="$3"
  local output_path="$4"
  local spec_path="$5"
  local results_json="$6"

  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] QA: $run/$game/$model_slug" >&2

  local qa_msg="Read $output_path and $spec_path. Score this HTML5 game build 0-10 on: functionality (30%), keyboard_controls (20%), visual_fidelity (20%), playability (20%), error_free (10%). Compute final_score = (functionality*0.30)+(keyboard_controls*0.20)+(visual_fidelity*0.20)+(playability*0.20)+(error_free*0.10). Update the file $results_json — set builds.$model_slug.qa_scores with all 5 dimensions plus final_score. Output: QA_DONE:$game $model_slug score=X"

  local qa_output
  qa_output=$(openclaw agent --agent bench-sonnet --session-id "qa-${run}-${game}-${model_slug}" --message "$qa_msg" --timeout 300 2>&1) || true

  local score
  score=$(echo "$qa_output" | grep -oP 'score=\K[\d.]+' | tail -1) || score="N/A"
  echo "$score"
}

update_results_json() {
  local results_json="$1"
  local model_slug="$2"
  local status="$3"

  python3 -c "
import json, sys
try:
    with open('$results_json') as f:
        d = json.load(f)
    if '$model_slug' in d.get('builds', {}):
        d['builds']['$model_slug']['status'] = '$status'
    with open('$results_json', 'w') as f:
        json.dump(d, f, indent=2)
except Exception as e:
    print(f'results.json update failed: {e}', file=sys.stderr)
"
}

# Full pipeline for a single game
run_game_pipeline() {
  local agent_id="$1"
  local session_id="$2"
  local game="$3"
  local game_name="$4"
  local run="$5"
  local model_slug="$6"
  local model_id="$7"
  local planner="$8"
  local run_dir="$9"

  local output_path="$run_dir/$game/$model_slug/index.html"
  local spec_path="$run_dir/$game/spec.md"
  local results_json="$run_dir/$game/results.json"

  local status="complete"
  local qa_score="N/A"

  if build_game "$agent_id" "$session_id" "$game" "$game_name" "$run" "$model_slug" "$model_id" "$planner" "$output_path" "$spec_path"; then
    status="complete"
    update_results_json "$results_json" "$model_slug" "complete"
    qa_score=$(qa_game "$run" "$game" "$model_slug" "$output_path" "$spec_path" "$results_json")
    update_results_json "$results_json" "$model_slug" "complete"
  else
    status="dnf"
    update_results_json "$results_json" "$model_slug" "dnf"
    send_telegram "❌ $run/$game/$model_slug DNF"
  fi

  local ts
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "[$ts] $run/$game/$model_slug → $status score=$qa_score" >> "$LOG_FILE"

  echo "$qa_score"
}

# ============================================================
# JOB 1: Opus Isolated Runs (R3 then R4 sequentially)
# ============================================================
job_opus_isolated() {
  echo "=== JOB 1: Opus Isolated Runs ===" >&2

  local R3_DIR="$WORKSPACE/run3-opus-isolated"
  local R4_DIR="$WORKSPACE/run4-gpt-isolated"
  local AGENT="bench-opus"
  local MODEL_ID="anthropic/claude-opus-4.6"

  # Run 3 missing: pac-man, donkey-kong
  declare -A GAME_NAMES=( [pac-man]="Pac-Man" [donkey-kong]="Donkey Kong" [pong]="Pong" [snake]="Snake" [galaga]="Galaga" [frogger]="Frogger" )

  for game in pac-man donkey-kong; do
    run_game_pipeline "$AGENT" "r3-opus-iso-${game}" "$game" "${GAME_NAMES[$game]}" "run3-opus-isolated" "opus" "$MODEL_ID" "anthropic/claude-opus-4-6" "$R3_DIR"
  done

  # Run 4 all 6 games (in order of simplicity)
  for game in pong snake galaga frogger pac-man donkey-kong; do
    run_game_pipeline "$AGENT" "r4-gpt-iso-${game}" "$game" "${GAME_NAMES[$game]}" "run4-gpt-isolated" "opus" "$MODEL_ID" "gpt-4o" "$R4_DIR"
  done

  echo "=== JOB 1 COMPLETE ===" >&2
  send_telegram "✅ Job 1 Complete: Opus Isolated R3+R4 done"
}

# ============================================================
# JOB 2: Gemini Pro — Runs 5 & 6
# ============================================================
job_gemini_pro() {
  echo "=== JOB 2: Gemini Pro ===" >&2

  local R5_DIR="$WORKSPACE/run5-opus-gemini"
  local R6_DIR="$WORKSPACE/run6-gpt-gemini"
  local AGENT="bench-gemini-pro"
  local MODEL_ID="google/gemini-3.1-pro-preview"
  local MODEL_SLUG="gemini-pro"

  declare -A GAME_NAMES=( [pong]="Pong" [snake]="Snake" [breakout]="Breakout" [space-invaders]="Space Invaders" [tetris]="Tetris" [asteroids]="Asteroids" [galaga]="Galaga" [frogger]="Frogger" [pac-man]="Pac-Man" [donkey-kong]="Donkey Kong" )

  local completed=0
  local total_score=0
  local score_count=0

  # Run 5
  for game in pong snake breakout space-invaders tetris asteroids galaga frogger pac-man donkey-kong; do
    local score
    score=$(run_game_pipeline "$AGENT" "r5-opus-gpro-${game}" "$game" "${GAME_NAMES[$game]}" "run5-opus-gemini" "$MODEL_SLUG" "$MODEL_ID" "anthropic/claude-opus-4-6" "$R5_DIR")
    completed=$((completed + 1))
    if [[ "$score" =~ ^[0-9] ]]; then
      total_score=$(python3 -c "print($total_score + $score)")
      score_count=$((score_count + 1))
    fi
    if [ $((completed % 5)) -eq 0 ]; then
      local avg="N/A"
      if [ $score_count -gt 0 ]; then
        avg=$(python3 -c "print(round($total_score/$score_count, 1))")
      fi
      send_telegram "✅ $completed Gemini Pro builds done — avg score $avg"
    fi
  done

  # Run 6
  for game in pong snake breakout space-invaders tetris asteroids galaga frogger pac-man donkey-kong; do
    local score
    score=$(run_game_pipeline "$AGENT" "r6-gpt-gpro-${game}" "$game" "${GAME_NAMES[$game]}" "run6-gpt-gemini" "$MODEL_SLUG" "$MODEL_ID" "gpt-4o" "$R6_DIR")
    completed=$((completed + 1))
    if [[ "$score" =~ ^[0-9] ]]; then
      total_score=$(python3 -c "print($total_score + $score)")
      score_count=$((score_count + 1))
    fi
    if [ $((completed % 5)) -eq 0 ]; then
      local avg="N/A"
      if [ $score_count -gt 0 ]; then
        avg=$(python3 -c "print(round($total_score/$score_count, 1))")
      fi
      send_telegram "✅ $completed Gemini Pro builds done — avg score $avg"
    fi
  done

  echo "=== JOB 2 COMPLETE ===" >&2
  send_telegram "✅ Job 2 Complete: Gemini Pro R5+R6 done"
}

# ============================================================
# JOB 3: Gemini Flash — Runs 5 & 6
# ============================================================
job_gemini_flash() {
  echo "=== JOB 3: Gemini Flash ===" >&2

  local R5_DIR="$WORKSPACE/run5-opus-gemini"
  local R6_DIR="$WORKSPACE/run6-gpt-gemini"
  local AGENT="bench-gemini-flash"
  local MODEL_ID="google/gemini-3-flash-preview"
  local MODEL_SLUG="gemini-flash"

  declare -A GAME_NAMES=( [pong]="Pong" [snake]="Snake" [breakout]="Breakout" [space-invaders]="Space Invaders" [tetris]="Tetris" [asteroids]="Asteroids" [galaga]="Galaga" [frogger]="Frogger" [pac-man]="Pac-Man" [donkey-kong]="Donkey Kong" )

  local completed=0
  local total_score=0
  local score_count=0

  # Run 5
  for game in pong snake breakout space-invaders tetris asteroids galaga frogger pac-man donkey-kong; do
    local score
    score=$(run_game_pipeline "$AGENT" "r5-opus-gflash-${game}" "$game" "${GAME_NAMES[$game]}" "run5-opus-gemini" "$MODEL_SLUG" "$MODEL_ID" "anthropic/claude-opus-4-6" "$R5_DIR")
    completed=$((completed + 1))
    if [[ "$score" =~ ^[0-9] ]]; then
      total_score=$(python3 -c "print($total_score + $score)")
      score_count=$((score_count + 1))
    fi
    if [ $((completed % 5)) -eq 0 ]; then
      local avg="N/A"
      if [ $score_count -gt 0 ]; then
        avg=$(python3 -c "print(round($total_score/$score_count, 1))")
      fi
      send_telegram "✅ $completed Gemini Flash builds done — avg score $avg"
    fi
  done

  # Run 6
  for game in pong snake breakout space-invaders tetris asteroids galaga frogger pac-man donkey-kong; do
    local score
    score=$(run_game_pipeline "$AGENT" "r6-gpt-gflash-${game}" "$game" "${GAME_NAMES[$game]}" "run6-gpt-gemini" "$MODEL_SLUG" "$MODEL_ID" "gpt-4o" "$R6_DIR")
    completed=$((completed + 1))
    if [[ "$score" =~ ^[0-9] ]]; then
      total_score=$(python3 -c "print($total_score + $score)")
      score_count=$((score_count + 1))
    fi
    if [ $((completed % 5)) -eq 0 ]; then
      local avg="N/A"
      if [ $score_count -gt 0 ]; then
        avg=$(python3 -c "print(round($total_score/$score_count, 1))")
      fi
      send_telegram "✅ $completed Gemini Flash builds done — avg score $avg"
    fi
  done

  echo "=== JOB 3 COMPLETE ===" >&2
  send_telegram "✅ Job 3 Complete: Gemini Flash R5+R6 done"
}

# ============================================================
# MAIN: Run all 3 jobs in parallel
# ============================================================
send_telegram "🚀 Benchmark starting: Opus Isolated (R3/R4) + Gemini Pro (R5/R6) + Gemini Flash (R5/R6)"

# Start all jobs in parallel
job_opus_isolated &
PID_JOB1=$!

job_gemini_pro &
PID_JOB2=$!

job_gemini_flash &
PID_JOB3=$!

echo "Jobs started: PID1=$PID_JOB1 PID2=$PID_JOB2 PID3=$PID_JOB3" >&2

# Wait for all to complete
wait $PID_JOB1 && echo "Job1 done" || echo "Job1 failed" >&2
wait $PID_JOB2 && echo "Job2 done" || echo "Job2 failed" >&2
wait $PID_JOB3 && echo "Job3 done" || echo "Job3 failed" >&2

echo "=== ALL JOBS COMPLETE ===" >&2
echo "ALL_DONE"
