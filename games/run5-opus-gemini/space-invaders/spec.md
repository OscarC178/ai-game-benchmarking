# Game Spec: Space Invaders

## 1. Overview
Space Invaders (Taito, 1978) — iconic fixed-shooter. A grid of aliens marches left-to-right, dropping one row closer each time they reach a wall. The player fires upward to destroy them. Aliens fire back randomly. Destroy all aliens to advance; get hit or let them reach you to lose. Features destructible shields for cover.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left

## 3. Game Objects

### Player Ship
- **Shape:** Upward-pointing trapezoid (draw as a flat-bottom triangle: tip at top-center, base at bottom). Simplified: 40×24px rectangle with 10×8px turret centered on top.
- **Size:** 40×32px total bounding box
- **Color:** #00FF00
- **Starting position:** x=380, y=550
- **Movement:** Horizontal only at 300px/s, clamped to canvas

### Alien Formation
- **Layout:** 11 columns × 5 rows = 55 aliens
- **Spacing:** 50px horizontal, 40px vertical between alien centers
- **Grid offset:** First alien center at x=120, y=80
- **Row types and colors (top to bottom):**
  - Row 1 (1 row): Small alien, #FF0000, 24×16px
  - Rows 2–3 (2 rows): Medium alien, #FFCC00, 28×20px
  - Rows 4–5 (2 rows): Large alien, #00CCFF, 32×20px
- **Movement:** Formation moves right at 30px/s. When any alien reaches x≥760, entire formation shifts down 20px and reverses direction to left. Same at x≤40. Speed increases by 5px/s for every 5 aliens destroyed.

### Player Bullet
- **Shape:** Rectangle
- **Size:** 3×12px
- **Color:** #FFFFFF
- **Movement:** Upward at 500px/s
- **Limit:** 1 on screen at a time

### Alien Bullet
- **Shape:** Rectangle
- **Size:** 3×12px
- **Color:** #FF4444
- **Movement:** Downward at 250px/s
- **Firing:** Random bottom-row alien fires every 1.0s (±0.3s random variance). Max 3 alien bullets on screen.

### Shields (4)
- **Shape:** Arch-shaped block made of 20×16 grid of 4×4px cells
- **Color:** #00FF00
- **Positions:** Evenly spaced at x = 140, 300, 460, 620, y=480
- **Destructible:** Each 4×4px cell is independently destroyable by any bullet (player or alien)

### Mystery Ship (UFO)
- **Shape:** Ellipse/saucer shape — draw as 48×16px rounded rectangle
- **Color:** #FF0000
- **Movement:** Appears randomly every 20–30 seconds, crosses screen left→right at 150px/s along y=35
- **Points:** 50, 100, 150, or 300 (random)

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Move left |
| ArrowRight / D | Move right |
| Space | Fire |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Player fires upward; only 1 player bullet on screen at a time.
2. Alien formation marches horizontally; reverses and drops 20px when edge alien hits boundary.
3. Random bottom-row alien fires downward every ~1s.
4. Destroying all 55 aliens advances to the next wave: aliens reset at original position, movement speed resets +10px/s base bonus per level.
5. Shields are destructible cell-by-cell by any bullet contact.
6. Player starts with 3 lives. Hit by alien bullet = lose a life.
7. If any alien reaches y ≥ 540, game over immediately.
8. Game over when lives = 0 or aliens reach bottom.

## 6. Collision Detection

- Player Bullet ↔ Alien: destroy alien, destroy bullet, add score
- Player Bullet ↔ Shield cell: destroy cell, destroy bullet
- Player Bullet ↔ Mystery Ship: destroy ship, add random bonus score
- Alien Bullet ↔ Player: lose life, destroy bullet
- Alien Bullet ↔ Shield cell: destroy cell, destroy bullet
- Alien ↔ Shield: destroy overlapping shield cells (formation pushes through)
- Alien formation y ≥ 540: instant game over

All AABB. Shield cells checked individually.

## 7. Scoring

- Starting score: 0
- Score display: top-left at (10, 24), #FFFFFF, 16px monospace
- Small alien (top row): 30 points
- Medium alien (rows 2–3): 20 points
- Large alien (rows 4–5): 10 points
- Mystery ship: random 50/100/150/300 points
- High score: localStorage, top-right

## 8. UI Elements

- **Score:** top-left "Score: {N}" 16px white monospace
- **High Score:** top-right "Best: {N}" 16px
- **Lives:** bottom-left, show remaining ship icons (small 20×16px green sprites) plus "×{N}"
- **Level:** bottom-right "Wave: {N}" 14px #AAAAAA
- **Game Over screen:** #000000CC overlay. "GAME OVER" 40px white centered. Score and restart prompt.
- **Start screen:** "SPACE INVADERS" centered y=220, 48px #00FF00 monospace. Alien type legend below showing point values. "Press Enter to Start" y=400, 20px #AAAAAA.
- **Pause:** "PAUSED" centered 36px white on #000000CC overlay.

