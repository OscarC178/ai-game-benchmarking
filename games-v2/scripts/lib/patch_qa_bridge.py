#!/usr/bin/env python3
"""
Injects a window.__qa state bridge into each Pac-Man game's main loop.
Safe to run multiple times — skips already-patched files.

Usage:
  python3 scripts/patch_qa_bridge.py                  # patch all pac-man games
  python3 scripts/patch_qa_bridge.py --dry-run        # preview only
"""

import re, sys, argparse
from pathlib import Path

GAMES_DIR = Path("/Users/oscar/.openclaw/workspace/games")
MARKER = "window.__qa ="

# Bridge template: inserted into main game loop, runs every frame in game's own scope.
# Variables probed defensively so any missing var just becomes null.
BRIDGE = """  // QA state bridge (auto-injected by patch_qa_bridge.py)
  try { window.__qa = {
    stateNum:  typeof state !== 'undefined' ? state : (typeof gameState !== 'undefined' ? gameState : (typeof game !== 'undefined' && game.state != null ? game.state : null)),
    pacX:      typeof pac   !== 'undefined' ? (pac.x  != null ? pac.x  : null) : null,
    pacY:      typeof pac   !== 'undefined' ? (pac.y  != null ? pac.y  : null) : null,
    pacDx:     typeof pac   !== 'undefined' ? (pac.dx != null ? pac.dx : null) : null,
    pacDy:     typeof pac   !== 'undefined' ? (pac.dy != null ? pac.dy : null) : null,
    pacNextDx: typeof pac   !== 'undefined' ? (pac.nextDx != null ? pac.nextDx : (pac.requestedDx != null ? pac.requestedDx : null)) : null,
    pacNextDy: typeof pac   !== 'undefined' ? (pac.nextDy != null ? pac.nextDy : (pac.requestedDy != null ? pac.requestedDy : null)) : null,
    marioX:    typeof mario !== 'undefined' ? (mario.x != null ? mario.x : null) : null,
    marioY:    typeof mario !== 'undefined' ? (mario.y != null ? mario.y : null) : null,
    marioVx:   typeof mario !== 'undefined' ? (mario.vx != null ? mario.vx : null) : null,
    marioVy:   typeof mario !== 'undefined' ? (mario.vy != null ? mario.vy : null) : null,
    score:     typeof score !== 'undefined' ? score : (typeof game !== 'undefined' && game.score != null ? game.score : null),
    lives:     typeof lives !== 'undefined' ? lives : (typeof game !== 'undefined' && game.lives != null ? game.lives : null),
    ts: Date.now(),
  }; } catch(e) { window.__qaErr = String(e); }
"""

def inject_after_raf(src: str, loop_name: str):
    """Find 'function <loop_name>(...)' and insert bridge after the first RAF call inside it."""
    # Match the loop function body
    fn_pat = re.compile(rf'function\s+{re.escape(loop_name)}\s*\([^)]*\)\s*\{{', re.MULTILINE)
    m = fn_pat.search(src)
    if not m:
        return None

    # Find the first requestAnimationFrame inside that function
    raf_pat = re.compile(r'requestAnimationFrame\([^)]+\);')
    raf_m = raf_pat.search(src, m.end())
    if not raf_m:
        return None

    # Insert bridge right after that RAF call + newline
    insert_pos = raf_m.end()
    # Check it's actually within the function (not another function)
    # Simple heuristic: must be within 3000 chars of the function open
    if insert_pos - m.start() > 5000:
        return None

    return src[:insert_pos] + "\n" + BRIDGE + src[insert_pos:]


def patch_file(path: Path, dry_run=False) -> str:
    src = path.read_text()

    if MARKER in src:
        return "already_patched"

    # Determine loop function name
    if "requestAnimationFrame(loop)" in src:
        loop_name = "loop"
    elif "requestAnimationFrame(gameLoop)" in src:
        loop_name = "gameLoop"
    elif "requestAnimationFrame(gameFrame)" in src:
        loop_name = "gameFrame"
    else:
        # Try to find any RAF call
        m = re.search(r'requestAnimationFrame\((\w+)\)', src)
        if m:
            loop_name = m.group(1)
        else:
            return "no_raf_found"

    patched = inject_after_raf(src, loop_name)
    if patched is None:
        # Fallback: inject at top of the RAF callback if loop is inline
        # Try to find "function loop(" anywhere
        return f"inject_failed (loop={loop_name})"

    if dry_run:
        print(f"  [DRY] Would patch: {path.relative_to(GAMES_DIR)} (loop={loop_name})")
        return "dry_run"

    path.write_text(patched)
    return f"patched (loop={loop_name})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--game", default="pac-man", help="Game subfolder name")
    args = ap.parse_args()

    targets = sorted(GAMES_DIR.glob(f"*/{ args.game}/*/index.html"))
    print(f"Found {len(targets)} {args.game} builds\n")

    results = {"patched": [], "already_patched": [], "failed": []}
    for t in targets:
        run = t.parts[-4]
        model = t.parts[-2]
        status = patch_file(t, dry_run=args.dry_run)
        tag = "✅" if "patched" in status else ("⏭️ " if "already" in status else "❌")
        print(f"  {tag}  {run}/{model}: {status}")
        if "patched" in status:
            results["patched"].append(f"{run}/{model}")
        elif "already" in status:
            results["already_patched"].append(f"{run}/{model}")
        else:
            results["failed"].append(f"{run}/{model}: {status}")

    print(f"\n✅ Patched:  {len(results['patched'])}")
    print(f"⏭️  Skipped: {len(results['already_patched'])}")
    print(f"❌ Failed:  {len(results['failed'])}")
    if results["failed"]:
        for f in results["failed"]:
            print(f"   {f}")

if __name__ == "__main__":
    main()
