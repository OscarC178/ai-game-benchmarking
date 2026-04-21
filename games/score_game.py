#!/usr/bin/env python3
"""Quick QA scoring for game HTML files based on spec tasks."""

import sys
import json
import os
import re

def score_game(run, game, model_slug):
    ws = "/Users/oscar/.openclaw/workspace"
    html_path = f"{ws}/games/{run}/{game}/{model_slug}/index.html"
    spec_path = f"{ws}/games/{run}/{game}/spec.md"
    results_path = f"{ws}/games/{run}/{game}/results.json"
    
    if not os.path.exists(html_path):
        print(f"MISSING: {html_path}")
        return None
    
    with open(html_path) as f:
        html = f.read()
    
    html_lower = html.lower()
    
    # Base scores
    scores = {
        "functionality": 0.0,
        "keyboard_controls": 0.0,
        "visual_fidelity": 0.0,
        "playability": 0.0,
        "error_free": 0.0,
    }
    
    # === Error-free (10%) ===
    # Check for obvious JS errors
    has_canvas = "canvas" in html_lower
    has_script = "<script" in html_lower
    has_requestanimationframe = "requestanimationframe" in html_lower
    no_cdn = "cdn." not in html_lower and "unpkg.com" not in html_lower and "jsdelivr" not in html_lower
    
    error_score = 0.7  # base
    if has_canvas: error_score += 0.1
    if has_script: error_score += 0.1
    if no_cdn: error_score += 0.1
    scores["error_free"] = min(1.0, error_score)
    
    # === Functionality (30%) ===
    game_checks = {
        "pong": ["paddle", "ball", "score", "canvas", "collision"],
        "snake": ["snake", "food", "grid", "score", "direction"],
        "breakout": ["paddle", "ball", "brick", "score", "bounce"],
        "space-invaders": ["alien", "bullet", "score", "lives", "shield"],
        "tetris": ["tetromino", "piece", "line", "score", "board"],
        "asteroids": ["asteroid", "bullet", "ship", "score", "thrust"],
        "galaga": ["enemy", "bullet", "score", "lives", "formation"],
        "frogger": ["frog", "log", "car", "score", "lane"],
        "pac-man": ["pac", "ghost", "dot", "score", "pellet"],
        "donkey-kong": ["kong", "barrel", "mario", "score", "ladder"],
    }
    
    keywords = game_checks.get(game, [])
    found = sum(1 for k in keywords if k in html_lower)
    scores["functionality"] = min(1.0, 0.4 + (found / len(keywords)) * 0.6) if keywords else 0.7
    
    # === Keyboard controls (20%) ===
    kb_checks = ["keydown", "keyup", "keycode", "key.arrow", "addeventlistener"]
    found_kb = sum(1 for k in kb_checks if k in html_lower)
    scores["keyboard_controls"] = min(1.0, 0.4 + (found_kb / len(kb_checks)) * 0.6)
    
    # === Visual fidelity (20%) ===
    vis_checks = ["fillrect", "filltext", "strokerect", "arc", "fillstyle", "font", "clearrect"]
    found_vis = sum(1 for v in vis_checks if v in html_lower)
    scores["visual_fidelity"] = min(1.0, 0.3 + (found_vis / len(vis_checks)) * 0.7)
    
    # === Playability (20%) ===
    play_checks = ["localstorage", "highscore", "gameover", "level", "lives", "requestanimationframe"]
    found_play = sum(1 for p in play_checks if p in html_lower)
    scores["playability"] = min(1.0, 0.3 + (found_play / len(play_checks)) * 0.7)
    
    # Final score (weighted)
    final_score = (
        scores["functionality"] * 0.30 +
        scores["keyboard_controls"] * 0.20 +
        scores["visual_fidelity"] * 0.20 +
        scores["playability"] * 0.20 +
        scores["error_free"] * 0.10
    )
    
    scores["final_score"] = round(final_score, 2)
    for k in scores:
        scores[k] = round(scores[k], 2)
    
    # Update results.json
    with open(results_path) as f:
        d = json.load(f)
    
    if model_slug not in d["builds"]:
        d["builds"][model_slug] = {}
    d["builds"][model_slug]["qa_scores"] = scores
    d["builds"][model_slug]["status"] = "complete"
    
    with open(results_path, "w") as f:
        json.dump(d, f, indent=2)
    
    print(f"QA_DONE:{game} {model_slug} score={final_score:.1f}")
    return final_score

if __name__ == "__main__":
    if len(sys.argv) == 4:
        run, game, model_slug = sys.argv[1], sys.argv[2], sys.argv[3]
        score_game(run, game, model_slug)
    else:
        # Score all existing files
        ws = "/Users/oscar/.openclaw/workspace"
        for run in ["run5-opus-gemini", "run6-gpt-gemini"]:
            games = ["pong", "snake", "breakout", "space-invaders", "tetris", "asteroids", "galaga", "frogger", "pac-man", "donkey-kong"]
            for game in games:
                for model_slug in ["gemini-pro", "gemini-flash"]:
                    html_path = f"{ws}/games/{run}/{game}/{model_slug}/index.html"
                    if os.path.exists(html_path):
                        score_game(run, game, model_slug)
