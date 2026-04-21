#!/usr/bin/env python3
"""Write a results.json skeleton for a game+run combination."""
import json, sys, os
from datetime import datetime

run = sys.argv[1]  # e.g. run1-opus-plan
game = sys.argv[2]  # e.g. pong
base = f"/Users/oscar/.openclaw/workspace/games/{run}/{game}"

task_ids = ["T01","T02","T03","T04","T05","T06","T07","T08","T09","T10","T11","T12"]

models = [
    {"id": "anthropic/claude-sonnet-4-6", "slug": "sonnet"},
    {"id": "anthropic/claude-opus-4-6", "slug": "opus"},
    {"id": "anthropic/claude-haiku-4-5", "slug": "haiku"},
    {"id": "openai/gpt-5.4", "slug": "gpt-5-4"},
    {"id": "openai/o3-mini", "slug": "o3-mini"},
]

builds = {}
for m in models:
    builds[m["slug"]] = {
        "model_id": m["id"],
        "slug": m["slug"],
        "status": "pending",
        "wall_clock_seconds": None,
        "tokens_input": None,
        "tokens_output": None,
        "estimated_cost_usd": None,
        "iterations": None,
        "errors_found": None,
        "errors_fixed": None,
        "task_checklist": {t: "pending" for t in task_ids},
        "last_completed_task": None,
        "first_failed_task": None,
        "qa_scores": {
            "functionality": None,
            "keyboard_controls": None,
            "visual_fidelity": None,
            "playability": None,
            "error_free": None,
            "final_score": None,
        }
    }

result = {
    "game": game,
    "run": run,
    "spec_generator": "anthropic/claude-opus-4-6" if "opus" in run else "openai/gpt-5.4",
    "created_at": datetime.utcnow().isoformat() + "Z",
    "qa_method": "static",
    "builds": builds,
    "delta_test": None
}

out_path = f"{base}/results.json"
os.makedirs(base, exist_ok=True)
with open(out_path, "w") as f:
    json.dump(result, f, indent=2)
print(f"Written: {out_path}")
