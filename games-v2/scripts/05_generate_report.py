#!/usr/bin/env python3
"""
05_generate_report.py — Compile all QA results into benchmark-report.md and launcher.html

Usage: python3 05_generate_report.py
Output: games-v2/reports/benchmark-report.md
        games-v2/reports/launcher.html
"""
import os
import json
import glob
from pathlib import Path
from datetime import datetime

V2_DIR = Path(__file__).parent.parent
BUILDS_DIR = V2_DIR / "builds"
STATIC_QA_DIR = V2_DIR / "qa" / "static"
BROWSER_QA_DIR = V2_DIR / "qa" / "browser"
SPECS_DIR = V2_DIR / "specs"
REPORTS_DIR = V2_DIR / "reports"

REPORTS_DIR.mkdir(exist_ok=True)

RUNS = ["r1-opus", "r2-gpt54", "r3-gemini-pro", "r4-glm5", "r5-control"]
GAMES = ["pong", "snake", "breakout", "space-invaders", "tetris", "asteroids", "galaga", "frogger", "pac-man", "donkey-kong"]
BUILDERS = ["bench-opus", "bench-sonnet", "bench-haiku", "bench-gpt54", "bench-gpt54mini", "bench-gemini-pro", "bench-gemini-flash", "bench-glm5"]

PLANNER_LABELS = {
    "r1-opus": "Opus 4.6",
    "r2-gpt54": "GPT-5.4",
    "r3-gemini-pro": "Gemini 3.1 Pro",
    "r4-glm5": "GLM-5",
    "r5-control": "No Planner",
}
BUILDER_LABELS = {
    "bench-opus": "Opus 4.6",
    "bench-sonnet": "Sonnet 4.6",
    "bench-haiku": "Haiku 4.5",
    "bench-gpt54": "GPT-5.4",
    "bench-gpt54mini": "GPT-5.4 Mini",
    "bench-gemini-pro": "Gemini 3.1 Pro",
    "bench-gemini-flash": "Gemini Flash",
    "bench-glm5": "GLM-5",
}

def load_static_qa(run_id, game, builder):
    path = STATIC_QA_DIR / run_id / game / builder / "result.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except:
        return None

def load_browser_qa(run_id, game, builder):
    path = BROWSER_QA_DIR / run_id / game / builder / "report.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except:
        return None

def is_dnf(run_id, game, builder):
    return (BUILDS_DIR / run_id / game / builder / "dnf.txt").exists()

def build_exists(run_id, game, builder):
    return (BUILDS_DIR / run_id / game / builder / "index.html").exists()

# Compile all results
results = []
for run_id in RUNS:
    for game in GAMES:
        for builder in BUILDERS:
            dnf = is_dnf(run_id, game, builder)
            exists = build_exists(run_id, game, builder)
            static = load_static_qa(run_id, game, builder)
            browser = load_browser_qa(run_id, game, builder)

            score = None
            if static and "final_score" in static:
                score = static["final_score"]

            browser_bugs = 0
            if browser and "bugs" in browser:
                browser_bugs = len(browser["bugs"])
            if browser and "errors" in browser:
                browser_bugs += len(browser["errors"])

            results.append({
                "run": run_id,
                "planner": PLANNER_LABELS.get(run_id, run_id),
                "game": game,
                "builder": builder,
                "builder_label": BUILDER_LABELS.get(builder, builder),
                "status": "dnf" if dnf else ("complete" if exists else "missing"),
                "final_score": score,
                "browser_bugs": browser_bugs,
                "dims": static.get("scores", {}) if static else {},
            })

# Save raw results JSON
(REPORTS_DIR / "results.json").write_text(json.dumps(results, indent=2))

# --- benchmark-report.md ---
def avg(vals):
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 2) if vals else None

lines = []
lines.append(f"# Benchmark V2 Report")
lines.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC*\n")
lines.append("## Summary\n")

# Builder averages across all runs
lines.append("### Builder Scores (avg across all planner runs)\n")
lines.append("| Builder | Avg Score | DNF | Builds |")
lines.append("|---------|-----------|-----|--------|")
for builder in BUILDERS:
    br = [r for r in results if r["builder"] == builder]
    scores = [r["final_score"] for r in br if r["final_score"] is not None]
    dnfs = sum(1 for r in br if r["status"] == "dnf")
    label = BUILDER_LABELS.get(builder, builder)
    lines.append(f"| {label} | {avg(scores) or 'N/A'} | {dnfs} | {len(br)} |")

lines.append("")

# Planner effect
lines.append("### Planner Effect (avg score by planner, across all builders)\n")
lines.append("| Planner | Avg Score | DNF |")
lines.append("|---------|-----------|-----|")
for run_id in RUNS:
    rr = [r for r in results if r["run"] == run_id]
    scores = [r["final_score"] for r in rr if r["final_score"] is not None]
    dnfs = sum(1 for r in rr if r["status"] == "dnf")
    label = PLANNER_LABELS.get(run_id, run_id)
    lines.append(f"| {label} | {avg(scores) or 'N/A'} | {dnfs} |")

lines.append("")

