#!/usr/bin/env python3
"""Regenerate launcher.html from all games on disk."""
import os, json

ROOT = "/Users/oscar/.openclaw/workspace/games"
OUT = os.path.join(ROOT, "launcher.html")

RUNS = {
    "run1-opus-plan":     "Run 1 — Opus Plans",
    "run2-gpt-plan":      "Run 2 — GPT-5.4 Plans",
    "run3-opus-isolated": "Run 3 — Opus Isolated (Opus specs)",
    "run4-gpt-isolated":  "Run 4 — Opus Isolated (GPT specs)",
    "run5-opus-gemini":   "Run 5 — Gemini (Opus specs)",
    "run6-gpt-gemini":    "Run 6 — Gemini (GPT specs)",
    "run7-opus-mini-nano":"Run 7 — mini/nano (Opus specs)",
    "run8-gpt-mini-nano": "Run 8 — mini/nano (GPT specs)",
}

MODEL_META = {
    "sonnet":       {"label": "Claude Sonnet 4.6",  "badge": "badge-sonnet"},
    "opus":         {"label": "Claude Opus 4.6",     "badge": "badge-opus"},
    "haiku":        {"label": "Claude Haiku 4.5",    "badge": "badge-haiku"},
    "gpt-5-4":      {"label": "GPT-5.4",              "badge": "badge-gpt"},
    "o3-mini":      {"label": "o3-mini",              "badge": "badge-o3"},
    "gemini-pro":   {"label": "Gemini 3.1 Pro",      "badge": "badge-gpro"},
    "gemini-flash": {"label": "Gemini 3 Flash",       "badge": "badge-gflash"},
    "gpt-5-4-mini": {"label": "GPT-5.4 Mini",         "badge": "badge-mini"},
    "gpt-5-4-nano": {"label": "GPT-5.4 Nano",         "badge": "badge-nano"},
    # alternate key styles used by some runs
    "gpt-5.4-mini": {"label": "GPT-5.4 Mini",         "badge": "badge-mini"},
    "gpt-5.4-nano": {"label": "GPT-5.4 Nano",         "badge": "badge-nano"},
}

# Spec style for each run (for filter + display)
RUN_SPEC = {
    "run1-opus-plan":      "opus",
    "run2-gpt-plan":       "gpt",
    "run3-opus-isolated":  "opus",
    "run4-gpt-isolated":   "gpt",
    "run5-opus-gemini":    "opus",
    "run6-gpt-gemini":     "gpt",
    "run7-opus-mini-nano": "opus",
    "run8-gpt-mini-nano":  "gpt",
}

GAME_LABELS = {
    "pong": "Pong", "snake": "Snake", "breakout": "Breakout",
    "space-invaders": "Space Invaders", "tetris": "Tetris",
    "asteroids": "Asteroids", "galaga": "Galaga",
    "frogger": "Frogger", "pac-man": "Pac-Man", "donkey-kong": "Donkey Kong",
}

games = []

