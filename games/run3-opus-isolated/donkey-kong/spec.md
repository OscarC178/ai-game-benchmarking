# Game Spec: Donkey Kong

## 1. Overview
Donkey Kong (Nintendo, 1981) — the original platformer. Mario (Jumpman) must climb a construction site of slanted girders while dodging barrels thrown by Donkey Kong to rescue Pauline at the top. Features the iconic Level 1 layout with 6 sloped platforms, ladders, and rolling/falling barrels. Gravity-based platforming with precise jump timing.

## 2. Canvas & Rendering
- Canvas size: 700×800px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left

## 3. Game Objects

### Mario (Player)
- **Shape:** Rectangle with simple detail — body block with head and legs (simplified: 2-color rectangle)
- **Size:** 24×32px
- **Color:** #CC0000 (red body), #FFAA77 (skin/face area — top 8px)
- **Starting position:** x=80, y=710 (bottom-left platform)
- **Movement:** Horizontal at 150px/s. Jump: initial velocity −340px/s upward, gravity 900px/s². Can move horizontally while jumping. Cannot jump while on a ladder.
- **Climbing:** On ladder: climb up/down at 100px/s. Mario snaps to ladder center-x while climbing.

### Donkey Kong
- **Shape:** Large brown rectangle with simple gorilla features
- **Size:** 64×56px
- **Color:** #885522 (brown body), #FFAA77 (face/chest 20×16px area)
- **Position:** x=100, y=80 (top-left platform, sitting)
- **Animation:** Periodically "tosses" a barrel — arm moves right (cosmetic, every 2–4 seconds)

### Pauline (Damsel)
- **Shape:** Small standing figure
- **Size:** 16×28px
- **Color:** #FF66AA (pink dress), #FFAA77 (skin)
- **Position:** x=310, y=38 (top platform, centered)
- **Animation:** "HELP!" text appears above her, blinking at 2Hz

