#!/usr/bin/env python3
"""
Aggregate benchmark data into guide/data.json for the interactive guide.

Reads:
  - workspace/verified-data.json       (per-build judge scores, dimensions)
  - workspace/review/ratings.json      (Oscar's in-progress human ratings)

Writes:
  - workspace/guide/data.json          (consumed by the guide dashboard)

Run: python3 guide/aggregate.py
"""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent
VERIFIED = WORKSPACE / "verified-data.json"
RATINGS = WORKSPACE / "review" / "ratings.json"
OUT = HERE / "data.json"


# Judge prompts and rubric — mirrored from the scripts that actually ran QA.
# Source of truth: scripts/qa_multijudge.py (V1), games-v2/scripts/03_static_qa.sh (V2).
# If upstream prompts change, update these strings.
JUDGE_RUBRIC = {
    "weights": {
        "functionality": 0.30,
        "keyboard_controls": 0.20,
        "visual_fidelity": 0.20,
        "playability": 0.20,
        "error_free": 0.10,
    },
    "dimensions": {
        "functionality": "Core mechanics implemented and actually playable",
        "keyboard_controls": "Controls implemented, responsive, correct mappings",
        "visual_fidelity": "Looks like the original arcade game — colours, shapes, layout",
        "playability": "Balanced difficulty, proper game loop (start / restart / game over)",
        "error_free": "Free of obvious bugs, syntax errors, broken logic",
    },
    "v1_prompt": (
        "You are a strict game QA reviewer. Read the HTML5 game source code and score it on 5 "
        "dimensions, 0-10 each.\n\n"
        "RUBRIC:\n"
        "- functionality (0-10): Core mechanics implemented and actually playable?\n"
        "- keyboard_controls (0-10): Controls implemented, responsive, correct?\n"
        "- visual_fidelity (0-10): Looks like the original arcade game? Correct colours, shapes, layout?\n"
        "- playability (0-10): Balanced difficulty, proper game loop (start/restart/game over)?\n"
        "- error_free (0-10): Free of obvious bugs, syntax errors, broken logic?\n\n"
        "SCORING:\n"
        "9-10: Excellent | 7-8: Good, minor issues | 5-6: Functional but notable gaps | "
        "3-4: Significant issues | 1-2: Barely works | 0: Broken\n\n"
        "GAME: {game}\n"
        "SPEC SUMMARY: {spec_summary}\n\n"
        "HTML SOURCE:\n{html_source}\n\n"
        "Respond ONLY with valid JSON, no markdown, no explanation:\n"
        "{\"functionality\":<0-10>,\"keyboard_controls\":<0-10>,\"visual_fidelity\":<0-10>,"
        "\"playability\":<0-10>,\"error_free\":<0-10>,\"notes\":\"<one sentence>\"}"
    ),
    "v2_prompt": (
        "You are scoring an HTML5 game build for a benchmark.\n\n"
        "Read the source file at this path: {build_file}\n\n"
        "Score on 5 dimensions (0–10 each):\n"
        "- functionality: game logic complete and correct\n"
        "- keyboard_controls: controls work as expected\n"
        "- visual_fidelity: rendering looks correct for this game type\n"
        "- playability: actually playable as a game\n"
        "- error_free: no obvious JS errors or crashes\n\n"
        "Weighted final: (func*0.30)+(kbd*0.20)+(vis*0.20)+(play*0.20)+(err*0.10)\n\n"
        "Output ONLY valid JSON, nothing else:\n"
        "{\"judge\":\"{judge}\",\"functionality\":N,\"keyboard_controls\":N,"
        "\"visual_fidelity\":N,\"playability\":N,\"error_free\":N,"
        "\"final_score\":N.NN,\"notes\":\"one sentence\"}"
    ),
    "v1_judges": [
        {"key": "gpt54", "label": "GPT-5.4", "model": "openai/gpt-5.4"},
        {"key": "opus", "label": "Opus", "model": "anthropic/claude-opus-4.6"},
        {"key": "gemini_flash", "label": "Gemini Flash", "model": "google/gemini-3-flash-preview"},
    ],
    "v2_judges": [
        {"key": "sonnet", "label": "Sonnet", "model": "bench-sonnet"},
        {"key": "gpt54", "label": "GPT-5.4", "model": "bench-gpt54"},
        {"key": "gemini_pro", "label": "Gemini Pro", "model": "bench-gemini-pro"},
    ],
}


# Display names for builder keys (both V1 bare and V2 bench- prefixed)
BUILDER_DISPLAY = {
    "sonnet": "Sonnet", "opus": "Opus", "haiku": "Haiku", "o3-mini": "o3-mini",
    "gpt-5-4": "GPT-5.4", "gpt-5.4-mini": "GPT-5.4 Mini", "gpt-5.4-nano": "GPT-5.4 Nano",
    "gemini-flash": "Gemini Flash", "gemini-pro": "Gemini Pro",
    "bench-sonnet": "Sonnet", "bench-opus": "Opus", "bench-haiku": "Haiku",
    "bench-gpt54": "GPT-5.4", "bench-gpt54mini": "GPT-5.4 Mini",
    "bench-gemini-flash": "Gemini Flash", "bench-gemini-pro": "Gemini Pro",
    "bench-glm5": "GLM-5",
}

