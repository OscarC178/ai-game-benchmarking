# Game Spec: Tetris

## 1. Overview
Tetris (Alexey Pajitnov, 1984) — the definitive puzzle game. Seven distinct tetrominoes fall from the top of a 10-wide grid. Rotate and position them to complete horizontal lines, which clear for points. Speed increases with level. Game ends when pieces stack to the top.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #111111
- Frame rate: 60 FPS
- Coordinate system: origin top-left
- Playfield: 10 columns × 20 rows, each cell 28×28px
- Playfield position: centered horizontally at x=240, y=10 (playfield is 280×560px)

## 3. Game Objects

### Playfield
- **Shape:** 10×20 cell grid with 1px #333333 grid lines
- **Size:** 280×560px
- **Background:** #000000
- **Border:** 2px #555555

### Tetrominoes (7 pieces)
Each is a set of 4 cells. Colors by type:
- **I:** #00FFFF (cyan) — horizontal 4×1
- **O:** #FFFF00 (yellow) — 2×2 square
- **T:** #AA00FF (purple) — T-shape
- **S:** #00FF00 (green) — S-skew
- **Z:** #FF0000 (red) — Z-skew
- **J:** #0000FF (blue) — J-shape
- **L:** #FF8800 (orange) — L-shape
- **Cell size:** 28×28px with 1px darker border for 3D effect
- **Starting position:** centered at top of playfield (column 3–4, row 0)