### Platforms (Girders)
6 platforms, each a sloped beam (slight tilt). Platform definitions (left-x, right-x, left-y, right-y):
- **Platform 1 (bottom):** (30, 670) to (670, 710) — slopes right-down. Height: 8px. Color: #FF4444.
- **Platform 2:** (30, 570) to (670, 610) — slopes left-down (opposite tilt).
- **Platform 3:** (30, 470) to (670, 510) — slopes right-down.
- **Platform 4:** (30, 370) to (670, 410) — slopes left-down.
- **Platform 5:** (30, 270) to (670, 310) — slopes right-down.
- **Platform 6 (top):** (100, 100) to (500, 100) — flat (Donkey Kong's platform). Height: 8px.
- **Note:** Each platform tilts by ~40px over its length (the y difference from left to right end).

### Ladders
Vertical connectors between platforms. Each ladder: 20px wide, #00CCFF, with rung lines every 16px.
- **Ladder positions (x, top-y, bottom-y):** approximately:
  - L1: x=600, connecting platform 1 to platform 2
  - L2: x=100, connecting platform 2 to platform 3
  - L3: x=500, connecting platform 3 to platform 4
  - L4: x=150, connecting platform 4 to platform 5
  - L5: x=400, connecting platform 5 to platform 6
  - Plus 2–3 broken ladders (cosmetic, partial height, cannot be climbed fully)

### Barrels
- **Shape:** Oval/rectangle
- **Size:** 20×16px
- **Color:** #CC6600 (brown) with #884400 horizontal band at center
- **Spawn:** From Donkey Kong's position every 2–4 seconds (random interval)
- **Movement:** Roll along platforms following the slope at 120px/s. At platform edge, fall straight down to the next platform (gravity 600px/s²). Random chance (20%) to take a ladder down instead of rolling off the edge.
- **Direction:** Alternates with platform slope (right on odd platforms, left on even).

### Oil Drum
- **Shape:** Barrel/drum
- **Size:** 28×32px
- **Color:** #4444FF (blue drum) with #FF4400 flames on top (animated flicker)
- **Position:** x=60, y=680 (bottom-left, below platform 1)
- **Function:** Barrels reaching this drum ignite it (cosmetic — fire enemies are optional/bonus)

### Hammer (Power-up, 2 per level)
- **Shape:** T-shape
- **Size:** 20×20px
- **Color:** #FFCC00 (yellow head), #885522 (brown handle)
- **Positions:** x=200, y=on platform 2; x=400, y=on platform 4
- **Mechanic:** Collecting activates hammer for 8 seconds. Mario auto-swings (animation toggle every 100ms). Contact with barrel while hammer active: destroy barrel, +300 points. Cannot climb ladders while hammer is active.

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Move left |
| ArrowRight / D | Move right |
| ArrowUp / W | Climb ladder up |
| ArrowDown / S | Climb ladder down |
| Space | Jump |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Mario walks on platforms, affected by slope (y adjusts to match platform surface).
2. Mario can jump with Space — parabolic arc. Cannot double-jump. Can move horizontally while airborne.
3. At a ladder (within 8px of ladder x-center), ArrowUp/Down enters climbing mode. Mario snaps to ladder x. Cannot jump while climbing. Exits climbing at top/bottom of ladder onto adjacent platform.
4. Donkey Kong throws barrels every 2–4 seconds. Barrels roll along platforms following slope direction, fall to the next platform at edges, and have a 20% chance of descending via ladder instead.
5. Contact with a barrel = death (unless hammer is active).
6. Collecting a hammer: 8-second power-up. Mario auto-swings, destroying barrels on contact (+300 pts). Cannot climb ladders with hammer.
7. Jumping over a barrel (barrel passes under Mario during jump): +100 points.
8. Reaching Pauline at the top completes the level. Next level: barrels spawn faster (−0.5s interval, minimum 1s), barrel roll speed +20px/s.
9. Player starts with 3 lives. Game over at 0 lives.

## 6. Collision Detection

- Mario ↔ Barrel (normal): Mario dies
- Mario ↔ Barrel (hammer active): destroy barrel, +300 pts
- Mario ↔ Barrel (jumping over, barrel below Mario's feet): +100 pts (barrel passes underneath)
- Mario ↔ Platform: stand on surface, adjust y to match slope
- Mario ↔ Ladder (within 8px x-range): allow climbing
- Mario ↔ Hammer pickup: activate hammer power-up
- Mario ↔ Pauline zone (top platform): level complete
- Barrel ↔ Platform edge: barrel falls to next platform
- Barrel ↔ Ladder (20% chance): barrel descends ladder
- Barrel ↔ Oil drum: barrel is destroyed (drum ignites)

AABB for all entity collisions. Platform collision uses line-segment math for slope.

## 7. Scoring

- Starting score: 0
- Score display: top-left at (10, 24), #FFFFFF, 16px monospace
- Jump over barrel: +100 points
- Destroy barrel with hammer: +300 points
- Collect hammer: +0 (points come from smashing)
- Complete level: +500 points + time bonus (remaining time × 10)
- High score: localStorage, top-right

## 8. UI Elements

- **Score:** top-left "Score: {N}" 16px white monospace
- **High Score:** top-right "Best: {N}" 16px
- **Lives:** top-left below score, Mario icons (16×16px) plus "×{N}"
- **Level:** top-right below high score, "L={N}" 14px #AAAAAA
- **Bonus timer:** top-center, "BONUS: {N}" starting at 5000, counting down by 100 every 2 seconds. Visual timer bar below text.
- **Game Over screen:** #000000CC overlay. "GAME OVER" 40px white centered. Score. "Press Enter to Restart."
- **Start screen:** "DONKEY KONG" centered y=320, 48px #FF4444 monospace. Donkey Kong and Mario silhouettes. "Press Enter to Start" y=440, 20px #AAAAAA.
- **Level complete:** "STAGE CLEAR!" 36px #FFFF00 centered for 2 seconds, then advance.
- **Pause:** "PAUSED" centered 36px white on #000000CC overlay.

## 9. Audio (Optional / Bonus)
- Jump: 330Hz triangle, 50ms
- Walk: alternating 110/130Hz clicks at step rate
- Barrel smash: noise burst, 80ms
- Death: descending 440→55Hz, 500ms
- Level complete: ascending arpeggio, 400ms
- Hammer active: fast repeating 660Hz/880Hz toggle at 8Hz

## 10. Implementation Notes

1. **Sloped platforms** are the trickiest part. Mario's y-position must interpolate along the platform's slope as he walks. Implement as a line segment: y = leftY + (x − leftX) / (rightX − leftX) × (rightY − leftY). Mario stands 32px above this y.
2. **Barrel physics on slopes:** Barrels roll downhill following the platform slope. On a right-sloping-down platform, barrels roll right. When they reach the edge, they fall with gravity to the next platform.
3. **Jump-over detection:** Track whether a barrel was below Mario during his jump arc and Mario's feet were above the barrel's top. Score +100 per barrel jumped once per barrel per jump.
4. **Ladder entry tolerance:** Mario must be within 8px of a ladder's center-x to climb. While climbing, Mario is immune to gravity and horizontal input.
5. **Barrel-ladder choice:** When a barrel reaches a ladder's x-position at a platform edge, 20% chance it diverts down the ladder instead of falling off the edge. This creates unpredictability.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Mario walks on sloped platforms with correct y-tracking
- [ ] Mario jumps with gravity arc, can move horizontally in air
- [ ] Mario climbs ladders up and down
- [ ] Barrels roll along slopes and fall between platforms
- [ ] Some barrels randomly take ladders down
- [ ] Contact with barrel kills Mario (without hammer)
- [ ] Hammer power-up destroys barrels on contact
- [ ] Jumping over barrel scores 100 points
- [ ] Reaching Pauline completes the level
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, 700×800 canvas, inline style (black bg, centered), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame loop with delta-time. Canvas clears to #000000 each frame. | Blank canvas renders at 60fps |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Sub-states: DYING, LEVEL_COMPLETE. Enter starts/restarts. P pauses. | State transitions work correctly |
| T04 | Platform & ladder layout | Define 6 platforms as line segments with slopes: Platform 1 (30,670)→(670,710), P2 (30,570)→(670,610) opposite slope, P3–P5 alternating, P6 (100,100)→(500,100) flat. Render as 8px-tall #FF4444 filled trapezoids. Define 5+ ladders as vertical rectangles (20px wide, #00CCFF, rungs every 16px) connecting adjacent platforms. Add 2–3 broken ladders (partial, non-functional). | Platforms render with visible slopes; ladders connect platforms |
| T05 | Mario — walking & slope | Draw 24×32px Mario (#CC0000 body, #FFAA77 head) at (80,710). Move left/right at 150px/s. Y-position tracks platform slope using line interpolation: y = leftY + (x−leftX)/(rightX−leftX) × (rightY−leftY) − 32. Clamp to platform edges. | Mario walks on slopes; y follows platform surface smoothly |
| T06 | Mario — jumping | Space triggers jump: initial velocity −340px/s, gravity 900px/s². Horizontal movement continues during jump at 150px/s. Land on platform when feet reach platform surface y. Cannot double-jump. Cannot jump while climbing. | Mario jumps in parabolic arc; lands on platforms correctly |
| T07 | Mario — ladder climbing | When Mario is within 8px of ladder center-x and presses Up/Down, enter climbing mode. Snap x to ladder center. Move up/down at 100px/s. Exit climbing at ladder top (land on upper platform) or bottom (land on lower platform). Disable gravity and horizontal movement while climbing. Cannot climb broken ladders fully. | Mario climbs ladders; snaps to center; exits at top/bottom |
| T08 | Barrel spawning & rolling | Donkey Kong tosses a barrel every 2–4s (random). Barrel (20×16px, #CC6600) starts at DK's position and rolls along current platform following slope direction at 120px/s. At platform edge: 80% chance fall with gravity (600px/s²) to next platform; 20% chance take ladder down. Direction alternates per platform. Barrels reaching oil drum (x=60, y=680) are destroyed (drum animates flames). | Barrels spawn, roll on slopes, fall/take ladders, reach oil drum |
| T09 | Collision — barrels & death | Mario ↔ barrel (AABB): Mario dies. Play death animation (Mario spins/flashes for 0.8s). Decrement life. Respawn at start (x=80, y=710). At 0 lives → GAME_OVER. | Barrel contact kills Mario; death animation; lives decrement |
| T10 | Jump-over scoring | When Mario is airborne and a barrel passes beneath him (barrel top < Mario feet), score +100 once per barrel per jump. Display "+100" floating text at jump position, fades over 0.5s. | Jumping over barrel shows +100; score increments |
| T11 | Hammer power-up | Place 2 hammers (#FFCC00 T-shape, 20×20px) on platforms 2 and 4. Collecting activates 8s timer. Mario auto-swings (animation toggle 100ms). Barrel contact while hammer active: destroy barrel +300 pts. Cannot climb ladders with hammer. Hammer blinks in last 2s. | Hammer pickup works; barrels destroyed on contact; ladder blocked; timer expires |
| T12 | DK, Pauline & level complete | Render Donkey Kong (64×56px, #885522) at (100,80) with barrel-toss animation every throw. Render Pauline (16×28px, #FF66AA) at (310,38) with blinking "HELP!" text. Mario reaching Pauline's zone on top platform: "STAGE CLEAR!" 36px #FFFF00 for 2s, +500 pts + bonus timer remaining × 10. Next level: barrel interval −0.5s (min 1s), roll speed +20px/s. | DK and Pauline render; reaching top completes level |
| T13 | Scoring, timer & HUD | "Score: {N}" top-left 16px. "Best: {N}" top-right (localStorage). Lives as Mario icons. "L={N}" top-right. "BONUS: {N}" top-center starting 5000, −100 every 2s. If bonus reaches 0, Mario dies. | Score, lives, level, bonus timer all display and function correctly |
| T14 | Start & Game Over screens | Start: "DONKEY KONG" y=320 48px #FF4444, DK/Mario silhouettes, "Press Enter" y=440. Game Over: #000000CC overlay, "GAME OVER" 40px, score, restart. | Screens display correctly; restart resets all state |
| T15 | Polish & debug | Fix remaining bugs. Ensure all acceptance criteria pass. Add metadata comment: `<!-- Donkey Kong | spec:run1-opus-plan | built-by:{model} -->` | All section 11 criteria pass; comment header present |
