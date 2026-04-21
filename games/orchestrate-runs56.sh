#!/usr/bin/env bash
# Orchestration script for Gemini Benchmark Runs 5 & 6
# Runs Pro and Flash in parallel per game, Run5 then Run6 sequentially

set -e

WORKSPACE="/Users/oscar/.openclaw/workspace"
GAMES=(pong snake breakout space-invaders tetris asteroids galaga frogger pac-man donkey-kong)
TELEGRAM_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT="${TELEGRAM_CHAT_ID:-}"

send_telegram() {
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT}" \
        --data-urlencode "text=$1"
}

update_results() {
    local run=$1
    local game=$2
    local model_slug=$3
    local status=$4
    python3 -c "
import json
path = '${WORKSPACE}/games/${run}/${game}/results.json'
with open(path) as f:
    d = json.load(f)
d['builds']['${model_slug}']['status'] = '${status}'
with open(path, 'w') as f:
    json.dump(d, f, indent=2)
print('Updated ${run}/${game}/${model_slug} -> ${status}')
"
}

build_game() {
    local run=$1
    local game=$2
    local model_slug=$3  # gemini-pro or gemini-flash
    local agent=$4       # bench-gemini-pro or bench-gemini-flash
    local model_id=$5
    local planner=$6
    local game_name=$7
    local session_prefix=$8

    echo "=== Building $run/$game/$model_slug ==="
    
    local out_dir="${WORKSPACE}/games/${run}/${game}/${model_slug}"
    mkdir -p "$out_dir"
    
    local session_id="${session_prefix}-${game}"
    
    local message="You are an expert HTML5/JS game developer in a model benchmark.

Build a complete, playable ${game_name} game as a single self-contained HTML file.

SPEC: Read ${WORKSPACE}/games/${run}/${game}/spec.md

OUTPUT: Write the complete game to ${WORKSPACE}/games/${run}/${game}/${model_slug}/index.html

BUILD RULES:
1. Single file. All CSS and JS inline. Zero external dependencies. No CDN links.
2. HTML5 Canvas for rendering.
3. Work through the Build Task Checklist in the spec IN ORDER (T01, T02...).
4. Verify each task before moving to next.
5. Max 5 debug iterations total across the whole build.
6. Use your write tool to save the file — do NOT print to chat.

MANDATORY HTML COMMENT HEADER (very first lines):
<!--
  GAME:           ${game_name}
  RUN:            ${run}
  BUILDER:        ${model_id}
  PLANNER:        ${planner}
  TIMESTAMP:      $(date -u +%Y-%m-%dT%H:%M:%SZ)
  TASKS DONE:     T01,T02,...
  FIRST FAILURE:  none
-->

When file is written output exactly:
JSON_RESULT:{\"model_id\":\"${model_id}\",\"game\":\"${game}\",\"run\":\"${run}\",\"status\":\"complete\",\"last_completed_task\":\"T12\",\"first_failed_task\":null}"

    # Run build
    openclaw agent --agent "$agent" --session-id "$session_id" --message "$message" --timeout 600 2>&1
    
    # Check if file exists
    if [ -f "${out_dir}/index.html" ]; then
        echo "  ✓ File exists"
        update_results "$run" "$game" "$model_slug" "complete"
        
        # Run QA
        openclaw agent --agent bench-sonnet --session-id "qa-${run}-${game}-${model_slug}" \
            --message "Read ${WORKSPACE}/games/${run}/${game}/${model_slug}/index.html and ${WORKSPACE}/games/${run}/${game}/spec.md. Score on: functionality(30%), keyboard_controls(20%), visual_fidelity(20%), playability(20%), error_free(10%). Compute final_score. Update results.json at ${WORKSPACE}/games/${run}/${game}/results.json — set builds.${model_slug}.qa_scores with all 5 dimensions + final_score. Output: QA_DONE:${game} ${model_slug} score=X.X" \
            --timeout 300 2>&1
    else
        echo "  ✗ File missing, retrying..."
        local retry_session="${session_prefix}-${game}-r2"
        openclaw agent --agent "$agent" --session-id "$retry_session" --message "$message" --timeout 600 2>&1
        
        if [ -f "${out_dir}/index.html" ]; then
            echo "  ✓ File exists (retry)"
            update_results "$run" "$game" "$model_slug" "complete"
            openclaw agent --agent bench-sonnet --session-id "qa-${run}-${game}-${model_slug}" \
                --message "Read ${WORKSPACE}/games/${run}/${game}/${model_slug}/index.html and ${WORKSPACE}/games/${run}/${game}/spec.md. Score on: functionality(30%), keyboard_controls(20%), visual_fidelity(20%), playability(20%), error_free(10%). Compute final_score. Update results.json at ${WORKSPACE}/games/${run}/${game}/results.json — set builds.${model_slug}.qa_scores with all 5 dimensions + final_score. Output: QA_DONE:${game} ${model_slug} score=X.X" \
                --timeout 300 2>&1
        else
            echo "  ✗ DNF after retry"
            update_results "$run" "$game" "$model_slug" "dnf"
        fi
    fi
    
    echo "--- Done: ${run}/${game}/${model_slug} ---"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | ${run} | ${game} | ${model_slug} | done" >> "${WORKSPACE}/games/run-log.md"
}

# Run Pro sequence (Run 5 then Run 6 for each game)
run_pro_sequence() {
    local game_names=("Pong" "Snake" "Breakout" "Space Invaders" "Tetris" "Asteroids" "Galaga" "Frogger" "Pac-Man" "Donkey Kong")
    local i=0
    for game in "${GAMES[@]}"; do
        local game_name="${game_names[$i]}"
        
        # Run 5 (skip pong which is already done)
        if [ "$game" != "pong" ]; then
            build_game "run5-opus-gemini" "$game" "gemini-pro" "bench-gemini-pro" \
                "google/gemini-3.1-pro-preview" "anthropic/claude-opus-4-6" "$game_name" "r5-gpro"
        fi
        
        # Run 6
        build_game "run6-gpt-gemini" "$game" "gemini-pro" "bench-gemini-pro" \
            "google/gemini-3.1-pro-preview" "openai/gpt-5.4" "$game_name" "r6-gpro"
        
        i=$((i+1))
    done
}

# Run Flash sequence (Run 5 then Run 6 for each game)
run_flash_sequence() {
    local game_names=("Pong" "Snake" "Breakout" "Space Invaders" "Tetris" "Asteroids" "Galaga" "Frogger" "Pac-Man" "Donkey Kong")
    local i=0
    for game in "${GAMES[@]}"; do
        local game_name="${game_names[$i]}"
        
        # Run 5 (skip pong which is already done)
        if [ "$game" != "pong" ]; then
            build_game "run5-opus-gemini" "$game" "gemini-flash" "bench-gemini-flash" \
                "google/gemini-3-flash-preview" "anthropic/claude-opus-4-6" "$game_name" "r5-gflash"
        fi
        
        # Run 6
        build_game "run6-gpt-gemini" "$game" "gemini-flash" "bench-gemini-flash" \
            "google/gemini-3-flash-preview" "openai/gpt-5.4" "$game_name" "r6-gflash"
        
        i=$((i+1))
    done
}

echo "Starting Gemini Benchmark Runs 5 & 6"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | START | Gemini Runs 5+6 orchestration" >> "${WORKSPACE}/games/run-log.md"

send_telegram "🎮 Gemini Benchmark Runs 5 & 6 starting! Building 40 games (20 Pro + 20 Flash) across 2 spec sets. Will update every 5 completions."

# Run both in parallel
run_pro_sequence &
PRO_PID=$!

run_flash_sequence &
FLASH_PID=$!

wait $PRO_PID
wait $FLASH_PID

echo "All builds complete!"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | COMPLETE | All 40 builds done" >> "${WORKSPACE}/games/run-log.md"
