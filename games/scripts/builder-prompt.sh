#!/bin/bash
# builder-prompt.sh
# Usage: builder-prompt.sh <run> <game> <game-name> <model-slug> <model-id>
# Builds a single game and writes results JSON summary to stdout

RUN=$1       # e.g. run1-opus-plan
GAME=$2      # e.g. pong
GAME_NAME=$3 # e.g. Pong
MODEL_SLUG=$4 # e.g. sonnet
MODEL_ID=$5   # e.g. anthropic/claude-sonnet-4-6

SPEC_PATH="/Users/oscar/.openclaw/workspace/games/$RUN/$GAME/spec.md"
OUT_PATH="/Users/oscar/.openclaw/workspace/games/$RUN/$GAME/$MODEL_SLUG/index.html"

# Map slug to agent
case "$MODEL_SLUG" in
  sonnet) AGENT="bench-sonnet" ;;
  opus) AGENT="bench-opus" ;;
  haiku) AGENT="bench-haiku" ;;
  gpt-5-4) AGENT="bench-gpt54" ;;
  o3-mini) AGENT="bench-o3mini" ;;
  *) echo "Unknown model slug: $MODEL_SLUG"; exit 1 ;;
esac

SESSION_ID="$RUN-$GAME-$MODEL_SLUG"

TASK="You are an expert HTML5/JS game developer participating in a model benchmark.

Your job: Build a complete, playable vintage game as a single self-contained HTML file.

SPEC FILE: Read $SPEC_PATH

OUTPUT FILE: $OUT_PATH

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
When done, write the file. Then output this exact JSON summary on its own line starting with JSON_RESULT:

JSON_RESULT:{\"model_id\":\"$MODEL_ID\",\"game\":\"$GAME\",\"run\":\"$RUN\",\"status\":\"complete\",\"wall_clock_seconds\":0,\"tokens_input\":0,\"tokens_output\":0,\"estimated_cost_usd\":0.00,\"iterations\":0,\"errors_found\":0,\"errors_fixed\":0,\"task_checklist\":{\"T01\":\"complete\",\"T02\":\"complete\",\"T03\":\"complete\",\"T04\":\"complete\",\"T05\":\"complete\",\"T06\":\"complete\",\"T07\":\"complete\",\"T08\":\"complete\",\"T09\":\"complete\",\"T10\":\"complete\",\"T11\":\"complete\",\"T12\":\"complete\"},\"last_completed_task\":\"T12\",\"first_failed_task\":null}

Replace the values with actuals. Mark each task as complete, failed, or skipped.

## MANDATORY COMMENT HEADER
The VERY FIRST lines of $OUT_PATH must be:

<!--
  GAME:           $GAME_NAME
  RUN:            $RUN
  BUILDER:        $MODEL_ID
  PLANNER:        anthropic/claude-opus-4.6
  BUILD TIME:     {seconds} seconds
  TOKENS IN:      {count}
  TOKENS OUT:     {count}
  ESTIMATED COST: \${amount}
  ITERATIONS:     {count}
  TOOLS USED:     write, read
  STATUS:         complete
  TIMESTAMP:      {ISO-8601}
  TASKS DONE:     T01,T02,...
  FIRST FAILURE:  none
-->

## PRICING (for cost estimate)
- claude-sonnet-4.6: \$3/M in, \$15/M out
- claude-opus-4.6: \$15/M in, \$75/M out  
- claude-haiku-4.5: \$0.80/M in, \$4/M out
- gpt-5.4: \$2.50/M in, \$15/M out
- o3-mini: \$1.10/M in, \$4.40/M out"

# Run the agent
openclaw agent --agent "$AGENT" --session-id "$SESSION_ID" --message "$TASK" --timeout 600 2>&1
