# Game Spec: Breakout

## 1. Overview
Breakout (Atari, 1976) — bounce a ball off a paddle to destroy rows of colored bricks. Clear all bricks to advance. Single-player with increasing ball speed per level. Clean, colorful brick layout against a black background.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left

## 3. Game Objects

### Paddle
- **Shape:** Rounded rectangle (4px border-radius effect — draw as rectangle)
- **Size:** 100×14px
- **Color:** #FFFFFF
- **Starting position:** x=350, y=560 (centered horizontally, near bottom)
- **Movement:** Horizontal only, mouse tracks paddle center-x (clamped to canvas). Also ArrowLeft/ArrowRight at 500px/s.

### Ball
- **Shape:** Circle
- **Size:** 8px radius
- **Color:** #FFFFFF
- **Starting position:** x=400, y=550 (resting above paddle center)
- **Movement:** Initial speed 350px/s, launches upward at random angle between 225° and 315° (upper half). Speed increases by 20px/s each level (cap 500px/s).

### Bricks
- **Layout:** 10 columns × 6 rows
- **Brick size:** 70×20px
- **Spacing:** 6px between bricks horizontally, 4px vertically
- **Grid offset:** x=19, y=50 (top-left of first brick)
- **Row colors (top to bottom):** #FF0000, #FF6600, #FFCC00, #00CC00, #0088FF, #8800FF
- **Each brick:** 1 hit to destroy

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Move paddle left |
| ArrowRight / D | Move paddle right |
| Mouse movement | Paddle tracks mouse x |
| Space | Launch ball (when attached to paddle) |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Ball starts attached to paddle. Space launches it.
2. Ball bounces off top wall, left wall, and right wall.
3. Ball bounces off paddle — angle varies based on hit offset from paddle center (same formula as Pong: offset × 60°).
4. Ball hitting a brick destroys the brick and reflects the ball (reflect the axis of penetration).
5. If ball falls below the paddle (y > 600), player loses a life.
6. Player starts with 3 lives.
7. Clearing all 60 bricks advances to the next level: bricks reset, ball speed +20px/s.
8. Game over when lives reach 0.
9. After losing a life, ball reattaches to paddle for relaunch.

## 6. Collision Detection

- Ball ↔ Top wall (y ≤ 0): reflect y-velocity
- Ball ↔ Left/Right walls (x ≤ 0 or x ≥ 800): reflect x-velocity
- Ball ↔ Paddle: reflect y-velocity, adjust angle based on hit offset
- Ball ↔ Brick: determine which face was hit (top/bottom → reflect y, left/right → reflect x), destroy brick
- Ball ↔ Bottom (y > 600): lose a life

Use AABB for brick collisions. Use circle-rect for paddle collision.

## 7. Scoring

- Starting score: 0
- Score display: top-left at (10, 24), #FFFFFF, 16px monospace
- Top-row bricks (red): 7 points
- Second row (orange): 5 points
- Third row (yellow): 4 points
- Fourth row (green): 3 points
- Fifth row (blue): 2 points
- Bottom row (purple): 1 point
- High score: stored in localStorage, displayed top-right

## 8. UI Elements

- **Score:** top-left, "Score: {N}"
- **Lives:** top-right, display as "♥" repeated (e.g., "♥♥♥"), 18px, #FF0000
- **Level:** top-center, "Level: {N}", 16px #AAAAAA
- **Game Over screen:** #000000CC overlay. "GAME OVER" centered 40px white. Final score and "Press Enter to Restart" below.
- **Start screen:** "BREAKOUT" centered y=250, 56px #FFFFFF monospace. "Press Enter to Start" at y=330, 20px #AAAAAA.
- **Pause:** "PAUSED" centered 36px white on #000000CC overlay.

## 9. Audio (Optional / Bonus)
- Paddle hit: 440Hz square, 30ms
- Brick hit: 660Hz square, 30ms
- Lose life: descending 440→110Hz, 300ms
- Level clear: ascending arpeggio 440→880Hz, 400ms

## 10. Implementation Notes

1. Brick collision must determine which face the ball hit to reflect the correct axis — don't just invert both velocities.
2. Ball should not clip through bricks at high speed — check collision per frame step or limit ball speed to prevent tunneling.
3. When ball is attached to paddle before launch, it must track paddle position exactly.
4. Ball should only destroy one brick per frame (first collision detected), then reflect and continue.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Paddle moves with arrow keys and mouse, stays in bounds
- [ ] Ball launches with Space, bounces off walls and paddle
- [ ] Bricks are destroyed on ball contact with correct color layout
- [ ] Score increments correctly per row value
- [ ] Lives decrement when ball falls below paddle
- [ ] Level advances when all bricks are cleared
- [ ] Game over screen appears at 0 lives
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, 800×600 canvas, inline style (black bg, centered, cursor:none over canvas), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame loop with delta-time. Canvas clears to #000000 each frame. | Blank canvas renders at 60fps |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Add sub-state BALL_ATTACHED for pre-launch. Enter starts, P pauses. | State transitions work correctly |
| T04 | Paddle | Draw 100×14px white rectangle at y=560. Move with ArrowLeft/ArrowRight at 500px/s AND mouse x-tracking. Clamp to canvas edges. | Paddle visible, moves with keyboard and mouse, stays in bounds |
| T05 | Brick grid | Render 10×6 grid of 70×20px bricks starting at (19,50) with 6px horizontal and 4px vertical spacing. Color rows top→bottom: #FF0000, #FF6600, #FFCC00, #00CC00, #0088FF, #8800FF. Track alive/dead state per brick. | 60 bricks render in correct colors and positions |
| T06 | Ball & launch | Draw 8px-radius white circle. Ball starts attached to paddle center, tracking paddle x. Space launches at 350px/s upward at random angle (225°–315°). Bounce off top/left/right walls. | Ball sits on paddle, launches on Space, bounces off walls |
| T07 | Paddle collision | AABB/circle-rect collision between ball and paddle. Reflect y-velocity. Adjust bounce angle based on offset from paddle center (offset × 60°). | Ball bounces off paddle at varying angles |
| T08 | Brick collision | Check ball against all alive bricks each frame. Determine hit face (top/bottom reflects y, left/right reflects x). Destroy brick on hit. Only process first collision per frame. | Bricks break on contact; ball reflects correctly |
| T09 | Scoring | +7/5/4/3/2/1 points per row (top to bottom). Display "Score: {N}" top-left 16px monospace. High score in localStorage, top-right. | Score matches row values; high score persists |
| T10 | Lives & level | Start with 3 lives. Display "♥♥♥" top-right 18px #FF0000. Lose life when ball y>600; reattach ball to paddle. At 0 lives → GAME_OVER. When all 60 bricks cleared: advance level, reset bricks, increase ball speed +20px/s (cap 500). Display "Level: {N}" top-center. | Lives decrement; level advances on clear; speed increases |
| T11 | Start & Game Over screens | Start: "BREAKOUT" y=250 56px white, "Press Enter to Start" y=330 20px #AAAAAA. Game Over: #000000CC overlay, "GAME OVER" 40px, score, restart prompt. Enter restarts cleanly. | Screens appear at correct times; restart resets all state |
| T12 | Polish & debug | Fix remaining bugs. Ensure all acceptance criteria pass. Add metadata comment: `<!-- Breakout | spec:run1-opus-plan | built-by:{model} -->` | All section 11 criteria pass; comment header present |
