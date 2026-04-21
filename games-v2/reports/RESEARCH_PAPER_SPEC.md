# Research Paper Build Spec — For Ross

## Task
Build a single self-contained HTML research paper at:
`/Users/oscar/.openclaw/workspace/games-v2/reports/research-paper.html`

## CRITICAL BUILD STRATEGY
The HTML will be ~80-120KB. **DO NOT try to write it in one tool call.** You WILL hit output limits.

**Approach:** Write a Python builder script (`/Users/oscar/.openclaw/workspace/games-v2/scripts/build_paper.py`) that:
1. Loads V1 and V2 data from JSON files on disk
2. Constructs the HTML programmatically (string concatenation, f-strings)
3. Embeds computed data as inline `<script>` JSON
4. Writes the final HTML to disk
5. Reports file size on completion

Then run: `cd /Users/oscar/.openclaw/workspace/games-v2 && python3 scripts/build_paper.py`

The Python script itself can be large — write it in 2-3 chunks if needed using the `edit` tool to append, or write it all at once if it fits.

---

## Data Sources (read these files)

### V1 Data
- **Scores:** `/Users/oscar/.openclaw/workspace/games-v2/reports/v1-data.json`
  - Array of objects: `{run, game, builder, model_id, score, status, spec_generator, has_html, html_path}`
  - 182 scored builds across 8 runs
  - Runs: run1-opus-plan, run2-gpt-plan, run3-opus-isolated, run4-gpt-isolated, run5-opus-gemini, run6-gpt-gemini, run7-opus-mini-nano, run8-gpt-mini-nano
  - Builder slugs: sonnet, opus, haiku, gpt-5-4, o3-mini, gemini-pro, gemini-flash, gpt54-mini, gpt54-nano
  - Opus-spec runs: run1, run3, run5, run7. GPT-spec runs: run2, run4, run6, run8

- **Full narrative:** `/Users/oscar/.openclaw/workspace/games/benchmark-report.md`
  - Read this for V1 findings, model narratives, spec effect analysis, tables, cost data
  - This is the primary V1 reference document

### V2 Data
- **Scores + spec sizes:** `/Users/oscar/.openclaw/workspace/games-v2/qa/playtest/report-data.json`
  - `{reports: [{run, game, builder, score, bugs, js_errors}], spec_sizes: {"run/game": linecount}}`
  - 398 builds across 5 runs × 8 builders × 10 games
  - Runs: r1-opus, r2-gpt54, r3-gemini-pro, r4-glm5, r5-control
  - Builder slugs: bench-opus, bench-sonnet, bench-haiku, bench-gpt54, bench-gpt54mini, bench-gemini-pro, bench-gemini-flash, bench-glm5

- **V2 planner generation prompt** (from `/Users/oscar/.openclaw/workspace/games-v2/scripts/01_generate_specs.sh`):
```
You are writing a game specification for a skilled developer who will implement {game_name} as a single self-contained HTML5 Canvas file with no external dependencies.

The developer is skilled but has never played this game. Write them a spec that gives them everything they need to build a complete, playable version.

No format is required. Write the spec however you think will best serve the developer. Be as detailed as you think necessary.
```

### V2 Existing Analysis (reference for charts/structure)
- `/Users/oscar/.openclaw/workspace/games-v2/reports/playtest-report.html` — V2 playtest report HTML (reference for styling)

---

## Display Name Mappings

### V1 Builders
| Slug | Display | Provider |
|------|---------|----------|
| sonnet | Claude Sonnet 4.6 | Anthropic |
| opus | Claude Opus 4.6 | Anthropic |
| haiku | Claude Haiku 4.5 | Anthropic |
| gpt-5-4 | GPT-5.4 | OpenAI |
| o3-mini | o3-mini | OpenAI |
| gemini-pro | Gemini 3.1 Pro | Google |
| gemini-flash | Gemini 3 Flash | Google |
| gpt54-mini | GPT-5.4 Mini | OpenAI |
| gpt54-nano | GPT-5.4 Nano | OpenAI |

### V2 Builders
| Slug | Display |
|------|---------|
| bench-opus | Opus |
| bench-sonnet | Sonnet |
| bench-haiku | Haiku |
| bench-gpt54 | GPT-5.4 |
| bench-gpt54mini | GPT-5.4 Mini |
| bench-gemini-pro | Gemini Pro |
| bench-gemini-flash | Gemini Flash |
| bench-glm5 | GLM-5 |

### V2 Planners (Runs)
| Run | Display | Avg Spec Lines |
|-----|---------|----------------|
| r1-opus | Opus | 503 |
| r2-gpt54 | GPT-5.4 | 349 |
| r3-gemini-pro | Gemini Pro | 93 |
| r4-glm5 | GLM-5 | 615 |
| r5-control | No Planner | 0 |

