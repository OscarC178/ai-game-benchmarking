# Game Spec: Pong

## 1. Overview
Pong (1972) — the foundational paddle-vs-ball arcade game. This benchmark version is single-player: the player controls the left paddle and plays against a CPU-controlled right paddle. The presentation should be minimal, readable, and faithful to the original feel.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left

## 3. Game Objects

### Player Paddle (Left)
- **Shape/Sprite:** Rectangle
- **Size:** 12×84px
- **Color:** #FFFFFF
- **Starting position:** x=32, y=258
- **Movement:** Vertical only at 420px/s, clamped to y=0..516

### CPU Paddle (Right)
- **Shape/Sprite:** Rectangle
- **Size:** 12×84px
- **Color:** #FFFFFF
- **Starting position:** x=756, y=258
- **Movement:** Tracks the ball with 320px/s max speed and an 80ms reaction delay so it is beatable

### Ball
- **Shape/Sprite:** Square
- **Size:** 12×12px
- **Color:** #FFFFFF
- **Starting position:** x=394, y=294
- **Movement:** Launch speed 340px/s; launch angle randomized between −28° and +28° toward a side. Speed increases by 22px/s after each paddle hit up to 620px/s.

### Center Divider
- **Shape/Sprite:** Dashed vertical line
- **Size:** 4px wide with 16px dash height and 10px gaps
- **Color:** #3A3A3A
- **Starting position:** centered at x=400 from top to bottom of the playfield
- **Movement:** static

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowUp / W | Move paddle up |
| ArrowDown / S | Move paddle down |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Ball starts in the center and launches after game start.
2. Ball reflects off top and bottom walls.
3. Ball reflects off paddles and changes angle based on hit position.
4. Ball exiting left side gives CPU 1 point.
5. Ball exiting right side gives player 1 point.
6. After each point, ball resets to center and relaunches after 0.9s toward the player who conceded the point.
7. First to 7 points wins.
8. Player victory displays “YOU WIN”; CPU victory displays “GAME OVER”.

## 6. Collision Detection

- Ball ↔ top/bottom wall: reflect y velocity
- Ball ↔ paddles: AABB collision, reflect x velocity and adjust outgoing angle
- Ball ↔ scoring boundaries: point awarded only after full ball exits playfield

Use AABB for paddle collisions.

## 7. Scoring

- Starting score: 0
- Score display: player score at x=300, y=54 and CPU score at x=500, y=54 in 48px #FFFFFF monospace
- Player point: +1
- CPU point: +1
- High score: stored in localStorage, display top-center in 12px #888888

## 8. UI Elements

- **Score:** large numeric scores near the top center
- **Lives / Health:** not applicable
- **Level indicator:** not applicable
- **Game Over screen:** centered text “YOU WIN” or “GAME OVER”, final score, “Press Enter to restart”
- **Start screen:** title “PONG” centered at y=210 in 64px #FFFFFF monospace, “Press Enter to Start” at y=344
- **Pause:** P key toggles a #000000CC overlay with centered “PAUSED”

## 9. Audio (Optional / Bonus)
- Paddle hit: 440Hz square wave, 45ms
- Wall bounce: 220Hz square wave, 45ms
- Score event: descending 700→320Hz tone over 180ms

## 10. Implementation Notes

1. CPU must be intentionally imperfect rather than frame-perfect.
2. Bounce angle should depend on impact offset from paddle center.
3. Ball speed should reset after each scored point.
4. Pause and end states must completely halt gameplay motion.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Player paddle responds correctly and stays on-screen
- [ ] CPU tracks the ball but can be beaten
- [ ] Ball bounces properly off paddles and walls
- [ ] Match ends at 7 points with correct message
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
| T05 | CPU paddle | Render the right-side paddle at x=756, y=258 with the same 12×84 size as the player paddle and implement delayed tracking AI with capped movement speed. | CPU paddle visibly tracks the ball but misses some fast corner shots |
| T06 | Ball launch and rebounds | Spawn the 12×12 ball at center, serve it toward a side at 340px/s with a randomized angle, and reflect it off top/bottom walls. | Ball launches cleanly and rebounds correctly from walls |
| T07 | Paddle bounce shaping | Apply paddle collision response using impact offset to change outgoing angle and increase ball speed gradually up to the 620px/s cap. | Paddle hits produce different rebound angles and longer rallies speed up |
| T08 | Scoring and re-serve flow | Detect full exits at left/right boundaries, update the correct score, reset the ball to center, and delay the next serve by 0.9 seconds. | Each point increments the correct side and triggers a clean re-serve |
| T09 | Collision detection | Implement all collision pairs from spec section 6. AABB unless spec says otherwise. | Collisions trigger correct outcomes (log to console if needed) |
| T10 | Scoring | Implement score counter. Render score top-left, high score top-right (localStorage). | Score increments on correct events; persists on reload |
| T11 | Lives / health | Render lives/health indicator top-right per spec section 8. Decrement on hit. | Lives display correctly; game over triggers at 0 |
| T12 | Game Over screen | Render GAME OVER overlay with final score. Enter key restarts. | Overlay appears; restart resets all state |
| T13 | Start screen | Render title screen with game name and "Press Enter to Start". | Appears on load before game begins |
| T14 | Polish & debug | Fix any remaining bugs. Ensure all acceptance criteria from section 11 pass. Add the metadata comment header. | All section 11 criteria pass; comment header present |
