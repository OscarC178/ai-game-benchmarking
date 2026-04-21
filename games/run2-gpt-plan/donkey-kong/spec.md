# Game Spec: Donkey Kong

## 1. Overview
Donkey Kong — an early-1980s platform arcade game where the player climbs girders and ladders, jumps rolling barrels, uses hammers, and reaches Pauline at the top. It feels authentic when the stage geometry is readable, the barrel patterns create escalating pressure, and Mario’s movement combines deliberate platforming with quick reactions.

## 2. Canvas & Rendering
- Canvas size: 700×800px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left
- Stage style: sloped girders, ladders, simple character sprites, high-contrast HUD

## 3. Game Objects

### Mario
- **Shape/Sprite:** Simple pixel-art plumber figure
- **Size:** 24×32px
- **Color:** red shirt #DD3333, blue overalls #3366CC, skin #FFD39B
- **Starting position:** x=80, y=710
- **Movement:** Horizontal at 150px/s, jump velocity -340px/s, gravity 900px/s², climb ladders vertically at 120px/s

### Donkey Kong
- **Shape/Sprite:** Large ape figure
- **Size:** 64×56px
- **Color:** brown #8B4513 with tan face/chest #D2A679
- **Starting position:** x=100, y=80
- **Movement:** Static animation at top platform, performs barrel throw loop

### Pauline
- **Shape/Sprite:** Small standing character with blinking text
- **Size:** 20×32px
- **Color:** dress #FF5CAA, hair #AA5500
- **Starting position:** x=310, y=38
- **Movement:** Static at goal platform with blinking “HELP!” text

### Girders
- **Shape/Sprite:** Sloped platforms with rivet details
- **Size:** six full-width or near-full-width platforms, 12px thick
- **Color:** #FF3366 with darker edge #992244
- **Starting position:** stacked from bottom to top across the stage
- **Movement:** static

### Ladders
- **Shape/Sprite:** Vertical ladder rails with rungs
- **Size:** 20px wide, variable heights
- **Color:** #66CCFF
- **Starting position:** placed between girders, including some broken ladders
- **Movement:** static

### Barrel
- **Shape/Sprite:** Brown rolling barrel with hoop lines
- **Size:** 18×18px
- **Color:** #AA6633 with #552200 hoops
- **Starting position:** near Donkey Kong’s hands at the top platform
- **Movement:** Rolls along girders, may descend ladders, falls between platforms where appropriate

### Hammer Pickup
- **Shape/Sprite:** Yellow hammer icon
- **Size:** 20×20px
- **Color:** #FFD700 handle/head with brown grip
- **Starting position:** two stage pickup spots on mid-level platforms
- **Movement:** static until collected; then orbits Mario as a swing animation timer effect

### Oil Drum
- **Shape/Sprite:** Blue drum with flame
- **Size:** 28×32px
- **Color:** drum #3366CC, flame #FF8800
- **Starting position:** bottom-left near x=40, y=736
- **Movement:** static decoration and barrel source target zone

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Move left |
| ArrowRight / D | Move right |
| ArrowUp / W | Climb up ladder |
| ArrowDown / S | Climb down ladder |
| Space | Jump |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Mario moves along girders, jumps, and climbs ladders.
2. Gravity applies whenever Mario is not on a girder or ladder.
3. Donkey Kong continuously spawns rolling barrels.
4. Barrels roll along sloped girders in the local downhill direction.
5. Some barrels may descend ladders based on chance and path rules.
6. Touching a barrel without a hammer costs one life.
7. Collecting a hammer grants temporary barrel-smashing ability.
8. Jumping over a barrel awards points.
9. Reaching Pauline completes the stage and starts a new stage with reset barrel pressure.
10. Player starts with 3 lives.
11. A bonus timer counts down during the stage.
12. Game over occurs at 0 lives.

## 6. Collision Detection