# Game difficulty
lines.append("### Game Difficulty (avg score by game)\n")
lines.append("| Game | Avg Score | DNF rate |")
lines.append("|------|-----------|----------|")
for game in GAMES:
    gr = [r for r in results if r["game"] == game]
    scores = [r["final_score"] for r in gr if r["final_score"] is not None]
    dnfs = sum(1 for r in gr if r["status"] == "dnf")
    lines.append(f"| {game} | {avg(scores) or 'N/A'} | {dnfs}/{len(gr)} |")

lines.append("")

# Browser QA summary
lines.append("### Browser QA — Bug Rates\n")
total_builds_tested = sum(1 for r in results if r["status"] == "complete")
builds_with_bugs = sum(1 for r in results if r["browser_bugs"] > 0)
lines.append(f"- Builds tested: {total_builds_tested}")
lines.append(f"- Builds with bugs: {builds_with_bugs} ({round(builds_with_bugs/max(total_builds_tested,1)*100)}%)")
lines.append("")

(REPORTS_DIR / "benchmark-report.md").write_text("\n".join(lines))
print(f"Report written to {REPORTS_DIR / 'benchmark-report.md'}")

# --- launcher.html ---
cards = []
for r in results:
    build_path = f"../builds/{r['run']}/{r['game']}/{r['builder']}/index.html"
    score_str = f"{r['final_score']:.1f}" if r['final_score'] is not None else "DNF"
    bug_str = f"🐛{r['browser_bugs']}" if r['browser_bugs'] > 0 else "✅"
    cards.append(f"""
    <div class="card {'dnf' if r['status']=='dnf' else ''}">
      <div class="card-header">
        <span class="game">{r['game']}</span>
        <span class="score">{score_str}</span>
        <span class="bugs">{bug_str}</span>
      </div>
      <div class="card-meta">
        <span class="planner">📋 {r['planner']}</span>
        <span class="builder">🔨 {r['builder_label']}</span>
      </div>
      {'<a href="' + build_path + '" target="_blank">▶ Play</a>' if r['status'] == 'complete' else '<span class="dnf-label">DNF</span>'}
    </div>""")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Benchmark V2 Launcher</title>
<style>
  body {{ font-family: monospace; background: #111; color: #eee; padding: 20px; }}
  h1 {{ color: #0f0; }}
  .filters {{ margin: 16px 0; display: flex; gap: 12px; flex-wrap: wrap; }}
  select {{ background: #222; color: #eee; border: 1px solid #444; padding: 6px 10px; border-radius: 4px; }}
  .grid {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 20px; }}
  .card {{ background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 12px; width: 200px; }}
  .card.dnf {{ border-color: #500; opacity: 0.6; }}
  .card-header {{ display: flex; justify-content: space-between; align-items: center; }}
  .game {{ font-weight: bold; font-size: 0.85em; }}
  .score {{ color: #0f0; font-size: 1.1em; }}
  .card-meta {{ margin: 8px 0; font-size: 0.75em; color: #888; display: flex; flex-direction: column; gap: 2px; }}
  a {{ color: #4af; text-decoration: none; font-size: 0.85em; }}
  a:hover {{ color: #8cf; }}
  .dnf-label {{ color: #f44; font-size: 0.85em; }}
</style>
</head>
<body>
<h1>Benchmark V2 — Game Launcher</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | {len([r for r in results if r['status']=='complete'])} builds / {len(results)} total</p>
<div class="filters">
  <select id="filter-run" onchange="applyFilters()">
    <option value="">All planners</option>
    {''.join(f'<option value="{r}">{PLANNER_LABELS[r]}</option>' for r in RUNS)}
  </select>
  <select id="filter-builder" onchange="applyFilters()">
    <option value="">All builders</option>
    {''.join(f'<option value="{b}">{BUILDER_LABELS[b]}</option>' for b in BUILDERS)}
  </select>
  <select id="filter-game" onchange="applyFilters()">
    <option value="">All games</option>
    {''.join(f'<option value="{g}">{g}</option>' for g in GAMES)}
  </select>
</div>
<div class="grid" id="grid">
{''.join(cards)}
</div>
<script>
const cards = document.querySelectorAll('.card');
function applyFilters() {{
  const run = document.getElementById('filter-run').value;
  const builder = document.getElementById('filter-builder').value;
  const game = document.getElementById('filter-game').value;
  cards.forEach(c => {{
    const matches =
      (!run || c.querySelector('.planner').textContent.includes(run)) &&
      (!builder || c.querySelector('.builder').textContent.includes(builder)) &&
      (!game || c.querySelector('.game').textContent === game);
    c.style.display = matches ? '' : 'none';
  }});
}}
</script>
</body>
</html>"""

(REPORTS_DIR / "launcher.html").write_text(html)
print(f"Launcher written to {REPORTS_DIR / 'launcher.html'}")
print(f"\nTotal builds: {len(results)}")
print(f"Complete: {sum(1 for r in results if r['status'] == 'complete')}")
print(f"DNF: {sum(1 for r in results if r['status'] == 'dnf')}")
print(f"With scores: {sum(1 for r in results if r['final_score'] is not None)}")
