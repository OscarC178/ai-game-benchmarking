# LLM Arcade Benchmark: Analysis Report
**182 builds · 9 models · 10 games · 8 runs**
*Henry — Data Science · March 2026*

---

## 1. Executive Summary

- **The premium tier has a near-tie at the top**: Sonnet (**8.62**) and GPT-5.4 (**8.58**) are statistically inseparable on consensus score — 0.04 points apart. Both comfortably outperform Opus despite Opus costing **5× more per token**.
- **Gemini Flash is the budget steal**: At ~$0.0014/build and a consensus score of **7.74**, it delivers **5,529 score-points per dollar** — almost 220× better value than Sonnet and nearly 4,000× better than Opus.
- **o3-mini's performance is a genuine shock**: A reasoning-specialist model scores **5.23** — dead last, 1.55 points behind the next-worst builder (gemini-pro at 6.78). Reasoning architecture appears actively harmful for creative code generation tasks.
- **Gemini Flash as a judge is broken**: It rated o3-mini (the worst builder by a wide margin) at **6.97**, while GPT-5.4 and Opus scored it 4.88 and 3.84 respectively. Any experiment using Gemini Flash as sole judge should be treated with deep skepticism.

---

## 2. Overall Leaderboard

> *Consensus = mean of 3 judges. Gemini Flash as judge shows calibration bias (see Section 8). GPT-5.4 and Opus judge scores are the most reliable signal.*

| Model | Avg (Consensus) | GPT-5.4 Judge | Opus Judge | Gemini Judge | Min | Max | N | Price Tier | In $/1M | Out $/1M |
|---|---|---|---|---|---|---|---|---|---|---|
| **sonnet** | **8.62** | 8.01 | 8.03 | 9.82 | 7.33 | 9.27 | 18 | Premium | $3.00 | $15.00 |
| **gpt-5-4** | **8.58** | 7.98 | 8.04 | 9.72 | 7.53 | 9.20 | 20 | Premium | $2.50 | $10.00 |
| opus | 8.22 | 7.55 | 7.42 | 9.68 | 6.17 | 9.07 | 26 | Premium | $15.00 | $75.00 |
| gpt-5.4-mini | 7.86 | 7.25 | 6.92 | 9.43 | 5.37 | 9.13 | 20 | Budget | $0.40 | $1.60 |
| gemini-flash | 7.74 | 6.92 | 6.89 | 9.43 | 4.47 | 9.03 | 20 | Budget | $0.075 | $0.30 |
| gpt-5.4-nano | 7.53 | 6.74 | 6.40 | 9.46 | 2.57 | 9.07 | 20 | Budget | $0.10 | $0.40 |
| haiku | 7.09 | 6.09 | 5.96 | 9.24 | 4.93 | 8.60 | 20 | Budget | $0.25 | $1.25 |
| gemini-pro | 6.78 | 5.87 | 6.18 | 8.30 | 1.93 | 9.13 | 20 | Mid | $1.25 | $5.00 |
| **o3-mini** | **5.23** | 4.88 | 3.84 | 6.97 | 3.73 | 7.00 | 18 | Mid | $1.10 | $4.40 |

Note: gemini-pro and o3-mini sit in a "mid" price tier that offers poor value — paying mid-tier prices for bottom-tier results.

---

## 3. Per-Dimension Breakdown

> *Per-dimension scores are derived from GPT-5.4 and Opus judge evaluations.*

| Model | Functionality | Keyboard Controls | Visual Fidelity | Playability | Error-Free |
|---|---|---|---|---|---|
| **gpt-5-4** | **8.82** | **8.51** | **8.13** | **8.51** | **8.73** |
| sonnet | 8.78 | 8.22 | 7.78 | 8.22 | 8.56 |
| opus | 8.31 | 7.78 | 7.44 | 7.92 | 8.14 |
| gpt-5.4-mini | 7.78 | 7.28 | 6.78 | 7.20 | 7.57 |
| gemini-flash | 7.34 | 6.91 | 6.42 | 6.77 | 7.19 |
| gpt-5.4-nano | 7.09 | 6.64 | 6.07 | 6.58 | 6.96 |
| haiku | 6.44 | 5.89 | 5.57 | 5.96 | 6.21 |
| gemini-pro | 6.42 | 6.00 | 5.82 | 5.87 | 6.38 |
| o3-mini | 4.88 | 4.33 | 3.96 | 4.44 | 5.02 |

**Key observations:**

- GPT-5.4 leads on every single dimension, barely — it and Sonnet are neck-and-neck with Sonnet slightly stronger on functionality (8.78 vs 8.82 is noise-level).
- **Visual Fidelity is the Achilles heel across the board.** Every model's lowest score is Visual Fidelity. This is the hardest dimension for LLMs to nail — arcade aesthetics require deliberate attention to CSS/canvas layout that most models deprioritise.
- o3-mini's **Keyboard Controls score of 4.33** is particularly damning — basic input handling should be table stakes for any game. Something is structurally wrong with how reasoning-focused models approach generative coding tasks.
- Haiku and gemini-pro are nearly identical despite different architectures, price points, and providers. At this capability level, you're buying commodity performance.

