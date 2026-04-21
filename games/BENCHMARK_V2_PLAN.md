# Benchmark V2 — Full Rebuild Plan

**Status:** Planning  
**Reason for rebuild:** Fundamental methodology flaw in V1 — spec structure was templated by the orchestrating agent, invalidating the planner comparison.  
**V1 cost:** ~$400 wasted on flawed design.

---

## What Went Wrong in V1

### The Core Flaw
The orchestrating agent (me) generated all spec prompts using the same 12-section template:
- Section 1: Overview
- Section 2: Canvas & Rendering
- Section 3: Game Objects
- Section 4: Controls
- Section 5: Game Rules & Logic
- Section 6: Collision Detection
- Section 7: Scoring
- Section 8: UI Elements
- Section 9: Audio
- Section 10: Implementation Notes
- Section 11: Acceptance Criteria
- Section 12: Build Task Checklist (T01–T14)

Both Opus and GPT-5.4 were handed this template and asked to fill it in. **Neither model was free to design the spec.** The result: both specs are structurally identical because I imposed the structure. The "planner comparison" measured nothing meaningful about planning quality — it measured how two models fill in the same form.

### Why This Invalidates the Planner Finding
The report claimed GPT-5.4 specs were inferior to Opus specs. That may be true, but the evidence is contaminated:
- We can't know what GPT-5.4 would have produced without the template
- We can't know if Opus would have chosen the same structure unprompted
- The "spec effect" on smaller builder models (Haiku scoring better on GPT specs) may be an artefact of GPT-5.4's template-filling style, not its planning ability

### Additional V1 Flaws Found
1. **Boilerplate task injection:** T01–T04 in GPT specs were generic filler. T09–T13/T14 were verbatim copy-pasted across all 10 games — including T11 "lives/health indicator" for games with no lives system (Pong, Tetris, Snake, etc.)
2. **Static QA misses runtime bugs:** The 3-judge QA panel gave 7–9/10 Playability scores to games that had movement-freezing bugs. Human play and browser agent both caught what static review missed.
3. **o3-mini confabulates:** Reports tasks complete without building. Inflates "iterations complete" metrics. Any benchmark including o3-mini needs a completion verification step.
4. **Opus DNFs = context length, not capability:** When given isolated context per game (Runs 3/4), Opus scored 9.41 avg. The DNFs in Runs 1/2 were context accumulation across all 10 games in one session.
5. **Gemini Flash > Gemini Pro:** Flash is cheaper, faster, and scores higher. Pro has catastrophic outliers. This finding IS valid — both used the same (template) specs and the same QA.
6. **Builder results are valid:** Even though the planner comparison is broken, builder model scores are real — each model independently wrote code from the same spec. File sizes and diffs confirm independent generation.

---

## What V1 Got Right (Keep These)

- **10-game progression** (Pong → Donkey Kong): good difficulty ramp, canonical arcade titles
- **Single-file HTML5 constraint:** creates a clear, measurable output
- **Task-by-task build order:** forced models to build incrementally — good discipline signal
- **Sonnet as QA judge:** consistent, cheap, reliable enough for first pass
- **Browser agent QA:** Playwright-based gameplay testing is genuinely better than static review — keep and expand
- **Isolated context per build:** learned from Opus DNFs — every builder should get a clean session
- **Results JSON schema:** solid, reusable
- **Launcher HTML:** good presentation layer, reusable with new data

---

## V2 Design

### The Central Question
**Can a model plan AND build? Does planning quality affect build quality when the planner is unconstrained?**

This is answerable if we fix the methodology.

### Planner Design — No Template
Give planners a single brief per game. No section headings. No task checklist format. No imposed structure. Just:

```
You are designing a spec for a developer who will build [GAME NAME] as a single self-contained HTML5 Canvas file.

The developer is competent but has no prior knowledge of this game. Your spec should give them everything they need to build a complete, playable version.

Write the spec however you think is best. No format is imposed.
```