---

## Paper Structure (6 parts)

### Part 0: Title + Abstract
- Title: "Building Games with AI: What 580 Builds Taught Us About Planning, Models, and the Limits of Specification"
- Subtitle: "A two-round benchmark of 9 AI models building vintage arcade games"
- 4-stat summary cards: Total Builds (580), Models Tested (10), Games (10), Rounds (2)
- 3-4 sentence abstract

### Part 1: The Experiment
**"How to benchmark AI game builders"**

1.1 **The Task** — Why vintage arcade games. Single HTML file constraint. The 10-game difficulty ladder:
Pong → Snake → Breakout → Space Invaders → Tetris → Asteroids → Galaga → Frogger → Pac-Man → Donkey Kong

1.2 **The Models** — Full roster table with provider, tier, pricing. Mark which appeared in V1 only, V2 only, or both.

1.3 **The Tooling** — OpenClaw agent framework. Isolated sessions per build. Build verification.

### Part 2: Round 1 — Same Plan, Different Builders
**V1: 9 models, 2 spec styles, ~180 builds**

2.1 **Methodology** — Two spec authors (Opus verbose, GPT-5.4 concise), both using imposed 12-section template. 3-judge static QA panel.

2.2 **Builder Rankings** — Leaderboard table + bar chart. Sonnet #1 (8.80), GPT-5.4 #2 (8.59). Include GPT-spec scores as primary, Opus-spec as secondary column.

2.3 **The Spec Effect** — Table showing delta per model. Key finding: small models benefit from simpler specs (Nano +0.70, Haiku +0.29). The T11 "implement lives" bug in GPT specs.

2.4 **Model Narratives** — Brief per-model story (2-3 lines each). Sonnet=reliable, Opus=capable but context-limited, Haiku=spec-dependent, GPT-5.4=hard-game specialist, o3-mini=confabulates, Gemini Flash>Pro.

2.5 **What V1 Got Wrong** — Critical admission: template contamination. Boilerplate tasks. Static QA misses runtime bugs. These directly informed V2.

### Part 3: Round 2 — Planning From Scratch
**V2: 5 planners, 8 builders, 400 builds**

3.1 **What We Changed** — No template. The verbatim planner prompt (in a styled blockquote). New QA: Playwright browser playtest. Control group (no planner).

3.2 **How Different Models Plan** — Spec length comparison bar chart. Side-by-side spec excerpt for Donkey Kong (Opus 605 lines with pixel coords vs Gemini Pro 93 lines with behaviour descriptions).

3.3 **Builder Rankings** — Leaderboard + bar chart. GPT-5.4 #1 (7.04), GPT-5.4 Mini last (2.98).

3.4 **Game Difficulty** — Rankings table. Frogger easiest (8.43), Snake hardest (3.85).

3.5 **The Opus Paradox** — THE key section. Needs:
- Pull quote: "The best planner produces the worst results. Opus-planned games score 4.90 — dead last. The control group with zero planning scores 6.59."
- Evidence table: Opus plan vs No plan, per game (Donkey Kong: 2.4 vs 7.9 = +5.4 delta)
- Root cause: over-specification with exact pixel coordinates
- The weak builder amplifier: strong builders Δ=-0.80, weak builders Δ=-3.10 
- Spec excerpt comparison (Opus Donkey Kong girder coordinates vs Gemini Pro "girders slope slightly")
- The GLM-5 exception (longest specs but vaguer = less damage)

3.6 **Planner Rankings** — Table: No Planner (6.59) → Opus (4.90). Spec length vs score correlation table.

### Part 4: Cross-Round Analysis
**"What V1 + V2 tell us together"**

4.1 **Builder Consistency** — Models that rank well in V1 rank well in V2. Tier system holds.

4.2 **Static QA vs Playtest QA** — V1 averages ~8/10, V2 averages ~5.8/10. The gap = games that look right in code but don't work when played.

4.3 **The Planning Paradox — Full Picture**
- V1 (constrained templates): Opus specs +0.12 (marginal advantage)
- V2 (unconstrained): Opus specs −1.69 (significant disadvantage)
- Interpretation: Opus is better at filling templates, worse at unguided planning for builder consumption

4.4 **Game Difficulty Across Rounds** — Pac-Man and Donkey Kong hardest in BOTH rounds. Pong easiest in both.

### Part 5: Practical Guide
**"How to set up AI agents for coding tasks"**

