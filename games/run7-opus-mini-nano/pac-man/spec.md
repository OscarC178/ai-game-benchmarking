# Game Spec: Pac-Man

## 1. Overview
Pac-Man (Namco, 1980) — the iconic maze-chase game. Navigate a yellow circle through a maze eating dots while avoiding four distinctly-behaved ghosts. Eat a power pellet to turn the tables and chase the ghosts. The maze, ghost AI personalities, and tunnel wrapping are essential to the authentic feel.

## 2. Canvas & Rendering
- Canvas size: 700×780px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left
- Maze grid: 28 columns × 31 rows, each cell 24×24px
- Maze offset: x=14, y=30 (centered with padding for score/lives UI)

## 3. Game Objects

### Pac-Man
- **Shape:** Circle with animated mouth (opening/closing wedge, 45° per frame at 10Hz)
- **Size:** 20px diameter (10px radius)
- **Color:** #FFFF00
- **Starting position:** Column 14, Row 23 (grid center-bottom area), x=350, y=582
- **Movement:** 120px/s, grid-aligned with cornering assist (can input next direction up to 4px before a turn). Mouth faces movement direction.

### Ghosts (4)
Each ghost is a 20×20px shape: semicircle top + wavy bottom edge (3 bumps). Each has unique color and AI:
- **Blinky (Red):** #FF0000. Start position: center box. Chase mode: targets Pac-Man's current tile.
- **Pinky (Pink):** #FFB8FF. Start position: inside ghost house. Chase mode: targets 4 tiles ahead of Pac-Man's facing direction.
- **Inky (Cyan):** #00FFFF. Start position: inside ghost house. Chase mode: uses vector from Blinky to 2 tiles ahead of Pac-Man, doubled.
- **Clyde (Orange):** #FFB852. Start position: inside ghost house. Chase mode: targets Pac-Man when >8 tiles away; targets scatter corner when ≤8 tiles.
- **Speed:** Normal 110px/s, frightened 60px/s, eaten (eyes only) 200px/s.

### Ghost House
- **Position:** Center of maze, rows 12–15, columns 11–16
- **Gate:** Top-center of house at row 12, columns 13–14 (ghosts exit here)
- **Color:** Gate is #FFB8FF (thin horizontal bar)

### Dots (Pellets)
- **Small dot:** 4×4px circle, #FFCC99
- **Count:** 240 small dots placed at every valid maze corridor intersection
- **Layout:** Dots fill all walkable corridors except the ghost house and tunnels

### Power Pellets (4)
- **Size:** 10×10px circle, blinking at 4Hz
- **Color:** #FFCC99
- **Positions:** Four corners of the maze — (1,3), (26,3), (1,23), (26,23) in grid coords

### Maze Walls
- **Color:** #2121DE (classic blue)
- **Line width:** 2px
- **Layout:** Classic Pac-Man maze layout. Define as a 28×31 grid where each cell is wall (1) or path (0). Use the standard Pac-Man maze topology with the center ghost house, two side tunnels, and characteristic T-junctions.

### Tunnel
- **Position:** Row 14, columns 0 and 27 (left and right edges)
- **Behavior:** Pac-Man and ghosts entering one side exit the other. Movement slows to 60% in the tunnel.

