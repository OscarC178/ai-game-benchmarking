# Game Spec: Tetris

## 1. Overview
Tetris — a falling-block puzzle game defined by precise grid logic, complete line clears, escalating gravity, and the constant pressure of stack management. It feels authentic when piece behavior is consistent, the playfield is readable, the next piece is visible, and movement/rotation remain reliable even under speed.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #111111
- Frame rate: 60 FPS
- Coordinate system: origin top-left

## 3. Game Objects

### Playfield
- **Shape/Sprite:** 10×20 rectangular well with bordered grid
- **Size:** 280×560px using 28×28px cells
- **Color:** fill #000000, border #555555, grid lines #333333
- **Starting position:** x=240, y=20
- **Movement:** static

### Tetrominoes
- **Shape/Sprite:** Standard I, O, T, S, Z, J, L block arrangements
- **Size:** each block cell is 28×28px
- **Color:** I #00FFFF, O #FFFF00, T #AA00FF, S #00FF00, Z #FF0000, J #0000FF, L #FF8800
- **Starting position:** spawn centered at top of well
- **Movement:** fall downward under gravity; player may move, rotate, soft drop, and hard drop

### Ghost Piece
- **Shape/Sprite:** translucent projection of active tetromino
- **Size:** matches active piece footprint
- **Color:** active piece color at about 30% opacity
- **Starting position:** directly below active piece at landing row
- **Movement:** updates continuously with active piece state

### Next Preview Box
- **Shape/Sprite:** outlined preview panel
- **Size:** 112×112px
- **Color:** border #555555, text #AAAAAA
- **Starting position:** x=560, y=60
- **Movement:** static

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Move piece left |
| ArrowRight / D | Move piece right |
| ArrowUp / W | Rotate clockwise |
| ArrowDown / S | Soft drop |
| Space | Hard drop |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Pieces are drawn from a 7-bag randomizer.
2. Gravity starts at 1000ms per row.
3. Level increases every 10 cleared lines.
4. Gravity decreases by 75ms per level to a 100ms minimum.
5. Single, double, triple, and Tetris line clears score 100, 300, 500, and 800 times the current level.
6. Soft drop awards 1 point per descended cell.
7. Hard drop awards 2 points per descended cell.
8. When a piece lands, a 500ms lock delay begins.
9. Up to 3 successful grounded moves/rotations may reset lock delay.
10. Game over occurs if a new piece cannot spawn legally.

## 6. Collision Detection

- Active Piece ↔ Walls: block movement or rotation
- Active Piece ↔ Floor: start grounded/lock logic
- Active Piece ↔ Placed Blocks: block movement or rotation
- Completed Rows ↔ Board: clear full lines and drop rows above

Use grid-cell collision checks for all piece logic.

## 7. Scoring

- Starting score: 0
- Score display: right panel, white text, 20px monospace values with 14px #AAAAAA labels
- Single line clear: +100 × level
- Double line clear: +300 × level
- Triple line clear: +500 × level
- Four-line clear: +800 × level
- Soft drop: +1 per cell
- Hard drop: +2 per cell
- High score: stored in localStorage, display in right panel

## 8. UI Elements

- **Score:** right panel
- **Lives / Health:** not applicable
- **Level indicator:** right panel with current level and lines cleared
- **Game Over screen:** centered text “GAME OVER”, score, “Press Enter to restart”
- **Start screen:** “TETRIS” centered over the well, seven-piece preview art, “Press Enter to Start”
- **Pause:** P key toggles pause overlay

## 9. Audio (Optional / Bonus)
- Move/rotate: short 220Hz click
- Line clear: ascending 440→880Hz tone
- Hard drop: low thud
- Game over: descending tone sequence

## 10. Implementation Notes

1. The 7-bag randomizer must guarantee one of each piece before reshuffling.
2. Rotation should include practical wall-kick attempts so pieces work near walls and stacks.
3. Ghost piece must update continuously and match the actual landing row.
4. Lock delay behavior is a common failure point and should not be skipped.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] All seven pieces spawn and render in correct colors
- [ ] Move, rotate, soft drop, and hard drop work correctly
- [ ] Ghost piece shows the correct landing position
- [ ] Line clears score correctly and advance level timing
- [ ] Score increments correctly
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

**THIS IS THE BUILDER'S WORK ORDER. Complete tasks in sequence. Do not skip ahead.**
**After completing each task, verify it works before moving to the next.**
**Mark each task complete in your output JSON (see results.json schema).**

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, canvas element, inline style (black bg), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame loop with delta-time tracking. Canvas clears each frame. | Console shows no errors; blank canvas renders at 60fps |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Enter key starts game. | State transitions logged to console |
| T04 | Player object | Draw player shape on canvas. Implement keyboard controls (per spec section 4). | Player visible, moves correctly, stays within bounds |
| T05 | Playfield and tetromino set | Build the 10×20 well at x=240, y=20 and define all seven tetrominoes with correct colors, spawn positions, and a 7-bag randomizer. | The well renders cleanly and all seven pieces appear with correct coloring over time |
| T06 | Movement, rotation, and ghost piece | Add horizontal movement, clockwise rotation, soft drop, hard drop, wall-kick handling, and a continuously updating ghost piece. | Pieces move and rotate reliably, and the ghost piece matches the true landing row |
| T07 | Locking and line clearing | Implement grounded lock delay with reset allowance, detect complete rows, flash and clear them, then collapse rows above. | Landed pieces do not lock instantly and full lines clear correctly |
| T08 | Level and gravity scaling | Track cleared lines, increase level every 10 lines, and reduce gravity interval down to the specified minimum. | The game speeds up as levels increase and line totals remain accurate |
| T09 | Collision detection | Implement all collision pairs from spec section 6. AABB unless spec says otherwise. | Collisions trigger correct outcomes (log to console if needed) |
| T10 | Scoring | Implement score counter. Render score top-left, high score top-right (localStorage). | Score increments on correct events; persists on reload |
| T11 | Lives / health | Render lives/health indicator top-right per spec section 8. Decrement on hit. | Lives display correctly; game over triggers at 0 |
| T12 | Game Over screen | Render GAME OVER overlay with final score. Enter key restarts. | Overlay appears; restart resets all state |
| T13 | Start screen | Render title screen with game name and "Press Enter to Start". | Appears on load before game begins |
| T14 | Polish & debug | Fix any remaining bugs. Ensure all acceptance criteria from section 11 pass. Add the metadata comment header. | All section 11 criteria pass; comment header present |