5.1 **Model Selection** — Decision tree / recommendation table:
- Ship quality, no supervision: Sonnet
- Budget builds: Gemini Flash or GPT-5.4 Nano  
- Hard problems: GPT-5.4
- Avoid: o3-mini (confabulates), Opus as planner for weak builders

5.2 **Spec Writing Best Practices**
- Match detail to builder capability
- Avoid pixel-exact coordinates — use relative/behavioral descriptions
- Prose > formulas for smaller models
- Game-specific task lists > generic templates

5.3 **Infrastructure Lessons**
- Isolated context per task
- Build verification step
- Automated playtest QA > static code review
- Workspace contamination: bench agents loading MEMORY.md etc.

5.4 **Cost Optimisation** — Score-per-dollar table from V1. Flash/Nano sweet spot.

5.5 **What We'd Do Differently**
- Clean workspace for bench agents
- Human playtest sample alongside automated QA
- Multiple builds per combo for statistical confidence
- Planner specs reviewed before builder phase
- Output token limit testing

### Part 6: Appendices
- Full V1 score table (all runs, all models, all games)
- Full V2 score table (all runs, all builders, all games)
- V2 bug type distribution
- Methodology notes / limitations

---

## Clickable Games — CRITICAL

Every game reference in tables and heatmaps should be a clickable link to the playable HTML file.

### Link Paths (relative to report location at `games-v2/reports/research-paper.html`)
- V1 games: `../../games/{run}/{game}/{builder}/index.html`
  - Example: `../../games/run1-opus-plan/pong/sonnet/index.html`
- V2 games: `../builds/{run}/{game}/{builder}/index.html`
  - Example: `../builds/r1-opus/pong/bench-sonnet/index.html`

In heatmap cells, make the score number itself a link. In tables, add a 🎮 icon link.

For the "Game Difficulty" sections and game name mentions, link to a "best version" — the highest-scoring build for that game.

---

## Visual Design

### Theme
- Background: #0d1117
- Surface/cards: #161b22  
- Border: #30363d
- Text: #e6edf3
- Dim/muted: #8b949e
- Accent/blue: #58a6ff
- Green: #3fb950
- Yellow: #d29922
- Red: #f85149