### Ghost Piece
- **Shape:** Same as current piece, projected to lowest valid position
- **Color:** Same as piece color at 30% opacity (#RRGGBB with alpha 0.3)

### Next Piece Preview
- **Position:** Right side panel at x=560, y=60
- **Label:** "NEXT" 14px #AAAAAA above the preview
- **Size:** 4×4 cell preview box (112×112px)

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Move piece left |
| ArrowRight / D | Move piece right |
| ArrowDown / S | Soft drop (accelerate fall) |
| ArrowUp / W | Rotate clockwise |
| Z | Rotate counter-clockwise |
| Space | Hard drop (instant place) |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Pieces spawn at top-center of the 10-wide grid. A random bag of all 7 pieces is shuffled; pieces are drawn in order (7-bag randomizer). When a bag empties, a new shuffled bag is generated.
2. Active piece falls 1 row per gravity tick. Gravity tick interval starts at 1000ms (level 1), decreases by 75ms per level (minimum 100ms).
3. ArrowLeft/Right moves piece 1 column. ArrowDown increases fall speed to 50ms/tick (soft drop). Space instantly drops to the ghost piece position (hard drop).
4. Rotate clockwise (ArrowUp) or counter-clockwise (Z). Use wall-kick: if rotation collides, try offsets (±1x, ±2x for I-piece) before rejecting.
5. When a piece lands (cannot fall further), lock it after 500ms delay (lock delay). Player can still move/rotate during lock delay. If piece moves down, lock delay resets (max 3 resets).
6. Completed horizontal lines (all 10 cells filled) are cleared simultaneously. Rows above drop down.
7. Scoring: 1 line = 100 × level, 2 lines = 300 × level, 3 lines = 500 × level, 4 lines (Tetris) = 800 × level. Soft drop: 1 point per cell. Hard drop: 2 points per cell dropped.
8. Level increases every 10 lines cleared.
9. Game over: new piece cannot spawn (top rows occupied).

## 6. Collision Detection

- Piece ↔ Playfield walls (x < 0 or x ≥ 10): block movement
- Piece ↔ Playfield floor (y ≥ 20): trigger landing/lock
- Piece ↔ Placed blocks (cell already occupied): block movement/rotation, trigger landing
- Rotation ↔ Walls/blocks: attempt wall-kick offsets before rejecting

Grid-based: check each of the 4 cells against the playfield array.

## 7. Scoring

- Starting score: 0
- Score display: right panel at x=560, y=200, "SCORE" label 14px #AAAAAA, value 20px #FFFFFF monospace
- Line clears: 100/300/500/800 × level for 1/2/3/4 lines
- Soft drop: 1 point per cell
- Hard drop: 2 points per cell
- Level display: right panel at x=560, y=280, "LEVEL" label + value
- Lines display: right panel at x=560, y=340, "LINES" label + total lines cleared
- High score: localStorage, right panel at x=560, y=420

## 8. UI Elements

- **Playfield:** centered with grid lines and border
- **Next piece:** right panel with labeled 4×4 preview box
- **Score/Level/Lines/High Score:** right panel, stacked vertically
- **Game Over screen:** #000000CC overlay over playfield. "GAME OVER" 36px white centered on playfield. Final score. "Press Enter to Restart."
- **Start screen:** "TETRIS" centered on playfield y=200, 48px #FFFFFF. Show all 7 piece shapes below in their colors. "Press Enter to Start" y=420 18px #AAAAAA.
- **Pause:** "PAUSED" centered on playfield, 36px white on #000000CC.

## 9. Audio (Optional / Bonus)
- Move/rotate: subtle 220Hz click, 20ms
- Line clear: ascending tone 440→880Hz, 150ms
- Tetris (4 lines): louder chord 200ms
- Hard drop: thud 110Hz, 60ms
- Game over: descending 440→55Hz, 500ms

## 10. Implementation Notes

1. Use the 7-bag randomizer (not pure random) — shuffle all 7 pieces, deal in order, reshuffle when empty.
2. Wall-kick on rotation: try offset (0,0), then (−1,0), (+1,0), (0,−1) for standard pieces. For I-piece also try (±2,0).
3. Ghost piece must update every frame to show where the piece would land — project piece downward until collision.
4. Lock delay (500ms) must be interruptible by movement — this prevents frustrating instant-locks at high speed.
5. Line clear should be visually distinct: flash the completed row white for 100ms before removing.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] All 7 tetromino types appear with correct shapes and colors
- [ ] Pieces move left/right, rotate with wall-kick, soft drop, hard drop
- [ ] Ghost piece shows landing position accurately
- [ ] Completed lines clear and rows above drop down
- [ ] Score increments correctly (line clears, soft/hard drop)
- [ ] Level increases every 10 lines, gravity speeds up
- [ ] Next piece preview shows correctly
- [ ] Game over when pieces stack to top
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, 800×600 canvas, inline style (#111111 bg, centered), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame at 60fps with delta-time. Separate gravity timer (starts 1000ms). Canvas clears to #111111 each frame. | Blank canvas renders; gravity timer accumulates |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Enter starts/restarts. P pauses. | State transitions work correctly |
| T04 | Playfield rendering | Draw 10×20 grid at (240,10) with 28×28px cells, #000000 fill, 1px #333333 grid lines, 2px #555555 border. | Playfield grid renders centered with visible lines |
| T05 | Tetromino definitions | Define all 7 piece types as arrays of 4 cell offsets. Define all 4 rotation states for each piece. Assign colors: I=#00FFFF, O=#FFFF00, T=#AA00FF, S=#00FF00, Z=#FF0000, J=#0000FF, L=#FF8800. | All 7 pieces can be printed to console with correct shapes |
| T06 | 7-bag randomizer & spawn | Implement 7-bag: shuffle all 7 types, deal in order, reshuffle when empty. Spawn piece at top-center (col 3–4, row 0). If spawn position is blocked → game over. | Pieces spawn in shuffled-bag order; no repeats within a bag |
| T07 | Piece movement & rotation | ArrowLeft/Right moves 1 column (with boundary/collision check). ArrowUp rotates clockwise, Z rotates CCW. Implement wall-kick: try offsets (0,0), (−1,0), (+1,0), (0,−1); I-piece also (±2,0). Reject rotation only if all offsets fail. | Pieces move/rotate correctly; wall-kick prevents stuck rotations |
| T08 | Gravity & drop | Piece falls 1 row per gravity tick. ArrowDown: soft drop at 50ms/tick (+1 pt/cell). Space: hard drop to ghost position (+2 pts/cell). Gravity interval = max(100, 1000 − 75 × (level−1)) ms. | Pieces fall at correct speed; soft/hard drop work; speed scales with level |
| T09 | Lock delay | When piece cannot fall further, start 500ms lock timer. Player can still move/rotate during lock. Movement down resets timer (max 3 resets). After timer expires, lock piece into playfield grid. | Piece locks after delay; can be repositioned during delay; max resets enforced |
| T10 | Ghost piece | Render a transparent (0.3 alpha) copy of current piece at its lowest valid position (projected straight down). Update every frame. | Ghost shows correct landing position for current piece |
| T11 | Line clearing | After locking, check all 20 rows. If row is fully filled (10 cells), flash white 100ms then clear. Drop all rows above down. Score: 100/300/500/800 × level for 1/2/3/4 lines. Increment total lines. Level up every 10 lines. | Lines clear correctly; multi-line scoring works; level advances |
| T12 | Next piece preview | Display next piece from bag in a 4×4 preview box at (560,60) with "NEXT" label. | Next piece shows and matches what actually spawns |
| T13 | Scoring & HUD | Right panel: SCORE at (560,200), LEVEL at (560,280), LINES at (560,340), HIGH SCORE at (560,420). All 14px #AAAAAA labels with #FFFFFF values. High score in localStorage. | All HUD elements display and update correctly |
| T14 | Start & Game Over screens | Start: "TETRIS" y=200 48px white centered on playfield, 7 piece shapes shown, "Press Enter" prompt. Game Over: #000000CC overlay, "GAME OVER" 36px, score, restart prompt. Enter restarts cleanly. | Screens show correctly; restart resets all state |
| T15 | Polish & debug | Fix remaining bugs. Ensure all acceptance criteria pass. Add metadata comment: `<!-- Tetris | spec:run1-opus-plan | built-by:{model} -->` | All section 11 criteria pass; comment header present |