# Which planner produced specs for this run (independent of which builder used them)
PLANNER_OF_RUN = {
    "run1-opus-plan": "opus", "run2-gpt-plan": "gpt54",
    "run3-opus-isolated": "opus", "run4-gpt-isolated": "gpt54",
    "run5-opus-gemini": "opus", "run6-gpt-gemini": "gpt54",
    "run7-opus-mini-nano": "opus", "run8-gpt-mini-nano": "gpt54",
    "r1-opus": "opus", "r2-gpt54": "gpt54", "r3-gemini-pro": "gemini-pro",
    "r4-glm5": "glm5", "r5-control": "control",
}

PLANNER_DISPLAY = {
    "opus": "Opus", "gpt54": "GPT-5.4", "gemini-pro": "Gemini Pro",
    "glm5": "GLM-5", "control": "Control (no spec)",
}

# Run context (spec format + context isolation) — important pedagogical metadata
RUN_CONTEXT = {
    "run1-opus-plan": "template + accumulated context",
    "run2-gpt-plan": "template + accumulated context",
    "run3-opus-isolated": "template + isolated context",
    "run4-gpt-isolated": "template + isolated context",
    "run5-opus-gemini": "template + accumulated (gemini builders)",
    "run6-gpt-gemini": "template + accumulated (gemini builders)",
    "run7-opus-mini-nano": "template + accumulated (mini/nano builders)",
    "run8-gpt-mini-nano": "template + accumulated (mini/nano builders)",
    "r1-opus": "free spec + isolated context",
    "r2-gpt54": "free spec + isolated context",
    "r3-gemini-pro": "free spec + isolated context",
    "r4-glm5": "free spec + isolated context",
    "r5-control": "no spec + isolated context",
}


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def num(v):
    """Coerce to float if possible, else None. Handles stray strings like '8.30'."""
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def spec_path_for(dataset, run, game):
    """Return workspace-relative spec path, or None if not found."""
    if dataset == "v1":
        p = WORKSPACE / "games" / run / game / "spec.md"
    else:
        p = WORKSPACE / "games-v2" / "specs" / run / game / "spec.md"
    return str(p.relative_to(WORKSPACE)) if p.exists() else None


def normalize_build(b, ratings):
    dataset = b["dataset"]
    run = b["run"]
    game = b["game"]
    builder = b["builder"]
    status = b.get("status", "unknown")
    qa = b.get("qa_scores") or {}

    build_id = f"{dataset}/{run}/{game}/{builder}"

    # --- Scores (V1 and V2 have different qa_scores shapes) ---
    if dataset == "v1":
        consensus = num(qa.get("consensus_final"))
        judges = {
            "gpt54": num(qa.get("gpt54_final")),
            "opus": num(qa.get("opus_final")),
            "gemini_flash": num(qa.get("gemini_final")),
        }
        dimensions = {k: num(v) for k, v in (qa.get("dimensions") or {}).items()}
        per_judge_dimensions = None  # V1 doesn't store per-judge per-dimension
        judge_notes = None
        judge_spread = num(qa.get("judge_spread"))
    else:
        consensus = num(qa.get("static_qa_final"))
        judges = {}
        per_judge_dimensions = {}
        judge_notes = {}
        for key, norm in [
            ("judge_sonnet", "sonnet"),
            ("judge_gpt54", "gpt54"),
            ("judge_gemini-pro", "gemini_pro"),
        ]:
            j = qa.get(key)
            if not j:
                continue
            judges[norm] = num(j.get("final_score"))
            per_judge_dimensions[norm] = {
                "functionality": num(j.get("functionality")),
                "keyboard_controls": num(j.get("keyboard_controls")),
                "visual_fidelity": num(j.get("visual_fidelity")),
                "playability": num(j.get("playability")),
                "error_free": num(j.get("error_free")),
            }
            judge_notes[norm] = j.get("notes")
        dimensions = {k: num(v) for k, v in (qa.get("static_qa_dimensions") or {}).items()}
        # Compute judge_spread from per-judge finals
        vals = [v for v in judges.values() if v is not None]
        judge_spread = round(max(vals) - min(vals), 2) if len(vals) >= 2 else None

    human_rating = ratings.get(build_id)

    return {
        "id": build_id,
        "dataset": dataset,
        "run": run,
        "run_context": RUN_CONTEXT.get(run, ""),
        "game": game,
        "builder": builder,
        "builder_display": BUILDER_DISPLAY.get(builder, builder),
        "planner": PLANNER_OF_RUN.get(run, "unknown"),
        "planner_display": PLANNER_DISPLAY.get(PLANNER_OF_RUN.get(run, ""), "Unknown"),
        "status": status,
        "consensus": consensus,
        "judges": judges,
        "judge_spread": judge_spread,
        "dimensions": dimensions,
        "per_judge_dimensions": per_judge_dimensions,
        "judge_notes": judge_notes,
        "tokens_input": b.get("tokens_input"),
        "tokens_output": b.get("tokens_output"),
        "cost_usd": b.get("estimated_cost_usd"),
        "cost_source": b.get("cost_source"),
        "html_size": b.get("html_size_bytes"),
        "browser_bugs": qa.get("browser_bugs_count") if dataset == "v2" else None,
        "spec_path": spec_path_for(dataset, run, game),
        "game_url": f"/game/{build_id}/" if status == "complete" else None,
        "has_human_rating": human_rating is not None,
        "human_rating": human_rating,
    }


