# Game Spec: Galaga

## 1. Overview
Galaga — an early-1980s fixed shooter defined by a scrolling starfield, a disciplined enemy formation, aggressive dive attacks, and the signature capture-and-rescue dual-fighter mechanic. It feels authentic when the formation is orderly at rest, chaotic during attacks, and the player ship remains vulnerable but precise.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left
- Background detail: 80 white stars scrolling downward at 20px/s

## 3. Game Objects

### Player Ship
- **Shape/Sprite:** White 5-point fighter silhouette
- **Size:** 28×30px bounding box
- **Color:** #FFFFFF
- **Starting position:** x=400, y=550
- **Movement:** Horizontal only at 350px/s, clamped within canvas

### Dual Ship
- **Shape/Sprite:** Two merged white fighters side-by-side
- **Size:** 60×30px overall
- **Color:** #FFFFFF
- **Starting position:** same y=550 after rescue event
- **Movement:** Same horizontal movement as player ship, wider hitbox, fires double shot pattern

### Boss Galaga
- **Shape/Sprite:** Green insect-like sprite silhouette
- **Size:** 28×24px
- **Color:** #00CC00
- **Starting position:** formation row 1
- **Movement:** Sways with formation and performs dives/capture attacks; requires 2 hits

### Butterfly Enemy
- **Shape/Sprite:** Winged enemy silhouette
- **Size:** 24×20px
- **Color:** #FF4444
- **Starting position:** formation row 2
- **Movement:** Sways with formation and may dive in curved paths

### Bee Enemy
- **Shape/Sprite:** Small compact enemy silhouette
- **Size:** 20×18px
- **Color:** #FFCC00
- **Starting position:** formation rows 3–4
- **Movement:** Sways with formation and may dive in curved paths

### Bee Variant
- **Shape/Sprite:** Small compact enemy silhouette
- **Size:** 20×18px
- **Color:** #00BBFF
- **Starting position:** formation row 5
- **Movement:** Sways with formation and may dive in curved paths

### Player Bullet
- **Shape/Sprite:** Rectangle
- **Size:** 3×14px
- **Color:** #FFFFFF
- **Starting position:** ship nose
- **Movement:** Travels upward at 550px/s; max 2 active in single mode, 4 in dual mode

### Enemy Bullet
- **Shape/Sprite:** Rectangle
- **Size:** 3×10px
- **Color:** #FF6666
- **Starting position:** diving enemy position
- **Movement:** Travels downward at 300px/s

### Tractor Beam
- **Shape/Sprite:** Semi-transparent vertical beam
- **Size:** 40×200px
- **Color:** #00FF00 with translucent look
- **Starting position:** emitted from a boss enemy during capture attack
- **Movement:** Remains locked beneath boss during beam phase

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Move left |
| ArrowRight / D | Move right |
| Space | Fire |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Enemies begin in a 10×5 formation centered near x=400, y=160.
2. The entire formation sways horizontally by ±20px at 0.5Hz.
3. Every 2–3 seconds, 1–3 valid enemies may break formation and dive in curved attack paths.
4. Diving enemies can fire 1–2 bullets during their attack run.
5. Boss enemies require 2 hits and show a damaged state after the first hit.
6. Some boss dives become capture attacks that project a tractor beam.
7. Sustained player overlap with the tractor beam captures the ship.
8. Destroying the boss that is holding a captured ship rescues it and enables dual-ship mode.
9. Player starts with 3 lives.
10. Clearing all enemies advances to the next stage and increases dive aggression.
11. Game over occurs at 0 lives.

## 6. Collision Detection

- Player Bullet ↔ Enemy: damage or destroy enemy and award score
- Enemy Bullet ↔ Player: player loses a life
- Diving Enemy ↔ Player: both destroyed; player loses a life
- Tractor Beam ↔ Player: capture after sustained overlap
- Player ↔ rescued ship merge event: activate dual-ship mode

Use AABB for all collisions.

## 7. Scoring

- Starting score: 0
- Bee in formation: +50 points
- Bee while diving: +100 points
- Butterfly in formation: +80 points
- Butterfly while diving: +160 points
- Boss in formation: +150 points
- Boss while diving: +400 points
- Score display: top-left, white text, 16px monospace
- High score: stored in localStorage, display at top-center

## 8. UI Elements

- **Score:** top-left
- **Lives / Health:** bottom-left as small ship icons
- **Level indicator:** stage number at bottom-right in 14px #AAAAAA
- **Game Over screen:** centered text “GAME OVER”, score, “Press Enter to restart”
- **Start screen:** “GALAGA” centered at y=200 in 56px #FFCC00 monospace, enemy legend beneath, “Press Enter to Start” at y=420
- **Pause:** P key toggles pause overlay

## 9. Audio (Optional / Bonus)
- Player fire: 1200Hz square blip
- Enemy hit: short noise burst
- Player death: descending 660→60Hz tone
- Tractor beam: pulsing oscillation while active

## 10. Implementation Notes

1. Dive paths must be visibly curved rather than simple diagonal lines.
2. Formation sway should not break enemy slot ownership; enemies return to their original formation columns when possible.
3. Dual-ship mode should widen both the fire pattern and the player hitbox.
4. Boss capture state must persist on the specific boss carrying the player’s ship.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Player ship moves horizontally and fires correctly
- [ ] Enemy formation sways and dive attacks occur in curved paths
- [ ] Boss enemies take two hits and show a damaged state
- [ ] Tractor beam can capture and later restore a ship
- [ ] Stage progression works after clearing enemies
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
| T05 | Starfield and formation layout | Create the 80-star scrolling background and render the full 10×5 enemy formation centered at x=400, y=160 with correct row colors, sizes, spacing, and sway motion. | Background scrolls continuously and all enemies appear in the proper formation slots |
| T06 | Dive attacks and enemy fire | Select 1–3 enemies every 2–3 seconds for curved dive attacks, allowing them to fire 1–2 bullets during dives and then return or recycle appropriately. | Dive attacks occur regularly, follow curved paths, and produce enemy bullets |
| T07 | Boss damage and tractor beam | Implement 2-hit boss enemies with a damaged intermediate state and add special capture dives that project a 40×200 beam beneath the boss. | Bosses survive the first hit, change appearance, and can deploy visible beams |
| T08 | Capture, rescue, and dual ship | Add sustained beam overlap capture, track the boss holding the captured ship, and restore the ship into dual-ship mode when that boss is destroyed later. | A captured ship can be rescued and changes the player into clear dual-fire mode |
| T09 | Collision detection | Implement all collision pairs from spec section 6. AABB unless spec says otherwise. | Collisions trigger correct outcomes (log to console if needed) |
| T10 | Scoring | Implement score counter. Render score top-left, high score top-right (localStorage). | Score increments on correct events; persists on reload |
| T11 | Lives / health | Render lives/health indicator top-right per spec section 8. Decrement on hit. | Lives display correctly; game over triggers at 0 |
| T12 | Game Over screen | Render GAME OVER overlay with final score. Enter key restarts. | Overlay appears; restart resets all state |
| T13 | Start screen | Render title screen with game name and "Press Enter to Start". | Appears on load before game begins |
| T14 | Polish & debug | Fix any remaining bugs. Ensure all acceptance criteria from section 11 pass. Add the metadata comment header. | All section 11 criteria pass; comment header present |
