# Game Spec: Frogger

## 1. Overview
Frogger — an early-1980s lane-crossing arcade game where the player guides a frog through traffic, across a river, and into home bays. It feels authentic when movement is grid-snapped, lane patterns are easy to read, and the tension comes from timing against vehicles, drifting platforms, and a visible countdown timer.

## 2. Canvas & Rendering
- Canvas size: 600×700px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left
- Grid: 15 columns × 13 rows of 40×40px cells

## 3. Game Objects

### Frog
- **Shape/Sprite:** Rounded green square with two eyes
- **Size:** 32×32px within a 40×40 cell
- **Color:** #22CC22 body, #000000 eyes, #FFFFFF pupils
- **Starting position:** column 7 on the bottom safe row at y=520
- **Movement:** Hops one full cell per input with an 80ms hop animation

### Road Vehicles
- **Shape/Sprite:** Rectangular cars and trucks with small window details
- **Size:** 48×32px cars, 64×32px cars, and 96×32px trucks depending on lane
- **Color:** lane-specific: #CCCC00, #3344AA, #DD2222, #CCCCCC, #FF66AA
- **Starting position:** distributed across five road lanes at y=480, 440, 400, 360, 320
- **Movement:** Constant horizontal motion with lane-specific direction and speed

### Logs
- **Shape/Sprite:** Brown rounded rectangles with bark lines
- **Size:** 120×32px, 160×32px, or 200×32px depending on lane
- **Color:** #885522 or #774411
- **Starting position:** distributed across river lanes at y=240, 160, 80
- **Movement:** Horizontal drift at lane-specific speeds

### Turtle Groups
- **Shape/Sprite:** Connected turtle backs with heads
- **Size:** 80×32px for 2 turtles, 120×32px for 3 turtles
- **Color:** #448844
- **Starting position:** distributed across river lanes at y=200 and 120
- **Movement:** Horizontal drift with periodic dive cycle making them temporarily unsafe

### Home Bays
- **Shape/Sprite:** Rectangular bay openings with frog icon when filled
- **Size:** 48×36px
- **Color:** empty #000066, filled #22CC22
- **Starting position:** x=20, 140, 260, 380, 500 at y=40
- **Movement:** static

### Timer Bar
- **Shape/Sprite:** Horizontal bar
- **Size:** up to 580×12px
- **Color:** transitions from #22CC22 to #CCCC00 to #DD2222 as time runs down
- **Starting position:** x=10, y=680
- **Movement:** shrinks over time, resets on successful frog arrival or death/respawn

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Hop left |
| ArrowRight / D | Hop right |
| ArrowUp / W | Hop up |
| ArrowDown / S | Hop down |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Frog moves exactly one 40px cell per input.
2. Frog dies on contact with any road vehicle.
3. In river rows, frog must be supported by a log or non-submerged turtle group.
4. Supported frog rides horizontally with the platform beneath it.
5. If carried beyond the screen edge, frog dies.
6. Turtle groups periodically dive and become unsafe while submerged.
7. Reaching an empty home bay fills it and awards score.
8. Landing on a filled home bay or a gap between bays kills the frog.
9. Filling all 5 home bays completes the level.
10. Lane speeds increase by 15% on each new level.
11. Player starts with 3 lives.
12. Each frog has a 30-second timer.
13. Game over occurs at 0 lives.

## 6. Collision Detection

- Frog ↔ Vehicle: frog dies
- Frog center ↔ Log/Turtle: frog is carried safely
- Frog ↔ Water without support: frog dies
- Frog ↔ Home Bay: fill if empty; die if filled or invalid gap
- Frog ↔ Screen edge while on platform: die if carried off-screen

Use AABB, with river support based on frog center overlap.

## 7. Scoring

- Starting score: 0
- Forward hop to a new furthest row: +10 points
- Reaching a home bay: +50 points
- Time bonus on home arrival: remaining whole seconds × 2
- Filling all five bays: +1000 points
- Score display: top-left, white text, 16px monospace
- High score: stored in localStorage, display at top-right

## 8. UI Elements

- **Score:** top-left
- **Lives / Health:** bottom-left as frog icons and/or remaining count
- **Level indicator:** bottom-right, 14px #AAAAAA
- **Game Over screen:** centered text “GAME OVER”, score, “Press Enter to restart”
- **Start screen:** “FROGGER” centered at y=280 in 52px #22CC22 monospace, “Press Enter to Start” at y=380
- **Pause:** P key toggles pause overlay

## 9. Audio (Optional / Bonus)
- Hop: short 600Hz square chirp
- Splash: descending noise burst
- Squash: low 110Hz thump
- Home bay fill: ascending 440→880Hz tone

## 10. Implementation Notes

1. Hop input should be locked during the 80ms movement animation.
2. Frog must inherit platform velocity continuously while supported in river lanes.
3. Diving turtle cycles must be readable and deterministic enough for the player to anticipate.
4. Home bay logic must clearly distinguish safe bay centers from deadly gaps.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Frog hops exactly one cell per key press
- [ ] Traffic and river platforms move in correct lanes and directions
- [ ] Vehicle collisions and drowning both kill the frog
- [ ] Frog rides logs and turtles correctly
- [ ] Home bays fill correctly and invalid landings kill the frog
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
| T05 | Lane layout and moving hazards | Build the five road lanes and five river lanes with their exact y-positions, object sizes, colors, directions, and speeds. Render the median and safe start strip distinctly. | Each lane shows the correct obstacle or platform type moving in the proper direction |
| T06 | Hop animation and river carrying | Implement one-cell frog hops with 80ms animation lockout, then carry the frog horizontally when standing on logs or visible turtles. | Frog moves one cell per input and rides platforms smoothly |
| T07 | Road deaths and drowning | Detect vehicle hits, unsupported river positions, and carried-off-screen failures. Deduct a life and respawn the frog when these hazards occur. | Traffic kills, drowning kills, and off-screen carrying kills reliably |
| T08 | Diving turtles | Add visible/sinking/submerged/rising cycles for turtle groups in the two turtle lanes and disable support while submerged. | Turtle platforms visibly change state and become unsafe while underwater |
| T09 | Home bay resolution | Implement the five home bays at the specified x positions, filling empty bays with a frog marker and rejecting filled bays or gap landings as deaths. | Safe bays fill correctly and wrong landings are punished |
| T10 | Timer and level progression | Add the 30-second timer bar, reset it on each life, award time bonus on successful bay arrival, and increase all lane speeds by 15% after all five bays are filled. | Timer pressure works and later levels move faster |
| T11 | Collision detection | Implement all collision pairs from spec section 6. AABB unless spec says otherwise. | Collisions trigger correct outcomes (log to console if needed) |
| T12 | Scoring | Implement score counter. Render score top-left, high score top-right (localStorage). | Score increments on correct events; persists on reload |
| T13 | Lives / health | Render lives/health indicator top-right per spec section 8. Decrement on hit. | Lives display correctly; game over triggers at 0 |
| T14 | Game Over screen | Render GAME OVER overlay with final score. Enter key restarts. | Overlay appears; restart resets all state |
| T15 | Start screen | Render title screen with game name and "Press Enter to Start". | Appears on load before game begins |
| T16 | Polish & debug | Fix any remaining bugs. Ensure all acceptance criteria from section 11 pass. Add the metadata comment header. | All section 11 criteria pass; comment header present |
