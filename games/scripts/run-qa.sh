#!/bin/bash
# run-qa.sh
# Spawns QA agent for a single game, updates results.json with scores
# Usage: run-qa.sh <run> <game> <game-name>

RUN=$1
GAME=$2
GAME_NAME=$3

BASE="/Users/oscar/.openclaw/workspace/games/$RUN/$GAME"
SCRIPTS="/Users/oscar/.openclaw/workspace/games/scripts"

QA_TASK="You are a QA engineer evaluating HTML5 game builds for a model benchmark.

For the game $GAME ($RUN), review each of the 5 model builds.

For each file below:
1. Read the file
2. Check which tasks were completed (read the TASKS DONE line in the comment header)
3. Score 0-10 on each dimension:
   - functionality: Is the game logic complete and correct?
   - keyboard_controls: Are controls implemented per the spec?
   - visual_fidelity: Does it look like the vintage game?
   - playability: Would a human enjoy playing this?
   - error_free: No obvious JS errors, syntax issues, or broken logic?
4. final_score = (functionality×0.30) + (keyboard_controls×0.20) + (visual_fidelity×0.20) + (playability×0.20) + (error_free×0.10)

Files to review:
- sonnet: $BASE/sonnet/index.html
- opus: $BASE/opus/index.html
- haiku: $BASE/haiku/index.html
- gpt-5-4: $BASE/gpt-5-4/index.html
- o3-mini: $BASE/o3-mini/index.html

Also read the spec at $BASE/spec.md for reference.

After reviewing all 5, write scores to $BASE/results.json

The results.json has a 'builds' section. For each model slug (sonnet, opus, haiku, gpt-5-4, o3-mini), update the 'qa_scores' object:
{
  \"functionality\": X,
  \"keyboard_controls\": X,
  \"visual_fidelity\": X,
  \"playability\": X,
  \"error_free\": X,
  \"final_score\": X
}

Also set the top-level field: \"qa_method\": \"static\"

When done, output:
QA_COMPLETE:$GAME - sonnet={S} opus={O} haiku={H} gpt-5-4={G} o3-mini={M} best={BEST} worst={WORST}"

openclaw agent --agent bench-sonnet --session-id "qa-$RUN-$GAME" --message "$QA_TASK" --timeout 300 2>&1
