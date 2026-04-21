# Game Spec: Frogger

## 1. Overview

Frogger (Konami, 1981). You are a frog at the bottom of the screen. Your goal is to reach one of five home slots at the top. Between you and home are two gauntlets: first a highway with lanes of traffic trying to run you over, then a river with logs and turtles you must ride across (because the frog can't swim — fall in the water and you die). You move in discrete hops, one grid cell at a time. There is no continuous movement — each press of a direction key advances the frog exactly one cell.

The game's tension comes from two interlocking rhythms: the traffic lanes move at different speeds in alternating directions, creating shifting gaps you must thread through, and the river objects move laterally while you stand on them, carrying you sideways toward the edges of the screen. You're never safe standing still — on the road, something will hit you; on the river, you'll be carried off-screen. The only safe zones are the starting strip, the median between road and river, and the home slots once you've reached them.

Five home slots must be filled, one frog at a time. Fill all five to complete the level. Each level is harder — traffic and river objects move faster, gaps between them shrink.

## 2. Canvas & Layout

- **Canvas:** 644×740px
- **Background:** #000000
- **Cell grid:** 14 columns × 15 rows, each cell 46×46px
- **Grid origin:** (0, 26) — the grid starts 26px below the top of the canvas (leaving room for the HUD)
- **Pixel mapping:** Cell (col, row) has its top-left corner at pixel (col × 46, row × 46 + 26)
- **Row layout (top to bottom):**

| Row | Zone | Contents |
|-----|------|----------|
| 0 | Home | Five home slots (goal) with foliage between them |
| 1 | River | Log lane (right) |
| 2 | River | Turtle lane (left) |
| 3 | River | Log lane (right) |
| 4 | River | Turtle lane (left) |
| 5 | River | Log lane (right) |
| 6 | Median | Safe zone (purple/dark strip — resting area) |
| 7 | Road | Car lane (left) |
| 8 | Road | Car lane (right) |
| 9 | Road | Truck lane (left) |
| 10 | Road | Car lane (right) |
| 11 | Road | Car lane (left) |
| 12 | Start | Safe starting strip |
| 13 | HUD row | Lives + timer bar area |

- **Frame rate:** 60 FPS via `requestAnimationFrame` with delta-time.

The visual layout is: grass (home) at top, blue water in the middle-upper section (rows 1–5), a thin resting median (row 6), grey/dark road in the middle-lower section (rows 7–11), and grass at the bottom (row 12 — start). Row 13 is below the play area for the HUD.

## 3. Game Objects

### Frog (Player)

- **Size:** 38×38px (centered within a 46×46 cell, 4px padding on each side)
- **Color:** #22CC22 (bright green) body, #114411 (darker) legs/details
- **Shape:** Draw as a simplified top-down frog: a rounded rectangle body (28×24px) with four small leg protrusions (6×10px each, at the four corners, angled outward). Two eye bumps on top (4×4px circles, #AAFFAA). The frog faces the current movement direction — rotate or mirror the sprite based on the last hop direction.
- **Rendering:** Always aligned to the grid. The frog does NOT exist between cells — each hop is instantaneous (visually animate a short 80ms transition for feel, but logically the frog snaps from cell to cell).
- **Starting position:** Row 12, column 7 (center-bottom).
- **Hitbox:** Rectangle, 30×30px (slightly smaller than rendering for fairness).

### Hop Animation

When the player presses a direction, the frog hops one cell. Animate this over 80ms:
- Frame 1 (0–30ms): frog "crouches" (compress by 20% vertically, legs tuck in)
- Frame 2 (30–60ms): frog in mid-air (stretch 15% in hop direction, translate)
- Frame 3 (60–80ms): frog lands at new cell (normal shape)

During this 80ms window, the frog is between cells. Use linear interpolation for the visual position. **Input is blocked during the hop animation** — the player cannot input a new direction until the current hop completes. This prevents accidental double-hops.

### Vehicles (Road Zone — Rows 7–11)

All vehicles are rectangles that move horizontally at constant speed. They loop: when a vehicle exits one side of the screen, it reappears on the other.

| Row | Vehicle | Size (px) | Color | Direction | Speed (px/s) | Spacing |
|-----|---------|-----------|-------|-----------|-------------|---------|
| 7 | Sedan | 42×36 | #FFCC00 (yellow) | Left | 80 | ~140px gap |
| 8 | Race car | 42×36 | #FF4444 (red) | Right | 130 | ~160px gap |
| 9 | Truck | 88×36 | #CCCCCC (grey) | Left | 60 | ~200px gap |
| 10 | Sedan | 42×36 | #FF8800 (orange) | Right | 100 | ~120px gap |
| 11 | Race car | 42×36 | #FF44FF (pink) | Left | 140 | ~180px gap |

**Vehicle count per lane:** Space vehicles so there are 3–5 per lane at any time, with consistent gaps. Use the spacing value as the approximate distance between vehicles. Generate enough to fill the screen width plus one extra (so one is always entering from the off-screen side).

**Vehicle rendering:** Rounded rectangles. Sedans are single blocks. Trucks are longer (roughly 2 cells wide). Add minimal detail: a windshield rectangle (lighter color, 10×16px) near the leading edge.

**Collision with frog:** Rectangle overlap. If the frog and any vehicle overlap → death.

### Logs (River Zone — Rows 1, 3, 5)

Logs are platforms the frog can ride across the river. The frog MUST be on a log (or turtle) to survive in the river zone. Standing on water (no platform beneath) → death.

| Row | Log size (px) | Color | Direction | Speed (px/s) | Count |
|-----|--------------|-------|-----------|-------------|-------|
| 1 | 138×40 (3 cells) | #8B4513 (brown) | Right | 70 | 3 |
| 3 | 184×40 (4 cells) | #A0522D (sienna) | Right | 50 | 3 |
| 5 | 92×40 (2 cells) | #6B3410 (dark brown) | Right | 100 | 4 |

**Log rendering:** Rounded rectangles with horizontal bark-line details (2–3 thin #5C2D0A lines across the length). Logs are slightly shorter than the cell height (40px vs 46px) and vertically centered in their row.

**Log looping:** Logs enter from one side and exit the other, continuously. Maintain enough logs to cover the lane plus buffer.

**Frog on log:** When the frog occupies a river row and its center overlaps a log, the frog is "riding" that log. Each frame, the frog's x-position moves with the log's speed × dt. If the frog is carried beyond the screen edges (x < -20 or x > 660), the frog dies (drowned by going off-screen).

### Turtles (River Zone — Rows 2, 4)

Turtles serve the same function as logs (platforms to ride on) but move in the opposite direction and have a critical additional behavior: some turtles dive underwater periodically.

| Row | Group size | Turtle count per group | Color | Direction | Speed (px/s) | Groups in lane |
|-----|-----------|----------------------|-------|-----------|-------------|---------------|
| 2 | 138px (3 turtles) | 3 | #00AA44 (green) shell | Left | 60 | 4 |
| 4 | 92px (2 turtles) | 2 | #00AA44 shell | Left | 90 | 4 |

**Turtle rendering:** Each turtle in a group is a small rounded shape (38×32px) — an oval body (#00AA44) with a slightly lighter shell pattern on top (#33CC66 diamond or hexagon, 16×12px). Groups of turtles travel together as a single platform.

**Diving turtles:** In each lane, one group is a "diving" group. This group periodically submerges:
- **Cycle:** 4 seconds visible → 0.5s sinking animation → 2s submerged (invisible and non-solid) → 0.5s surfacing animation → repeat.
- **Sinking animation:** Turtles lower gradually (y offset increases 4px) and fade to 40% opacity over 0.5s.
- **Surfacing animation:** Reverse — rise and fade back in over 0.5s.
- **When submerged:** The turtles are not rendered and the frog CANNOT stand on them. If the frog is standing on a diving group when it submerges → the frog falls in the water → death.
- **Warning:** The sinking animation (0.5s of lowering/fading) IS the warning. The frog is safe during the sinking phase — only dies when fully submerged.

### Home Slots (Row 0)

Five goal positions evenly spaced across the top row. The frog must land in one to "score" it.

**Slot positions (column centers):** Columns 1, 4, 7, 10, 13 (roughly evenly spaced with foliage/lily-pad areas between them).

**Slot rendering:**
- **Empty slot:** A dark cove/opening in the top foliage — a 44×42px dark area (#001a00) framed by green bushes (#226622). A subtle lily pad shape (small ellipse, #33AA33, 20×12px) floats in each empty slot.
- **Filled slot:** When a frog reaches the slot, a small frog icon (#22CC22, 20×20px) appears in the slot permanently for the rest of the level. The lily pad is replaced by the sitting frog.
- **Blocked slot:** A frog has already been placed. Landing on a filled slot kills the frog (the slot is occupied). The player must aim for empty slots.

**Foliage between slots:** Rows 0 is mostly dense green vegetation (#226622 to #338833) with the five openings. Landing on foliage (not in a slot opening) kills the frog — you must land precisely in a slot.

**Home landing detection:** When the frog's center enters row 0, check if its x-position aligns with any empty slot's x-range (slot center ± 20px). If yes → slot filled, score awarded. If no (on foliage or on a filled slot) → death.

### Bonus Fly

Occasionally, a bonus insect appears in one of the empty home slots.

- **Appearance:** A small red or gold insect icon (10×10px, #FF4444 or #FFD700). Pulses slightly (scale oscillation 100%–110% at 3Hz).
- **Spawn:** After the first home slot is filled, there is a 30% chance per 5-second interval that a fly appears in a random empty slot. Only one fly at a time.
- **Duration:** The fly stays for 8 seconds, then vanishes.
- **Points:** Collecting the fly (by entering the slot it's in) awards 200 bonus points in addition to the normal slot-entry points.
- **Visual distinction:** The slot with a fly should be immediately obvious — add a slight glow or flash around the fly.

### Snake (Bonus Hazard — Level 3+)

Starting from level 3, a snake occasionally appears on log in the river zone.

- **Appearance:** A wavy S-shape, 30×14px, #CC2222, riding on a random log.
- **Behavior:** Sits on a log and rides with it. The snake occupies a portion of the log.
- **Hazard:** If the frog lands on the snake's portion of the log → death.
- **Duration:** 8–15 seconds, then disappears.
- **Spawn:** One at a time, every 10–20 seconds while there are logs visible.

### Crocodile (River Hazard — Level 4+)

Starting from level 4, a crocodile occasionally appears in home slots or the river.

**In home slot:** A crocodile head pokes out of an empty home slot. It opens and closes its jaws (two frames, alternating every 300ms). The slot is dangerous while the jaws are open (landing = death) but safe while they're closed (the frog can land on the crocodile's closed mouth to fill the slot). Duration: 6 seconds. A subtle reward mechanic — the player must time their arrival.

**In river (optional, advanced):** A crocodile body appears in a log lane, moving with the current. Its body is safe to stand on (like a log), but its head (front 30px, rendered with open jaws) is lethal. This adds a log-like platform that has a dangerous zone at one end.

## 4. Controls

| Input | Action |
|-------|--------|
| Arrow Up / W | Hop one cell up (toward home) |
| Arrow Down / S | Hop one cell down (toward start) |
| Arrow Left / A | Hop one cell left |
| Arrow Right / D | Hop one cell right |
| Enter | Start / Restart |
| P or Escape | Pause / Unpause |

**Critical input rule: one hop per press.** Each keypress produces exactly one hop. Holding a key does NOT auto-repeat. The player must release and press again for each hop. This tap-to-move mechanic is fundamental to Frogger — continuous movement would make the game trivially easy or impossibly chaotic.

Implementation: edge-triggered. On `keydown`, if the key was not already held (track state), initiate a hop. Ignore further keydown events for that key until a `keyup` is received. During the 80ms hop animation, buffer at most one input (if the player presses a direction during a hop, queue it and execute when the hop completes). Only buffer one — discard additional inputs during a hop.

**No diagonal movement.** Only cardinal directions. If the player presses Up and Right simultaneously, only one (the first detected) is processed.

**Boundary clamping:** The frog cannot hop off the left edge (column < 0), right edge (column > 13), or below the starting row (row > 12). The frog CAN hop up from row 1 into row 0 (the home row) — this is how you fill home slots.

## 5. Zone Rules Summary

| Zone | Rows | Ground color | Stationary frog | Hazards |
|------|------|-------------|----------------|---------|
| Home | 0 | Dark green foliage #226622 | Dies unless in an empty slot | Foliage (miss slot), filled slot, croc, water between slots |
| River | 1–5 | Blue water #0044AA | Dies (drowning — must ride a platform) | Water, diving turtles, off-screen carry, snake on log |
| Median | 6 | Purple #442266 | Safe | None |
| Road | 7–11 | Dark grey #222222 | Safe (but vehicles keep coming) | Vehicles |
| Start | 12 | Green #226622 | Safe | None |

**The road** is grey with faint lane markings (1px horizontal dashed white lines between rows 7–8, 8–9, 9–10, 10–11). Each road lane has a slightly different shade of dark grey.

**The river** is solid blue (#0044AA to #003388) with a subtle horizontal ripple effect — 2–3 thin wavy lines (#0055BB) that scroll slowly leftward at 10px/s. The water is always visible behind logs/turtles (logs and turtles render on top of the water).

## 6. Collision & Death

Frogger has many ways to die:

1. **Hit by vehicle** on the road (rectangle overlap, checked every frame).
2. **Falling in water** — frog is on a river row (1–5) and not overlapping any log or turtle group → instant death.
3. **Carried off-screen** — riding a log/turtle that carries the frog past x < -20 or x > 660.
4. **Diving turtles** — standing on turtles when they fully submerge.
5. **Missing a home slot** — hopping into row 0 but not aligned with an empty slot (landing on foliage).
6. **Occupied home slot** — hopping into a slot that already has a frog.
7. **Timer expired** — each life has a time limit (section 7).
8. **Snake on log** — hopping onto the snake portion of a log.
9. **Crocodile jaws open** — landing in a slot with an open-jawed crocodile.

**Death animation:** The frog flattens and turns red (#FF4444) briefly (200ms), then a small splash or impact effect plays (4–6 small particle lines radiating outward, fading over 300ms). Total death sequence: 500ms. Then respawn.

**Respawn:** If lives remain, the frog reappears at the start position (row 12, column 7) after a 1-second pause. All lane objects continue moving during the pause. The frog's timer resets.

**There is no invulnerability on respawn.** Frogger is immediate.

## 7. Timer

Each life has a **30-second time limit** to reach a home slot.

**Timer display:** A horizontal bar at the bottom of the screen (in the HUD area, y ≈ 720). Full width = 30 seconds. The bar shrinks from right to left as time elapses.
- Color: #00CC00 when > 10 seconds remain, #FFCC00 when 5–10 seconds, #FF4444 when < 5 seconds.
- Width: 200px at full, scales proportionally.

**When timer expires:** The frog dies (same death animation). Lose a life. Timer resets on respawn.

**Timer pause:** Timer does NOT tick during death animation, respawn pause, or game pause.

**Successful hop to home:** Remaining time awards bonus points (10 points per second remaining, rounded down). Timer resets for the next frog.

## 8. Scoring

| Event | Points |
|-------|--------|
| Forward hop (toward home) | 10 |
| Reaching a home slot | 50 |
| Time bonus (per second remaining) | 10 per second |
| Bonus fly in home slot | 200 |
| Level complete (all 5 homes filled) | 1,000 |

**Forward hop only.** Only upward hops (toward home) score 10 points. Sideways and backward hops score nothing. Points are awarded per unique row reached — hopping up to row 8 scores 10 points, but hopping back to row 9 and then up to row 8 again does NOT score again. Track the farthest-forward row reached on this life; only award 10 points when exceeding it.

**High score:** `localStorage` key `"frogger_best"`. Loaded on init, updated when exceeded.

**Extra life:** At 10,000 points. Once only. Maximum 6 lives.

## 9. Lives & Level Progression

**Starting lives:** 3.

**Level completion:** All 5 home slots filled. Award 1,000 bonus points. Brief celebration (1.5 seconds — all five home frogs blink, a jingle plays). Then:
- Clear all home slots (reset to empty).
- Reset frog to start position.
- Increase difficulty:

| Level | Vehicle speed multiplier | River speed multiplier | Timer | Gaps between vehicles |
|-------|------------------------|----------------------|-------|----------------------|
| 1 | 1.0× | 1.0× | 30s | Normal |
| 2 | 1.15× | 1.1× | 28s | Slightly tighter |
| 3 | 1.3× | 1.2× | 26s | Tighter + snake appears |
| 4 | 1.45× | 1.3× | 24s | Tight + crocodile |
| 5 | 1.6× | 1.4× | 22s | Very tight |
| 6+ | +0.1× per level (cap 2.5×) | +0.1× (cap 2.0×) | 20s (minimum) | Minimum viable |

**Gap tightening:** Reduce the spacing between vehicles by ~10% per level (minimum spacing: 60px — enough for the frog to barely fit). This increases the precision required to cross the road.

## 10. Game States

```
TITLE → PLAYING → (DEATH → RESPAWN → PLAYING) → LEVEL_CLEAR → PLAYING
            ↕                                         or
         PAUSED                                    GAME_OVER
```

### TITLE

- Road and river zones render with vehicles and logs in motion (attract mode).
- A frog sits at the start position, idle.
- **"FROGGER"** centered at y ≈ 250, 48px bold monospace. Color: cycle between #22CC22 and #FFFF44 every 500ms (green-yellow alternation).
- Below: a simple illustration — a 3-frame animating frog (crouch → hop → land, looping at 2Hz).
- **"Press Enter to Start"** at y ≈ 450, 18px, #AAAAAA, blinking.
- **"Best: {N}"** at y ≈ 490, 14px, #555555.
- Enter → PLAYING (level 1).

### PLAYING

- All game logic active: lane movement, collision, timer, input.
- P / Escape → PAUSED.

### PAUSED

- All movement and timers freeze.
- Draw a semi-transparent overlay: #000000 at 70% over the play area.
- "PAUSED" centered, 36px, #FFFFFF.
- "P to resume" 14px, #AAAAAA.
- P / Escape → PLAYING.

### DEATH

- Death animation plays (500ms).
- 1-second pause.
- Decrement lives.
- If lives remain → RESPAWN → PLAYING.
- If 0 lives → GAME_OVER.

### LEVEL_CLEAR

- All 5 slots filled.
- 1.5-second celebration: all home frogs blink at 6Hz, screen border flashes #22CC22 briefly.
- +1,000 points.
- Load next level: reset slots, increase difficulty.
- → PLAYING.

### GAME_OVER

- Lane objects continue moving (the world doesn't care that you died).
- "GAME OVER" centered at y ≈ 300, 40px, #FF4444.
- "Score: {N}" at y ≈ 350, 24px, #FFFFFF.
- If new high: "NEW BEST!" at y ≈ 385, 18px, #FFD700, pulsing.
- "Level reached: {N}" at y ≈ 415, 16px, #AAAAAA.
- "Enter to restart" at y ≈ 460, 16px, #888888, blinking.
- Enter → TITLE.

## 11. HUD

### Top (above play area, y = 0–25)

| Element | Position | Style |
|---------|----------|-------|
| Score | x = 16, y = 20 | "Score: {N}" 16px monospace, #FFFFFF |
| High score | x = 350 (centered), y = 20 | "Best: {N}" 14px monospace, #888888 |
| Level | Right-aligned, x = 620, y = 20 | "Lv {N}" 14px monospace, #AAAAAA |

### Bottom (below play area, y = 700+)

| Element | Position | Style |
|---------|----------|-------|
| Lives | x = 16, y = 720 | Small frog icons (16×16px, #22CC22), one per remaining life (not counting the active frog). Max 5 icons. |
| Timer bar | x = 300, y = 718, w = 200, h = 10 | Shrinking bar. Green → yellow → red. Outlined 1px #333333. |
| "TIME" label | x = 260, y = 724 | 11px monospace, #AAAAAA |

## 12. Visual Details

### Water

Rows 1–5 background: #003388 (deep blue). Render 3–4 horizontal wavy lines at different y-offsets within the water zone. Each line is a sine wave: `y = baseY + sin(x/40 + time × 2) × 2`, drawn as a 1px path in #0055BB. The waves scroll slowly left at 10px/s. This gives the water a subtle animated shimmer.

### Road

Rows 7–11 background: #1a1a1a. Between each lane, draw a 1px dashed center line — alternating 8px white (#444444) dashes and 8px gaps. This suggests road markings without being distracting.

### Median

Row 6: #332244 (dark purple). Flat, no detail. Maybe small pebble dots (#443355, 2×2px, scattered randomly — generate once and cache).

### Foliage (Row 0, start row 12)

Rich green (#226622) with darker (#114411) patches for depth. The home slot openings are darker recesses (#001a00) with the lily-pad accent inside each.

### Start Zone (Row 12)

Bright grass green (#33AA33) with small grid-line indentations suggesting tiles.

### Log Details

Horizontal bark lines (1px #5C2D0A) across each log at random-but-fixed intervals. Knot circles (4px diameter, #6B3410) placed 1–2 per log. Generate these per log on creation and cache them.

### Turtle Details

Shell: rounded body (#00AA44) with a geometric shell pattern on top (a small hexagonal or diamond outline in #33CC66). Legs: small stubs (3×6px) extending from each side. Head: small circle protruding from the front.

## 13. Audio

Web Audio API. `AudioContext` on first user interaction.

| Event | Sound | Implementation |
|-------|-------|----------------|
| Hop | Short click | 300Hz square, 30ms, gain 0.12 |
| Reach home | Satisfying chime | 523Hz→784Hz sine, 80ms each, gain 0.2 |
| Level complete | Victory jingle | C5→E5→G5→C6 (523→659→784→1047Hz), 70ms each, gain 0.22 |
| Death (vehicle) | Crunch | 150Hz square, 150ms + brief noise burst 50ms, gain 0.25 |
| Death (water) | Splash | Brief white noise → filter sweep high-to-low, 200ms, gain 0.2 |
| Timer warning (<5s) | Tick-tick | 800Hz square, 15ms, repeating at 2Hz, gain 0.1 |
| Bonus fly collected | Sparkle | 880Hz→1320Hz sine, 100ms, gain 0.18 |
| Extra life | Chime | 880Hz→1100Hz, 80ms each, gain 0.18 |

All audio optional. Graceful on failure.

## 14. Lane Object Spawning and Wrapping

### Vehicle Spawning

For each road lane, pre-generate a full set of vehicles that covers the screen width plus 200px buffer on each side. Vehicles are evenly spaced within the lane using the gap value from section 3.

**Wrapping:** When a vehicle exits one side of the screen (e.g., moving left and x + width < -50), reposition it to the other side (x = 700). This creates the illusion of endless traffic. Since vehicles are evenly spaced, the cyclical wrapping produces a consistent pattern.

### Log and Turtle Spawning

Same approach. Pre-generate and evenly space. Logs and turtle groups are wider than vehicles, so fewer fit on screen. Ensure at least one platform is always reachable from any horizontal position in each river lane — the player must never face an impossible gap. Test: with the frog at any x on the median, there should always be a reachable platform within a few seconds in each river lane.

### Object Pool

Use simple arrays. All vehicles, logs, and turtle groups for the current level are created at level start. Remove nothing — just wrap positions. The count per lane is fixed for the level.

## 15. River Platform Detection

Every frame while the frog is on a river row (rows 1–5):

1. **Check if the frog overlaps any platform** (log or non-submerged turtle group). Overlap = frog center point falls within the platform's bounding rectangle.
2. **If overlapping a platform:** The frog is safe. Apply the platform's horizontal velocity to the frog's x-position: `frog.x += platform.speed × platform.direction × dt`. Then clamp/check: if `frog.x < -20` or `frog.x > 660` → death (carried off-screen).
3. **If NOT overlapping any platform:** The frog is in the water → death (drowning).

**Check after hop:** When the frog hops into a river row, immediately check platform overlap. If the hop lands the frog directly in water (no platform at the landing cell), the frog dies. The death happens on landing, not gradually — there's no treading-water grace period.

**Grid snapping vs. continuous x:** The frog moves in grid hops vertically and horizontally, but its x-position on river rows becomes **continuous** due to platform carry. While riding a platform, the frog's x-position is no longer grid-aligned. When the frog hops up/down from a river row, snap to the nearest column (round x to the nearest cell center). When the frog hops left/right on a river row, move one cell from the current (potentially non-aligned) x-position.

This hybrid system — grid-snapped y, continuous-drifting x — is authentic to Frogger and essential for the river sections to feel right.

## 16. Home Slot Entry Logic

When the frog attempts to enter row 0 (hops up from row 1):

1. **Compute frog x-center** at the moment of the hop.
2. **For each of the 5 home slots**, check: is the frog's x-center within ± 20px of the slot's center x?
3. **If yes, and the slot is empty:**
   - Slot is filled (render a frog icon there for the rest of the level).
   - Score: +50 points + time bonus (10 × seconds remaining).
   - If bonus fly is present in this slot: +200 additional points.
   - If all 5 slots are now filled → LEVEL_CLEAR.
   - Otherwise: frog respawns at start (row 12, col 7). Timer resets. Forward-row tracker resets.
4. **If yes, but the slot is occupied:** Death (filled slot collision).
5. **If no slot matches:** Death (landed on foliage or between slots).

## 17. Implementation Notes

1. **Discrete Y, continuous X.** The frog's row (y-position in grid terms) is always an integer. But its x-pixel position can be fractional when carried by river platforms. All lane objects have continuous x-positions updated by dt. The grid is a logical construct for movement and collision zones, not a rendering constraint.

2. **Lane direction convention.** Define each lane's direction as +1 (rightward) or -1 (leftward). Vehicle/log velocity = speed × direction. This makes the update loop uniform.

3. **Platform carry must be frame-accurate.** Each frame, move the frog by exactly the platform's displacement that frame (velocity × dt). Don't snap the frog to the platform's center — the frog maintains its relative position on the platform. If the frog hopped onto the left end of a log, it stays on the left end as the log moves.

4. **Overlap detection for river.** Use the frog's current x-position (which may be non-grid-aligned) and the platform's current x-position and width. Check `frogCenterX >= platform.x && frogCenterX <= platform.x + platform.width`. Since platforms are wider than the frog, this center-point check is sufficient and forgiving.

5. **Delta-time all movement.** Vehicles, logs, turtles, and frog carry all use dt. Cap dt at 50ms.

6. **Turtle dive timing.** Each diving turtle group has its own phase offset (randomized on creation). One group per lane dives; the others stay surfaced permanently. Track dive state: SURFACED, SINKING, SUBMERGED, SURFACING. Use a timer per group. Only groups in SURFACED state are solid platforms.

7. **Level reset on clear.** Reset: all 5 home slots to empty, frog to start, farthest-row tracker, timer. Do NOT reset: score, lives, high score. Do update: speed multipliers, gap sizes, timer length, hazard spawning.

8. **Rendering order (back to front):**
   - Water background (rows 1–5)
   - Road background (rows 7–11)
   - Median background (row 6)
   - Start/Home backgrounds (rows 0, 12)
   - Water ripple effect
   - Logs
   - Turtles (skip submerged)
   - Vehicles
   - Snake (on top of its log)
   - Home slot content (filled frogs, bonus fly, crocodile)
   - Frog
   - Foliage overhang on row 0 (render OVER the frog to create the visual of the frog tucking into the slot)
   - Death animation / particles
   - HUD

9. **Home row foliage as an overlay.** The foliage in row 0 should partially cover items below it. Render the foliage greenery AFTER the frog and platforms, so it visually frames the home slot openings. The frog disappears "into" the slot. Home slot frogs render inside the opening, beneath the foliage overlay.

10. **Forward-row scoring.** Track `farthestRow` (initialized to 12 each life). When the frog hops forward to a new row that's numerically less than `farthestRow` (remember row 0 is the top), update `farthestRow` and award 10 points. This prevents farming points by hopping back and forth.

## 18. Acceptance Criteria

- [ ] Loads with no console errors
- [ ] Title screen with attract-mode lane animations
- [ ] Frog hops exactly one cell per key press (no continuous movement, no diagonal)
- [ ] Hop animation is brief (80ms) and blocks input during transition
- [ ] Five road lanes with vehicles of varying sizes, speeds, and directions
- [ ] Vehicle collision kills the frog
- [ ] Five river lanes with logs and turtle groups moving laterally
- [ ] Frog rides logs and turtles (x-position carried by platform)
- [ ] Falling in water (no platform) kills the frog
- [ ] Being carried off-screen on a platform kills the frog
- [ ] Diving turtles submerge periodically; frog dies if standing on submerged turtles
- [ ] Five home slots at the top; frog must land precisely in an empty slot
- [ ] Landing on foliage or a filled slot kills the frog
- [ ] All 5 slots filled completes the level
- [ ] 30-second timer per life (scales down with levels); expiry kills frog
- [ ] Timer bar changes color as time runs out
- [ ] Forward-only hop scoring (10 per new row reached)
- [ ] Difficulty increases per level (faster traffic, faster river, shorter timer)
- [ ] Score, high score (persisted), lives, timer display correctly
- [ ] Pause freezes everything
- [ ] Game over screen with score and restart

## 19. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML scaffold | DOCTYPE, 644×740 canvas, #000000, centered, inline CSS, `<script>` | Black canvas, no errors |
| T02 | Game loop & input | `requestAnimationFrame` + delta-time (capped 50ms). Key state for arrows/WASD (edge-triggered, one hop per press, input buffer depth 1 during hop animation). Enter, P/Escape. | Loop runs; each keypress = one hop; no held-key repeat |
| T03 | State machine | TITLE, PLAYING, PAUSED, DEATH, LEVEL_CLEAR, GAME_OVER. Transitions per spec. | All states reachable; transitions correct |
| T04 | Zone rendering | Draw all 15 rows: green home (row 0 with slot openings), blue water (1–5), purple median (6), grey road with lane markings (7–11), green start (12), HUD (13). Water ripple effect. | Play area renders with all zones identifiable |
| T05 | Frog rendering & hopping | 38×38px frog, direction-facing. Hop animation (80ms, crouch→stretch→land). Input blocked during hop. Grid-aligned landing. | Frog hops one cell per press; animation plays; can't double-hop |
| T06 | Vehicles | 5 road lanes with vehicles (3–5 per lane). Varying sizes, speeds, directions per spec. Continuous horizontal movement. Wrap at screen edges. | Vehicles stream across road lanes; visible and continuous |
| T07 | Vehicle collision | Rectangle overlap between frog and any vehicle → death. Death animation (500ms). Respawn after 1s. | Frog dies when hit; animation plays; respawn works |
| T08 | Logs | 3 river lanes with logs. Continuous movement, wrapping. Correct sizes and speeds per spec. Bark-line detail. | Logs stream across water; render with detail |
| T09 | Turtles | 2 river lanes with turtle groups (3 and 2 per group). Moving leftward, wrapping. One group per lane dives (4s up, 0.5s sink, 2s down, 0.5s surface). | Turtles visible; diving groups sink and surface on cycle |
| T10 | River platform riding | Frog on river row must overlap a platform or die. Frog x-position carried by platform each frame. Off-screen carry → death. Submerged turtles → death. | Frog rides platforms; drowns without one; dies at edges; dies on submerging turtles |
| T11 | Home slots | 5 home slot positions in row 0. Landing in empty slot: fill it, +50 pts + time bonus, respawn frog. Landing on foliage/filled slot: death. Filled slots show frog icon. | Slots fill correctly; precise alignment required; foliage is lethal |
| T12 | Level completion | All 5 slots filled → +1000 pts, celebration (1.5s), reset slots, increase difficulty. Speed multiplier, gap tightening, timer reduction per spec. | Levels advance; visible difficulty increase |
| T13 | Timer | 30s per life (scaling per level). Timer bar in HUD: green→yellow→red. Expiry → death. Pauses during death/pause. Time bonus on slot fill. | Timer counts down; visual feedback; expiry kills; bonus works |
| T14 | Scoring | 10 per new forward row reached. 50 per home slot + time bonus. 1000 per level clear. High score in localStorage. Extra life at 10k. | All scores correct; high score persists; forward-only counting |
| T15 | Bonus fly | Appears in random empty slot after first fill. 30% chance per 5s. Stays 8s. Pulses visually. +200 pts on collection. | Fly appears; pulses; scores on collection; vanishes on timeout |
| T16 | HUD | Score, high score, level (top). Lives (frog icons), timer bar with label (bottom). | All HUD elements render with correct values |
| T17 | Title & game over | Title: "FROGGER" + attract mode lanes + hopping frog animation + start prompt. Game over: score, high score, level, restart. Pause overlay. | Screens render and transition correctly |
| T18 | Audio | Hop click, home chime, level jingle, death crunch/splash, timer warning ticks, fly sparkle, extra life. All optional. | Sounds trigger correctly; game works silently |
| T19 | Snake & crocodile (levels 3+/4+) | Snake on random log (collidable hazard). Crocodile in home slot (open jaws = death, closed = safe). Both time-limited. | Hazards spawn at correct levels; collision rules correct |
| T20 | Polish & testing | All acceptance criteria. Edge cases: frog on platform edge when it wraps, frog at screen edge hopping sideways, simultaneous key presses, all-slots-but-one-filled with fly, death during platform carry, timer expiry during hop animation, level 5+ speed stress. | All criteria met; game feels fair and responsive |
