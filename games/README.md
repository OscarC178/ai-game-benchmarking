# Vintage Games Benchmark

Two-run overnight benchmark pitting 5 AI models against each other building 10 vintage HTML5/JS games.

**Status:** ✅ Complete  
**Report:** [benchmark-report.md](./benchmark-report.md)

## Runs
- **Run 1:** Specs by `anthropic/claude-opus-4.6` → builds in `run1-opus-plan/`
- **Run 2:** Specs by `openai/gpt-5.4` → builds in `run2-gpt-plan/`

## Final Scores — Run 1 (Opus-Planned Specs)

| Game | Sonnet | Opus | Haiku | GPT-5.4 | o3-mini |
|------|--------|------|-------|---------|---------|
| Pong ⭐ | 9.03 | 9.07 | 7.90 | 8.80 | 5.20 |
| Snake ⭐ | 9.27 | 9.00 | 8.60 | 9.13 | 7.00 |
| Breakout ⭐⭐ | 8.73 | 8.60 | 8.17 | 8.87 | 6.87 |
| Space Invaders ⭐⭐ | 8.33 | 8.70 | 7.47 | 8.67 | 5.07 |
| Tetris ⭐⭐ | 9.03 | 8.63 | 6.73 | 8.97 | 6.57 |
| Asteroids ⭐⭐⭐ | 8.83 | 8.80 | 7.50 | 9.07 | 4.93 |
| Galaga ⭐⭐⭐ | 8.20 | 8.23 | 6.83 | 7.70 | 4.00 |
| Frogger ⭐⭐⭐ | 8.30 | 8.47 | 6.00 | 8.37 | 3.77 |
| Pac-Man ⭐⭐⭐⭐ | 7.33 | DNF | 4.93 | 8.17 | 3.90 |
| Donkey Kong ⭐⭐⭐⭐ | 7.67 | DNF | 5.33 | 8.00 | 3.97 |
| **Average** | **8.47** | **8.56*** | **6.95** | **8.57 🏆** | **5.13** |

## Final Scores — Run 2 (GPT-5.4-Planned Specs)

| Game | Sonnet | Opus | Haiku | GPT-5.4 | o3-mini |
|------|--------|------|-------|---------|---------|
| Pong ⭐ | 9.03 | 8.97 | 8.23 | 9.20 | 5.77 |
| Snake ⭐ | 9.10 | 8.97 | 8.23 | 9.20 | 6.67 |
| Breakout ⭐⭐ | 8.97 | 8.90 | 8.27 | 9.03 | 6.87 |
| Space Invaders ⭐⭐ | 8.70 | 8.53 | 7.53 | 8.93 | 6.20 |
| Tetris ⭐⭐ | 9.03 | 8.30 | 7.83 | 8.60 | 6.53 |
| Asteroids ⭐⭐⭐ | 8.93 | 9.07 | 8.17 | 9.07 | 4.73 |
| Galaga ⭐⭐⭐ | 8.17 | 8.50 | 6.13 | 7.53 | 4.20 |
| Frogger ⭐⭐⭐ | 8.50 | 8.80 | 7.10 | 8.37 | 4.17 |
| Pac-Man ⭐⭐⭐⭐ | 8.20 | 7.53 | 5.07 | 8.23 | 4.43 |
| Donkey Kong ⭐⭐⭐⭐ | 7.90 | 7.20 | 5.87 | 7.70 | 3.73 |
| **Average** | **8.65 🏆** | **8.48** | **7.24** | **8.59** | **5.33** |

## Overall Winner (Both Runs Combined)

| Model | Run 1 | Run 2 | Combined |
|-------|-------|-------|---------|
| GPT-5.4 | **8.57** | 8.59 | **8.58** |
| Sonnet | 8.47 | **8.65** | 8.56 |
| Opus | 8.56* | 8.48 | 8.52* |
| Haiku | 6.95 | 7.24 | 7.10 |
| o3-mini | 5.13 | 5.33 | 5.23 |

*Opus excludes 2 DNFs from run1 average

**Overall winner: GPT-5.4** (8.58 combined, no DNFs, most consistent)

## Models

| Slug | Model | Notes |
|------|-------|-------|
| sonnet | anthropic/claude-sonnet-4-6 | Best on complex games Run 2 |
| opus | anthropic/claude-opus-4-6 | 2 DNFs (context limit) in Run 1 |
| haiku | anthropic/claude-haiku-4-5 | Fast/cheap, cliff at complexity |
| gpt-5-4 | openai/gpt-5.4 | Overall winner, also wrote Run 2 specs |
| o3-mini | openai/o3-mini | Consistent minimal implementations |

## Human Scoring

Human scores are in `results.json` under `human_scores` — currently all null. Oscar to fill in after playing each game.

Best to start with: `run1-opus-plan/pong/gpt-5-4/index.html` (highest QA score = best first impression)
