# Benchmark Data Audit Report

**Generated:** 2026-04-12

## Summary

| Dataset | Total | Complete | DNF | Pending/Missing | Issues |
|---------|-------|----------|-----|-----------------|--------|
| V1 | 290 | 182 | 8 | 100 | 7 |
| V2 | 400 | 397 | 2 | 1 | 1 |
| **Total** | **690** | **579** | **10** | — | **8** |

## V1 Data Quality

- **Zero token data:** 117 of 182 complete builds report 0 tokens
- **Zero cost data:** 158 of 182 complete builds report $0.00
- Token data source: runs 1-6 mostly missing, runs 7-8 available via `runs_7_8_build_results.json`
- Schema inconsistency: early runs use `spec_generator`, later runs use `planner`
- Gemini Flash judge inflation: avg gap of ~1.8 points above GPT-5.4/Opus consensus

### Leaderboard Verification

| Model | Reported Avg | Computed Avg | Delta | Reported n | Found n | Status |
|-------|-------------|-------------|-------|-----------|---------|--------|
| sonnet | 8.62 | 8.62 | +0.00 | 18 | 18 | OK |
| gpt-5-4 | 8.58 | 8.58 | +0.00 | 20 | 20 | OK |
| opus | 8.22 | 8.22 | +0.00 | 26 | 26 | OK |
| gpt-5.4-mini | 7.86 | 7.86 | +0.00 | 20 | 20 | OK |
| gemini-flash | 7.74 | 7.91 | +0.17 | 20 | 20 | ISSUE |
| gpt-5.4-nano | 7.53 | 7.53 | +0.00 | 20 | 20 | OK |
| haiku | 7.09 | 7.09 | +0.00 | 20 | 20 | OK |
| gemini-pro | 6.78 | 7.91 | +1.13 | 20 | 20 | ISSUE |
| o3-mini | 5.23 | 5.23 | +0.00 | 18 | 18 | OK |

## V2 Data Quality

- **Browser-bug scoring:** 351 of 397 complete builds score 10.0 (nearly useless for discrimination)
- **Static QA:** NOT YET RUN — placeholder nulls in verified-data.json
- **DNFs:** 2 (r1-opus/galaga/bench-opus, r1-opus/donkey-kong/bench-glm5)
- **Missing:** 1 (r1-opus/tetris/bench-gemini-pro)

### Planner Comparison (browser-bug scores only)

| Planner | Avg Score | n | Perfect 10s | Non-10s | Avg Bugs |
|---------|-----------|---|-------------|---------|----------|
| r1-opus | 9.56 | 77 | 64 | 13 | 3.88 |
| r2-gpt54 | 9.82 | 80 | 66 | 14 | 0.17 |
| r3-gemini-pro | 9.93 | 80 | 74 | 6 | 0.07 |
| r4-glm5 | 9.89 | 80 | 72 | 8 | 0.11 |
| r5-control | 9.82 | 80 | 75 | 5 | 2.00 |

### Spec Lengths by Planner

| Planner | Avg Bytes | Total Bytes | Specs |
|---------|-----------|-------------|-------|
| r1-opus | 29,551 | 295,518 | 10 |
| r2-gpt54 | 13,384 | 133,849 | 10 |
| r3-gemini-pro | 6,696 | 66,964 | 10 |
| r4-glm5 | 16,205 | 162,059 | 10 |
| r5-control | 90 | 907 | 10 |

## Issues

- V1 leaderboard mismatch: gemini-flash — reported 7.74, computed 7.91
- V1 leaderboard mismatch: gemini-pro — reported 6.78, computed 7.91
- V1 judge avg mismatch: gemini-flash/gpt54 — reported 6.92, computed 7.23
- V1 judge avg mismatch: gemini-flash/opus — reported 6.89, computed 7.07
- V1 judge avg mismatch: gemini-pro/gpt54 — reported 5.87, computed 6.88
- V1 judge avg mismatch: gemini-pro/opus — reported 6.18, computed 7.43
- V1 judge avg mismatch: gemini-pro/gemini — reported 8.3, computed 9.44
- V2: r1-opus/galaga/bench-opus marked dnf but HTML exists on disk

## Key Finding: Leaderboard Stale for gemini-flash and gemini-pro

The `benchmark-dataset.json` leaderboard reports:
- gemini-flash: 7.74 avg (actual from per-build results: **7.91**, delta +0.17)
- gemini-pro: 6.78 avg (actual from per-build results: **7.91**, delta +1.13)

Both models have n=20 in both the leaderboard and per-build data, so this isn't a count issue. The leaderboard was likely computed from an earlier QA pass before rescoring. **The per-build results.json files are the source of truth** — `verified-data.json` uses the per-build data.

All other 7 models match within rounding tolerance (±0.00).

## Data Files

- **Canonical dataset:** `verified-data.json` (this audit's output)
- **V1 source of truth:** `games/benchmark-dataset.json`
- **V1 per-build:** `games/run{1-8}/*/results.json`
- **V1 token data:** `games/runs_7_8_build_results.json`
- **V2 results:** `games-v2/reports/results.json`
- **V2 builds:** `games-v2/builds/r{1-5}/*/bench-*/index.html`
- **V2 specs:** `games-v2/specs/r{1-5}/*/spec.md`
