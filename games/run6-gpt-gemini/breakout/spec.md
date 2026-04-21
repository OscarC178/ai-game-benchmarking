# Game Spec: Breakout

## 1. Overview
Breakout — a paddle-and-ball brick breaker from the late 1970s where the player clears a wall of colored bricks by carefully redirecting a fast-moving ball. It feels authentic when collisions are crisp, the paddle is responsive, the brick wall is orderly, and the level pace ramps up cleanly.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left

## 3. Game Objects

### Paddle
- **Shape/Sprite:** Rectangle
- **Size:** 104×14px
- **Color:** #FFFFFF
- **Starting position:** x=348, y=560
- **Movement:** Horizontal only at 520px/s, clamped to screen edges

### Ball
- **Shape/Sprite:** Circle
- **Size:** radius 8px
- **Color:** #FFFFFF
- **Starting position:** x=400, y=548, attached above paddle center
- **Movement:** Launches upward at 340px/s with angle between 240° and 300°; speed increases by 20px/s per level up to 520px/s

### Bricks
- **Shape/Sprite:** Rectangles
- **Size:** 70×20px each
- **Color:** row 1 #FF0000, row 2 #FF6A00, row 3 #FFD400, row 4 #20C020, row 5 #1E88FF, row 6 #8A2BE2
- **Starting position:** top-left brick at x=19, y=52 with 10 columns × 6 rows
- **Movement:** static until destroyed

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Move paddle left |
| ArrowRight / D | Move paddle right |
| Space | Launch ball |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Ball begins attached to the paddle.
2. Space launches the ball upward.
3. Ball bounces off left, right, and top walls.
4. Ball bounces off paddle with angle based on impact position.
5. Ball destroys one brick per impact.
6. Ball falling below the bottom costs one life and reattaches to paddle.
7. Player starts with 3 lives.
8. Clearing all bricks advances to the next level.
9. Each level slightly increases base ball speed.
10. Game over occurs when lives reach 0.

## 6. Collision Detection

- Ball ↔ Wall: reflect on left, right, and top walls
- Ball ↔ Paddle: reflect upward and adjust angle from hit offset
- Ball ↔ Brick: destroy brick and reflect on collision axis
- Ball ↔ Bottom boundary: lose life and reset serve

Use circle-vs-rect checks for paddle and bricks.

## 7. Scoring

- Starting score: 0
- Score display: top-left, white text, 16px monospace
- Row 1 brick: +7 points
- Row 2 brick: +5 points
- Row 3 brick: +4 points
- Row 4 brick: +3 points
- Row 5 brick: +2 points
- Row 6 brick: +1 point
- High score: stored in localStorage, display at top-right

## 8. UI Elements

- **Score:** top-left
- **Lives / Health:** top-right as red hearts or markers
- **Level indicator:** top-center in 16px #AAAAAA monospace
- **Game Over screen:** centered text “GAME OVER”, score, “Press Enter to restart”
- **Start screen:** “BREAKOUT” centered at y=246 in 56px #FFFFFF monospace, “Press Enter to Start” below
- **Pause:** P key toggles pause overlay

## 9. Audio (Optional / Bonus)
- Paddle hit: short 430Hz square beep
- Brick hit: short 670Hz square beep
- Life lost: descending tone sweep
- Level clear: quick ascending arpeggio

## 10. Implementation Notes

1. Ball should remain perfectly attached to the paddle before launch.
2. Destroy only one brick per update step to avoid unstable reflections.
3. Paddle bounce angle should vary noticeably across the paddle width.
4. Restart must reset bricks, score, lives, level, and ball state cleanly.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Paddle moves correctly and stays within bounds
- [ ] Ball launches and bounces correctly
- [ ] Bricks render and disappear correctly on hit
- [ ] Lives decrease when the ball falls below the bottom
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
| T05 | Brick wall layout | Build the 10×6 brick field starting at x=19, y=52 with the specified brick size, spacing, and row colors. | All 60 bricks appear in the right colors and positions |
| T06 | Ball attachment and launch | Attach the ball above the paddle before launch, then fire it upward at the specified speed and angle range when Space is pressed. | Ball tracks the paddle before launch and serves correctly |
| T07 | Paddle and wall rebound shaping | Reflect the ball from walls and the paddle, with paddle hit offset affecting the outgoing angle so edge hits create sharper trajectories. | Bounce behavior is stable and visibly changes based on paddle contact point |
| T08 | Brick destruction and level advance | Destroy struck bricks one at a time, award row-based score values, and rebuild the wall when all bricks are cleared while increasing base speed. | Bricks disappear correctly and clearing the board starts a faster new level |
| T09 | Collision detection | Implement all collision pairs from spec section 6. AABB unless spec says otherwise. | Collisions trigger correct outcomes (log to console if needed) |
| T10 | Scoring | Implement score counter. Render score top-left, high score top-right (localStorage). | Score increments on correct events; persists on reload |
| T11 | Lives / health | Render lives/health indicator top-right per spec section 8. Decrement on hit. | Lives display correctly; game over triggers at 0 |
| T12 | Game Over screen | Render GAME OVER overlay with final score. Enter key restarts. | Overlay appears; restart resets all state |
| T13 | Start screen | Render title screen with game name and "Press Enter to Start". | Appears on load before game begins |
| T14 | Polish & debug | Fix any remaining bugs. Ensure all acceptance criteria from section 11 pass. Add the metadata comment header. | All section 11 criteria pass; comment header present |