# Canonical planner runs for spec browsing — V1 has duplicate spec files across runs
# because runs 3-8 reused run1/run2 specs verbatim. Showing all 8 would be redundant.
CANONICAL_SPEC_RUNS = [
    ("v1", "run1-opus-plan"),
    ("v1", "run2-gpt-plan"),
    ("v2", "r1-opus"),
    ("v2", "r2-gpt54"),
    ("v2", "r3-gemini-pro"),
    ("v2", "r4-glm5"),
    ("v2", "r5-control"),
]


def collect_specs():
    """Return list of spec records: one per (dataset, run, game) canonical combination."""
    specs = []
    for dataset, run in CANONICAL_SPEC_RUNS:
        if dataset == "v1":
            root = WORKSPACE / "games" / run
        else:
            root = WORKSPACE / "games-v2" / "specs" / run
        if not root.exists():
            continue
        for game_dir in sorted(root.iterdir()):
            if not game_dir.is_dir():
                continue
            spec_file = game_dir / "spec.md"
            if not spec_file.exists():
                continue
            specs.append({
                "dataset": dataset,
                "run": run,
                "planner": PLANNER_OF_RUN.get(run, "unknown"),
                "planner_display": PLANNER_DISPLAY.get(PLANNER_OF_RUN.get(run, ""), "Unknown"),
                "game": game_dir.name,
                "bytes": spec_file.stat().st_size,
                "lines": sum(1 for _ in spec_file.open()),
                "path": str(spec_file.relative_to(WORKSPACE)),
                "spec_url": f"/spec/{dataset}/{run}/{game_dir.name}",
            })
    return specs


def build_meta(builds):
    v1 = [b for b in builds if b["dataset"] == "v1"]
    v2 = [b for b in builds if b["dataset"] == "v2"]
    v1_status = Counter(b["status"] for b in v1)
    v2_status = Counter(b["status"] for b in v2)
    specs = collect_specs()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_builds": len(builds),
        "v1": {
            "total": len(v1),
            "complete": v1_status.get("complete", 0),
            "dnf": v1_status.get("dnf", 0),
            "pending": v1_status.get("pending", 0),
        },
        "v2": {
            "total": len(v2),
            "complete": v2_status.get("complete", 0),
            "dnf": v2_status.get("dnf", 0),
            "missing": v2_status.get("missing", 0),
        },
        "judges": {
            "v1": {"gpt54": "GPT-5.4", "opus": "Opus", "gemini_flash": "Gemini Flash"},
            "v2": {"sonnet": "Sonnet", "gpt54": "GPT-5.4", "gemini_pro": "Gemini Pro"},
        },
        "runs": sorted({b["run"] for b in builds}),
        "games": sorted({b["game"] for b in builds}),
        "builders": sorted({b["builder_display"] for b in builds}),
        "planners": sorted({b["planner"] for b in builds}),
        "human_ratings_count": sum(1 for b in builds if b["has_human_rating"]),
        "rubric": JUDGE_RUBRIC,
        "specs": specs,
    }


def main():
    verified = load_json(VERIFIED)
    ratings = load_json(RATINGS)

    raw_builds = verified.get("builds", [])
    if not raw_builds:
        print(f"ERROR: no builds found in {VERIFIED}")
        return 1

    builds = [normalize_build(b, ratings) for b in raw_builds]
    meta = build_meta(builds)

    OUT.write_text(json.dumps({"meta": meta, "builds": builds}, indent=2))

    print(f"Wrote {OUT}")
    print(f"  Total: {meta['total_builds']} builds")
    print(f"  V1:  {meta['v1']['complete']} complete / {meta['v1']['dnf']} dnf / {meta['v1']['pending']} pending")
    print(f"  V2:  {meta['v2']['complete']} complete / {meta['v2']['dnf']} dnf / {meta['v2']['missing']} missing")
    print(f"  Human ratings: {meta['human_ratings_count']}")
    print(f"  Games: {len(meta['games'])}  Builders: {len(meta['builders'])}  Runs: {len(meta['runs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
