# Game Spec: Snake

## 1. Overview
Snake (late 1970s, popularized by Nokia in the 1990s) — guide a growing snake to eat food without hitting yourself or the walls. Grid-based movement with a retro chunky-pixel feel. Single-player, ever-increasing difficulty via snake length.

## 2. Canvas & Rendering
- Canvas size: 600×600px
- Background color: #111111
- Frame rate: 60 FPS (game logic ticks at a separate rate, starting 8 ticks/s)
- Coordinate system: origin top-left
- Grid: 20×20 cells, each cell 30×30px

## 3. Game Objects

### Snake Head
- **Shape:** Filled square (1 grid cell)
- **Size:** 28×28px (2px inset from cell edges for grid visibility)
- **Color:** #4CAF50
- **Starting position:** grid (10, 10) — center of grid
- **Movement:** 1 cell per tick in current direction (up/down/left/right), starting direction: right

### Snake Body Segments
- **Shape:** Filled square per segment
- **Size:** 28×28px
- **Color:** #388E3C (slightly darker than head)
- **Starting state:** 2 body segments trailing behind head at (9,10) and (8,10)

### Food
- **Shape:** Filled square
- **Size:** 28×28px
- **Color:** #F44336
- **Position:** Random unoccupied grid cell. New food spawns immediately after previous is eaten.

### Grid Lines (subtle)
- **Color:** #1A1A1A
- **Width:** 1px between cells

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowUp / W | Change direction to up |
| ArrowDown / S | Change direction to down |
| ArrowLeft / A | Change direction to left |
| ArrowRight / D | Change direction to right |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Snake moves 1 grid cell per tick in its current direction.
2. Player can change direction, but cannot reverse directly (e.g., moving right cannot change to left).
3. When snake head occupies the same cell as food: food is consumed, snake grows by 1 segment, score increases, tick rate increases by 0.5 ticks/s (cap at 15 ticks/s).
4. Lose condition: snake head collides with any body segment or any wall (grid boundary).
5. There is no win condition — play for high score.
6. Only one direction change is processed per tick (buffer the first input).

## 6. Collision Detection

- Snake Head ↔ Food (same grid cell): consume food, grow snake, spawn new food
- Snake Head ↔ Body Segment (same grid cell): game over
- Snake Head ↔ Wall (x<0 or x≥20 or y<0 or y≥20): game over

Grid-based detection (integer coordinate comparison).

## 7. Scoring

- Starting score: 0
- Score display: top-left at (10, 24), #FFFFFF, 16px monospace
- Eating food: +10 points
- High score: stored in localStorage, displayed top-right at (590, 24) right-aligned, 16px monospace, #FFFFFF

## 8. UI Elements

- **Score:** top-left, "Score: {N}"
- **High Score:** top-right, "Best: {N}"
- **Game Over screen:** semi-transparent #000000CC overlay. "GAME OVER" centered at y=260, 40px #FFFFFF monospace. "Score: {N}" at y=310, 24px. "Press Enter to Restart" at y=360, 18px #AAAAAA.
- **Start screen:** "SNAKE" centered at y=240, 56px #4CAF50 monospace. "Press Enter to Start" at y=320, 20px #AAAAAA.
- **Pause:** "PAUSED" centered, 36px #FFFFFF on #000000CC overlay.

## 9. Audio (Optional / Bonus)
- Eat food: short 880Hz sine wave, 40ms
- Die: descending 440→110Hz sawtooth over 300ms

## 10. Implementation Notes

1. Buffer only one direction input per tick — ignore additional inputs until next tick to prevent double-turn deaths.
2. Food must spawn on an unoccupied cell (not on any snake segment). If the grid is completely full, player wins (extremely unlikely but handle gracefully).
3. Snake movement is grid-snapped — there is no sub-cell interpolation.
4. Tick rate (game speed) is separate from render frame rate. Render at 60fps but only advance game state at the tick rate.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Snake moves in grid cells, direction changes work
- [ ] Cannot reverse direction (left↔right, up↔down)
- [ ] Eating food grows the snake and increments score by 10
- [ ] Game speed increases as snake eats food
- [ ] Collision with wall or self triggers game over
- [ ] High score persists across page reloads
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, 600×600 canvas, inline style (#111111 bg, centered), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame at 60fps with delta-time. Separate tick timer starting at 8 ticks/s for game logic. Canvas clears to #111111 each frame. | Blank canvas renders; tick timer accumulates correctly |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Enter starts/restarts. P toggles pause. | State transitions work correctly |
| T04 | Snake & movement | Draw snake head (#4CAF50) and 2 body segments (#388E3C) as 28×28px squares on the 20×20 grid. Move 1 cell per tick in current direction (initial: right). Implement arrow key / WASD direction changes. Prevent 180° reversal. Buffer 1 input per tick. | Snake visible, moves on grid, direction changes correctly, no reversal |
| T05 | Grid rendering | Draw subtle #1A1A1A grid lines (1px) between all 20×20 cells. | Grid lines visible behind snake |
| T06 | Food & eating | Spawn #F44336 28×28px food square on a random unoccupied cell. On snake head entering food cell: consume, grow snake by 1 segment, spawn new food on unoccupied cell, increase tick rate by 0.5/s (cap 15). | Food appears; eating grows snake; new food avoids snake; speed increases |
| T07 | Collision detection | Detect snake head entering a body segment cell (game over) or going out of 20×20 bounds (game over). Transition to GAME_OVER state on collision. | Hitting wall or self triggers game over |
| T08 | Scoring | Display "Score: {N}" top-left at (10,24) 16px white monospace. +10 per food eaten. Store high score in localStorage. Display "Best: {N}" top-right at (590,24) right-aligned. | Score increments correctly; high score persists on reload |
| T09 | Game Over screen | Render #000000CC overlay with "GAME OVER" at y=260 40px, final score at y=310 24px, "Press Enter to Restart" at y=360 18px #AAAAAA. Enter resets all state. | Overlay appears on death; restart works cleanly |
| T10 | Start screen | Render "SNAKE" at y=240 56px #4CAF50. "Press Enter to Start" at y=320 20px #AAAAAA. No snake or food visible until game starts. | Title screen shows on load; Enter starts game |
| T11 | Pause screen | P key toggles PAUSED state. Show "PAUSED" centered 36px #FFFFFF on #000000CC overlay. Game logic and tick timer stop while paused. | Pause freezes game; unpause resumes correctly |
| T12 | Polish & debug | Fix remaining bugs. Ensure all acceptance criteria pass. Add metadata comment: `<!-- Snake | spec:run1-opus-plan | built-by:{model} -->` | All section 11 criteria pass; comment header present |