- Mario ↔ Barrel: lose life unless hammer is active, otherwise destroy barrel
- Mario ↔ Hammer Pickup: activate hammer mode and remove pickup
- Mario ↔ Ladder: enter climb state when aligned and moving vertically
- Mario ↔ Pauline goal zone: complete stage
- Mario Jump Arc ↔ Barrel pass-under: award jump-over points if Mario clears the barrel cleanly

Use AABB for all collisions.

## 7. Scoring

- Starting score: 0
- Jump over a barrel: +100 points
- Smash barrel with hammer: +300 points
- Reach Pauline / clear stage: +1000 points
- Bonus timer adds remaining value on stage clear
- Score display: top-left, white text, 16px monospace
- High score: stored in localStorage, display at top-right

## 8. UI Elements

- **Score:** top-left
- **Lives / Health:** top-right as small Mario heads or numeric lives
- **Level indicator:** bonus timer and stage text in HUD
- **Game Over screen:** centered text “GAME OVER”, score, “Press Enter to restart”
- **Start screen:** “DONKEY KONG” centered at y=260 in 48px #FF3366 monospace, “Press Enter to Start” below
- **Pause:** P key toggles pause overlay

## 9. Audio (Optional / Bonus)
- Jump: short rising tone
- Hammer active: repeating rhythmic tick
- Barrel smash: bright hit sound
- Death: descending arcade tone

## 10. Implementation Notes

1. Girder slopes and ladder transitions must be handled carefully so Mario snaps to valid surfaces without jitter.
2. Barrel motion should follow platform slope direction and support ladder descent choices on marked ladders.
3. Hammer mode must temporarily replace normal jumping and destroy barrels on contact.
4. Stage-clear and death resets should restore barrel state cleanly without corrupting ladder/platform alignment.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Mario can run, jump, and climb ladders correctly
- [ ] Barrels roll along girders and threaten the player
- [ ] Hammer pickups work and can smash barrels
- [ ] Reaching Pauline clears the stage
- [ ] Bonus timer counts down during play
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
| T05 | Stage geometry | Build the six sloped girders, full ladder layout including broken ladders, Donkey Kong at the top-left platform, Pauline at the top goal, and the oil drum at bottom-left. | The full stage reads clearly and all main landmarks appear in correct areas |
| T06 | Mario movement and climbing | Implement grounded running, jumping with gravity, platform following on slopes, ladder enter/exit alignment, and vertical climbing on valid ladders. | Mario can move across girders and transition onto ladders without jitter |
| T07 | Barrel spawning and rolling | Spawn barrels from Donkey Kong on a repeating timer, roll them down platform slopes, and allow them to descend selected ladders or fall between levels where valid. | Barrels continuously travel through the stage in believable classic patterns |
| T08 | Hammer pickups and smashing | Add two hammer pickups, activate timed hammer mode on collection, disable normal jumping during hammer use if desired, and destroy barrels on contact while active. | Hammer mode is obvious, temporary, and reliably smashes barrels |
| T09 | Goal, bonus timer, and stage reset | Add the countdown bonus timer, award stage-clear points on reaching Pauline, then reset stage objects and Mario position for the next stage while preserving score/lives. | Pauline can be reached, the stage clears, and the next stage starts cleanly |
| T10 | Collision detection | Implement all collision pairs from spec section 6. AABB unless spec says otherwise. | Collisions trigger correct outcomes (log to console if needed) |
| T11 | Scoring | Implement score counter. Render score top-left, high score top-right (localStorage). | Score increments on correct events; persists on reload |
| T12 | Lives / health | Render lives/health indicator top-right per spec section 8. Decrement on hit. | Lives display correctly; game over triggers at 0 |
| T13 | Game Over screen | Render GAME OVER overlay with final score. Enter key restarts. | Overlay appears; restart resets all state |
| T14 | Start screen | Render title screen with game name and "Press Enter to Start". | Appears on load before game begins |
| T15 | Polish & debug | Fix any remaining bugs. Ensure all acceptance criteria from section 11 pass. Add the metadata comment header. | All section 11 criteria pass; comment header present |
