# Game Spec: Space Invaders

## 1. Overview

Space Invaders (Taito, 1978 — the game that launched the arcade industry). You are a laser cannon at the bottom of the screen. Above you, a grid of 55 alien invaders marches side to side, dropping one row closer to you each time they reach a screen edge. You shoot upward, one bullet at a time. They shoot downward, multiple bullets at once. Four destructible shield bunkers stand between you. A mystery ship occasionally streaks across the top for bonus points.

The genius of Space Invaders is a single emergent mechanic: **as you destroy aliens, the remaining ones move faster.** The grid is slow and almost relaxing with all 55 aliens alive. By the time you've killed 50 of them, the last 5 are screaming across the screen. This acceleration is not a separate speed setting — it falls directly out of how you implement the movement cycle. Get this right and the tension curve is automatic.

## 2. Canvas & Layout

- **Canvas:** 760×640px
- **Background:** #000000 (pure black — Space Invaders is stark)
- **HUD top:** y = 0–32. Score and high score.
- **Play area:** y = 32–590. Where all gameplay happens.
- **HUD bottom:** y = 590–620. Lives and level indicator.
- **Green baseline:** A 2px horizontal line at y = 588, color #00FF00. This is the "ground" — iconic to Space Invaders. The player and shields sit above it.
- **Frame rate:** 60 FPS render loop via `requestAnimationFrame` with delta-time.
- **Coordinate system:** Origin top-left.

## 3. Game Objects

### Player (Laser Cannon)