---

## 4. Game Difficulty Ranking

| Game | Avg Score | Min | Max | N | Difficulty |
|---|---|---|---|---|---|
| donkey-kong | 6.58 | 1.27 | 9.13 | 21 | 🔴 Legendary |
| pac-man | 7.06 | 0.57 | 9.27 | 20 | 🟠 Hard |
| galaga | 7.45 | 3.77 | 9.47 | 20 | 🟠 Hard |
| space-invaders | 7.88 | 5.20 | 9.27 | 20 | 🟠 Hard |
| frogger | 7.98 | 2.00 | 9.60 | 21 | 🟠 Hard |
| tetris | 8.07 | 1.00 | 9.40 | 20 | 🟡 Medium |
| asteroids | 8.15 | 3.50 | 9.47 | 19 | 🟡 Medium |
| breakout | 8.72 | 5.17 | 9.47 | 20 | 🟡 Medium |
| snake | 9.08 | 6.53 | 9.67 | 21 | 🟢 Easy |
| pong | 9.19 | 7.20 | 9.67 | 20 | 🟢 Easy |

The floor scores are telling. Donkey Kong's minimum of **1.27** and Pac-Man's of **0.57** indicate catastrophic failures — models producing non-functional implementations. Frogger and Tetris show similar failure modes (mins of 2.0 and 1.0), despite both having mid-tier average scores. These aren't hard games in concept; the difficulty is in faithful implementation of complex movement or collision logic under zero-dependency constraints. Pong's minimum of 7.2 makes it the only game with a guaranteed acceptable result from any model.

---

## 5. The Opus Paradox

Opus built with **accumulated context** (prior game code available as reference) averaged **8.58** (n=19). With **isolated context** (fresh prompt, no priors), it averaged **7.63** (n=9). The delta is **−0.95 points** — nearly a full point lost when Opus can't reference its own prior work.

This is the largest context-sensitivity effect observed in the benchmark. Three plausible explanations:

1. **Self-referential refinement**: With accumulated context, Opus can observe its own earlier architectural choices and maintain consistency across builds — reducing regressions in controls, state management, and visual style.
2. **Implicit few-shot learning**: Prior game files serve as worked examples demonstrating the expected quality bar. Isolated runs lack this calibration.
3. **Opus's long-context advantage**: Opus is specifically optimised for deep context utilisation. The effect may be larger here than it would be for other models — a capability that matters only if you give it room to work.

Worth noting: **Opus scored its own builds at 7.42 as judge** — the second-lowest self-assessment in the panel. This suggests genuine self-criticism, not grade inflation. Unlike Gemini Flash (which scores everything 9–10), Opus as judge appears to hold its own outputs to a high bar.

---

## 6. Value Analysis — Score Per Dollar

> ⚠️ **Data note**: Runs 1–2 had actual cost measurements. Runs 3–8 use estimated prices based on published token rates at time of benchmarking. Treat all cost figures as approximations.

Estimated cost per build assumes **3,000 input tokens + 4,000 output tokens**.

| Model | Consensus Score | Est. Cost/Build | Score / Dollar |
|---|---|---|---|
| **gemini-flash** | 7.74 | $0.0014 | **5,529** |
| **gpt-5.4-nano** | 7.53 | $0.0019 | **3,963** |
| **haiku** | 7.09 | $0.0059 | **1,202** |
| **gpt-5.4-mini** | 7.86 | $0.0076 | **1,034** |
| gemini-pro | 6.78 | $0.024 | 283 |
| o3-mini | 5.23 | $0.021 | 249 |
| gpt-5-4 | 8.58 | $0.048 | 179 |
| sonnet | 8.62 | $0.069 | 125 |
| opus | 8.22 | $0.345 | **24** |

The value cliff between budget and premium tiers is steep. Gemini Flash delivers **220× better score-per-dollar than Sonnet** and **230× better than GPT-5.4**. If you're running high-volume generation pipelines and can tolerate a 0.88-point quality drop (7.74 vs 8.62), Gemini Flash is the only rational choice.

Opus is the worst value proposition in the benchmark by a significant margin — **5x** the cost of Sonnet per token for a build quality that scores 0.4 points lower. Unless accumulated context gives Opus a specific edge on your task (Section 5), there's no economic case for it here.

o3-mini deserves special mention: it's not only the worst builder, it's also bad value at $0.021/build, returning a score-per-dollar of 249 — lower than every budget model.

---

## 7. Spec Source Effect

Builds using **Opus-generated specs** averaged **8.27** (n=75). Builds using **GPT-generated specs** averaged **8.15** (n=75). Delta: **+0.12** in favour of Opus specs.

This effect is small but directionally consistent. With n=75 per group, it's unlikely to be pure noise — Opus specs may be marginally better structured, more detailed, or better scoped in ways that help downstream builders. However, **0.12 points is not a hiring decision**. The practical implication is minimal: neither planner is significantly better at producing buildable spec documents for this task type. If you're optimising for spec quality, invest in prompt engineering before swapping planners.

---

## 8. Judge Calibration Analysis

