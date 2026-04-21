#!/usr/bin/env bash
# 03_static_qa.sh — Phase 3: 3-judge static QA
# Judges: bench-sonnet, bench-gemini-pro, bench-gpt54
# Dimensions: functionality(30%) keyboard_controls(20%) visual_fidelity(20%) playability(20%) error_free(10%)
# Final score = average of 3 judge weighted totals
#
# Usage: ./03_static_qa.sh [--run r1-opus] [--game pong]

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V2_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILDS_DIR="$V2_DIR/builds"
QA_DIR="$V2_DIR/qa/static"
NOTIFY="$SCRIPT_DIR/lib/telegram_notify.sh"

notify() { bash "$NOTIFY" "$1" 2>/dev/null || true; }
log()    { echo "[$(date +%H:%M:%S)] $*"; }

FILTER_RUN=""
FILTER_GAME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run)  FILTER_RUN="$2";  shift 2 ;;
    --game) FILTER_GAME="$2"; shift 2 ;;
    *) shift ;;
  esac
done

RUNS=(r1-opus r2-gpt54 r3-gemini-pro r4-glm5 r5-control)
GAMES=(pong snake breakout space-invaders tetris asteroids galaga frogger pac-man donkey-kong)
BUILDERS=(bench-opus bench-sonnet bench-haiku bench-gpt54 bench-gpt54mini bench-gemini-pro bench-gemini-flash bench-glm5)
JUDGES=(bench-sonnet bench-gemini-pro bench-gpt54)
QA_TIMEOUT=180

mkdir -p "$QA_DIR"

total=0; done_count=0; failed=0

notify "🔬 V2 Static QA starting — 3 judges per build"

for run_id in "${RUNS[@]}"; do
  [[ -n "$FILTER_RUN" && "$run_id" != "$FILTER_RUN" ]] && continue

  for game_slug in "${GAMES[@]}"; do
    [[ -n "$FILTER_GAME" && "$game_slug" != "$FILTER_GAME" ]] && continue

    for agent_id in "${BUILDERS[@]}"; do
      build_file="$BUILDS_DIR/$run_id/$game_slug/$agent_id/index.html"
      qa_dir="$QA_DIR/$run_id/$game_slug/$agent_id"
      result_file="$qa_dir/result.json"

      # Skip DNF and missing
      [[ -f "$BUILDS_DIR/$run_id/$game_slug/$agent_id/dnf.txt" ]] && continue
      [[ ! -f "$build_file" ]] && continue
      # Already scored
      [[ -f "$result_file" ]] && { ((done_count++)) || true; continue; }

      mkdir -p "$qa_dir"
      ((total++)) || true
      log "QA $run_id/$game_slug/$agent_id"

      judge_jsons=()

      for judge in "${JUDGES[@]}"; do
        session_id="v2-qa-${run_id}-${game_slug}-${agent_id}-${judge}-$$"

        prompt="You are scoring an HTML5 game build for a benchmark.

Read the source file at this path: ${build_file}

Score on 5 dimensions (0–10 each):
- functionality: game logic complete and correct
- keyboard_controls: controls work as expected
- visual_fidelity: rendering looks correct for this game type
- playability: actually playable as a game
- error_free: no obvious JS errors or crashes

Weighted final: (func*0.30)+(kbd*0.20)+(vis*0.20)+(play*0.20)+(err*0.10)

Output ONLY valid JSON, nothing else:
{\"judge\":\"${judge}\",\"functionality\":N,\"keyboard_controls\":N,\"visual_fidelity\":N,\"playability\":N,\"error_free\":N,\"final_score\":N.NN,\"notes\":\"one sentence\"}"

        raw=$(openclaw agent \
          --agent "$judge" \
          --session-id "$session_id" \
          --message "$prompt" \
          --timeout "$QA_TIMEOUT" \
          --json 2>/dev/null) || true

        # Extract JSON from reply
        judge_json=$(echo "$raw" | python3 -c "
import sys, json, re
try:
    d = json.load(sys.stdin)
    payloads = d.get('result', {}).get('payloads', [])
    reply = payloads[0].get('text', '') if payloads else (d.get('reply','') or d.get('text','') or '')
    m = re.search(r'\{[^{}]+\}', reply, re.DOTALL)
    print(m.group(0) if m else '')
except:
    pass
" 2>/dev/null || echo "")

        if [[ -n "$judge_json" ]] && echo "$judge_json" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
          echo "$judge_json" > "$qa_dir/${judge}.json"
          judge_jsons+=("$judge_json")
        else
          log "WARN: $judge gave no valid JSON"
        fi

        sleep 2
      done

      # Average across judges
      if [[ ${#judge_jsons[@]} -gt 0 ]]; then
        python3 - "${judge_jsons[@]}" > "$result_file" <<'PYEOF'
import sys, json

judge_jsons = sys.argv[1:]
results = []
for j in judge_jsons:
    try:
        results.append(json.loads(j))
    except:
        pass

dims = ["functionality","keyboard_controls","visual_fidelity","playability","error_free"]
weights = {"functionality":0.30,"keyboard_controls":0.20,"visual_fidelity":0.20,"playability":0.20,"error_free":0.10}

avg = {}
for d in dims:
    vals = [float(r[d]) for r in results if d in r]
    avg[d] = round(sum(vals)/len(vals), 2) if vals else 0.0

final = round(sum(avg[d]*weights[d] for d in dims), 2)

print(json.dumps({
    "final_score": final,
    "scores": avg,
    "judges": [r.get("judge","?") for r in results],
    "judge_finals": [r.get("final_score") for r in results],
    "notes": [r.get("notes","") for r in results]
}, indent=2))
PYEOF
        score=$(python3 -c "import json; print(json.load(open('$result_file'))['final_score'])" 2>/dev/null || echo "?")
        log "OK    $run_id/$game_slug/$agent_id score=$score"
        ((done_count++)) || true
      else
        echo '{"error":"all_judges_failed","final_score":null}' > "$result_file"
        log "FAIL  $run_id/$game_slug/$agent_id — no judge results"
        ((failed++)) || true
      fi

    done
  done
done

echo ""
echo "============================================"
echo "Static QA complete — ${done_count} scored, ${failed} failed"
echo "============================================"
notify "✅ Static QA done — ${done_count} scored, ${failed} failed. Run 04_browser_qa.sh next."
