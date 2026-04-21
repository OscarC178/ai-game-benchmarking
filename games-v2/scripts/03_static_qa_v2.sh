#!/usr/bin/env bash
# 03_static_qa_v2.sh — Phase 3: 3-judge static QA via PaleBlueDot API
# Judges: Sonnet 4.6, Gemini 3.1 Pro, GPT-5.4
# Dimensions: functionality(30%) keyboard_controls(20%) visual_fidelity(20%) playability(20%) error_free(10%)
# Final score = average of 3 judge weighted totals
#
# Usage: ./03_static_qa_v2.sh [--run r1-opus] [--game pong] [--dry-run]
# Requires: PALEBLUEDOT_API_KEY env var

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V2_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILDS_DIR="$V2_DIR/builds"
QA_DIR="$V2_DIR/qa/static"
PBD_URL="https://open.palebluedot.ai/v1/chat/completions"

if [[ -z "$PALEBLUEDOT_API_KEY" ]]; then
  echo "ERROR: PALEBLUEDOT_API_KEY not set" >&2; exit 1
fi

log() { echo "[$(date +%H:%M:%S)] $*"; }

FILTER_RUN=""
FILTER_GAME=""
DRY_RUN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run)     FILTER_RUN="$2";  shift 2 ;;
    --game)    FILTER_GAME="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true;     shift ;;
    *) shift ;;
  esac
done

RUNS=(r1-opus r2-gpt54 r3-gemini-pro r4-glm5 r5-control)
GAMES=(pong snake breakout space-invaders tetris asteroids galaga frogger pac-man donkey-kong)
BUILDERS=(bench-opus bench-sonnet bench-haiku bench-gpt54 bench-gpt54mini bench-gemini-pro bench-gemini-flash bench-glm5)

JUDGE_NAMES=(sonnet gemini-pro gpt54)
JUDGE_MODELS=("anthropic/claude-sonnet-4.6" "google/gemini-3.1-pro-preview" "openai/gpt-5.4")

mkdir -p "$QA_DIR"

total=0; done_count=0; skipped=0; failed=0