Then feed that spec verbatim to the builder. The builder gets what the planner produced — nothing more, nothing less.

### Planner Models (V2)
- **Claude Opus 4.6** 
- **GPT-5.4.** 
- **Gemini 3.1 Pro** 
- **No planner (raw game name only):** control condition — builder gets just the game name and build rules. No spec. Tests whether specs add value at all.

### Builder Models (V2)
Keep the ones with valid V1 findings:
- Claude Opus 4.6
- Claude Sonnet 4.6 (top performer, reliable baseline)
- Claude Haiku 4.5 (small model, most sensitive to spec quality)
- Gemini 3.1 Pro
- Gemini Flash (slots between Haiku and Sonnet — interesting)
- GPT-4o Mini (replace Nano/Mini from V1 — cleaner OpenRouter billing)
- GPT-5.4 Full
- GPT 5.4 Mini


### Games (V2)
Same 10. The progression is good and the games are canonical.

### Run Structure (V2)
| Run | Planner | Builders |
|-----|---------|---------|
| R1 | Sonnet (free-form) | Sonnet, Haiku, Flash, GPT-4o Mini |
| R2 | GPT-4o (free-form) | Sonnet, Haiku, Flash, GPT-4o Mini |
| R3 | Gemini 3.1 Pro (free-form) | Sonnet, Haiku, Flash, GPT-4o Mini |
| R4 | No planner (control) | Sonnet, Haiku, Flash, GPT-4o Mini |

4 runs × 10 games × 4 builders = **160 builds**

### QA (V2)
Two-stage:
1. **Static QA** (Sonnet judge, Gemini Pro 3.1 judge, GPT 5.4 judge, same 5 dimensions) 
2. **Browser agent QA** (Playwright, keyboard inputs, state bridge) — for every build, not just Pac-Man/DK

The browser agent catches what static misses. Make it mandatory, not optional.

---

## Implementation Checklist (V2)

### Before Writing Any Code
- [ ] Agree on planner prompt (no template, just brief)
- [ ] Agree on 4 planner models
- [ ] Agree on 4 builder models
- [ ] Agree on QA pipeline (static + browser mandatory)
- [ ] Confirm budget envelope

### Spec Generation
- [ ] Write planner prompt (game brief only, no structure)
- [ ] Run planners: 3 models × 10 games = 30 specs
- [ ] **Human review all 30 specs before any builds run** — catch structural failures early, not after $400 in builds
- [ ] Store specs in `games-v2/run{N}-{planner}/` structure

### Build Orchestration
- [ ] Isolated context per builder (lesson from Opus DNFs)
- [ ] Verify file exists before marking complete (lesson from o3-mini)
- [ ] No JSON_RESULT self-reporting — verify by file presence + basic HTML parse
- [ ] Parallel builds per game (keep, it works)
- [ ] Hard timeout: 15 min per build

### QA
- [ ] Static QA: same 5-dimension rubric (comparability with V1)
- [ ] Browser QA: run on every build, not just spot checks
- [ ] window.__qa state bridge: patch generically, not per-game
- [ ] Screenshot on freeze/error for evidence

### Reporting
- [ ] Reuse launcher.html structure
- [ ] Add "planner vs no-planner" delta as primary finding
- [ ] Show raw planner spec alongside build for every entry
- [ ] Browser QA results as a column, not a footnote

---

## Key Lessons — Don't Repeat These

1. **Never template the thing you're testing.** If you're testing planning, let the planner plan.
2. **Human review specs before building.** 30 specs take 30 minutes to read. 160 builds at $400 take one embarrassing session to waste.
3. **Static QA is not playability testing.** Browser agent is mandatory.
4. **o3-mini self-reports completion.** Verify by artefact, not by model output.
5. **Isolated context per build.** Never accumulate games in one session.


---

*Last updated: 2026-04-01*
*V1 cost: ~$400*
*V2 target: ~$353 with better methodology*
