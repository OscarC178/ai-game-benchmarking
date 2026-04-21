# Benchmark V2 — Plan

**Status:** Planning  
**Folder:** `/Users/oscar/.openclaw/workspace/games-v2/`  
**V1 cost:** ~$400 on a flawed design. This document captures every lesson.

---

## Why V1 Failed

The orchestrating agent imposed a 12-section spec template on every planner. Both Opus and GPT-5.4 filled in the same form — neither was free to design the spec. The "planner comparison" measured how models fill a template, not planning quality. The whole planner finding is invalid.

**Everything else V1 found holds:**
- Builder model rankings (Sonnet reliable, Haiku spec-sensitive, Gemini Flash > Pro, o3-mini confabulates)
- Browser agent QA catches bugs static review misses
- Isolated context per build is mandatory (Opus DNF root cause: context accumulation)
- Static QA is insufficient — playability bugs require actual gameplay testing

---

## V2 Design

### Central Question
**Does planner model quality affect build quality when planners are unconstrained?**

### Planner Prompt (no template, no structure imposed)
```
You are writing a game specification for a developer who will implement [GAME NAME] 
as a single self-contained HTML5 Canvas file with no external dependencies.

The developer is skilled but has never played this game. Write them a spec that 
gives them everything they need to build a complete, playable version.

No format is required. Write it however you think will best serve the developer.
```

That's it. The planner decides structure, depth, format. We measure what they choose.

### Planner Models
| Planner | Model ID | Notes |
|---------|----------|-------|
| Claude Opus 4.6 | `anthropic/claude-opus-4.6` | Top Anthropic |
| GPT-5.4 | `openai/gpt-5.4` | Top OpenAI |
| Gemini 3.1 Pro | `google/gemini-3-pro` | Top Google |
| GLM-5 | `palebluedot/z-ai/glm-5` | Top Zhipu — via PaleBlueDot |
| No planner (control) | — | Builder gets game name + build rules only |

### Builder Models
| Builder | Model ID | Notes |
|---------|----------|-------|
| Claude Opus 4.6 | `anthropic/claude-opus-4.6` | Top tier |
| Claude Sonnet 4.6 | `anthropic/claude-sonnet-4-6` | V1 top performer |
| Claude Haiku 4.5 | `anthropic/claude-haiku-4-5` | Small model, spec-sensitive |
| GPT-5.4 | `openai/gpt-5.4` | Top OpenAI |
| GPT-5.4 Mini | `openai/gpt-5.4-mini` | Small OpenAI |
| Gemini 3.1 Pro | `google/gemini-3-pro` | Top Google |
| Gemini 3 Flash | `google/gemini-3-flash` | V1: better than Pro |
| GLM-5 | `palebluedot/z-ai/glm-5` | New — tests across builder role too |

### Games (same 10, same order)
1. Pong
2. Snake
3. Breakout
4. Space Invaders
5. Tetris
6. Asteroids
7. Galaga
8. Frogger
9. Pac-Man
10. Donkey Kong

### Run Structure
Each run = one planner's specs × all 8 builders × 10 games.

| Run | Planner | Spec dir |
|-----|---------|----------|
| R1 | Claude Opus 4.6 | `specs/r1-opus/` |
| R2 | GPT-5.4 | `specs/r2-gpt54/` |
| R3 | Gemini 3.1 Pro | `specs/r3-gemini-pro/` |
| R4 | GLM-5 | `specs/r4-glm5/` |
| R5 | No planner (control) | `specs/r5-control/` |

5 runs × 10 games × 8 builders = **400 builds**

### QA Pipeline
**Stage 1 — Static (3 judges):**
- Claude Sonnet 4.6
- Gemini 3.1 Pro  
- GPT-5.4
- Same 5 dimensions: functionality (30%), keyboard_controls (20%), visual_fidelity (20%), playability (20%), error_free (10%)
- Final score = average of 3 judges

**Stage 2 — Browser agent (mandatory, every build):**
- Playwright keyboard input simulation
- `window.__qa` state bridge (generic patch, not per-game)
- Detects: position frozen, score never increments, state never transitions, JS errors
- Screenshot on any anomaly
- Reports stored in `qa/browser/`

---

## Critical Implementation Rules (learned from V1)

### Context Management — MANDATORY
1. **Every planner call = fresh isolated session.** No game bleeds into the next.
2. **Every builder call = fresh isolated session.** Never accumulate.
3. **Memory flush after each game:** After each game's builds complete, the orchestrator explicitly kills the session and starts a new one for the next game. No `--resume`, no `--session-id` reuse.
4. **Automatic restart on timeout:** If a build session hangs past the hard timeout (15 min), kill it, increment the attempt counter, restart with a fresh session.

