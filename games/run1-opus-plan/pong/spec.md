# Game Spec: Pong

## 1. Overview
Pong (1972) — the game that started it all. Two paddles, one ball, first to 7 wins. This is a single-player version: the player controls the left paddle, the CPU controls the right. The feel should be snappy and responsive with a clean, minimal aesthetic true to the original.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left

## 3. Game Objects

### Player Paddle (Left)
- **Shape:** Rectangle
- **Size:** 12×80px
- **Color:** #FFFFFF
- **Starting position:** x=30, y=260 (vertically centered)
- **Movement:** Up/Down at 400px/s, clamped to canvas bounds

### CPU Paddle (Right)
- **Shape:** Rectangle
- **Size:** 12×80px
- **Color:** #FFFFFF
- **Starting position:** x=758, y=260
- **Movement:** Tracks ball y with 300px/s speed limit, slight smoothing (easing factor 0.08)

### Ball
- **Shape:** Square (retro style)
- **Size:** 12×12px
- **Color:** #FFFFFF
- **Starting position:** x=394, y=294 (center)
- **Movement:** Initial speed 350px/s, launches at random angle ±30° toward a random side. Speed increases by 25px/s each paddle hit (cap 600px/s)

### Center Line
- **Shape:** Dashed vertical line, 4px wide, segments 15px with 10px gaps
- **Color:** #444444
- **Position:** x=400, full height

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowUp / W | Move paddle up |
| ArrowDown / S | Move paddle down |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Ball launches from center toward a random side at game start and after each point.
2. Ball bounces off top and bottom walls (y-axis reflection).
3. Ball bounces off paddles (x-axis reflection + angle adjustment based on hit position: hitting the paddle edge produces a steeper angle, center produces a flatter angle).
4. If ball passes the left edge, CPU scores +1. If ball passes the right edge, player scores +1.
5. After a point, ball resets to center and launches toward the player who was scored upon after a 1-second delay.
6. First to 7 points wins the match.
7. Win condition: player reaches 7 — show "YOU WIN".
8. Lose condition: CPU reaches 7 — show "GAME OVER".

## 6. Collision Detection

- Ball ↔ Top/Bottom walls: reflect ball's y-velocity
- Ball ↔ Player Paddle: reflect ball's x-velocity, adjust angle based on paddle hit offset, increase speed by 25px/s
- Ball ↔ CPU Paddle: same reflection and speed increase logic
- Ball ↔ Left edge (past paddle): CPU scores a point
- Ball ↔ Right edge (past paddle): Player scores a point

Use AABB for paddle collisions.

## 7. Scoring

- Starting score: 0–0
- Score display: player score at x=300, CPU score at x=500, y=50, #FFFFFF, 48px monospace, centered
- Scoring a point: +1 to the appropriate side
- High score: best player score (wins) stored in localStorage, displayed at top-center y=16, 12px, #888888

## 8. UI Elements

- **Scores:** Large centered numbers as described above
- **Start screen:** "PONG" at center y=200, 64px white monospace. "Press Enter to Start" at y=350, 20px #AAAAAA
- **Game Over screen:** "YOU WIN" or "GAME OVER" centered, 48px white. Final score below. "Press Enter to Restart" below that, 18px #AAAAAA
- **Pause:** "PAUSED" centered, 36px #FFFFFF overlay with semi-transparent #000000CC background

## 9. Audio (Optional / Bonus)
- Paddle hit: short 440Hz square wave, 50ms
- Wall bounce: short 220Hz square wave, 50ms
- Score point: descending tone 660→330Hz over 200ms

## 10. Implementation Notes

1. CPU paddle AI must not be perfect — use a speed cap (300px/s) and easing so it can miss fast shots near the edges.
2. Ball angle off paddle should vary: offset = (ballCenterY − paddleCenterY) / (paddleHeight/2), angle = offset × 60°.
3. After scoring, enforce a 1-second delay before the ball relaunches — don't just immediately fling it.
4. Ball speed resets to 350px/s after each point.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Player paddle moves up/down with arrow keys and stays in bounds
- [ ] CPU paddle tracks ball with imperfect AI
- [ ] Ball bounces off walls and paddles correctly
- [ ] Score increments when ball passes a paddle
- [ ] Ball angle varies based on paddle hit position
- [ ] Game ends at 7 points with correct win/lose message
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, 800×600 canvas, inline style (black bg, centered), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame loop with delta-time tracking. Canvas clears to #000000 each frame. | Console shows no errors; blank black canvas renders at 60fps |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Enter key transitions IDLE→PLAYING and GAME_OVER→IDLE. P toggles PAUSED. | State transitions work correctly |
| T04 | Player paddle | Draw 12×80px white rectangle at x=30. Implement ArrowUp/W and ArrowDown/S movement at 400px/s. Clamp to canvas bounds. | Paddle visible, moves correctly, stays within bounds |
| T05 | CPU paddle | Draw 12×80px white rectangle at x=758. AI tracks ball y-position with 300px/s speed cap and 0.08 easing factor. | CPU paddle moves toward ball but can miss fast shots |
| T06 | Ball & physics | Draw 12×12px white square at center. Launch at 350px/s in random ±30° angle. Bounce off top/bottom walls (y-reflection). | Ball moves, bounces off top/bottom walls correctly |
| T07 | Paddle collision | Implement AABB collision between ball and both paddles. Reflect x-velocity on hit. Vary bounce angle based on paddle hit offset (±60°). Increase ball speed by 25px/s per hit (cap 600px/s). | Ball bounces off paddles at varying angles; speed increases |
| T08 | Scoring | Detect ball passing left/right edges. Increment appropriate score. Display scores at x=300 and x=500, y=50, 48px white monospace. Reset ball to center with 1s delay after each point. Reset ball speed to 350px/s. | Scores display and increment; ball resets after point |
| T09 | Center line & HUD | Draw dashed center line (4px wide, #444444, 15px segments, 10px gaps). Store high score (player wins) in localStorage, display at top-center 12px #888888. | Center line visible; high score persists across reloads |
| T10 | Win/Lose condition | End game when either side reaches 7 points. Show "YOU WIN" or "GAME OVER" centered, 48px white, with final score and restart prompt. | Game ends at 7; correct message shown; Enter restarts |
| T11 | Start screen | Render "PONG" at center y=200, 64px white monospace. "Press Enter to Start" at y=350, 20px #AAAAAA. No game objects visible until Enter pressed. | Title screen appears on load; Enter starts game |
| T12 | Polish & debug | Fix remaining bugs. Ensure all acceptance criteria pass. Add metadata comment header: `<!-- Pong | spec:run1-opus-plan | built-by:{model} -->` | All section 11 criteria pass; comment header present |
