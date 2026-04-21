# Game Spec: Frogger

## 1. Overview
Frogger (Konami, 1981) — guide a frog across a busy road and a hazardous river to reach five home bays at the top. The game alternates between two distinct zones: a 5-lane road with traffic and a 5-lane river with floating logs and turtles. Vibrant, chunky pixel aesthetic. Timing and pattern-reading are everything.

## 2. Canvas & Rendering
- Canvas size: 600×700px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left
- Grid: 13 rows × 15 columns, each cell 40×40px (playfield 600×520px)
- Top 40px and bottom 40px reserved for UI; playfield starts at y=40

## 3. Game Objects

### Frog (Player)
- **Shape:** Rounded square with two small circles for eyes on top
- **Size:** 32×32px (centered in 40×40 cell)
- **Color:** #22CC22 body, #000000 eyes with #FFFFFF pupils
- **Starting position:** Column 7 (x=280), bottom safe row y=520
- **Movement:** Grid-snapped hops — 1 cell (40px) per keypress with a quick 80ms hop animation

### Road Lanes (5 lanes, y=360 to y=520 area)
Layout from bottom to top (player crosses bottom-up):
- **Safe strip (start):** y=520, #222244 (dark purple-grey)
- **Lane 1 (y=480):** Cars, #333333 road. Yellow cars 64×32px, #CCCC00, move right at 80px/s, spacing ~200px
- **Lane 2 (y=440):** Trucks, #333333 road. Blue trucks 96×32px, #3344AA, move left at 60px/s, spacing ~250px
- **Lane 3 (y=400):** Fast cars, #333333 road. Red cars 48×32px, #DD2222, move right at 140px/s, spacing ~180px
- **Lane 4 (y=360):** Trucks, #333333 road. White trucks 96×32px, #CCCCCC, move left at 70px/s, spacing ~220px
- **Lane 5 (y=320):** Race cars, #333333 road. Pink cars 48×32px, #FF66AA, move right at 160px/s, spacing ~240px

### Median (Safe Zone)
- **Position:** y=280
- **Color:** #224422 (dark green)
- **Function:** Safe resting spot between road and river

### River Lanes (5 lanes, y=120 to y=280 area)
Layout from median upward:
- **Lane 6 (y=240):** Small logs, 3 cells (120×32px), #885522, move right at 60px/s, spacing ~200px
- **Lane 7 (y=200):** Turtles, groups of 3 (120×32px), #448844, move left at 50px/s, spacing ~180px. Every 3rd group dives underwater for 2s every 5s.
- **Lane 8 (y=160):** Long logs, 5 cells (200×32px), #774411, move right at 40px/s, spacing ~300px
- **Lane 9 (y=120):** Turtles, groups of 2 (80×32px), #448844, move left at 70px/s, spacing ~160px. Every 2nd group dives.
- **Lane 10 (y=80):** Medium logs, 4 cells (160×32px), #885522, move right at 80px/s, spacing ~250px

