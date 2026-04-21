#!/usr/bin/env python3
"""
Multi-judge QA scorer — scores every built game with 3 judges:
  - openai/gpt-5.4
  - anthropic/claude-opus-4.6
  - google/gemini-3.1-pro-preview

Stores scores as qa_scores_gpt54, qa_scores_opus, qa_scores_gemini.
Computes consensus (average of 3) and stores as qa_scores_consensus.
Also backfills html_size_bytes from disk for any build missing it.

Usage:
  python3 qa_multijudge.py                      # score all builds missing any judge
  python3 qa_multijudge.py --judge opus         # only run opus judge
  python3 qa_multijudge.py --judge gpt54        # only run gpt54 judge
  python3 qa_multijudge.py --judge gemini       # only run gemini judge
  python3 qa_multijudge.py --dry-run            # show what would run
  python3 qa_multijudge.py --rescore-all        # force redo every judge on every build
  python3 qa_multijudge.py --run run7           # limit to one run
"""
import os, sys, json, time, pathlib, requests, argparse, concurrent.futures, threading

API_KEY = os.environ.get("PALEBLUEDOT_API_KEY", "")
BASE_URL = "https://open.palebluedot.ai/v1"

GAMES_DIR = pathlib.Path("/Users/oscar/.openclaw/workspace/games")

JUDGES = {
    "gpt54":  {"model": "openai/gpt-5.4",               "field": "qa_scores_gpt54"},
    "opus":   {"model": "anthropic/claude-opus-4.6",     "field": "qa_scores_opus"},
    "gemini": {"model": "google/gemini-3-flash-preview", "field": "qa_scores_gemini"},
}

WEIGHTS = {
    "functionality":    0.30,
    "keyboard_controls":0.20,
    "visual_fidelity":  0.20,
    "playability":      0.20,
    "error_free":       0.10,
}

RUBRIC_PROMPT = """You are a strict game QA reviewer. Read the HTML5 game source code and score it on 5 dimensions, 0-10 each.

RUBRIC:
- functionality (0-10): Core mechanics implemented and actually playable?
- keyboard_controls (0-10): Controls implemented, responsive, correct?
- visual_fidelity (0-10): Looks like the original arcade game? Correct colours, shapes, layout?
- playability (0-10): Balanced difficulty, proper game loop (start/restart/game over)?
- error_free (0-10): Free of obvious bugs, syntax errors, broken logic?

SCORING:
9-10: Excellent | 7-8: Good, minor issues | 5-6: Functional but notable gaps | 3-4: Significant issues | 1-2: Barely works | 0: Broken

GAME: {game}
SPEC SUMMARY: {spec_summary}

HTML SOURCE:
{html_source}

Respond ONLY with valid JSON, no markdown, no explanation:
{{"functionality":<0-10>,"keyboard_controls":<0-10>,"visual_fidelity":<0-10>,"playability":<0-10>,"error_free":<0-10>,"notes":"<one sentence>"}}"""

write_lock = threading.Lock()

def call_api(model: str, prompt: str) -> str:
    # Gemini Pro outputs reasoning tokens — Flash does not, but give headroom anyway
    max_tok = 600 if "gemini" in model else 400
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}],
              "max_tokens": max_tok, "temperature": 0.2},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def parse_scores(raw: str) -> dict:
    raw = raw.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    raw = raw.strip()
    # Find JSON object
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        raw = raw[start:end]
    scores = json.loads(raw)
    final = sum(scores.get(k, 0) * w for k, w in WEIGHTS.items())
    scores["final_score"] = round(final, 2)
    return scores

def compute_consensus(fields_present: list[dict]) -> dict:
    """Average scores across multiple judge results."""
    dims = list(WEIGHTS.keys())
    consensus = {}
    for dim in dims:
        vals = [j[dim] for j in fields_present if isinstance(j.get(dim), (int, float))]
        consensus[dim] = round(sum(vals) / len(vals), 2) if vals else None
    finals = [j["final_score"] for j in fields_present if isinstance(j.get("final_score"), (int, float))]
    consensus["final_score"] = round(sum(finals) / len(finals), 2) if finals else None
    # Judge disagreement (max spread on final)
    if len(finals) >= 2:
        consensus["judge_spread"] = round(max(finals) - min(finals), 2)
    return consensus

def score_one(game: str, run_name: str, model_slug: str, html_path: pathlib.Path,
              spec_path: pathlib.Path, judge_key: str):
    judge = JUDGES[judge_key]
    html = html_path.read_text(errors="replace")
    if len(html) > 80000:
        html = html[:80000] + "\n...[truncated]"
    spec_summary = spec_path.read_text()[:500] if spec_path.exists() else ""
    prompt = RUBRIC_PROMPT.format(game=game, spec_summary=spec_summary, html_source=html)
    raw = call_api(judge["model"], prompt)
    return parse_scores(raw)