### Heatmap Cell Colors
Score 0-1: dark red (#3d1010, text #ff7b72)
Score 2-3: red (#3b1818, text #f47067)
Score 4-5: orange-yellow (#332d14, text #d29922)
Score 6-7: yellow-green (#2a3a1e, text #a3be8c)
Score 8-9: green (#1a3f2a, text #56d364)
Score 10: bright green (#1a4a2e, text #3fb950, bold)

### Pull Quotes
Styled boxes with left accent border, larger italic text, designed to be screenshot-able for social media. Use for 3-4 key findings:
1. "The best planner produces the worst results"
2. "Sonnet showed up for every game with no failures" (from V1)
3. "Planning quality ≠ build quality" 
4. "Games that look right in code don't work when played"

### Interactive Elements
- **Tabs** for switching between V1 and V2 views in relevant sections
- **Collapsible sections** (click to expand) for detailed tables / appendices
- **Bar charts** rendered as CSS (div widths, not canvas/SVG)
- **Heatmaps** as HTML tables with colored cells
- All interactivity in vanilla JS (no libraries)

### Responsive
- Max-width: 1000px, centered
- Tables scroll horizontally on mobile
- Font sizes scale appropriately

---

## Key V1 Numbers (embed these)

### V1 GPT-Spec Builder Rankings
| Model | Avg | 
|-------|-----|
| Sonnet | 8.80 |
| GPT-5.4 | 8.59 |
| Opus | 8.61 (excl DNFs) |
| Gemini Flash | 7.99 |
| Gemini Pro | 7.93 |
| GPT-5.4 Mini | 7.93 |
| GPT-5.4 Nano | 7.88 |
| Haiku | 7.24 |
| o3-mini | 5.36 |

### V1 Spec Effect (GPT−Opus delta)
| Model | Delta |
|-------|-------|
| Nano | +0.70 |
| Haiku | +0.29 |
| o3-mini | +0.23 |
| Flash | +0.16 |
| Mini | +0.13 |
| Sonnet | +0.07 |
| Pro | +0.03 |
| GPT-5.4 | −0.06 |

### V1 Cost Table
| Model | $/M in/out | Est/game | Score/$ |
|-------|-----------|----------|---------|
| Gemini Flash | $0.075/$0.30 | ~$0.001 | 7,990 |
| GPT Nano | $0.15/$0.60 | ~$0.002 | 3,940 |
| GPT Mini | $0.40/$1.60 | ~$0.005 | 1,586 |
| Haiku | $0.80/$4 | ~$0.01 | 724 |
| o3-mini | $1.10/$4.40 | ~$0.01 | 536 |
| Gemini Pro | $1.25/$5 | ~$0.015 | 529 |
| Sonnet | $3/$15 | ~$0.05 | 176 |
| GPT-5.4 | $2.50/$15 | ~$0.05 | 172 |
| Opus | $15/$75 | ~$0.25 | 34 |

---

## Key V2 Numbers (embed these)

### V2 Builder Rankings  
| Builder | Avg |
|---------|-----|
| GPT-5.4 | 7.04 |
| Opus | 6.62 |
| Sonnet | 6.42 |
| Gemini Flash | 6.38 |
| GLM-5 | 6.27 |
| Gemini Pro | 6.16 |
| Haiku | 4.88 |
| GPT-5.4 Mini | 2.98 |

### V2 Planner Rankings
| Planner | Avg | Spec Lines |
|---------|-----|------------|
| No Planner | 6.59 | 0 |
| GPT-5.4 | 6.20 | 349 |
| Gemini Pro | 5.91 | 93 |
| GLM-5 | 5.59 | 615 |
| Opus | 4.90 | 503 |

### V2 Game Difficulty
| Game | Avg |
|------|-----|
| Frogger | 8.43 |
| Tetris | 7.51 |
| Galaga | 7.08 |
| Space Invaders | 6.17 |
| Pong | 5.95 |
| Breakout | 5.47 |
| Donkey Kong | 5.21 |
| Asteroids | 4.75 |
| Pac-Man | 4.03 |
| Snake | 3.85 |

### V2 Opus vs No Plan (per game)
| Game | Opus Plan | No Plan | Δ |
|------|-----------|---------|---|
| Donkey Kong | 2.4 | 7.9 | +5.4 |
| Pac-Man | 3.9 | 6.9 | +3.0 |
| Tetris | 5.7 | 8.0 | +2.3 |
| Asteroids | 3.9 | 5.4 | +1.5 |
| Breakout | 4.8 | 6.0 | +1.3 |
| Space Invaders | 5.6 | 6.9 | +1.3 |
| Pong | 3.5 | 4.6 | +1.1 |
| Frogger | 8.8 | 9.9 | +1.1 |
| Galaga | 6.0 | 6.9 | +0.9 |
| Snake | 4.2 | 3.5 | −0.8 |

### V2 Weak vs Strong Builder Amplifier
| Tier | With Opus Plan | No Plan | Δ |
|------|---------------|---------|---|
| Strong (Opus, Sonnet, GPT-5.4) | 5.87 | 6.67 | +0.80 |
| Weak (Haiku, GPT-5.4 Mini, Flash) | 3.37 | 6.47 | +3.10 |

---

## Spec Excerpts to Include

### Opus Donkey Kong (lines 1-10 of spec, showing pixel precision):
```
# Game Spec: Donkey Kong
## 1. Overview
Donkey Kong (Nintendo, 1981)...
## 2. Canvas & Layout
- Canvas: 672×768px
## 3. Level Layout — The Girder Map
### Girder Definitions
Girder 1 (bottom): (40, 620) → (632, 592) slope: rises left-to-right
Platform 6 (top): Girder: (200, 100) → (472, 100) [flat, short]
Platform 5 (DK's): Girder: (56, 172) → (512, 186) [slight downward slope to right]
```

### Gemini Pro Donkey Kong (conceptual, 93 lines total):
```
# Game Specification: Donkey Kong
## 1. Core Concept
Donkey Kong is a classic single-screen platform arcade game. The player 
controls a small carpenter ("Mario") starting at the bottom of the screen.
## 3. Visual Layout
- Canvas Size: ~600px width by ~750px height
- Level 6 (Top): Only spans the middle third of the screen
- Levels 1 to 5 (Girders): Five long horizontal beams. They are sloped.
  - L1 (bottom) slopes slightly upward to the right
  - L2 slopes upward to the left (etc.)
```

---

## Final Checklist
- [ ] Python builder script written to `games-v2/scripts/build_paper.py`
- [ ] Script loads V1 data from `reports/v1-data.json`
- [ ] Script loads V2 data from `qa/playtest/report-data.json`
- [ ] Script computes all aggregations (builder avgs, game avgs, planner avgs, heatmaps, cross-round)
- [ ] HTML has all 6 parts per structure above
- [ ] All games are clickable (V1: ../../games/..., V2: ../builds/...)
- [ ] Dark theme, responsive, interactive
- [ ] Pull quotes styled and present
- [ ] Heatmaps with color-coded cells
- [ ] Tabs and collapsible sections work
- [ ] File written to `games-v2/reports/research-paper.html`
- [ ] File size reported on completion
