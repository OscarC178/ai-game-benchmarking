#!/usr/bin/env python3
"""
Merge Tally form responses into review/ratings.json.

Usage:
    python3 scripts/merge_tally_ratings.py path/to/tally-export.csv

How to get the CSV:
  1. In Tally → your form → Responses tab → Export → CSV
  2. Save it somewhere locally
  3. Run this script, passing the file path

The script:
  - Reads the CSV row-by-row
  - Normalises each response to the ratings.json schema (runs / mechanics /
    completable / fun / visual / flags / notes / timestamp)
  - Looks up the build_id (must be a hidden pre-filled field in your form)
  - Merges into review/ratings.json, preferring the newer rating on conflict
  - Prints a summary of what was added / updated / skipped
  - Does NOT automatically push; inspect the diff, then git commit + push if happy

Expected Tally form columns (rename your form fields to match, or edit
FIELD_MAP below if you've used different labels):
  build_id              — hidden, pre-filled from the URL
  runs                  — yes / no
  mechanics             — 1-5
  completable           — 1-5
  fun                   — 1-5
  visual                — 1-5
  flags                 — comma-separated list of tags (crashes, unwinnable, ...)
  notes                 — free text
  Submitted at          — timestamp (Tally adds this automatically)

Missing or malformed rows are printed with a reason and skipped.
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent
RATINGS_FILE = WORKSPACE / "review" / "ratings.json"

# Map Tally CSV column headers → canonical field names.
# Edit this if your form uses different labels.
FIELD_MAP = {
    "build_id":     ["build_id", "Build ID"],
    "runs":         ["runs", "Runs?", "Does it run?"],
    "mechanics":    ["mechanics", "Mechanics"],
    "completable":  ["completable", "Completable"],
    "fun":          ["fun", "Fun"],
    "visual":       ["visual", "Visual"],
    "flags":        ["flags", "Flags"],
    "notes":        ["notes", "Notes"],
    "submitted_at": ["Submitted at", "submitted_at", "timestamp"],
    "email":        ["email", "Email"],  # optional
}


def lookup(row, key):
    """Find the first matching column from FIELD_MAP aliases."""
    for alias in FIELD_MAP.get(key, [key]):
        if alias in row and row[alias] not in ("", None):
            return row[alias].strip()
    return None


def coerce_int(val):
    if val is None or val == "":
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def normalise_flags(raw):
    if not raw:
        return []
    # Tally multi-select comes back as comma-separated or newline-separated
    parts = [p.strip().lower().replace(" ", "-") for p in raw.replace("\n", ",").split(",")]
    return [p for p in parts if p]


def parse_timestamp(raw):
    if not raw:
        return datetime.now(timezone.utc).isoformat()
    # Tally formats vary — try a couple
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    return raw  # pass through whatever it is


def normalise_row(row):
    build_id = lookup(row, "build_id")
    if not build_id:
        return None, "no build_id"
    return {
        "build_id": build_id,
        "rating": {
            "runs":        (lookup(row, "runs") or "").lower() or None,
            "mechanics":   coerce_int(lookup(row, "mechanics")),
            "completable": coerce_int(lookup(row, "completable")),
            "fun":         coerce_int(lookup(row, "fun")),
            "visual":      coerce_int(lookup(row, "visual")),
            "flags":       normalise_flags(lookup(row, "flags")),
            "notes":       (lookup(row, "notes") or "").strip(),
            "timestamp":   parse_timestamp(lookup(row, "submitted_at")),
            "source":      "crowd",
            "email":       lookup(row, "email"),  # optional — remove if you don't want emails in ratings.json
        }
    }, None


def main(csv_path):
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"ERROR: {csv_path} not found", file=sys.stderr)
        return 1

    # Load existing ratings
    existing = json.loads(RATINGS_FILE.read_text()) if RATINGS_FILE.exists() else {}
    existing_keys = set(existing.keys())

    added, updated, skipped = 0, 0, 0
    reasons = {}

    with csv_file.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            parsed, reason = normalise_row(row)
            if parsed is None:
                skipped += 1
                reasons[reason] = reasons.get(reason, 0) + 1
                continue

            bid = parsed["build_id"]
            new_rating = parsed["rating"]

            if bid in existing:
                # Keep newer timestamp
                existing_ts = existing[bid].get("timestamp", "")
                if new_rating["timestamp"] > existing_ts:
                    existing[bid] = new_rating
                    updated += 1
                else:
                    skipped += 1
                    reasons["older than existing"] = reasons.get("older than existing", 0) + 1
            else:
                existing[bid] = new_rating
                added += 1

    # Write back
    RATINGS_FILE.write_text(json.dumps(existing, indent=2, sort_keys=True))

    print(f"Merged {csv_path} → {RATINGS_FILE}")
    print(f"  added:   {added}")
    print(f"  updated: {updated}")
    print(f"  skipped: {skipped}")
    if reasons:
        for r, n in reasons.items():
            print(f"           · {r}: {n}")
    print(f"  total ratings now: {len(existing)} (was {len(existing_keys)})")
    print()
    print("Next: re-run the aggregator so guide/data.json picks up the changes:")
    print("    python3 guide/aggregate.py")
    print("Then commit + push to trigger a Vercel redeploy:")
    print("    git add review/ratings.json guide/data.json")
    print("    git commit -m 'Merge crowd ratings batch'")
    print("    git push")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/merge_tally_ratings.py path/to/tally-export.csv", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