- **Shape:** A simplified cannon silhouette. Draw it as: a wide base rectangle (32px × 8px), a narrower middle rectangle (20px × 8px, centered), and a narrow barrel (4px × 10px, centered on top). All #00FF00. Total footprint: roughly 32px wide × 26px tall.
- **Y position:** Fixed. Base sits at y = 558 (30px above the green baseline).
- **Starting X:** Centered horizontally (x = 364).
- **Movement speed:** 200px/s, horizontal only.
- **Wall clamping:** Left edge ≥ 10, right edge ≤ 750.
- **Death animation:** When hit, the cannon is replaced by two alternating "explosion" frames (jagged shapes in #00FF00, roughly the same footprint but with irregular edges — draw them as 3–4 random rectangles scattered across the cannon's area). Alternate between the two frames every 100ms for 1 second, then the cannon reappears at center (or game over if no lives remain).

### Player Bullet

- **One bullet at a time.** The player cannot fire again until the current bullet hits something or exits the top of the screen. This constraint is fundamental to Space Invaders' pacing — it forces the player to aim rather than spray.
- **Shape:** Thin rectangle, 3px wide × 12px tall, #FFFFFF.
- **Speed:** 450px/s upward (negative y).
- **Origin:** Spawns at the tip of the cannon barrel.
- **Collision targets:** Aliens, shields, mystery ship, top of play area (y < 32 = bullet dissipates).

### Alien Grid

The heart of the game. 55 aliens arranged in a 11-column × 5-row formation.

**Row types (top to bottom):**

| Row | Alien type | Color | Points | Shape description |
|-----|-----------|-------|--------|-------------------|
| 1 (top) | Small | #FF0000 | 30 | A small shape: 12×10px. Draw as an 8px wide top row, 12px wide middle, two 2×4px "legs" on each side at bottom. Think of it as a small squid-like figure. |
| 2 | Small | #FF0000 | 30 | Same as row 1. |
| 3 | Medium | #FFE700 | 20 | A wider shape: 16×10px. Rounded top (draw as a rectangle with two small "antenna" protrusions on top + wider body + shorter legs). Bug-like. |
| 4 | Medium | #FFE700 | 20 | Same as row 3. |
| 5 (bottom) | Large | #00FF00 | 10 | Widest: 18×10px. Broad flat top, even wider middle row with "arm" protrusions on each side, narrow legs. Crab-like. |

**Rendering note:** These aliens were originally pixel art sprites. For this implementation, approximate them with filled rectangles composed to suggest the silhouette. Each alien should be recognizably different from the others. An alternative: draw them on a tiny offscreen canvas or describe them as a small pixel grid (e.g., an 8×8 or 12×8 bitmap array of 1s and 0s, rendered pixel-by-pixel at 2px scale). The bitmap approach is actually simpler and more authentic:

```
// Example: small alien, frame 1 (8×8 grid, each cell = 2×2px → 16×16px rendered)
[
  [0,0,0,1,1,0,0,0],
  [0,0,1,1,1,1,0,0],
  [0,1,1,1,1,1,1,0],
  [1,1,0,1,1,0,1,1],
  [1,1,1,1,1,1,1,1],
  [0,0,1,0,0,1,0,0],
  [0,1,0,1,1,0,1,0],
  [1,0,1,0,0,1,0,1],
]
```

Define two frames per alien type (frame A and frame B). Toggle between them each time the grid moves one step. This creates the iconic "marching" animation — the legs/arms shift between two poses in sync with the movement beat.

**Grid spacing:**
- Column spacing: 48px center-to-center (aliens are 16–18px wide, leaving ~30px gaps)
- Row spacing: 36px center-to-center
- Grid starts centered horizontally. First alien (top-left) at approximately x = 96, y = 96.

**Grid storage:** An array of 55 alien objects, each with:
```
{ alive: true, type: "small"|"medium"|"large", row: 0-4, col: 0-10, x: number, y: number, points: number }
```

Or a 2D array [row][col]. Dead aliens are marked `alive = false` and stop rendering/colliding, but their grid slot is preserved for movement calculations.

### Alien Movement — The Core Mechanic

The alien grid does NOT move continuously. It moves in **discrete steps** — one step at a time, with a **pause between steps**. The interval between steps is what creates the accelerating tempo.

**Step behavior:**

1. All living aliens shift **2px** in the current horizontal direction (left or right).
2. After each step, check: has any living alien's edge reached the side boundary (x ≤ 10 for left, x ≥ 740 for right)?
3. If yes: on the **next** step, the entire grid shifts **down by 20px** instead of sideways, and the horizontal direction reverses. Then sideways movement resumes in the new direction.
4. Each step, all aliens toggle their animation frame (A↔B). The animation is tied to the movement rhythm.

**Step timing (the acceleration):**

The interval between steps is a function of how many aliens are alive. With all 55 alive, the interval is long (the march is slow). As aliens die, the interval shortens (the march speeds up). This is the entire tension curve.

```
baseInterval = 800ms  (with all 55 aliens)
interval = baseInterval × (aliveCount / 55)
minimum interval = 50ms  (the last few aliens are terrifyingly fast)
```

So: 55 alive = 800ms between steps. 28 alive = ~400ms. 10 alive = ~145ms. 3 alive = ~43ms (clamped to 50ms). The last alien is an 800 × (1/55) ≈ 15ms interval, clamped to 50ms — roughly 20 steps per second, which looks frantic.

**Important:** This is not smooth acceleration. It's step-by-step. Kill one alien, the next step comes slightly sooner. Kill ten, you notice the march getting faster. Kill forty-five and the survivors are sprinting. The player can feel each kill making the remaining aliens angrier.

**Frame-accurate implementation:** Use an accumulator. Each frame, add `dt` to the accumulator. When it exceeds the current interval, execute one step and subtract the interval. Recalculate the interval whenever an alien dies.

### Alien Bullets

- **Active at once:** Up to 3 alien bullets simultaneously on screen. If 3 are active, no new ones fire until one is removed.
- **Shape:** 3px wide × 10px tall, #FFFFFF. Optionally: draw them as a zigzag pattern (alternating 2px left-right offsets every 3px of height) to distinguish from the player's straight bullet.
- **Speed:** 180px/s downward.
- **Firing logic:** Each step (when the aliens move), there is a chance an alien fires. Pick a random alive alien from the **bottom-most living row of each column** (only the alien with the clearest shot down its column can fire — aliens don't shoot through their own formation). Roll a probability: roughly 2–3% per eligible column per step at level 1, increasing by 0.5% per level (cap at 6%).
- **Collision targets:** Player, shields, green baseline (bullet dissipates at y > 588).

### Shields (Bunkers)

Four shield clusters evenly spaced between the player and the alien grid.

- **Count:** 4
- **Position:** Evenly distributed horizontally. Approximate x-positions for shield centers: 152, 304, 456, 608. Y-position: top edge at y = 480 (well below the alien grid's starting position, well above the player).
- **Size:** Each shield is roughly 52px wide × 36px tall.
- **Shape:** An arch/dome — a rectangle with a bite taken out of the bottom-center (a roughly 16px wide × 12px tall rectangular notch, creating the classic bunker shape with two legs).
- **Color:** #00FF00.

**Pixel-based erosion — the defining shield mechanic:**

Shields are not simple rectangles with HP. They erode pixel by pixel. Every bullet (player or alien) that hits a shield destroys a small cluster of pixels at the impact point (roughly a 6×6px circle of pixels removed). Over time, shields develop holes. Eventually, bullets pass through entirely.

**Implementation:** Represent each shield as a small offscreen canvas (or a 2D boolean array at pixel resolution). When drawing the shield, read this buffer. On bullet collision:
1. Check if the bullet overlaps any active (filled) pixel of the shield.
2. If yes: destroy pixels in a ~6px radius around the impact point (set them to empty). Remove the bullet.
3. Render the shield from its pixel buffer each frame.

This approach gives realistic, gradual destruction — chunks get blown out, holes form naturally, the player can see bullets starting to sneak through damaged areas.

**Alien collision with shields:** When the alien grid descends low enough that aliens overlap shields, the overlapping shield pixels are destroyed (the aliens eat through them). Check each alive alien's bounding box against the shield pixel buffers and clear any overlapping pixels. Aliens are not harmed by shields.

### Mystery Ship (UFO)

- **Shape:** A classic flying saucer silhouette, roughly 32px wide × 14px tall. Draw as: an ellipse or rounded rectangle (wide, short) with a small dome on top (a smaller rounded rectangle centered). Color: #FF0000.
- **Y position:** Fixed at y = 52 (just below the HUD, above the alien grid).
- **Movement:** Crosses the screen horizontally at 100px/s. Enters from one side, exits the other. Direction alternates each appearance (first from left, next from right, etc.).
- **Spawn timing:** First appearance after 25 seconds of gameplay. After that, appears every 20–30 seconds (random interval within that range). Only appears when there are at least 8 aliens alive (it doesn't show up for the final few).
- **Points:** Variable — 50, 100, 150, or 300. Classically, this was determined by the player's shot count, but for simplicity: pick randomly from [50, 100, 100, 100, 150, 150, 300] (weighted toward 100, with 300 as a rare jackpot).
- **On hit:** The ship is replaced by its point value displayed as floating text (same position, in #FFFFFF, 16px, visible for 1 second, then fades). Play a distinct sound.
- **On exit:** If it crosses the entire screen without being hit, it simply disappears. No penalty.
- **Does NOT fire.** The mystery ship is a target of opportunity only.

## 4. Controls

| Input | Action |
|-------|--------|
| Arrow Left / A | Move cannon left |
| Arrow Right / D | Move cannon right |
| Space | Fire (one bullet at a time) |
| Enter | Start game / Restart from game over |
| P or Escape | Pause / Unpause |

Keyboard input: held-key state map via keydown/keyup. Movement is continuous while held. Fire is edge-triggered (one shot per press — do NOT auto-fire while Space is held. Require the player to release and re-press for each shot. This preserves the deliberate, aimed shooting feel.)

## 5. Collision Detection

### Player Bullet ↔ Alien

Check the bullet's bounding box against each alive alien's bounding box. On hit:
- Mark alien `alive = false`
- Remove bullet (player can fire again)
- Add points
- Spawn a small explosion (see section 9)
- Recalculate step interval (aliens got faster)
- Check if all aliens are dead → level complete

### Player Bullet ↔ Shield

Check bullet against each shield's pixel buffer. On hit:
- Erode ~6px radius of pixels
- Remove bullet

### Player Bullet ↔ Mystery Ship

Check bounding box. On hit:
- Remove mystery ship
- Show points
- Remove bullet
- Play sound

### Alien Bullet ↔ Player

Check against the cannon's bounding box. On hit:
- Begin player death animation
- Remove bullet
- Decrement lives (after animation)

### Alien Bullet ↔ Shield

Same as player bullet ↔ shield. Alien bullets also erode shields.

### Alien ↔ Player Y-level

If any alive alien's bottom edge reaches y ≥ 558 (the player's row), the game immediately ends regardless of remaining lives. The aliens have landed. This is the fail state that drives urgency — the grid is constantly descending, and if the player takes too long, the aliens simply overrun them.

### Alien ↔ Shield Overlap

When aliens descend into shield territory, any alive alien's bounding box that overlaps a shield erases the overlapping shield pixels. This happens naturally as the grid drops lower and lower.

## 6. Scoring

| Target | Points |
|--------|--------|
| Large alien (bottom row) | 10 |
| Medium alien (rows 3–4) | 20 |
| Small alien (rows 1–2) | 30 |
| Mystery ship | 50, 100, 150, or 300 (random weighted) |

**High score:** `localStorage` key `"invaders_best"`. Loaded on init. Updated when current score exceeds it.

**Extra life:** Awarded once at 1,500 points. Maximum 5 lives.

## 7. Lives and Level Progression

**Starting lives:** 3.

**On death:**
1. Player death animation plays (1 second of alternating explosion frames).
2. All active bullets (player and alien) are removed from the field.
3. If lives remain: cannon respawns at center. Brief 1-second invulnerability (cannon blinks at 8Hz). Alien grid and movement continue from where they were — they do NOT reset.
4. If 0 lives: → GAME_OVER.

**Level completion** occurs when all 55 aliens are destroyed. On level clear:
1. Brief 1-second pause. "LEVEL CLEAR" text optional (the original didn't show it — the new wave simply appeared).
2. Reset the alien grid: all 55 alive, back at starting position.
3. Rebuild all four shields to full.
4. Increase difficulty:
   - Alien bullets fire more frequently (+0.5% per eligible column per step, cap at 6%)
   - Alien grid starts 20px lower per level (so they reach the player faster). Starting y: 96 for level 1, 116 for level 2, 136 for level 3 (cap at 176 — don't start them inside the shields).
   - `baseInterval` decreases by 50ms per level (min 500ms): 800, 750, 700, 650, 600, 550, 500. The speed curve stays the same shape but starts at a faster baseline.
5. Player keeps their score and current lives.

## 8. Game States

```
TITLE → PLAYING → (DEATH → PLAYING or GAME_OVER) → TITLE
           ↕
        PAUSED
```

### TITLE

- Black screen with the green baseline at y = 588
- **"SPACE INVADERS"** centered at y = 140, 42px bold monospace, #FFFFFF
- Below the title, a "character showcase" — display one of each alien type with its point value:
  ```
  =?? ........... 30 points
  =?? ........... 20 points  
  =?? ........... 10 points
  ??? ........... mystery
  ```
  Render the actual alien shape (frame A) next to its point value. Use the correct color for each. The mystery ship renders in #FF0000 with "= ? MYSTERY" next to it.
- **"Press Enter to Start"** at y = 450, 20px, #AAAAAA, blinking at 2Hz.
- **"Best: {N}"** at y = 500, 16px, #555555
- **Attract mode (optional but recommended):** A handful of aliens (maybe 5) march back and forth in the space above the text, changing animation frames as they step. Cosmetic — just gives the screen some life.
- Enter → PLAYING (level 1)

### PLAYING

- All game logic active: alien march, player movement, shooting, collisions.
- P or Escape → PAUSED.

### PAUSED

- All movement/timers freeze (alien step accumulator, mystery ship timer, everything).
- Overlay: #000000 at 60% opacity.
- "PAUSED" centered, 36px, #FFFFFF.
- "P to resume" below, 14px, #888888.
- P or Escape → PLAYING.

### DEATH (Sub-state of PLAYING)

- Player death animation plays (1s).
- Alien grid keeps marching during the animation (this is authentic — the aliens don't pause to mourn you). Alien bullets stop firing during this phase to give the player a moment.
- After animation: if lives > 0, respawn cannon + brief invulnerability, resume full gameplay. If lives = 0 → GAME_OVER.

### GAME_OVER

- Aliens and player disappear (or freeze in place — either works).
- "GAME OVER" centered at y = 270, 44px, #FF0000.
- "Score: {N}" at y = 330, 24px, #FFFFFF.
- If new high score: "HIGH SCORE!" at y = 365, 18px, #FFE700, pulsing.
- "Wave reached: {N}" at y = 395, 16px, #888888.
- "Enter to play again" at y = 450, 16px, #666666, blinking at 2Hz.
- Enter → TITLE.

## 9. Visual Effects

### Alien Explosion

When an alien is destroyed, render a small explosion sprite at its position for 200ms: a burst shape (8–10 small lines radiating outward from center, 6–8px long, in #FFFFFF). Then it vanishes. Simple. Don't overdesign this — the satisfaction comes from the gap in the formation and the speed-up, not from a fancy particle system.

### Mystery Ship Score Float

When the mystery ship is hit, its point value (as text, e.g., "300") appears at the ship's last position in #FFFFFF, 16px. It remains for 1 second, then fades out (opacity 1.0 → 0.0 over 300ms at the end).

### Player Death Explosion

Two jagged "wreckage" frames. Frame A: a few angular shapes exploding outward from the cannon's center. Frame B: different angular shapes. Alternate A↔B every 100ms for 1 second. Color: #00FF00 (same as cannon — it's the cannon being destroyed, not a fireball). After 1s, the area clears.

### Shield Erosion Glow (Optional)

When a shield pixel cluster is destroyed, briefly flash the eroded area #FFFFFF for 1 frame (16ms). Subtle but communicates the hit.

### Screen Borders

The original game had a thin colored border. Render a 1px #333333 line around the entire canvas perimeter. Understated.

## 10. Audio

Web Audio API. `AudioContext` on first user interaction.

Space Invaders has one of the most iconic soundscapes in gaming — the four-note descending march beat that speeds up with the aliens. This is worth implementing.

### The March Beat

**Four bass notes cycling:** As the aliens step, play one note per step, cycling through four frequencies:

```
Step 1: 80Hz
Step 2: 72Hz
Step 3: 64Hz
Step 4: 56Hz
(repeat)
```

Each note: square wave, 80ms duration, gain 0.3. The notes cycle regardless of which step they're on — just maintain a counter 0→1→2→3→0→1→... and advance it each step.

As the aliens speed up (step interval decreases), the beats come faster. This is automatic — you don't need to separately accelerate the music. The march beat IS the movement timing. When 55 aliens are alive and steps are 800ms apart, you get a slow, ominous heartbeat. When 5 aliens are left with 70ms intervals, the beat becomes a frantic buzz. This emergent audio is one of the most celebrated design moments in game history.

### Other Sounds

| Event | Sound | Implementation |
|-------|-------|----------------|
| Player fires | Sharp zap | 1200Hz square, 60ms, rapid pitch bend down to 400Hz, gain 0.2 |
| Alien destroyed | Crunch | 300Hz square, 80ms, pitch bend down to 100Hz, gain 0.25 |
| Player hit | Long low boom | 120Hz square, 600ms, gain 0.35, fade out |
| Mystery ship appears | Repeating high warble | 500Hz sine, amplitude-modulated at 8Hz (tremolo), continuous while the ship is on screen, gain 0.15. Stop when ship exits or is hit. |
| Mystery ship hit | Descending whistle | 1000Hz sine → 200Hz over 300ms, gain 0.2 |
| Extra life | Short fanfare | 880Hz→1100Hz, 80ms each, gain 0.2 |

All audio is optional. Graceful failure on any error.

## 11. HUD

### Top Bar (y = 0–32)

| Element | Position | Style |
|---------|----------|-------|
| "SCORE" label | x = 20, y = 14 | 13px monospace, #FFFFFF |
| Score value | x = 20, y = 30 | 17px monospace, #00FF00 |
| "HI-SCORE" label | Centered, x = 380, y = 14 | 13px monospace, #FFFFFF |
| High score value | Centered, x = 380, y = 30 | 17px monospace, #FF0000 |

### Bottom Bar (y = 590–620)

| Element | Position | Style |
|---------|----------|-------|
| Lives | x = 20, y = 608 | Display the lives count as a numeral followed by small cannon icons (12px wide miniatures of the player cannon, #00FF00), one per remaining life (excluding the active one). Max 4 icons. |
| "WAVE {N}" | Right-aligned, x = 730, y = 608 | 14px monospace, #AAAAAA |

### Green Baseline

A 2px tall filled rectangle from x = 0 to x = 780 at y = 588. Color: #00FF00. This is the "ground" of the game — player and shields exist above it. Iconic to the visual identity.

## 12. Implementation Notes

1. **The alien step system is not delta-time continuous movement.** The aliens do not glide. They jump 2px per step, with a pause between steps. The interval between steps is what changes. Use an accumulator:
   ```
   marchAccumulator += dt
   currentInterval = baseInterval × (aliveCount / totalAliens)
   if marchAccumulator >= currentInterval:
       performOneStep()
       marchAccumulator -= currentInterval
   ```
   After tab-switch (large dt), cap accumulated time to one step to prevent the grid from jumping many steps at once.

2. **Column-bottom firing.** To find which alien can fire from each column: iterate the column from bottom row (4) upward. The first alive alien is the shooter candidate. Only these aliens are eligible to fire. This prevents aliens from shooting through their own formation.

3. **Shield pixel buffer.** The cleanest approach: for each shield, create an `ImageData` object (or a plain 2D boolean array) at the shield's pixel resolution (52×36). Initialize it with the shield shape (true/filled where the shield exists, false where it doesn't, including the bottom notch). On bullet collision, clear a circular region. On render, iterate the buffer and draw filled pixels. This is fast enough for 4 shields at this resolution.

   Alternative: use four small offscreen `<canvas>` elements (one per shield). Draw the initial shape. Use `globalCompositeOperation = 'destination-out'` to erase pixels on impact (draw a filled circle in the erase zone). Render the offscreen canvas onto the main canvas each frame. This is arguably simpler and leverages the canvas API for pixel operations.

4. **Player bullet limit.** Track with a simple boolean `playerBulletActive`. Set true on fire, false when the bullet hits anything or exits the screen. Only allow firing when false.

5. **Alien bullet limit.** Maintain an array of active alien bullets (max length 3). On each alien step, if `alienBullets.length < 3`, pick an eligible shooter and spawn a bullet.

6. **Fire key debounce.** Space fires on the keydown event, not on continuous hold. Set a `spaceWasDown` flag. Only fire if Space is currently pressed AND it was not pressed last frame. This prevents holding Space from trying to fire every frame (it would just make a "click" sound of failure anyway, since only one bullet exists, but the intent should be edge-triggered).

7. **Alien descend offset is permanent.** When the grid hits a wall and descends, the y-offset applies to all aliens and persists. They don't go back up. Over the course of a level, the grid slowly ratchets downward. This is the implicit timer — even if the player doesn't die, the aliens will eventually reach the ground.

8. **Delta-time for player movement and bullets only.** The alien march is step-based (accumulator). Don't try to delta-time the alien positions — they move in discrete jumps.

9. **Mystery ship timer:** Track remaining time until next appearance. Only count down during PLAYING state (not during DEATH animation or PAUSED). When the mystery ship is on screen, suspend the next-appearance timer until it exits or is destroyed.

10. **The grid "edge detection" should check living aliens only.** The rightmost living alien determines when the grid hits the right wall, not the rightmost column slot (which might be dead). If column 10 is all dead but column 9 has a survivor, column 9's position determines the boundary. Similarly for the left side.

## 13. Acceptance Criteria

- [ ] Loads with no console errors
- [ ] Title screen with alien point values display and start prompt
- [ ] 55 aliens in a 5×11 grid, three distinct visual types
- [ ] Aliens march side-to-side in discrete steps, dropping one row at screen edges
- [ ] Aliens visibly accelerate as their numbers decrease
- [ ] Two-frame alien animation toggles with each step
- [ ] Player moves left/right and fires one bullet at a time
- [ ] Bullets destroy aliens on contact; correct points per alien type
- [ ] Four shields that erode pixel-by-pixel from both player and alien bullets
- [ ] Aliens fire downward (max 3 bullets); only bottom-of-column aliens can shoot
- [ ] Mystery ship crosses the top periodically; awards random bonus points on hit
- [ ] Player death animation on hit; respawn with brief invulnerability
- [ ] Aliens reaching the player's row ends the game immediately
- [ ] Level clears when all 55 aliens are destroyed; next wave starts harder
- [ ] March beat audio speeds up with alien count (four cycling bass notes)
- [ ] Score, high score (persisted), lives, and wave number display correctly
- [ ] Pause freezes all game logic
- [ ] Game over screen with score and restart option

## 14. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML scaffold | DOCTYPE, 760×640 canvas, #000000 background, centered, inline CSS, empty `<script>` | Black canvas renders, no errors |
| T02 | Game loop & input | `requestAnimationFrame` with delta-time (capped 50ms). Key-state map: arrows, WASD, Space (edge-triggered), Enter, P, Escape. | Smooth loop; keys tracked; Space fires once per press |
| T03 | State machine | TITLE, PLAYING (with DEATH sub-state), PAUSED, GAME_OVER. Transitions: Enter starts, P pauses, death/respawn/game-over. | All states reachable; transitions correct |
| T04 | HUD & baseline | Top: score + high score labels. Bottom: lives (count + cannon icons) + wave number. Green 2px baseline at y=588. | HUD renders correctly; baseline visible |
| T05 | Player cannon | Green cannon shape at y=558. Moves left/right at 200px/s with arrows/AD. Clamped to play area. | Cannon visible and moves smoothly |
| T06 | Player bullet | Space fires a single white bullet upward at 450px/s. One active at a time. Dissipates above y=32. | Bullet fires, travels up, disappears; can't fire two |
| T07 | Alien grid: rendering | 55 aliens in 5×11 formation. Three types with distinct shapes and colors. Two animation frames per type. Correct spacing and starting position. | All aliens visible, distinct types recognizable |
| T08 | Alien grid: movement | Step-based march. 2px horizontal per step. Hit edge → descend 20px, reverse. Animation frame toggles per step. Step interval = baseInterval × (alive/55), min 50ms. | Aliens march, descend at edges, accelerate as killed |
| T09 | Alien-bullet collision | Player bullet vs alive aliens (bounding box). Kill alien, remove bullet, award points, show explosion (200ms). Recalculate step interval. 0 aliens → level complete. | Aliens die; score updates; gap appears in formation; aliens speed up |
| T10 | Shields | Four bunkers at y=480. Arch shape with bottom-center notch. Pixel-buffer representation. #00FF00. | Four green shields render in correct positions and shape |
| T11 | Shield erosion | Player and alien bullets erode ~6px radius of shield pixels on impact. Bullets removed on shield hit. Aliens descending into shields erase overlapping pixels. | Shields develop holes; bullets stopped; aliens eat through shields |
| T12 | Alien bullets | Up to 3 active. Spawn from bottom-of-column aliens on march steps. 180px/s downward. Collision with player, shields, baseline. Fire probability increases with level. | Alien bullets rain down; hit player/shields; max 3 active |
| T13 | Player death & lives | Alien bullet hitting cannon → death animation (1s alternating explosion frames). Lives -1. Respawn at center with 1s blinking invulnerability. 0 lives → GAME_OVER. Aliens keep marching during death animation. | Death animation plays; respawn works; game over triggers |
| T14 | Mystery ship | Appears every 20–30s after initial 25s delay. Crosses at y=52 at 100px/s. Random weighted points on hit (50–300). Score floats for 1s. Alternates direction. Won't appear with <8 aliens alive. | UFO crosses screen; awards points; disappears after crossing or hit |
| T15 | Level progression | All aliens dead → new wave. Grid resets to starting (or lower) position. Shields rebuild. Fire rate increases. Base interval decreases. Starting y lowers per level (cap at 176). Player keeps score/lives. | Levels advance; difficulty noticeably increases |
| T16 | Alien landing check | Any alive alien reaching y ≥ 558 → instant game over, regardless of lives. | Aliens touching cannon row ends game immediately |
| T17 | Audio: march beat | Four cycling bass notes (80/72/64/56 Hz), one per alien step. Beat naturally accelerates as aliens die. | Ominous slow beat with 55 aliens; frantic buzz with few remaining |
| T18 | Audio: effects | Player fire (zap), alien destroy (crunch), player death (boom), mystery ship (warble while present), mystery hit (whistle), extra life. Graceful failure. | All sounds trigger correctly; march beat dominates soundscape |
| T19 | Title & game over screens | Title: "SPACE INVADERS", alien point legend, attract-mode aliens, start prompt, high score. Game Over: score, high score callout, wave reached, restart. | All screens render and transition correctly |
| T20 | Polish & testing | Full acceptance criteria pass. Edge cases: last alien at max speed, shooting during death anim (shouldn't fire), mystery ship during level transition, shield erosion edge pixels, rapid restart, tab-switch recovery. | All criteria met; game feels tight and complete |