### Home Bays (5 goal slots)
- **Position:** y=40, evenly spaced at x = 20, 140, 260, 380, 500
- **Size:** 48×36px each
- **Color:** #000066 (empty), #22CC22 (filled — show a small frog icon)
- **Spacing:** gaps between bays are water (#0044AA)

### Water Background
- **Rows y=40 to y=280 (river area):** #0044AA

### Road Background
- **Rows y=320 to y=520 (road area):** #333333

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowUp / W | Hop up one cell |
| ArrowDown / S | Hop down one cell |
| ArrowLeft / A | Hop left one cell |
| ArrowRight / D | Hop right one cell |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Frog hops exactly one grid cell per keypress with a brief 80ms animation.
2. On road lanes: hitting any vehicle kills the frog.
3. On river lanes: frog MUST be on a log or turtle group. Landing in water (no platform) kills the frog.
4. While on a log/turtle, frog moves with the platform (carried along).
5. If frog is carried off-screen left or right, it dies.
6. Diving turtles: when a turtle group is submerged, frog standing on it falls into water and dies.
7. Reaching an empty home bay scores points and marks that bay as filled (show frog icon).
8. Landing on an already-filled bay or on the gaps between bays (water) kills the frog.
9. Filling all 5 bays completes the level. Next level: all vehicles and platforms move 15% faster. Bays reset to empty.
10. Player starts with 3 lives.
11. 30-second timer per frog. If time runs out, frog dies. Timer bar displayed at bottom.
12. Game over when lives = 0.

## 6. Collision Detection

- Frog ↔ Vehicle (road lanes): frog dies
- Frog ↔ Log/Turtle (river lanes): frog rides platform
- Frog ↔ Water (river lane, no platform): frog dies
- Frog ↔ Home Bay (empty): score, fill bay
- Frog ↔ Home Bay (filled) or gap: frog dies
- Frog ↔ Screen edge (carried off): frog dies

Use AABB. Check frog center point against platform rectangles in river lanes.

## 7. Scoring

- Starting score: 0
- Score display: top-left at (10, 28), #FFFFFF, 16px monospace
- Hop forward: +10 points (only for net forward progress — returning doesn't re-score)
- Reaching home bay: +50 points
- Time bonus: remaining seconds × 2 points when reaching a bay
- Completing all 5 bays: +1000 bonus
- High score: localStorage, top-right

## 8. UI Elements

- **Score:** top-left "Score: {N}" 16px white monospace (on top bar y=0–40 area, overlaid on the home row)
- **High Score:** top-right "Best: {N}"
- **Lives:** bottom-left, small frog icons (20×20px green squares) plus "×{N}"
- **Timer:** bottom bar, green bar shrinking from right to left, 580px max width at y=680, height 12px. Color fades #22CC22 → #CCCC00 → #DD2222 as time decreases.
- **Level:** bottom-right "Level: {N}" 14px #AAAAAA
- **Game Over screen:** #000000CC overlay. "GAME OVER" 40px white centered. Score. "Press Enter to Restart."
- **Start screen:** "FROGGER" centered y=280, 52px #22CC22 monospace. Small frog icon. "Press Enter to Start" y=380, 20px #AAAAAA.
- **Pause:** "PAUSED" centered 36px white on #000000CC overlay.

## 9. Audio (Optional / Bonus)
- Hop: 600Hz square, 30ms
- Splash (death in water): noise burst descending, 150ms
- Squash (hit by car): 110Hz square, 100ms
- Fill bay: ascending 440→880Hz, 100ms
- Level complete: arpeggio 300ms

## 10. Implementation Notes

1. Frog movement is grid-snapped — no free-pixel movement. Each hop moves exactly 40px. Input should be debounced so holding a key doesn't zoom across the screen.
2. River riding: when frog is on a platform, add the platform's velocity to the frog's position each frame. This is the core river mechanic.
3. Diving turtles cycle: 3s visible → 1s sinking (blink) → 2s submerged → 1s rising (blink) → repeat. Frog dies if standing on submerged turtles.
4. Track forward progress for scoring — only the furthest row reached counts. Going back and forward again doesn't re-score.
5. Vehicles and platforms wrap around screen edges — they exit one side and re-enter the other seamlessly.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Frog hops one cell per keypress on a grid
- [ ] Vehicles move in correct lanes at correct speeds
- [ ] Frog dies on contact with vehicles
- [ ] Frog rides logs and turtles across river lanes
- [ ] Frog dies when landing in water (no platform)
- [ ] Reaching empty home bay scores points and fills it
- [ ] All 5 bays filled completes the level
- [ ] Timer counts down and kills frog at zero
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, 600×700 canvas, inline style (black bg, centered), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame loop with delta-time. Canvas clears each frame. Draw colored zone backgrounds: #222244 safe strip y=520, #333333 road y=320–480, #224422 median y=280, #0044AA river y=40–240, #000066 home bays y=40. | Colored zones render correctly |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Enter starts/restarts. P pauses. | State transitions work correctly |
| T04 | Frog & movement | Draw 32×32px #22CC22 frog at grid (7, bottom). Arrow keys move exactly 1 cell (40px) per press with 80ms hop animation. Clamp to canvas bounds (0–14 columns, rows within playfield). Debounce input — no movement during hop animation. | Frog visible, hops one cell per keypress, stays in bounds |
| T05 | Road vehicles | Create 5 road lanes with vehicles: Lane 1 (y=480) yellow cars 64×32 right 80px/s; Lane 2 (y=440) blue trucks 96×32 left 60px/s; Lane 3 (y=400) red cars 48×32 right 140px/s; Lane 4 (y=360) white trucks 96×32 left 70px/s; Lane 5 (y=320) pink cars 48×32 right 160px/s. Vehicles wrap around screen edges. | Vehicles render and move in correct directions/speeds; wrap seamlessly |
| T06 | Road collision | Frog ↔ vehicle AABB collision → frog dies. On death: play death animation (frog flashes red 3 times over 500ms), decrement life, respawn at start position. | Frog dies on vehicle contact; death animation plays; life decremented |
| T07 | River platforms | Create 5 river lanes with logs and turtles: Lane 6 (y=240) logs 120×32 right 60px/s; Lane 7 (y=200) turtle groups 120×32 left 50px/s; Lane 8 (y=160) long logs 200×32 right 40px/s; Lane 9 (y=120) turtle groups 80×32 left 70px/s; Lane 10 (y=80) logs 160×32 right 80px/s. All wrap around edges. | Platforms render and move correctly in river lanes |
| T08 | River riding & drowning | When frog is in river zone: check if frog center overlaps any platform. If yes, frog rides with platform (position += platform velocity × dt). If no platform overlap, frog dies (splash). If frog carried off-screen edge, frog dies. | Frog rides platforms; falls in water without platform; dies if carried off-screen |
| T09 | Diving turtles | Mark every 3rd group in lane 7 and every 2nd group in lane 9 as divers. Dive cycle: 3s visible → 1s sinking (blink at 8Hz) → 2s submerged (invisible, no collision) → 1s rising (blink) → repeat. Frog on submerged turtles dies. | Turtles dive cyclically; frog dies when standing on submerged turtles |
| T10 | Home bays | Render 5 bays at y=40 at x=20,140,260,380,500 (48×36px, #000066 empty). When frog reaches a bay row and overlaps an empty bay, fill it (#22CC22 with small frog icon), add 50 pts + time bonus. Landing on filled bay or gap between bays = death. | Bays fill on arrival; landing on gap or filled bay kills frog |
| T11 | Timer & level progression | 30s countdown timer per frog life. Render as shrinking bar at y=680 (green→yellow→red). Time out = death. When all 5 bays filled: +1000 bonus, advance level, reset bays, increase all speeds by 15%. | Timer counts down; death at zero; level advances on 5 bays |
| T12 | Scoring & HUD | "Score: {N}" top-left 16px. +10 per forward hop (track max row). +50 per bay. Time bonus. High score in localStorage top-right. Lives as frog icons bottom-left. "Level: {N}" bottom-right. | Score, lives, level, high score all correct |
| T13 | Start & Game Over screens | Start: "FROGGER" y=280 52px #22CC22, frog icon, "Press Enter" y=380. Game Over: overlay, score, restart prompt. | Screens display correctly; restart resets all state |
| T14 | Polish & debug | Fix remaining bugs. Ensure all acceptance criteria pass. Add metadata comment: `<!-- Frogger | spec:run1-opus-plan | built-by:{model} -->` | All section 11 criteria pass; comment header present |
