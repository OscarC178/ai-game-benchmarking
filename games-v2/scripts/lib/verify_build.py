#!/usr/bin/env python3
"""
verify_build.py — Artefact verification for benchmark V2.
Trust files, not model self-reports.

Usage: python3 verify_build.py <path>
Exit codes: 0=ok, 1=failed
Prints: "ok" or failure reason
"""
import sys
import os

def verify_build(path):
    if not os.path.exists(path):
        return "missing"
    size = os.path.getsize(path)
    if size < 500:
        return f"too_small ({size} bytes)"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return f"read_error ({e})"
    if "<canvas" not in content.lower():
        return "no_canvas"
    if "requestAnimationFrame" not in content:
        return "no_gameloop"
    if "</html>" not in content.lower():
        return "incomplete_html"
    return "ok"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: verify_build.py <path>", file=sys.stderr)
        sys.exit(1)
    result = verify_build(sys.argv[1])
    print(result)
    sys.exit(0 if result == "ok" else 1)