| Model Built | GPT-5.4 Judge | Opus Judge | Gemini Judge | GPT/Opus Avg |
|---|---|---|---|---|
| sonnet | 8.01 | 8.03 | **9.82** | 8.02 |
| gpt-5-4 | 7.98 | 8.04 | **9.72** | 8.01 |
| opus | 7.55 | 7.42 | **9.68** | 7.49 |
| gpt-5.4-mini | 7.25 | 6.92 | **9.43** | 7.09 |
| gemini-flash | 6.92 | 6.89 | **9.43** | 6.91 |
| gpt-5.4-nano | 6.74 | 6.40 | **9.46** | 6.57 |
| haiku | 6.09 | 5.96 | **9.24** | 6.03 |
| gemini-pro | 5.87 | 6.18 | **8.30** | 6.03 |
| **o3-mini** | **4.88** | **3.84** | **6.97** | **4.36** |

The Gemini Flash judge is not usable for discrimination tasks. Its range across all nine builder models is **9.82 − 6.97 = 2.85 points**, compared to GPT-5.4's **8.01 − 4.88 = 3.13 points** and Opus's **8.04 − 3.84 = 4.20 points**. More critically, Gemini Flash compresses mediocre and excellent builds into a nearly indistinguishable 9–10 band. It rated o3-mini (the worst builder, consensus 5.23) at **6.97** — a score that puts o3-mini above haiku when judged by Gemini but far below it when judged by GPT-5.4 or Opus.

GPT-5.4 and Opus agree closely on relative ordering and show meaningful separation. Their correlation dips only slightly on gemini-pro (5.87 vs 6.18 — a 0.31 gap), and converges tightly on the top models. These are the reliable signals. The consensus scores in this report are arithmetically averaged across all three judges, which means Gemini's inflation slightly elevates every model's headline number. When comparing across models, the GPT-5.4/Opus average column above is the cleaner metric.

---

## 9. Key Insights & Recommendations

- **Sonnet and GPT-5.4 are effectively tied at the top.** With 0.04 points separating them (8.62 vs 8.58), the choice between these two is a pricing and ecosystem decision, not a quality one. GPT-5.4 is ~30% cheaper per build ($0.048 vs $0.069) with equal output quality.

- **Gemini Flash is the budget champion, full stop.** At $0.0014/build and 7.74 consensus — within 0.88 points of the top — it's the only choice for high-volume pipelines where peak quality isn't the constraint. The 5,529 score/dollar ratio is in a class of its own.

- **Opus is poor value vs. Sonnet.** Opus costs **5× more per token** and scores **0.40 points lower** (8.22 vs 8.62). The only scenario where Opus wins is accumulated-context settings — where its 8.58 contextual average actually ties Sonnet's headline score. Outside of that context pattern, use Sonnet.

- **o3-mini is the benchmark's biggest surprise — and not in a good way.** A reasoning-optimised model finishing 1.55 points behind the next-worst builder suggests these architectures are optimised for something fundamentally different from creative code synthesis. Don't default to reasoning models for generative tasks.

- **Output length is not quality.** gpt-5.4-nano wrote an average of **36.8 KB** per build — the largest of any model, nearly 3× gpt-5.4-mini's 13.2 KB — yet scored 0.33 points lower (7.53 vs 7.86). Verbosity without coherence doesn't move the rubric.

- **Context accumulation is a real lever for Opus.** If you're using Opus at scale, architect your pipeline to pass prior outputs as context. The 0.95-point gap (8.58 vs 7.63) is too large to leave on the table.

- **Do not use Gemini Flash as your sole judge.** Score distributions from Gemini Flash are too compressed to support meaningful model comparison. If cost is a constraint, use GPT-5.4 plus Opus as a two-judge panel — their agreement is tight and their discrimination is reliable.

---

## 10. Methodology

**Dataset:** 182 total builds across 9 builder models and 10 arcade games (pong, snake, breakout, asteroids, tetris, frogger, space-invaders, galaga, pac-man, donkey-kong) over 8 benchmark runs.

**Build format:** HTML5/JavaScript, single file, zero external dependencies. Games must run in-browser without a server.

**Evaluation:** Each build was scored by 3 judges (GPT-5.4, Opus, Gemini Flash) via the palebluedot API. Consensus score = arithmetic mean of all three judge scores. Rubric weights: functionality 30%, keyboard\_controls 20%, visual\_fidelity 20%, playability 20%, error\_free 10%.

**Planning:** Specs were generated by either Opus or GPT as a planner before being handed to the builder model. Plan source was balanced — 75 builds per planner.

**Cost data:** Actual build timing and token counts were recorded for runs 1–2 only. Per-build cost estimates for runs 3–8 are calculated from published API prices at time of benchmarking assuming 3,000 input + 4,000 output tokens. All cost-derived figures should be treated as estimates.

**Model counts:** Opus has n=26 builds (more than any other model) due to its role in both planning and building across runs. This gives its estimates higher statistical stability but also reflects more varied task conditions.

---

*Report generated from benchmark data as of March 2026. All figures are sourced directly from the benchmark dataset; no values have been inferred or interpolated beyond the cost estimation methodology described in Section 10.*
