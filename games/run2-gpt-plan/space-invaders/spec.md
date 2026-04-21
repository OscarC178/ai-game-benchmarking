# Game Spec: Space Invaders

## 1. Overview
Space Invaders — a fixed-screen shooter from the late 1970s where the player defends against a descending alien formation behind destructible shields. It feels authentic when the formation marches as a unit, the player is limited to one shot at a time, shields erode under fire, and later waves accelerate the pressure.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left

## 3. Game Objects

### Player Ship
- **Shape/Sprite:** Simplified pixel-like ship silhouette
- **Size:** 40×32px
- **Color:** #00FF00
- **Starting position:** x=380, y=550
- **Movement:** Horizontal only at 300px/s, clamped inside canvas

### Alien Formation
- **Shape/Sprite:** 11×5 grid of three alien silhouette types
- **Size:** top row 24×16px, middle rows 28×20px, bottom rows 32×20px
- **Color:** top row #FF0000, middle rows #FFCC00, bottom rows #00CCFF
- **Starting position:** first alien center at x=120, y=80 with 50px horizontal and 40px vertical spacing
- **Movement:** marches horizontally at 30px/s, reverses and drops 20px at side limits

### Player Bullet
- **Shape/Sprite:** Rectangle
- **Size:** 3×12px
- **Color:** #FFFFFF
- **Starting position:** player ship center top
- **Movement:** upward at 500px/s; only 1 may exist at a time

### Alien Bullet
- **Shape/Sprite:** Rectangle
- **Size:** 3×12px
- **Color:** #FF4444
- **Starting position:** fired from bottom-most alive alien in a selected column
- **Movement:** downward at 250px/s; maximum 3 active at once

### Shields
- **Shape/Sprite:** 4 clusters of destructible 4×4px cells forming arch shapes
- **Size:** each shield roughly 80×64px depending on cell mask
- **Color:** #00FF00
- **Starting position:** origins at x=140, 300, 460, 620 with y=480
- **Movement:** static until eroded by impacts

### Mystery Ship
- **Shape/Sprite:** Red saucer
- **Size:** 48×16px
- **Color:** #FF0000
- **Starting position:** enters from left or right edge at y=35
- **Movement:** horizontal at 150px/s, spawning every 20–30 seconds

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Move left |
| ArrowRight / D | Move right |
| Space | Fire |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. The player may have only one bullet on screen at a time.
2. The alien formation moves as one unit and drops downward when it reverses.
3. Alien movement speed should increase as fewer aliens remain.
4. Alien bullets are fired from valid bottom-most aliens only.
5. Shields absorb both player and alien shots cell-by-cell.
6. Destroying all aliens advances to the next wave.
7. Player starts with 3 lives.
8. Game ends if lives reach 0.
9. Game also ends if the alien formation descends to y≥540.
10. Mystery ship awards a random bonus value when destroyed.

## 6. Collision Detection

- Player Bullet ↔ Alien: destroy alien and bullet, award alien score
- Player Bullet ↔ Shield Cell: destroy both
- Player Bullet ↔ Mystery Ship: destroy both and award bonus score
- Alien Bullet ↔ Shield Cell: destroy both
- Alien Bullet ↔ Player Ship: lose a life and remove bullet
- Alien ↔ Shield Cell: erase overlapped shield cells
- Alien Formation ↔ descent line: trigger game over when low enough

Use AABB for all collisions.

## 7. Scoring

- Starting score: 0
- Score display: top-left, white text, 16px monospace
- Top-row alien: +30 points
- Middle-row alien: +20 points
- Bottom-row alien: +10 points
- Mystery ship: +50, +100, +150, or +300 points
- High score: stored in localStorage, display at top-right

## 8. UI Elements

- **Score:** top-left
- **Lives / Health:** bottom-left as ship icons or numeric lives
- **Level indicator:** wave number bottom-right
- **Game Over screen:** centered text “GAME OVER”, score, “Press Enter to restart”
- **Start screen:** “SPACE INVADERS” centered at y=220 in 48px #00FF00 monospace, with score legend below and “Press Enter to Start”
- **Pause:** P key toggles pause overlay

## 9. Audio (Optional / Bonus)
- Player shot: 900Hz square beep
- Alien hit: short noise burst
- Player death: descending tone sweep
- Formation march: repeating heartbeat-like pulse

## 10. Implementation Notes

1. Only the lowest alive alien in each column may fire.
2. Formation edge checks must use the current alive alien bounds, not the original grid width.
3. Shields should be built from individual cells rather than large rectangles.
4. Mystery ship timing should reset after either destruction or exit.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Player ship moves and fires correctly with one-shot limit
- [ ] Alien formation marches, reverses, and drops correctly
- [ ] Shields erode correctly under fire
- [ ] Alien bullets can damage shields and player
- [ ] Clearing all aliens advances the wave
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
| T05 | Alien formation | Render the 11×5 alien formation with exact row sizes, colors, spacing, and values, and move it horizontally as a unified block that reverses and drops at edges. | Formation appears correctly and performs the classic march pattern |
| T06 | Player shot, alien shots, and shields | Add the one-shot player bullet system, bottom-most alien firing logic with a 3-bullet cap, and four cell-based destructible shields. | Bullets originate from valid sources and shields chip away under fire |
| T07 | Wave progression and UFO | Remove aliens on hits, speed up the formation as it thins, start a new wave when cleared, and spawn the mystery ship on a 20–30 second timer. | Later moments and new waves feel faster, and the UFO appears periodically |
| T08 | Descent loss condition | Track alien drop depth and trigger game over when the formation reaches the loss line near y=540. | Letting aliens descend far enough always ends the game |
| T09 | Collision detection | Implement all collision pairs from spec section 6. AABB unless spec says otherwise. | Collisions trigger correct outcomes (log to console if needed) |
| T10 | Scoring | Implement score counter. Render score top-left, high score top-right (localStorage). | Score increments on correct events; persists on reload |
| T11 | Lives / health | Render lives/health indicator top-right per spec section 8. Decrement on hit. | Lives display correctly; game over triggers at 0 |
| T12 | Game Over screen | Render GAME OVER overlay with final score. Enter key restarts. | Overlay appears; restart resets all state |
| T13 | Start screen | Render title screen with game name and "Press Enter to Start". | Appears on load before game begins |
| T14 | Polish & debug | Fix any remaining bugs. Ensure all acceptance criteria from section 11 pass. Add the metadata comment header. | All section 11 criteria pass; comment header present |
