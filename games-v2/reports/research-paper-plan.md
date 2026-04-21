# Research Paper Plan — AI Game Building Benchmark

## Decision: Two Papers or One?

**Recommendation: ONE paper, two parts.** The V1→V2 story is the paper's spine — it's a learning journey. Splitting would lose the "we learned X, so we redesigned Y" narrative that makes it genuinely useful.

If it runs long, we can always split later. Better to plan for one and trim than plan for two and have overlap.

---

## Structure

### Part 0: Abstract + Setup
- What we tested: Can AI models build complete, playable games from scratch?
- Scale: 580+ game builds across 9 models, 10 games, 2 benchmark rounds
- Key findings preview (3-4 bullet max)
- Who this is for: developers evaluating AI coding tools, AI researchers, curious humans

### Part 1: The Experiment Design
**"How to benchmark AI game builders"**

#### 1.1 The Task
- Why vintage arcade games? (self-contained, well-understood, clear success criteria)
- The constraint: single HTML file, zero dependencies, Canvas only
- 10-game difficulty ladder: Pong → Snake → Breakout → Space Invaders → Tetris → Asteroids → Galaga → Frogger → Pac-Man → Donkey Kong
- Why this ordering matters (each game introduces new complexity)

#### 1.2 The Models
- Full model roster across both rounds:
  - **Anthropic:** Opus 4.6, Sonnet 4.6, Haiku 4.5
  - **OpenAI:** GPT-5.4, GPT-5.4 Mini, GPT-5.4 Nano, o3-mini
  - **Google:** Gemini 3.1 Pro, Gemini 3 Flash
  - **Z-AI:** GLM-5 (V2 only)
- Model tiers: frontier, mid-tier, value
- Pricing table

#### 1.3 The Tooling
- OpenClaw agent framework — what it is, how we used it
- Isolated sessions per build (and why — learned from V1 Opus DNFs)
- Build verification pipeline
- The "bench-*" agent setup

### Part 2: Round 1 — Same Plan, Different Builders
**"V1: Who builds the best game from the same blueprint?"**

#### 2.1 Methodology
- Two spec authors: Opus (verbose, precise) and GPT-5.4 (concise, prose)
- **Critical admission:** both used a 12-section template imposed by the orchestrating agent
- 8 runs, 9 models, ~80 builds
- Multi-judge QA: GPT-5.4 + Opus + Gemini Flash scoring panel

#### 2.2 Builder Rankings
- Full leaderboard with scores
- Interactive heatmap: model × game
- The narrative: Sonnet = reliable, GPT-5.4 = hard-game specialist, Opus = capable but context-limited

#### 2.3 The Spec Effect
- Does the plan matter when the planner is constrained?
- Opus specs (+0.12 avg) vs GPT specs — marginal difference
- BUT: massive effect on small models (Nano: +0.70, Haiku: +0.29)
- The smoking gun: GPT boilerplate T11 "implement lives" for games without lives
- Key insight: simpler specs help weaker builders

#### 2.4 The Things We Got Wrong
- Template contamination — we measured form-filling, not planning
- Static QA misses runtime bugs (Pac-Man turn trap, DK ladder snap)
- o3-mini confabulation — builds look complete but aren't
- Opus DNFs were infrastructure, not capability
- These mistakes directly informed V2's design

### Part 3: Round 2 — Planning From Scratch
**"V2: Does planning quality affect build quality?"**

#### 3.1 What We Changed
- No template: each planner gets only "write a spec for [game], your way"
- The exact prompt (verbatim)
- 5 planners: Opus, GPT-5.4, Gemini Pro, GLM-5, + no-planner control
- 8 builders × 10 games × 5 runs = 400 builds
- New QA: automated Playwright browser playtesting (plays the actual game)

#### 3.2 Spec Analysis — How Different Models Plan
- Spec length comparison: Opus (503 lines), GLM-5 (615), GPT-5.4 (349), Gemini Pro (93)
- Spec style comparison (side-by-side excerpts): Opus pixel-precise vs Gemini high-level
- What each planner prioritises (coordinates vs behaviour vs feel)

#### 3.3 Builder Rankings (Playtest)
- Full leaderboard: GPT-5.4 (7.04) → GPT-5.4 Mini (2.98)
- Game difficulty: Frogger (8.43) easiest → Snake (3.85) hardest
- Heatmap: builder × game

