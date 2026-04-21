# Game Spec: Snake

## 1. Overview
Snake — a grid-based arcade game where the player steers a growing snake to eat food and survive as long as possible. The benchmark version should emphasize clear grid logic, readable visuals, and steadily increasing tension.

## 2. Canvas & Rendering
- Canvas size: 600×600px
- Background color: #111111
- Frame rate: 60 FPS
- Coordinate system: origin top-left

## 3. Game Objects

### Snake Head
- **Shape/Sprite:** Filled square
- **Size:** 28×28px inset in a 30×30 cell
- **Color:** #4CAF50
- **Starting position:** grid cell (10,10)
- **Movement:** one cell per tick; initial direction right

### Snake Body
- **Shape/Sprite:** Filled square per segment
- **Size:** 28×28px
- **Color:** #2E7D32
- **Starting position:** segments at (9,10) and (8,10)
- **Movement:** follows head path cell-by-cell

### Food
- **Shape/Sprite:** Filled square
- **Size:** 28×28px
- **Color:** #F44336
- **Starting position:** random free grid cell
- **Movement:** static until consumed and respawned

### Grid
- **Shape/Sprite:** 1px line lattice
- **Size:** covers 20×20 cells
- **Color:** #1A1A1A
- **Starting position:** full canvas board
- **Movement:** static

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowUp / W | Turn up |
| ArrowDown / S | Turn down |
| ArrowLeft / A | Turn left |
| ArrowRight / D | Turn right |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Snake advances exactly one cell per movement tick.
2. Initial speed is 8 ticks per second.
3. Snake cannot reverse directly into itself.
4. Eating food increases length by 1 and awards 10 points.
5. Each food eaten increases speed by 0.5 ticks/s up to 15 ticks/s.
6. Hitting a wall or the snake’s own body ends the run.
7. Only one queued direction change is allowed per tick window.
8. If the board becomes full, freeze play as a completed run.

## 6. Collision Detection

- Head ↔ Food: same grid cell = consume food and grow
- Head ↔ Body: same grid cell = game over
- Head ↔ Wall: outside 0..19 grid range = game over

Use grid-cell comparisons for all collision logic.

## 7. Scoring

- Starting score: 0
- Score display: top-left, white text, 16px monospace
- Food eaten: +10 points
- Board fill completion: no extra score required unless desired by builder
- High score: stored in localStorage, display at top-right

## 8. UI Elements

- **Score:** top-left
- **Lives / Health:** not applicable
- **Level indicator:** not applicable
- **Game Over screen:** centered text “GAME OVER”, score, “Press Enter to restart”
- **Start screen:** “SNAKE” centered at y=236 in 56px #4CAF50 monospace, “Press Enter to Start” at y=320
- **Pause:** P key toggles pause overlay

## 9. Audio (Optional / Bonus)
- Eat food: 900Hz sine beep, 40ms
- Death: descending 440→120Hz sawtooth tone, 280ms

## 10. Implementation Notes

1. Rendering should stay at 60 FPS while movement advances on a fixed tick timer.
2. Only the first valid turn input within a tick window should be buffered.
3. Food must never spawn on any existing snake segment.
4. Restart must fully reset score, length, speed, and queued input state.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Snake moves one cell per tick and turns correctly
- [ ] Direct reversal is prevented
- [ ] Food grows the snake and increases score
- [ ] Wall and self collisions end the game
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
| T05 | Snake body progression | Initialize the snake with head and body segments at the specified starting cells and update the body chain correctly as the head advances one grid step at a time. | Snake length and body follow behavior remain correct across many moves |
| T06 | Food spawning and growth | Spawn food only in unoccupied grid cells and, on collection, grow the snake by one segment while immediately placing new food elsewhere. | Food never overlaps the snake and eating it visibly increases length |
| T07 | Input buffering and no-reverse rule | Allow one queued direction change per tick and reject any turn that would reverse directly into the neck segment. | Quick key presses feel responsive but illegal reversals never happen |
| T08 | Speed escalation | Raise movement speed by 0.5 ticks/s each time food is eaten up to 15 ticks/s without affecting render smoothness. | Snake becomes noticeably faster after several foods |
| T09 | Collision detection | Implement all collision pairs from spec section 6. AABB unless spec says otherwise. | Collisions trigger correct outcomes (log to console if needed) |
| T10 | Scoring | Implement score counter. Render score top-left, high score top-right (localStorage). | Score increments on correct events; persists on reload |
| T11 | Lives / health | Render lives/health indicator top-right per spec section 8. Decrement on hit. | Lives display correctly; game over triggers at 0 |
| T12 | Game Over screen | Render GAME OVER overlay with final score. Enter key restarts. | Overlay appears; restart resets all state |
| T13 | Start screen | Render title screen with game name and "Press Enter to Start". | Appears on load before game begins |
| T14 | Polish & debug | Fix any remaining bugs. Ensure all acceptance criteria from section 11 pass. Add the metadata comment header. | All section 11 criteria pass; comment header present |