### DNF Handling
- Each build gets **3 attempts** (fresh session each time)
- After 3 failures: mark as DNF, log reason, move on
- DNF = file missing OR file <500 bytes OR file fails basic HTML parse
- Do NOT trust JSON_RESULT self-reporting — always verify the artefact

### Overnight Safety — SEQUENTIAL EXECUTION (no parallel)
- **All builds run sequentially, one at a time.** Parallel execution caused timeouts in V1.
- Order: game 1 → all 8 builders sequentially → game 2 → all 8 builders → ...
- Hard timeout: 15 min per build attempt
- Context cleared and session killed between every single build
- Heartbeat Telegram message every 30 min with progress summary
- Final summary posted to Telegram when complete
- All output written to disk continuously — crash recovery reads existing files and skips completed builds

### Verification (not self-reporting)
```python
def verify_build(path):
    if not os.path.exists(path): return "missing"
    if os.path.getsize(path) < 500: return "empty"
    with open(path) as f:
        content = f.read()
    if "<canvas" not in content: return "no_canvas"
    if "requestAnimationFrame" not in content: return "no_gameloop"
    return "ok"
```

---

## Folder Structure

```
games-v2/
  PLAN.md                    ← this file
  specs/
    r1-opus/
      pong/spec.md
      snake/spec.md
      ...
    r2-gpt54/
    r3-gemini-pro/
    r4-glm5/
    r5-control/              ← empty specs (control condition)
  builds/
    r1-opus/
      pong/
        opus/index.html
        sonnet/index.html
        haiku/index.html
        ...
      snake/
        ...
  qa/
    static/
      r1-opus/pong/opus.json
      ...
    browser/
      r1-opus/pong/opus-report.json
      r1-opus/pong/opus-screenshot.png
  reports/
    launcher.html
    benchmark-report.md
  scripts/
    01_generate_specs.sh     ← Phase 1: planner calls
    02_build_games.sh        ← Phase 2: builder calls (overnight)
    03_static_qa.sh          ← Phase 3: 3-judge static QA
    04_browser_qa.sh         ← Phase 4: Playwright browser QA
    05_generate_report.py    ← Phase 5: compile results → report
    lib/
      verify_build.py        ← artefact verification (not self-report)
      session_manager.py     ← isolated session spawn + kill
      qa_bridge_patch.py     ← generic window.__qa injector
      telegram_notify.sh     ← progress heartbeats
```

---

## Phase Gates (don't skip these)

### Gate 1: Before any builds
- [ ] All 40 specs generated (4 planners × 10 games)
- [ ] **Oscar reviews all 40 specs** — confirms no obvious failures, structural diversity visible
- [ ] Control specs confirmed empty (just game name)
- [ ] Budget estimate confirmed

### Gate 2: After spec review
- [ ] Oscar approves to proceed
- [ ] Session manager tested with 1 game × 1 builder (smoke test)
- [ ] Verify_build.py tested against known good/bad files
- [ ] Telegram heartbeat tested

### Gate 3: After builds complete
- [ ] DNF rate checked — if >20% DNF, investigate before running QA
- [ ] Spot-check 5 random builds manually
- [ ] Oscar approves QA phase

### Gate 4: Final
- [ ] Static QA complete
- [ ] Browser QA complete
- [ ] Report generated
- [ ] Oscar reviews before publish

---

## Budget Estimate

| Item | Count | Unit cost | Total |
|------|-------|-----------|-------|
| Planning: 4 planners × 10 games | 40 | ~$0.50 | ~$20 |
| Building: 400 builds × avg $1.20 | 400 | $1.20 | ~$480 |
| Static QA: 400 builds × 3 judges | 1200 | $0.15 | ~$180 |
| Browser QA: 400 builds | 400 | $0.05 | ~$20 |
| Buffer (10%) | — | — | ~$70 |
| **Total** | | | **~$770** |

*Note: Opus as both planner and builder inflates cost. Adjust if budget is a constraint — can drop Opus as builder to save ~$120.*

---

## Key Rules (never break these)

1. **No templates given to planners.** Brief only.
2. **Human reviews specs before builds start.** Gate 1 is not optional.
3. **Every session is isolated.** No context accumulation.
4. **Verify artefacts, not model output.** Trust files, not JSON_RESULT.
5. **3 attempts then DNF.** Don't hang on one broken build.
6. **Browser QA is mandatory.** Static is supplementary.

---

*Created: 2026-04-01*  
*V1 cost: ~$400*  
*V2 estimated: ~$770 (more models, better methodology)*