for run_slug, run_label in RUNS.items():
    run_dir = os.path.join(ROOT, run_slug)
    if not os.path.isdir(run_dir):
        continue
    for game_slug in os.listdir(run_dir):
        game_path = os.path.join(run_dir, game_slug)
        if not os.path.isdir(game_path):
            continue
        for model_slug in os.listdir(game_path):
            model_path = os.path.join(game_path, model_slug)
            html_path  = os.path.join(model_path, "index.html")
            if not os.path.isdir(model_path) or not os.path.isfile(html_path):
                continue
            meta = MODEL_META.get(model_slug, {"label": model_slug, "badge": "badge-sonnet"})
            spec = RUN_SPEC.get(run_slug, "unknown")

            # Pull score directly from results.json
            score = None
            results_path = os.path.join(game_path, "results.json")
            if os.path.exists(results_path):
                try:
                    with open(results_path) as rf:
                        rdata = json.load(rf)
                    build = rdata.get("builds", {}).get(model_slug, {})
                    qa = build.get("qa_scores_consensus") or build.get("qa_scores") or {}
                    if qa.get("final_score"):
                        score = round(float(qa["final_score"]), 2)
                except Exception:
                    pass

            # Also pull per-dimension scores for tooltip
            dims = {}
            if os.path.exists(results_path):
                try:
                    with open(results_path) as rf:
                        rdata = json.load(rf)
                    build = rdata.get("builds", {}).get(model_slug, {})
                    qa = build.get("qa_scores_consensus") or build.get("qa_scores") or {}
                    for dim in ["functionality","keyboard_controls","visual_fidelity","playability","error_free"]:
                        if qa.get(dim) is not None:
                            dims[dim] = round(float(qa[dim]), 1)
                except Exception:
                    pass

            games.append({
                "run":        run_slug,
                "runLabel":   run_label,
                "spec":       spec,
                "game":       game_slug,
                "gameLabel":  GAME_LABELS.get(game_slug, game_slug),
                "model":      model_slug,
                "modelLabel": meta["label"],
                "badge":      meta["badge"],
                "path":       f"{run_slug}/{game_slug}/{model_slug}/index.html",
                "score":      score,
                "dims":       dims,
            })

total_runs = len({g["run"] for g in games})
total_models = len({g["model"] for g in games})
total_builds = len(games)

games_json = json.dumps(games, separators=(',', ':'))