#### 3.4 The Opus Paradox
- **The headline:** The "best" planner produces the worst results
- Evidence table: Opus plan (4.90) vs No plan (6.59)
- Per-game breakdown: Donkey Kong Δ = +5.45 for no plan
- Root cause: over-specification (exact pixel coords, physics constants)
- The weak builder amplifier: strong builders -0.80, weak builders -3.10
- The GLM-5 exception: longer specs but vaguer = less damage
- Comparison to V1's constrained finding (+0.12 for Opus)
- **The takeaway:** Planning quality ≠ build quality. Best plans ≠ best outcomes.

#### 3.5 The Control Group Surprise
- No-planner builds win overall (6.59)
- When does structure help? (simple games, strong builders)
- When does it hurt? (complex games, weak builders)
- The software engineering analogy: over-architected specs for junior devs

### Part 4: Cross-Round Analysis
**"What V1 + V2 Tell Us Together"**

#### 4.1 The Builder Consistency Story
- Models that rank well in V1 rank well in V2 (Sonnet, GPT-5.4)
- The tier system holds: frontier > mid > value > budget
- The one exception: GPT-5.4 Mini (decent in V1, catastrophic in V2 playtest)

#### 4.2 Static QA vs Playtest QA
- V1 used 3-judge static panel: averages ~8/10
- V2 used Playwright playtest: averages ~5.8/10
- The gap: games that "look right in code" but don't work when played
- Specific examples with screenshots

#### 4.3 Game Difficulty — Universal Truths
- Pac-Man and Donkey Kong are hardest in BOTH rounds
- Pong and Snake are easiest in BOTH rounds
- The complexity factors: state machines, physics, AI

#### 4.4 The Planning Paradox — Full Picture
- V1 (constrained): Opus specs +0.12 (marginal advantage)
- V2 (unconstrained): Opus specs -1.69 (significant disadvantage)
- Interpretation: Opus is better at filling templates, worse at unguided planning
- Or: Opus plans are better documents but worse implementation guides

### Part 5: Practical Guide
**"How to set up AI agents for coding tasks"**

#### 5.1 Model Selection Guide
- Decision tree: budget → complexity → supervision level
- **Ship quality, no supervision:** Sonnet
- **Budget builds, needs review:** Gemini Flash or GPT-5.4 Nano
- **Hard problems:** GPT-5.4
- **Avoid for autonomous coding:** o3-mini (confabulates)
- **Avoid as planner for weaker builders:** Opus

#### 5.2 Spec Writing Best Practices
- Match spec detail to builder capability
- Avoid pixel-exact coordinates — use relative descriptions
- Prose > formulas for smaller models
- Game-specific task lists > generic templates
- Fewer constraints = more room for the builder's strengths

#### 5.3 Infrastructure Lessons
- Isolated context per task (Opus DNF fix)
- Build verification step (o3-mini confabulation catch)
- Automated playtest QA > static code review
- Per-build timeouts (Playwright hangs)
- Workspace contamination: bench agents shouldn't load your MEMORY.md

#### 5.4 Cost Optimisation
- Score-per-dollar table
- The Flash/Nano sweet spot
- When to pay for frontier (Pac-Man, Donkey Kong)
- When budget is fine (Pong, Frogger, Tetris)

#### 5.5 What We'd Do Differently Next Time
- Clean workspace for bench agents (no SOUL.md, MEMORY.md bleeding in)
- Human playtest sample alongside automated QA
- Multiple builds per model×game for statistical confidence
- Planner specs reviewed for correctness before builder phase
- Output token limit testing (did maxTokens bottleneck any builds?)

### Part 6: Appendices
- Full score tables (V1 + V2)
- Bug type distribution
- Spec excerpts (Opus vs Gemini Pro vs GPT-5.4 for same game)
- Links to playable games (launcher.html)
- Methodology notes / limitations / caveats

---

## Design Notes

- **Responsive HTML** — reads well on mobile and desktop
- **Dark theme** — matches existing reports
- **Interactive elements:** collapsible sections, heatmaps, bar charts
- **Tabs where appropriate** (V1 vs V2 comparison views)
- **Pull quotes** for key findings (designed to be screenshot-able for social)
- **Estimated length:** ~8000-10000 words equivalent with charts
- **All data inline** — no external JSON fetches, works as standalone file

---

## Data Sources

- `games/benchmark-report.md` — V1 full report
- `games/run*/*/results.json` — V1 per-game scores
- `games-v2/qa/playtest/all-results.json` — V2 playtest scores
- `games-v2/qa/playtest/report-data.json` — V2 data + spec sizes
- `games-v2/specs/*/spec.md` — all V2 specs
- `games-v2/scripts/01_generate_specs.sh` — V2 planner prompt
- `games-v2/PLAN.md` / `games/BENCHMARK_V2_PLAN.md` — methodology docs