call_judge() {
  local model="$1"
  local game="$2"
  local run="$3"
  local builder="$4"
  local source_file="$5"

  # Read source, truncate to 50KB to stay in context
  local source_html
  source_html=$(head -c 51200 "$source_file")

  local prompt="You are a strict QA judge for an HTML5 retro game benchmark. The game is: ${game} (${run}, builder: ${builder}).

Score this build honestly on 5 dimensions (0-10 each, where 5=mediocre, 7=good, 10=flawless):
- functionality: Is the core game logic complete? Do all mechanics work? (30%)
- keyboard_controls: Do controls respond correctly? Are they mapped properly? (20%)
- visual_fidelity: Does it look like a proper ${game} game? Correct sprites/shapes/colors/layout? (20%)
- playability: Is it actually fun/playable as a game? Smooth movement, fair difficulty? (20%)
- error_free: No JS errors, no crashes, no broken rendering? (10%)

BE STRICT. Most AI-generated games have issues. A 10 means PERFECT — rare.
Calculate weighted final: (functionality*0.30)+(keyboard_controls*0.20)+(visual_fidelity*0.20)+(playability*0.20)+(error_free*0.10)

Output ONLY valid JSON:
{\"judge\":\"JUDGE_NAME\",\"functionality\":N,\"keyboard_controls\":N,\"visual_fidelity\":N,\"playability\":N,\"error_free\":N,\"final_score\":N.NN,\"notes\":\"one sentence\"}"

  # Build JSON payload using python to handle escaping
  local payload
  payload=$(python3 -c "
import json,sys
prompt=sys.argv[1]
source=open(sys.argv[2]).read()[:51200]
msg = prompt + '\n\nHere is the full source code:\n\n' + source
print(json.dumps({
  'model': sys.argv[3],
  'messages': [{'role':'user','content':msg}],
  'max_tokens': 4096,
  'temperature': 0.3
}))
" "$prompt" "$source_file" "$model" 2>/dev/null)

  if [[ -z "$payload" ]]; then
    echo ""
    return
  fi

  local raw
  raw=$(curl -s -X POST "$PBD_URL" \
    -H "Authorization: Bearer $PALEBLUEDOT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    --max-time 120 2>/dev/null)

  # Extract JSON from response
  echo "$raw" | python3 -c "
import sys, json, re
try:
    d = json.load(sys.stdin)
    content = d['choices'][0]['message']['content']
    # Find JSON object with required fields
    m = re.search(r'\{[^{}]*\"functionality\"[^{}]*\}', content, re.DOTALL)
    if m:
        obj = json.loads(m.group(0))
        for f in ['functionality','keyboard_controls','visual_fidelity','playability','error_free','final_score']:
            assert f in obj, f'missing {f}'
        print(json.dumps(obj))
    else:
        print('')
except Exception as e:
    print('', file=sys.stderr)
    print('')
" 2>/dev/null
}

log "=== V2 Static QA starting — 3 judges per build ==="

for run_id in "${RUNS[@]}"; do
  [[ -n "$FILTER_RUN" && "$run_id" != "$FILTER_RUN" ]] && continue

  for game_slug in "${GAMES[@]}"; do
    [[ -n "$FILTER_GAME" && "$game_slug" != "$FILTER_GAME" ]] && continue

    for agent_id in "${BUILDERS[@]}"; do
      build_file="$BUILDS_DIR/$run_id/$game_slug/$agent_id/index.html"
      qa_dir="$QA_DIR/$run_id/$game_slug/$agent_id"
      result_file="$qa_dir/result.json"

      [[ -f "$BUILDS_DIR/$run_id/$game_slug/$agent_id/dnf.txt" ]] && continue
      [[ ! -f "$build_file" ]] && continue

      if [[ -f "$result_file" ]]; then
        ((skipped++)) || true
        continue
      fi

      mkdir -p "$qa_dir"
      ((total++)) || true

      if $DRY_RUN; then
        log "DRY  $run_id/$game_slug/$agent_id"
        continue
      fi

      log "QA   $run_id/$game_slug/$agent_id"

      judge_jsons=()

      for i in 0 1 2; do
        judge_name="${JUDGE_NAMES[$i]}"
        model="${JUDGE_MODELS[$i]}"
        judge_file="$qa_dir/${judge_name}.json"

        if [[ -f "$judge_file" ]]; then
          judge_jsons+=("$(cat "$judge_file")")
          continue
        fi

        judge_json=$(call_judge "$model" "$game_slug" "$run_id" "$agent_id" "$build_file")

        if [[ -n "$judge_json" ]]; then
          echo "$judge_json" > "$judge_file"
          judge_jsons+=("$judge_json")
          score_p=$(echo "$judge_json" | python3 -c "import sys,json; print(json.load(sys.stdin)['final_score'])" 2>/dev/null || echo "?")
          log "  ✓ $judge_name: $score_p"
        else
          log "  ✗ $judge_name: no valid JSON"
        fi

        sleep 0.5
      done

      if [[ ${#judge_jsons[@]} -gt 0 ]]; then
        # Write judge JSONs to temp file for python to read
        tmpjudge="/tmp/qa_judges_$$.jsonl"
        printf '%s\n' "${judge_jsons[@]}" > "$tmpjudge"
        python3 -c "
import json, sys
results = []
for line in open(sys.argv[1]):
    line = line.strip()
    if line:
        try: results.append(json.loads(line))
        except: pass

dims = ['functionality','keyboard_controls','visual_fidelity','playability','error_free']
weights = {'functionality':0.30,'keyboard_controls':0.20,'visual_fidelity':0.20,'playability':0.20,'error_free':0.10}

avg = {}
for d in dims:
    vals = [float(r[d]) for r in results if d in r]
    avg[d] = round(sum(vals)/len(vals), 2) if vals else 0.0

final = round(sum(avg[d]*weights[d] for d in dims), 2)

with open(sys.argv[2], 'w') as f:
    json.dump({
        'final_score': final,
        'scores': avg,
        'num_judges': len(results),
        'judges': [r.get('judge','?') for r in results],
        'judge_finals': [r.get('final_score') for r in results],
        'notes': [r.get('notes','') for r in results]
    }, f, indent=2)
" "$tmpjudge" "$result_file"
        rm -f "$tmpjudge"
        score=$(python3 -c "import json; print(json.load(open('$result_file'))['final_score'])" 2>/dev/null || echo "?")
        log "OK   $run_id/$game_slug/$agent_id → $score (${#judge_jsons[@]} judges)"
        ((done_count++)) || true
      else
        echo '{"error":"all_judges_failed","final_score":null}' > "$result_file"
        log "FAIL $run_id/$game_slug/$agent_id — no judge results"
        ((failed++)) || true
      fi

    done
  done
done

echo ""
echo "============================================"
echo "Static QA complete"
echo "  Scored:  ${done_count}"
echo "  Skipped: ${skipped} (already done)"
echo "  Failed:  ${failed}"
echo "  Total:   $((done_count + skipped + failed))"
echo "============================================"
