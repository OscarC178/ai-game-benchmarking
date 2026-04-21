#!/usr/bin/env python3
"""Parse builder output and update results.json with actual metrics."""
import json, sys, re, os

run = sys.argv[1]     # e.g. run1-opus-plan
game = sys.argv[2]    # e.g. pong
model_slug = sys.argv[3]  # e.g. sonnet
output_file = sys.argv[4]  # path to agent output text file

results_path = f"/Users/oscar/.openclaw/workspace/games/{run}/{game}/results.json"

with open(output_file, "r") as f:
    content = f.read()

# Look for JSON_RESULT line
json_result = None
for line in content.split("\n"):
    line = line.strip()
    if line.startswith("JSON_RESULT:"):
        try:
            json_result = json.loads(line[len("JSON_RESULT:"):])
            break
        except:
            pass

# Load existing results
with open(results_path, "r") as f:
    results = json.load(f)

# Check if index.html was written
html_path = f"/Users/oscar/.openclaw/workspace/games/{run}/{game}/{model_slug}/index.html"
html_exists = os.path.exists(html_path)
html_size = os.path.getsize(html_path) if html_exists else 0

if json_result:
    # Update with reported data
    build = results["builds"][model_slug]
    build["status"] = json_result.get("status", "complete" if html_exists else "failed")
    build["wall_clock_seconds"] = json_result.get("wall_clock_seconds", 0)
    build["tokens_input"] = json_result.get("tokens_input", 0)
    build["tokens_output"] = json_result.get("tokens_output", 0)
    build["estimated_cost_usd"] = json_result.get("estimated_cost_usd", 0)
    build["iterations"] = json_result.get("iterations", 0)
    build["errors_found"] = json_result.get("errors_found", 0)
    build["errors_fixed"] = json_result.get("errors_fixed", 0)
    build["task_checklist"] = json_result.get("task_checklist", build["task_checklist"])
    build["last_completed_task"] = json_result.get("last_completed_task")
    build["first_failed_task"] = json_result.get("first_failed_task")
    build["html_size_bytes"] = html_size
    print(f"Updated {model_slug}: status={build['status']}, last_task={build['last_completed_task']}")
elif html_exists:
    # HTML was written but no JSON summary found — partial success
    results["builds"][model_slug]["status"] = "complete_no_summary"
    results["builds"][model_slug]["html_size_bytes"] = html_size
    print(f"Updated {model_slug}: html exists ({html_size}B) but no JSON summary")
else:
    # Nothing worked
    results["builds"][model_slug]["status"] = "failed"
    print(f"Updated {model_slug}: FAILED (no html, no JSON summary)")

with open(results_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"Saved: {results_path}")