### Fruit Bonus
- **Shape:** Circle 16×16px
- **Color:** #FF0000 (cherry for level 1)
- **Position:** Below ghost house at column 14, row 17 (x=350, y=438)
- **Appears:** When 70 dots eaten and when 170 dots eaten. Disappears after 10 seconds if not collected.

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowUp / W | Move up |
| ArrowDown / S | Move down |
| ArrowLeft / A | Move left |
| ArrowRight / D | Move right |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Pac-Man moves continuously in the current direction until hitting a wall. Player inputs queue the next direction, which executes when a valid turn is available (cornering tolerance: ±4px from cell center).
2. Eating a small dot: +10 points. Eating a power pellet: +50 points, ghosts enter Frightened mode for 8 seconds (6s at level 2, 4s at level 3+).
3. Frightened ghosts turn blue (#2121FF) and reverse direction immediately. They move randomly at intersections. Eating frightened ghosts in sequence: 200, 400, 800, 1600 points. Eaten ghosts become eyes-only and return to the ghost house at 200px/s, then respawn.
4. Ghost modes cycle: Scatter (7s) → Chase (20s) → Scatter (7s) → Chase (20s) → Scatter (5s) → Chase (20s) → Scatter (5s) → Chase (indefinite). Frightened mode interrupts and resumes the timer after.
5. Scatter targets (corners): Blinky → top-right, Pinky → top-left, Inky → bottom-right, Clyde → bottom-left.
6. Ghosts cannot reverse direction except when mode changes (scatter↔chase transitions and entering frightened).
7. Ghost house release: Blinky starts outside. Pinky exits after 0s, Inky after 30 dots eaten, Clyde after 60 dots eaten.
8. Clearing all 244 dots (240 small + 4 power) completes the level. Next level: ghosts move 5% faster, frightened time decreases.
9. Player starts with 3 lives. Contact with a non-frightened ghost = death.
10. Extra life at 10,000 points.
11. Game over at 0 lives.

## 6. Collision Detection

- Pac-Man ↔ Dot (same tile): eat dot, remove from maze
- Pac-Man ↔ Power Pellet (same tile): eat, trigger Frightened mode
- Pac-Man ↔ Ghost (normal/chase/scatter): Pac-Man dies
- Pac-Man ↔ Ghost (frightened): eat ghost, +200/400/800/1600 cascade
- Pac-Man ↔ Fruit: eat fruit, bonus points
- Pac-Man ↔ Wall: stop movement
- Ghost ↔ Wall: cannot enter (pathfinding avoids walls)

Tile-based collision (check if two objects occupy the same grid tile).

## 7. Scoring

- Starting score: 0
- Score display: top-left at (14, 22), #FFFFFF, 16px monospace
- Small dot: 10 points
- Power pellet: 50 points
- Frightened ghost sequence: 200 → 400 → 800 → 1600 (resets per power pellet)
- Fruit (level 1 cherry): 100 points
- Extra life: at 10,000 points
- High score: localStorage, top-right

## 8. UI Elements

- **Score:** top-left "Score: {N}" 16px white monospace
- **High Score:** top-right "Best: {N}" 16px
- **Lives:** bottom-left below maze, Pac-Man icons (14px yellow circles) plus "×{N}"
- **Level:** bottom-right "Level: {N}" 14px #AAAAAA
- **"READY!" text:** Displayed in #FFFF00 centered below ghost house for 2s at level start
- **Game Over screen:** "GAME OVER" in #FF0000, centered in the maze area, 32px. Score and "Press Enter to Restart" below.
- **Start screen:** "PAC-MAN" centered y=300, 52px #FFFF00 monospace. Show ghost characters with names and colors below. "Press Enter to Start" y=500, 20px #AAAAAA.
- **Pause:** "PAUSED" centered 36px white on #000000CC overlay.

## 9. Audio (Optional / Bonus)
- Waka-waka: alternating 440Hz/330Hz, 40ms each, while eating dots
- Power pellet: low 110Hz pulsing while ghosts are frightened
- Eat ghost: ascending 440→1320Hz, 100ms
- Death: descending spiral tone, 500ms
- Level start: short jingle (ascending scale 300ms)

## 10. Implementation Notes

1. **Ghost AI is the hardest part.** Each ghost must use distinct targeting logic in Chase mode. At each intersection, a ghost picks the direction that minimizes Euclidean distance to its target tile (never reversing except on mode change). Simplify if needed but all 4 must behave differently.
2. **Maze definition:** Encode the 28×31 grid as a 2D array. Use constants: 0=path, 1=wall, 2=dot, 3=power pellet, 4=ghost house, 5=gate, 6=tunnel. Draw walls by checking adjacency and rendering 2px #2121DE lines on wall-cell borders facing path-cells.
3. **Cornering assist** is critical for playability — without it, turning feels broken. Allow direction input to "pre-buffer" and execute when Pac-Man is within 4px of the next intersection center.
4. **Frightened ghost timer:** ghosts flash white/blue alternating at 4Hz during the last 2 seconds of frightened mode as a warning.
5. Tunnel slows all entities to 60% speed while inside (columns 0–3 and 24–27).

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Pac-Man moves through maze, stops at walls, turns at intersections
- [ ] Cornering assist makes turning feel responsive
- [ ] Dots and power pellets are eaten on contact
- [ ] Four ghosts have visually distinct colors and AI behaviors
- [ ] Power pellet makes ghosts frightened (blue, edible)
- [ ] Eating frightened ghosts gives escalating points (200–1600)
- [ ] Ghost modes cycle between scatter and chase
- [ ] Tunnel wrapping works for Pac-Man and ghosts
- [ ] Level completes when all 244 dots eaten
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, 700×780 canvas, inline style (black bg, centered), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame loop with delta-time. Canvas clears to #000000 each frame. | Blank canvas renders at 60fps |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Sub-states: READY (2s countdown), DYING (death animation). Enter starts/restarts. P pauses. | State transitions work correctly |
| T04 | Maze rendering | Define 28×31 grid array encoding walls, paths, dots, power pellets, ghost house, gate, tunnel. Render walls as 2px #2121DE lines on wall-cell borders. Render small dots as 4px #FFCC99 circles at path centers. Render 4 power pellets as 10px blinking circles at corner positions. Maze offset at (14,30). | Maze renders recognizably; dots and power pellets visible |
| T05 | Pac-Man movement | Draw 20px yellow circle with animated mouth (wedge opening/closing at 10Hz, facing movement direction). Move at 120px/s, grid-aligned. Stop at walls. Queue next direction input. Cornering assist: allow turn when within 4px of intersection center. Tunnel wrap at row 14 columns 0↔27. | Pac-Man moves smoothly, turns at intersections, wraps through tunnel |
| T06 | Dot eating | When Pac-Man's tile contains a dot, remove it (set grid cell to 0). +10 per small dot, +50 per power pellet. Track total dots eaten (244 total). | Dots disappear on contact; score increments; dot count tracks |
| T07 | Ghost rendering & house | Draw 4 ghosts as 20×20px shapes (semicircle + wavy bottom) in their colors: Blinky #FF0000, Pinky #FFB8FF, Inky #00FFFF, Clyde #FFB852. Draw eyes (white sclera + blue pupil pointing in movement direction). Render ghost house gate as #FFB8FF bar. Blinky starts outside house; others inside. Ghosts exit house upward through gate. Release order: Pinky immediately, Inky after 30 dots, Clyde after 60 dots. | 4 colored ghosts visible; exit house in correct order |
| T08 | Ghost AI — scatter & chase | Implement mode cycling: Scatter(7s)→Chase(20s)→Scatter(7s)→Chase(20s)→Scatter(5s)→Chase(20s)→Scatter(5s)→Chase(∞). In Scatter: each ghost targets its corner (Blinky top-right, Pinky top-left, Inky bottom-right, Clyde bottom-left). In Chase: Blinky targets Pac-Man tile; Pinky targets 4 tiles ahead; Inky uses Blinky-vector method; Clyde targets Pac-Man if >8 tiles away, else scatter corner. At intersections, choose direction minimizing Euclidean distance to target (never reverse). | Ghosts switch modes on timer; each ghost exhibits distinct behavior |
| T09 | Frightened mode | On power pellet eat: all ghosts enter Frightened for 8s (6s level 2, 4s level 3+). Ghosts turn #2121FF, reverse direction, move randomly at 60px/s. Last 2s: flash white/blue at 4Hz. Eating frightened ghost: 200→400→800→1600 cascade (reset per pellet). Eaten ghost becomes eyes-only (#FFFFFF sclera, blue pupil) returning to house at 200px/s, then respawns normal. | Power pellet triggers blue ghosts; eating gives escalating score; eyes return to house |
| T10 | Player death | Non-frightened ghost on Pac-Man tile = death. Play death animation (Pac-Man shrinks/deflates over 1s). Decrement life. Respawn all positions after 1.5s. At 0 lives → GAME_OVER. | Death animation plays; respawn works; game over at 0 lives |
| T11 | Fruit & level progression | Spawn fruit (#FF0000 16px circle) at (col 14, row 17) when 70 and 170 dots eaten. Disappears after 10s. +100 points. Level complete when all 244 dots eaten. Next level: reset maze dots, ghosts +5% speed, frightened time −2s (min 2s). | Fruit appears and scores; level advances on clear |
| T12 | Scoring & HUD | "Score: {N}" top-left 16px. "Best: {N}" top-right (localStorage). Lives as Pac-Man icons bottom-left. "Level: {N}" bottom-right. Extra life at 10,000 pts. "READY!" in #FFFF00 below ghost house for 2s at level start. | All HUD elements display correctly |
| T13 | Start & Game Over screens | Start: "PAC-MAN" y=300 52px #FFFF00, ghost legend with colors/names, "Press Enter" y=500. Game Over: "GAME OVER" #FF0000 32px centered in maze, score, restart prompt. | Screens display correctly; restart resets all state |
| T14 | Polish & debug | Fix remaining bugs. Ensure all acceptance criteria pass. Add metadata comment: `<!-- Pac-Man | spec:run1-opus-plan | built-by:{model} -->` | All section 11 criteria pass; comment header present |
