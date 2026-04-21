# Interactive Guide — Project Plan

A 5-tab interactive field guide to AI model evaluation. Reader learns by playing the 580+ retro games we built, not by reading descriptions of them. The retro games are the evidence; the guide is the frame.

## Anchoring concept: AI Iron Triangle

**Speed ↔ Cost ↔ Accuracy/Quality** — where "quality" includes *truthfulness under pressure*. A model may give a wrong answer to appease the user or match expected output. Gemini Flash's judge-inflation is the canonical example: fast, cheap, seemingly high-quality, but the quality was appeasement, not accuracy. Tab 1 lessons hang off this frame.

## The 5 tabs

| # | Tab | Job |
|---|---|---|
| 1 | **Lazy TLDR / Lessons** | 6-8 practical lessons with "apply this" takeaways. Gateway to evidence. |
| 2 | **Library** | Every game playable, filterable, rateable. Side-by-side compare. Foundation tab. |
| 3 | **Plans & Prompts** | Meta-prompt + planner specs. V1 story: same template, different fills. V2 story: free prompt, different interpretations. |
| 4 | **QA Data** | Full judge-score table, per-dimension, per-judge, sortable. Judge prompt viewable. Row-click → Library. |
| 5 | **Paper** | The academic companion, with live side-by-side exhibits embedded at key findings. |

## Pedagogical pattern (every exhibit)

**Hook → Play → Reveal → Explain.** Don't tell the reader a finding; let them discover it, then explain what they just saw.

## Build phases

### Phase 1 — Foundation (COMPLETE)
- [x] Data audit complete
- [x] PLAN.md written
- [x] `guide/aggregate.py` — reads verified-data.json + review/ratings.json → writes `guide/data.json`
- [x] `guide/server.py` — serves guide, games, specs, data
- [x] `guide/index.html` — 5-tab shell (Tabs 1/3/4/5 stubbed)
- [x] **Tab 2 Library MVP** — grid of 690 builds, filters (version/planner/run/builder/game/min-score/has-rating/include-dnf), click-to-play modal with iframe + per-judge scores + dimensions + judge notes + inline human-rating form
- [x] Smoke-test end-to-end: all endpoints HTTP 200, ratings.json unchanged (103 preserved)

**Startup:** `python3 guide/server.py` then http://localhost:5858

### Phase 2 — Tab 4 (QA Data) — COMPLETE
- [x] Sortable table: every build × judge × dimension (column headers sort on click)
- [x] Row-click → opens game in Tab 2 Library modal
- [x] Judge prompt + rubric viewable (collapsible panel — V1 and V2 prompts both shown)
- [x] Filter by dataset, game, planner, builder, min-spread, has-rating, include-DNF
- [x] Judge spread computed and shown (flags rows where judges disagreed ≥2 points)
- [x] Human rating inline indicator on each row

### Phase 3 — Tab 3 (Plans & Prompts) — COMPLETE
- [x] V1 framing card: "All V1 planners were given the same 12-section template"
- [x] V2 framing card: "All V2 planners were given the same free-form prompt"
- [x] V2 meta-prompt shown verbatim (from `games-v2/scripts/01_generate_specs.sh`)
- [x] V1 12-section template listed + note that exact prompt string wasn't saved to disk
- [x] Browse specs by game; game dropdown defaults to Pong (clearest diversity)
- [x] All 70 specs (7 canonical planners × 10 games) loaded with byte counts
- [x] Byte-count visualizer bar — longest spec = full width, others scale relative
- [x] Click-to-expand lazy loads the spec markdown, rendered via `marked` CDN
- [x] V1 specs hidden by default (cleaner V2 story); toggle to include V1
- [x] Server `/spec/{dataset}/{run}/{game}` endpoint extended to accept 3-part paths

