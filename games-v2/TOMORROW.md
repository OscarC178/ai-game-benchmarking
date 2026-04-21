# V2 Benchmark — Tomorrow's Run Plan

*Prepared: 2026-04-01 00:50 BST*

---

## Overview

400 builds across 5 planners × 10 games × 8 builders.
Sequential only. Fresh session context per build. 3 attempts then DNF.

---

## Phase 1 — Spec Generation (~45 min)

```bash
cd /Users/oscar/.openclaw/workspace/games-v2/scripts
./01_generate_specs.sh
```

Generates 40 specs (4 planners × 10 games). Control specs (r5) are written automatically.
You'll get a Telegram message when done.

**⛔ GATE: You must review the specs before approving Phase 2.**

Quick review command:
```bash
# See all specs side by side for one game
cat games-v2/specs/r1-opus/pong/spec.md
cat games-v2/specs/r2-gpt54/pong/spec.md
cat games-v2/specs/r3-gemini-pro/pong/spec.md
cat games-v2/specs/r4-glm5/pong/spec.md
```

Check: are they structurally different? Do they look like each planner made its own choices?
If yes → approve Phase 2.

---

## Phase 2 — Builds (~6–8 hrs)

```bash
./02_build_games.sh
```

Runs all 400 builds sequentially. Telegram heartbeat every 30 min.
Crash-safe — if it dies, just re-run and it skips completed builds.
Partial reruns: `./02_build_games.sh --run r1-opus --game pong`

---

## Phase 3 — Static QA (~2 hrs)

```bash
./03_static_qa.sh
```

3 judges (Sonnet, Gemini Pro, GPT-5.4) score each build on 5 dimensions.
Skips DNFs automatically.

---

## Phase 4 — Browser QA (~1 hr)

```bash
./04_browser_qa.sh
```

Playwright plays each game via keyboard inputs, detects freezes, JS errors, stuck states.
Mandatory on every build — not optional like in V1.

---

## Phase 5 — Report

```bash
python3 05_generate_report.py
```

Outputs:
- `games-v2/reports/benchmark-report.md`
- `games-v2/reports/launcher.html`

---

## Models Used

### Planners
| Run | Model |
|-----|-------|
| r1-opus | Claude Opus 4.6 (PBD) |
| r2-gpt54 | GPT-5.4 (PBD) |
| r3-gemini-pro | Gemini 3.1 Pro (PBD) |
| r4-glm5 | GLM-5 (PBD) |
| r5-control | No planner |

### Builders
| Agent | Model |
|-------|-------|
| bench-opus | Claude Opus 4.6 |
| bench-sonnet | Claude Sonnet 4.6 |
| bench-haiku | Claude Haiku 4.5 |
| bench-gpt54 | GPT-5.4 |
| bench-gpt54mini | GPT-5.4 Mini |
| bench-gemini-pro | Gemini 3.1 Pro |
| bench-gemini-flash | Gemini Flash |
| bench-glm5 | GLM-5 |

### QA Judges
Sonnet 4.6 + Gemini 3.1 Pro + GPT-5.4

---

## Key Rules (don't skip)

1. Review specs before approving builds
2. Builds are verified by file artefact, not model self-report
3. DNF = 3 failed attempts, then skip and continue
4. Sequential only — never run two phases in parallel
5. Browser QA is mandatory, not optional

---

## Estimated Budget

| Phase | Est. Cost |
|-------|-----------|
| Spec generation (40 specs) | ~$20 |
| Builds (400 × ~$1.20 avg) | ~$480 |
| Static QA (400 × 3 judges) | ~$120 |
| Browser QA | ~$20 |
| **Total** | **~$640** |

---

## If Something Goes Wrong

- **Script crashes mid-run:** re-run the same script, it skips completed work
- **High DNF rate (>25%):** stop, check build-log.txt, fix before continuing
- **GLM-5 errors:** it's new to PBD — if it consistently fails, comment it out of BUILDER_ORDER in 02_build_games.sh and continue
- **Telegram not working:** check TELEGRAM_BOT_TOKEN env var, or just watch build-log.txt directly

---

*All scripts in: `/Users/oscar/.openclaw/workspace/games-v2/scripts/`*