tmpl = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vintage Games Benchmark — Game Launcher</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0f; color: #e0e0e0; min-height: 100vh; }}
  header {{ padding: 32px 40px 24px; border-bottom: 1px solid #1e1e2e; }}
  header h1 {{ font-size: 24px; font-weight: 700; color: #fff; margin-bottom: 6px; }}
  header p {{ font-size: 14px; color: #888; }}
  header .stats {{ display: flex; gap: 24px; margin-top: 16px; }}
  header .stat {{ font-size: 13px; color: #aaa; }}
  header .stat span {{ color: #7c6af7; font-weight: 600; }}
  .filters {{ padding: 20px 40px; display: flex; gap: 12px; flex-wrap: wrap; border-bottom: 1px solid #1e1e2e; }}
  .filter-group {{ display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }}
  .filter-label {{ font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.05em; margin-right: 4px; }}
  .filter-btn {{ padding: 5px 12px; border-radius: 20px; border: 1px solid #2a2a3e; background: transparent; color: #aaa; font-size: 12px; cursor: pointer; transition: all 0.15s; }}
  .filter-btn:hover {{ border-color: #7c6af7; color: #c0b8ff; }}
  .filter-btn.active {{ background: #7c6af7; border-color: #7c6af7; color: #fff; font-weight: 500; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; padding: 28px 40px; }}
  .card {{ background: #12121e; border: 1px solid #1e1e2e; border-radius: 12px; overflow: hidden; transition: transform 0.15s, border-color 0.15s; }}
  .card:hover {{ transform: translateY(-2px); border-color: #3a3a5e; }}
  .card-header {{ padding: 14px 16px 10px; border-bottom: 1px solid #1e1e2e; }}
  .card-game {{ font-size: 15px; font-weight: 600; color: #fff; }}
  .card-model {{ font-size: 12px; color: #7c6af7; margin-top: 3px; }}
  .card-run {{ font-size: 11px; color: #555; margin-top: 2px; }}
  .card-body {{ padding: 10px 16px 14px; display: flex; align-items: center; justify-content: space-between; }}
  .score {{ font-size: 22px; font-weight: 700; }}
  .score.high {{ color: #4ade80; }}
  .score.mid {{ color: #facc15; }}
  .score.low {{ color: #f87171; }}
  .score.none {{ color: #444; font-size: 14px; }}
  .play-btn {{ display: inline-flex; align-items: center; gap: 5px; padding: 7px 14px; background: #7c6af7; color: #fff; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: 500; transition: background 0.15s; }}
  .play-btn:hover {{ background: #9b8cff; }}
  .empty {{ text-align: center; padding: 60px; color: #444; grid-column: 1/-1; }}
  .model-badge {{ display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }}
  .badge-sonnet {{ background: #1a3a5c; color: #7eb8f7; }}
  .badge-opus {{ background: #3a1a5c; color: #c78bf7; }}
  .badge-haiku {{ background: #1a3a2a; color: #7bf7a8; }}
  .badge-gpt {{ background: #3a2a1a; color: #f7c87b; }}
  .badge-o3 {{ background: #3a1a1a; color: #f77b7b; }}
  .badge-gpro {{ background: #1a2a3a; color: #7bf0f7; }}
  .badge-gflash {{ background: #1a3a3a; color: #7bf7e8; }}
  .badge-mini {{ background: #2a3a1a; color: #c8f77b; }}
  .badge-nano {{ background: #3a3a1a; color: #f7e87b; }}
  .dims {{ font-size: 10px; color: #555; margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; }}
  .dim {{ background: #1a1a2e; border-radius: 3px; padding: 1px 5px; }}
  .spec-pill {{ display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; margin-left: 4px; }}
  .spec-opus {{ background: #2a1a4a; color: #c07af7; }}
  .spec-gpt {{ background: #1a2a1a; color: #7af77a; }}
  .report-link {{ display: block; text-align: center; padding: 8px; font-size: 12px; color: #7c6af7; text-decoration: none; border-top: 1px solid #1e1e2e; }}
  .report-link:hover {{ color: #9b8cff; }}
</style>
</head>
<body>
<header>
  <h1>🕹️ Vintage Games Benchmark</h1>
  <p>{total_builds} playable HTML5 games built by {total_models} AI models across {total_runs} benchmark runs · <a href="benchmark-report.md" style="color:#7c6af7">📄 Full Report</a></p>
  <div class="stats">
    <div class="stat">Models: <span>{total_models}</span></div>
    <div class="stat">Games: <span>10</span></div>
    <div class="stat">Runs: <span>{total_runs}</span></div>
    <div class="stat">Total builds: <span>{total_builds}</span></div>
  </div>
</header>
<div class="filters">
  <div class="filter-group">
    <span class="filter-label">Game</span>
    <button class="filter-btn active" data-filter="game" data-value="all">All</button>
    <button class="filter-btn" data-filter="game" data-value="pong">Pong</button>
    <button class="filter-btn" data-filter="game" data-value="snake">Snake</button>
    <button class="filter-btn" data-filter="game" data-value="breakout">Breakout</button>
    <button class="filter-btn" data-filter="game" data-value="space-invaders">Space Invaders</button>
    <button class="filter-btn" data-filter="game" data-value="tetris">Tetris</button>
    <button class="filter-btn" data-filter="game" data-value="asteroids">Asteroids</button>
    <button class="filter-btn" data-filter="game" data-value="galaga">Galaga</button>
    <button class="filter-btn" data-filter="game" data-value="frogger">Frogger</button>
    <button class="filter-btn" data-filter="game" data-value="pac-man">Pac-Man</button>
    <button class="filter-btn" data-filter="game" data-value="donkey-kong">Donkey Kong</button>
  </div>
  <div class="filter-group">
    <span class="filter-label">Model</span>
    <button class="filter-btn active" data-filter="model" data-value="all">All</button>
    <button class="filter-btn" data-filter="model" data-value="sonnet">Sonnet</button>
    <button class="filter-btn" data-filter="model" data-value="opus">Opus</button>
    <button class="filter-btn" data-filter="model" data-value="haiku">Haiku</button>
    <button class="filter-btn" data-filter="model" data-value="gpt-5-4">GPT-5.4</button>
    <button class="filter-btn" data-filter="model" data-value="o3-mini">o3-mini</button>
    <button class="filter-btn" data-filter="model" data-value="gemini-pro">Gemini Pro</button>
    <button class="filter-btn" data-filter="model" data-value="gemini-flash">Gemini Flash</button>
    <button class="filter-btn" data-filter="model" data-value="gpt-5-4-mini">GPT-5.4 Mini</button>
    <button class="filter-btn" data-filter="model" data-value="gpt-5-4-nano">GPT-5.4 Nano</button>
  </div>
  <div class="filter-group">
    <span class="filter-label">Spec</span>
    <button class="filter-btn active" data-filter="spec" data-value="all">All</button>
    <button class="filter-btn" data-filter="spec" data-value="opus">Opus specs</button>
    <button class="filter-btn" data-filter="spec" data-value="gpt">GPT specs</button>
  </div>
</div>
<div class="grid" id="grid"></div>
<script>
const games = {games_json};
let filters = {{ game: 'all', model: 'all', spec: 'all' }};
function scoreClass(s) {{ if (s === null) return 'none'; if (s >= 8) return 'high'; if (s >= 5) return 'mid'; return 'low'; }}
function scoreText(s) {{ if (s === null) return 'No score'; return s.toFixed(2); }}
function badgeMap(slug) {{ const m = {{ 'sonnet':'Sonnet','opus':'Opus','haiku':'Haiku','gpt-5-4':'GPT-5.4','o3-mini':'o3-mini','gemini-pro':'Gemini Pro','gemini-flash':'Gemini Flash','gpt-5-4-mini':'GPT-5.4 Mini','gpt-5-4-nano':'GPT-5.4 Nano' }}; return m[slug] || slug; }}
function render() {{
  const grid = document.getElementById('grid');
  const filtered = games.filter(g =>
    (filters.game  === 'all' || g.game  === filters.game) &&
    (filters.model === 'all' || g.model === filters.model || g.model.replace(/\./g,'-') === filters.model) &&
    (filters.spec  === 'all' || g.spec  === filters.spec)
  );
  if (!filtered.length) {{ grid.innerHTML = '<div class="empty">No games match this filter.</div>'; return; }}
  grid.innerHTML = filtered.map(g => {{
    const dimHtml = g.dims && Object.keys(g.dims).length ? `<div class="dims">
      ${{g.dims.functionality    !== undefined ? `<span class="dim" title="Functionality">Func:${{g.dims.functionality}}</span>` : ''}}
      ${{g.dims.keyboard_controls!== undefined ? `<span class="dim" title="Controls">Ctrl:${{g.dims.keyboard_controls}}</span>` : ''}}
      ${{g.dims.visual_fidelity  !== undefined ? `<span class="dim" title="Visual Fidelity">Visuals:${{g.dims.visual_fidelity}}</span>` : ''}}
      ${{g.dims.playability      !== undefined ? `<span class="dim" title="Playability">Play:${{g.dims.playability}}</span>` : ''}}
      ${{g.dims.error_free       !== undefined ? `<span class="dim" title="Error-Free">Errors:${{g.dims.error_free}}</span>` : ''}}
    </div>` : '';
    return `<div class="card" data-game="${{g.game}}" data-model="${{g.model}}" data-spec="${{g.spec}}">
    <div class="card-header">
      <div class="card-game">${{g.gameLabel}}</div>
      <div class="card-model">${{g.modelLabel}}</div>
      <div class="card-run">${{g.runLabel}}</div>
      <span class="model-badge ${{g.badge}}">${{badgeMap(g.model)}}</span>
      <span class="spec-pill spec-${{g.spec}}">${{g.spec === 'opus' ? 'Opus spec' : 'GPT spec'}}</span>
    </div>
    <div class="card-body">
      <div>
        <div class="score ${{scoreClass(g.score)}}">${{scoreText(g.score)}}</div>
        ${{dimHtml}}
      </div>
      <a class="play-btn" href="${{g.path}}" target="_blank">▶ Play</a>
    </div>
  </div>`;
  }}).join('');
}}
document.querySelectorAll('.filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const type = btn.dataset.filter, val = btn.dataset.value;
    filters[type] = val;
    document.querySelectorAll(`[data-filter="${{type}}"]`).forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    render();
  }});
}});
render();
</script>
</body>
</html>'''

with open(OUT, 'w') as f:
    f.write(tmpl)

print(f"✅ Wrote {OUT}")
print(f"   Games: {total_builds} | Models: {total_models} | Runs: {total_runs}")