def update_results(results_path: pathlib.Path, model_slug: str, judge_key: str,
                   scores: dict, html_size):
    """Thread-safe update of results.json."""
    field = JUDGES[judge_key]["field"]
    with write_lock:
        if results_path.exists():
            d = json.loads(results_path.read_text())
        else:
            d = {"game": results_path.parent.name, "builds": {}}
        builds = d.setdefault("builds", {})
        if model_slug not in builds or not isinstance(builds[model_slug], dict):
            builds[model_slug] = {}
        build = builds[model_slug]

        build[field] = scores
        build[f"{field}_judge"] = JUDGES[judge_key]["model"]
        build[f"{field}_scored_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Backfill html_size_bytes if missing
        if html_size is not None and not build.get("html_size_bytes"):
            build["html_size_bytes"] = html_size

        # Recompute consensus from whatever judges are present
        present = [build[JUDGES[j]["field"]] for j in JUDGES
                   if isinstance(build.get(JUDGES[j]["field"]), dict)]
        if present:
            build["qa_scores_consensus"] = compute_consensus(present)
            build["qa_judges_count"] = len(present)

        # Keep legacy qa_scores pointing at consensus for backwards compat
        if build.get("qa_scores_consensus"):
            build["qa_scores"] = build["qa_scores_consensus"]
            build["status"] = "complete"

        results_path.write_text(json.dumps(d, indent=2))

def collect_work(filter_run=None, filter_judge=None, rescore_all=False):
    """Return list of (run_name, game, model_slug, html_path, spec_path, judge_key) tuples."""
    work = []
    judge_keys = [filter_judge] if filter_judge else list(JUDGES.keys())

    for run_dir in sorted(GAMES_DIR.iterdir()):
        if not run_dir.is_dir() or not run_dir.name.startswith("run"): continue
        if filter_run and filter_run not in run_dir.name: continue

        for game_dir in sorted(run_dir.iterdir()):
            if not game_dir.is_dir(): continue
            game = game_dir.name
            spec_path = game_dir / "spec.md"
            results_path = game_dir / "results.json"

            existing = {}
            if results_path.exists():
                try:
                    d = json.loads(results_path.read_text())
                    existing = d.get("builds", d)
                except: pass

            for model_dir in sorted(game_dir.iterdir()):
                if not model_dir.is_dir(): continue
                model_slug = model_dir.name
                html_path = model_dir / "index.html"
                if not html_path.exists() or html_path.stat().st_size < 500: continue

                build = existing.get(model_slug, {}) if isinstance(existing.get(model_slug), dict) else {}
                for judge_key in judge_keys:
                    field = JUDGES[judge_key]["field"]
                    already_scored = isinstance(build.get(field), dict) and build[field].get("final_score")
                    if not already_scored or rescore_all:
                        work.append((run_dir.name, game, model_slug, html_path, spec_path,
                                     results_path, judge_key))
    return work

def run_task(item, dry_run=False):
    run_name, game, model_slug, html_path, spec_path, results_path, judge_key = item
    tag = f"{run_name}/{game}/{model_slug} [{judge_key}]"
    if dry_run:
        print(f"  WOULD SCORE: {tag}")
        return "dry"

    html_size = html_path.stat().st_size

    for attempt in range(3):
        try:
            scores = score_one(game, run_name, model_slug, html_path, spec_path, judge_key)
            update_results(results_path, model_slug, judge_key, scores, html_size)
            print(f"  ✅ {tag} → {scores['final_score']:.1f}")
            return "ok"
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                print(f"  ❌ {tag} → {e}")
                return "error"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", choices=list(JUDGES.keys()), help="Only run one judge")
    parser.add_argument("--run", help="Only score specific run")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rescore-all", action="store_true")
    parser.add_argument("--workers", type=int, default=6, help="Parallel workers (default 6)")
    args = parser.parse_args()

    if not API_KEY and not args.dry_run:
        print("ERROR: PALEBLUEDOT_API_KEY not set"); sys.exit(1)

    work = collect_work(filter_run=args.run, filter_judge=args.judge, rescore_all=args.rescore_all)

    print(f"{'DRY RUN — ' if args.dry_run else ''}{'='*60}")
    print(f"Jobs to run: {len(work)} (workers={args.workers})")
    print(f"{'='*60}")

    if args.dry_run:
        for item in work:
            run_task(item, dry_run=True)
        print(f"\nTotal: {len(work)} would be scored")
        return

    ok = err = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(run_task, item): item for item in work}
        for f in concurrent.futures.as_completed(futures):
            result = f.result()
            if result == "ok": ok += 1
            elif result == "error": err += 1

    print(f"\n{'='*60}")
    print(f"DONE — {ok} scored, {err} errors")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