### Phase 4 — Tab 1 (TLDR / Lessons) — COMPLETE
- [x] Iron Triangle banner at the top (Speed/Cost/Quality, quality-as-appeasement framing)
- [x] 8 lesson cards with **live stats computed from data.json** (not hardcoded)
- [x] Iron Triangle highlighted as **Lesson 05** — centrepiece with amber border + badge
- [x] Each card has a **"See evidence" button** that switches tabs and pre-sets filters (cross-navigation)
- [x] Tab 1 is now the default landing tab
- [x] Lessons: 01 Have a plan · 02 Context is methodology · 03 Training data decides · 04 Specs can hurt · **05 The Iron Triangle** · 06 Taste is non-negotiable · 07 It's the pair not the model · 08 Know natural limits
- [x] Beginners-guide content NOT mined — reserved for Phase 6 redesign

### Phase 5 — Tab 5 (Paper integration + polish) — COMPLETE
- [x] Tab 5: full paper embedded via lazy-loaded iframe, with "open in new tab" and "beginners guide" shortcuts
- [x] 3 live side-by-side exhibits embedded in `paper/index.html`:
  - Section 3 (Game Difficulty): Snake (9.27) vs Donkey Kong (8.00) — training data story
  - Finding 6 (Specs): Sonnet + Opus spec (8.37) vs Sonnet + Control (9.00) — same builder, spec hurts
  - Finding 8 (Judges): DK by GPT-5.4 Nano — GPT 1.2, Opus 3.8, Flash 8.6 (spread 7.4)
- [x] Shareable hash URLs: `#lessons` / `#library` / `#prompts` / `#qa` / `#paper` and `#lib/<dataset>/<run>/<game>/<builder>` opens the library modal
- [x] Deep-link support: paper exhibits use `target="_top"` on "↗ open" links so iframes and direct-paper both navigate the guide shell to the right build
- [x] Hash updates when modal opens/closes — readers can copy the URL to share any build

### Phase 6 — Beginners guide redesign (deferred)
- [ ] Invoke `frontend-design` skill on `guide/beginners-guide.html`
- [ ] Content review: what stays, what migrates into Tab 1 lessons
- [ ] Link from new guide to beginners-guide as supplementary reading

## Open questions

- **Visitor ratings:** ephemeral-local only (browser localStorage), accumulate to a shared file, or both? Current lean: ephemeral-local with "Oscar's ratings" as canonical.
- **V1 prompt file reconstruction:** the 12-section template can serve as "the prompt" for both V1 planners. Good enough.
- **Galaga DNF discrepancy:** `audit-report.md` flags `r1-opus/galaga/bench-opus` as DNF but HTML exists. Surface in QA tab or silently treat as DNF? Lean: surface — honesty is the guide's brand.
- **V1 judge notes (parked):** verified-data.json has no per-build notes for V1. Raw text exists at `games/run{1,2}*/{game}/qa-output.txt` — one judge's analysis of 5 builds per game, in free markdown. Option: add a "View raw V1 QA analysis" link in the modal that serves the whole file. Deferred for now.

## Known caveats to surface (not hide) in guide

- Runs 1-6 have no token data — cost is estimated, not metered
- Gemini Flash as V1 judge inflated all scores by ~2.4pts — the canonical AI-appeasement example
- V1 vs V2 scores not directly comparable — different judge panels
- 8 V1 DNFs and 3 V2 DNFs — 2 V2 DNFs were never rebuilt
- No human ground-truth yet — only Oscar's in-progress ratings
- 46 of 397 V2 builds failed objective Playwright checks — subset exists but wasn't integrated (potential Chapter 6 convergent-validity exhibit)

## Data sources (for aggregate.py)

| Source | Content |
|---|---|
| `verified-data.json` | Per-build consensus + per-judge + per-dimension scores (V1 & V2) |
| `games-v2/reports/results.json` | V2 browser-bug results, DNF status |
| `review/ratings.json` | Oscar's in-progress human ratings |
| `games-v2/specs/{run}/{game}/spec.md` | V2 planner specs |
| `games/run{1,2}*/{game}/spec.md` | V1 planner specs |
| `audit-report.md` | DNF log, data health notes |
| `games/runs_7_8_build_results.json` | Actual token/cost data (runs 7-8 only) |

## Checklist progress

Mark items complete with `[x]`. Refer back to this file before each new work session.
