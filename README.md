# Can AI Build a Game? — 580 Builds, 9 Models, Zero Intervention

A benchmark of AI code generation using retro arcade games as the evidence. 580+ one-shot builds across 9 models, scored by 3 AI judges and partially by human playtesting.

## What's here

| Path | What |
|---|---|
| `paper/index.html` | Full research paper — methodology, findings, limitations, live exhibits |
| `guide/index.html` | Interactive dashboard — 5 tabs: Lessons, Library, Plans & Prompts, QA Data, Paper |
| `guide/beginners-guide.html` | Prose field manual — "AI Coding Without the Waste" |
| `guide/server.py` | Local HTTP server that serves all three pages + games + specs + data |
| `guide/aggregate.py` | Aggregator — reads `verified-data.json` + `review/ratings.json` → writes `guide/data.json` |
| `review/` | Human-rating tool + Oscar's 104 in-progress ratings (`ratings.json`) |
| `verified-data.json` | Full benchmark dataset — 690 scored builds, per-judge, per-dimension |
| `audit-report.md` | Methodology audit (DNFs, Flash judge inflation, token data gaps) |
| `games/` | V1 builds — 8 runs × up to 9 builders × 10 games, plus orchestration scripts |
| `games-v2/` | V2 builds, planner specs, and orchestration scripts |
| `scripts/qa_multijudge.py` | Judge prompt + rubric (source of truth for V1 QA) |

## Run it locally

```bash
python3 guide/server.py
```

Then open:
- `http://localhost:5858/` — interactive dashboard
- `http://localhost:5858/paper` — research paper
- `http://localhost:5858/beginners-guide` — field manual
- `http://localhost:5858/game/v2/r1-opus/pong/bench-sonnet/` — any individual game build

No dependencies. Python 3 standard library only. External assets (Chart.js, marked.js, Google Fonts) load from CDN.

## Regenerating `guide/data.json`

If you add new ratings via the review tool or edit `verified-data.json`:

```bash
python3 guide/aggregate.py
```

This re-reads the sources and re-emits `guide/data.json`, which the dashboard consumes.

## Environment variables (optional)

The orchestration scripts in `games/scripts/` and `games-v2/scripts/` support Telegram notifications for long-running builds. They're no-ops if the env vars aren't set:

```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
```

The QA script (`scripts/qa_multijudge.py`) expects an API key for PaleBlueDot:

```bash
export PALEBLUEDOT_API_KEY="..."
```

None of these are required to view the paper, dashboard, or games — only to regenerate builds and QA from source.

## Structure

```
ai-game-benchmarking/
├── paper/            # Research paper (white background, editorial)
├── guide/            # Dashboard + beginners guide (warm cream)
├── review/           # Human-rating tool + ratings.json
├── games/            # V1 builds + orchestration
├── games-v2/         # V2 builds, specs, orchestration
├── scripts/          # Judge rubric/prompt
├── verified-data.json  # Full scored dataset
└── audit-report.md   # Methodology audit
```

All three HTML pages share a design language — Fraunces display serif, IBM Plex Sans body, JetBrains Mono numerics. The paper uses a near-white background (research-paper feel); the dashboard and beginners guide use a warm cream palette.

## Status

The paper and guides are feature-complete. The review tool has 104 ratings captured so far out of a planned full 580-build human audit. The `audit-report.md` documents the known data gaps (missing token data for runs 1–6, V1 Flash-judge inflation, etc.).