## 9. Audio (Optional / Bonus)
- Player shoot: 880Hz square, 50ms
- Alien destroyed: noise burst, 80ms
- Player hit: descending 440→55Hz, 400ms
- Alien march: alternating 2-tone heartbeat (lower pitch as fewer aliens remain)

## 10. Implementation Notes

1. Alien formation speed must increase as aliens are destroyed — recalculate after each kill based on remaining count.
2. Only bottom-row aliens (lowest alive alien per column) should fire bullets.
3. Shields must be pixel-grid destructible (each 4×4px cell independently tracked as alive/dead).
4. When the formation reverses direction, ALL aliens must drop simultaneously — don't animate them dropping one by one.
5. Mystery ship timer should reset after it exits or is destroyed.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Player ship moves horizontally, stays in bounds
- [ ] Aliens march in formation, reverse at edges, drop down
- [ ] Player bullet destroys aliens on contact
- [ ] Alien bullets damage player and shields
- [ ] Shields are cell-by-cell destructible
- [ ] Alien speed increases as aliens are destroyed
- [ ] Mystery ship appears periodically and is destroyable
- [ ] Game over when lives = 0 or aliens reach bottom
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, 800×600 canvas, inline style (black bg, centered), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame loop with delta-time. Canvas clears to #000000 each frame. | Blank canvas renders at 60fps |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Enter starts/restarts. P pauses. | State transitions work correctly |
| T04 | Player ship | Draw 40×32px green (#00FF00) player shape at y=550. Move with ArrowLeft/ArrowRight at 300px/s. Clamp to canvas. | Ship visible, moves horizontally, stays in bounds |
| T05 | Alien formation | Create 11×5 grid of aliens with correct sizes and colors per row type (red 24×16, yellow 28×20, cyan 32×20). Position starting at center (120,80) with 50px/40px spacing. Track alive/dead per alien. Draw all alive aliens. | 55 aliens render in correct rows/colors/positions |
| T06 | Alien movement | Formation moves right at 30px/s. When rightmost alive alien reaches x≥760, all aliens shift down 20px and reverse to left. Same at x≤40. Increase speed by 5px/s for every 5 aliens destroyed. | Formation marches, reverses, drops; speed scales with kills |
| T07 | Player bullet | Space fires 3×12px white bullet upward at 500px/s from player center. Only 1 bullet on screen at a time. Bullet destroyed when off-screen (y<0). | Bullet fires, moves up, disappears off-screen; only 1 at a time |
| T08 | Alien bullets | Every ~1s (±0.3s), a random bottom-row alien fires 3×12px #FF4444 bullet downward at 250px/s. Max 3 alien bullets on screen. Remove when off-screen (y>600). | Alien bullets fire from bottom-row aliens at random intervals |
| T09 | Shields | Place 4 shields at x=140,300,460,620, y=480. Each shield is a 20×16 grid of 4×4px #00FF00 cells (arch shape — remove cells from bottom corners to form arch). Each cell independently destructible by any bullet. | Shields render as arches; bullets destroy individual cells |
| T10 | Collision — bullets | Player bullet ↔ alien: destroy both, add score (30/20/10 per type). Player bullet ↔ shield cell: destroy both. Alien bullet ↔ player: lose life, destroy bullet. Alien bullet ↔ shield cell: destroy both. | All collision pairs trigger correct outcomes |
| T11 | Mystery ship | Spawn #FF0000 48×16px saucer at y=35 every 20–30s (random). Moves left→right at 150px/s. Award random 50/100/150/300 points if hit. Remove when off-screen. Reset timer after exit or destroy. | UFO appears periodically, moves across, is hittable |
| T12 | Scoring & HUD | Display "Score: {N}" top-left, "Best: {N}" top-right (localStorage). Show lives as ship icons bottom-left. Show "Wave: {N}" bottom-right. | Score, high score, lives, wave all display correctly |
| T13 | Wave progression | When all 55 aliens destroyed: advance wave, reset alien grid, increase base speed by 10px/s per wave. If any alien y≥540: instant game over. | Level advances on clear; aliens reaching bottom ends game |
| T14 | Start & Game Over screens | Start: "SPACE INVADERS" y=220 48px #00FF00, alien legend, "Press Enter to Start" y=400. Game Over: overlay with score and restart. | Screens appear correctly; restart resets all state |
| T15 | Polish & debug | Fix remaining bugs. Ensure all acceptance criteria pass. Add metadata comment: `<!-- Space Invaders | spec:run1-opus-plan | built-by:{model} -->` | All section 11 criteria pass; comment header present |
