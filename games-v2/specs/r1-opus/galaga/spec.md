# Galaga — HTML5 Canvas Implementation Specification

## Overview

Galaga is a fixed-screen space shooter arcade game originally released by Namco in 1981. The player controls a single spaceship at the bottom of the screen and shoots upward to destroy waves of insect-like alien enemies. The enemies enter the screen in choreographed flight formations, settle into a grid pattern at the top, and periodically dive-bomb the player while shooting. The game loops through increasingly difficult stages indefinitely until the player's ships are exhausted.

This spec describes everything you need to implement a complete, faithful, and playable version as a single HTML5 Canvas file with no external dependencies.

---

## Deliverable

- **One file:** `galaga.html`
- **No external resources:** all graphics drawn with Canvas 2D API, all sounds synthesized with Web Audio API (or omitted gracefully if you prefer silent)
- **Target resolution:** 384×672 logical pixels (7:12 aspect ratio), scaled to fit the viewport while preserving aspect ratio
- **Frame rate:** 60 fps via `requestAnimationFrame`

---

## Screen Layout

```
┌──────────────────────┐  ← top of canvas (y = 0)
│  STAGE  01   HI-SCORE│  ← score bar (~40px tall)
│  1UP  00000  00000   │
├──────────────────────┤
│                      │
│   [enemy formation]  │  ← play field, enemies occupy
│                      │    roughly top 40% when settled
│                      │
│                      │
│   [player ship]      │  ← player locked to bottom strip
│  ■ ■ ■               │  ← remaining lives display
└──────────────────────┘  ← bottom of canvas (y = 672)
```

- **Score bar:** top 40px. Show "1UP", current score (6 digits, zero-padded), "HI-SCORE", high score, "STAGE", stage number.
- **Play field:** y = 40 to y = 632.
- **Bottom strip (y = 632–672):** remaining-lives icons (small ship sprites) on left; stage badge icons on right (optional).

---

## Player Ship

### Appearance
Draw a white or cyan fighter jet shape pointing upward. Suggest: a symmetrical delta-wing silhouette ~24×24px. Simple polygon fill is fine:
- Center point at top (nose): `(0, -12)`
- Wing tips: `(-12, 8)` and `(12, 8)`
- Engine/tail notch: `(-6, 12)`, `(0, 8)`, `(6, 12)`

Fill with a gradient or flat color (white, light cyan, or `#4af`). Add a small engine glow ellipse at the base.

### Position
- Horizontally centered at start.
- Y fixed at `y = 590` (bottom of play field).
- Moves left/right only. Cannot move up/down in normal play.

### Movement
- Speed: **4 px/frame** while key held.
- Clamped to horizontal play field bounds with ship half-width margin.
- Controls: **Left/Right arrow keys** or **A/D**.

### Shooting
- Press **Space** or **Z** to fire.
- Player may have at most **1 bullet on screen** at a time (classic behavior).
- Bullet: 3×12px white rectangle moving upward at **10 px/frame**.
- Cooldown: none beyond the one-bullet limit.
- Bullet originates from ship nose position.

### Lives
- Start with **3 lives**.
- Displayed as small ship icons in bottom-left strip.
- On death: brief explosion animation, then respawn at center after ~2 seconds. During respawn, player is invincible for 2 seconds (blinking).
- Game over when all lives exhausted.

### Death Condition
- Hit by any enemy bullet.
- Collided with a diving enemy ship (enemy passes through player's bounding box).

---

## Enemy Types

There are three enemy types arranged in a formation grid. All are drawn using simple geometric shapes or polygons — no sprites needed, but be colorful.

### 1. Bee (Grunt)
- **Count in formation:** 24 (bottom two rows of 8)
- **Color:** Yellow and red
- **Point value:** 50 (in formation), 100 (diving)
- **Shape suggestion:** A small winged insect shape ~16×16px. Two wing polygons on each side, small oval body. Wings can flap by alternating between two shapes each second.
- **Behavior:** Standard enemy. Dives alone.

### 2. Butterfly (Mid-tier)
- **Count in formation:** 16 (middle two rows of 8)
- **Color:** Blue and white/cyan
- **Point value:** 80 (in formation), 160 (diving)
- **Shape suggestion:** Rounded rectangular body with two large wing lobes on each side (~18×18px). Wings animate.
- **Behavior:** Standard enemy. Dives alone or in small groups.

### 3. Boss Galaga (Captain)
- **Count in formation:** 4 (top row, 4 spread out with gaps)
- **Color:** Red and purple/magenta, larger (~22×22px)
- **Point value:** 150 (in formation), 400 (diving solo)
- **Shape suggestion:** Beetle-like. Wider body, claw-like appendages, distinct head.
- **Special ability:** **Tractor Beam** (see below).
- **Dual Boss:** If you shoot one of the two Boss Galaga escort fighters first (not the Boss itself), the Boss can capture the player's ship and later appear in formation with the captured ship beside it. Worth 1000 pts to destroy the dual boss; rescued ship joins player (dual fighter mode — see below).

---

## Formation Layout

When all enemies have entered and settled, they sit in a 10-column × 5-row grid, roughly centered horizontally in the upper play field (~y = 80 to y = 240).

```
Row 0 (y≈80):   _ B _ _ B _ _ B _ _   ← 4 Boss Galaga, cols 2,3,6,7 (or similar)
Row 1 (y≈120):  M M M M M M M M M M  ← Actually butterflies occupy rows 1-2
Row 2 (y≈150):  M M M M M M M M M M
Row 3 (y≈190):  G G G G G G G G G G  ← Bees occupy rows 3-4
Row 4 (y≈220):  G G G G G G G G G G
```

Where B = Boss Galaga (4 total), M = Butterfly (16 total), G = Bee (24 total).

**Formation as a unit** slowly drifts left and right, bouncing off invisible walls (~20px from edge), moving ~0.5 px/frame. The entire grid moves together.

Enemy positions are stored relative to formation origin. Each enemy has a grid slot `(col, row)` and an offset from origin. When an enemy returns from a dive, it flies back to its grid slot.

---

## Stage Entry (Challenging Stage entrance / normal wave entrance)

At the start of each stage, enemies enter the screen in a scripted flight pattern before settling into formation. They do **not** shoot during entry.

### Entry Flight Path

Enemies enter in small groups sequentially, each following a curved Bézier or arc path from off-screen to their formation slot:

1. **First group** (Bees, right side): fly in from top-right, loop around in a wide arc, settle into bottom-right of formation.
2. **Second group** (Bees, left side): mirror of first.
3. **Third group** (Butterflies): fly in from top, spiral inward, settle into middle rows.
4. **Fourth group** (Boss Galaga): enter last, dramatic loop from top-center, settle into top row.

Groups enter with a ~20 frame stagger between individual ships within a group. Total entry sequence takes roughly 10–15 seconds.

**Simplified entry you can implement:** Each enemy follows a series of 3–5 waypoints defined per group, moving at ~3 px/frame, using simple lerp or arc movement between waypoints. When within ~4px of their formation slot, they snap in and enter the "in-formation" state.

---

## Enemy AI — Diving

Once all enemies have settled (or after entry begins in later stages), enemies begin to dive.

### Dive Trigger
- Every 2–4 seconds (random), pick a random enemy from those in formation.
- On later stages, 2–3 enemies may dive simultaneously.
- Boss Galaga is triggered to dive with escorts occasionally.

### Dive Path
A diving enemy leaves its formation slot and follows a curved path toward the player:

1. **Swoop phase:** Accelerate off in an arc (down and to one side), curve around.
2. **Attack phase:** Head toward player's current X position.
3. **Exit phase:** If not shot, continue off-screen bottom, then loop around from top and re-enter formation slot from above.

Speed during dive: ~3–5 px/frame, faster in later stages.

**Implementation suggestion:** Define dive as a sequence of Bézier curve segments. A simple approach:
- Use a cubic Bézier from current position through two control points to a point below the screen.
- Then a straight move off-bottom.
- Then reappear at top, arc back to formation slot.

### Enemy Shooting During Dive
- Diving enemies shoot bullets downward, aimed at player's X at time of shot.
- One bullet per dive, approximately halfway through the dive.
- Boss Galaga may shoot 2 bullets.
- Enemy bullets: small red/orange pixel (4×8px), speed ~5 px/frame downward.
- Multiple enemy bullets can be on screen simultaneously (up to ~6).

### Return to Formation
After exiting bottom of screen, the enemy reappears at the top and follows its scripted arc path back to its grid slot. It re-enters formation state when close enough to snap in.

---

## Boss Galaga — Tractor Beam

This is a special mechanic unique to Boss Galaga enemies.

### Trigger
- Occasionally (once per stage, or probabilistically), a Boss Galaga dives **alone** (no escorts if they're dead).
- When the Boss reaches approximately y = 300 (mid-field) and player is roughly aligned horizontally (within 60px), it **activates the tractor beam**.

### Tractor Beam Behavior
- A wide cone/beam extends downward from the Boss (~40px wide at base, 80px wide at tip), colored blue with an animated pulsing glow.
- Beam height extends down approximately 120px below the Boss.
- **If the beam overlaps the player ship:** The player ship slowly rises upward (regardless of player input), moving at ~2 px/frame toward the Boss.
- Once the player ship reaches the Boss: **capture animation** plays (ship shrinks and docks next to the Boss). Player loses a life. If no lives remain, this triggers game over differently — the captured ship counts as lost.
- The Boss then returns to formation with the captured ship displayed next to it as an icon.
- **Capture shot:** The tractor beam can be interrupted by shooting the Boss while the beam is active. Boss dies, beam cancels, player ship (if being pulled) is rescued (no life lost). Award 1000 pts.

### Rescue / Dual Fighter Mode
- If the captured ship is still in formation (Boss not yet destroyed), the player can shoot the dual-Boss (Boss + captured ship).
- When hit, the dual-Boss takes damage: first hit destroys the Boss half, **rescuing the captured ship** — it flies down and merges with the player's ship.
- **Dual Fighter Mode:** Player controls TWO ships side by side. Both ships shoot simultaneously (staggered slightly). Both can die independently. 1000 pts for the rescue shot.
- If one of the dual ships is hit, the player reverts to single ship.

---

## Collision Detection

Use axis-aligned bounding box (AABB) collision:

| Collider A | Collider B | Result |
|---|---|---|
| Player bullet | Enemy | Enemy dies, score awarded |
| Enemy bullet | Player | Player dies |
| Enemy (diving) | Player | Both die (enemy destroyed, player dies) |
| Player bullet | Enemy bullet | No interaction (bullets pass through each other) |
| Tractor beam region | Player | Begin capture sequence |

**Recommended hitboxes** (smaller than visual size for fairness):
- Player: 18×14px centered on ship
- Player bullet: 2×10px
- Enemy (bee/butterfly): 12×12px centered
- Boss Galaga: 16×16px centered
- Enemy bullet: 3×6px
- Tractor beam: rectangle beneath Boss, 40px wide × 120px tall

---

## Scoring

| Event | Points |
|---|---|
| Bee in formation | 50 |
| Bee diving | 100 |
| Butterfly in formation | 80 |
| Butterfly diving | 160 |
| Boss Galaga in formation | 150 |
| Boss Galaga diving (solo) | 400 |
| Dual Boss Galaga (both ships) | 1000 |
| Captured ship rescued | 1000 |
| Challenging Stage — all destroyed | Bonus (see below) |

**Extra life:** Award an extra life at 20,000 points (one time only, or optionally also at 70,000).

**Hi-Score:** Track in a local variable (not persistent unless you add localStorage). Display on screen. Update if current score exceeds it.

---

## Challenging Stages

Every 3 regular stages, a **Challenging Stage** occurs (Stage 3, 6, 9, etc.).

### Rules
- No formation. Enemies fly in scripted paths across the screen in rapid groups.
- Player cannot die — no enemy bullets, no collision death.
- Player has unlimited bullets (or at least 2 on screen at once).
- Enemies fly across and off-screen; player has one pass to shoot them.
- Duration: ~30 seconds or until all enemies have passed.
- Enemies that are not destroyed simply exit and are not seen again.

### Scoring Bonus
- Hitting all enemies in the stage awards a bonus:
  - "PERFECT" — 10,000 pts (if every single enemy destroyed)
  - Otherwise: 100 pts per enemy hit, no bonus.
- Display result on screen: "HIT = XX / 40" and bonus if achieved.

### Enemy Patterns (Challenging Stage)
Enemies fly in from various sides in groups of 4–8, following sine-wave or circular arc paths. Suggest ~40 total enemies per challenging stage. They move faster than in regular stages.

---

## Stage Progression

After all enemies are destroyed in a regular stage:
- Brief pause (~1.5 seconds).
- "STAGE XX" card displayed.
- Next stage begins with full formation re-entry.

Difficulty increases per stage:
- Enemy dive speed: +0.2 px/frame per stage (cap at ~7 px/frame)
- Dive frequency: reduce interval by 0.1s per stage (floor ~1s)
- Enemy bullets: speed +0.15 px/frame per stage (cap ~8)
- Number of simultaneous divers: increases from 1 at stage 1 to max 3 by stage 5+
- Entry speed: slightly faster each stage

---

## Game States

Implement a simple state machine:

```
TITLE → PLAYING → STAGE_INTRO → ENTRY → BATTLE → CHALLENGING_STAGE
                                                 ↓
                                              STAGE_CLEAR → STAGE_INTRO (loop)
                                                 ↓
                                              GAME_OVER → TITLE
```

### TITLE
- Show "GALAGA" in large text (draw each letter with canvas paths or just use `fillText` with a retro font — `monospace` or `'Press Start 2P'` if you embed a Google Font, but no external deps means stick to system monospace).
- Show "PRESS ENTER TO START" blinking.
- Show hi-score.
- Show a looping demo of enemies entering formation (optional).

### STAGE_INTRO
- Display "STAGE X" for ~2 seconds.
- Black screen or darkened play field.

### ENTRY
- Enemies fly in to formation.
- Player can move but not shoot (optional — some versions allow shooting during entry).

### BATTLE
- Main gameplay loop.
- Enemies in formation, diving, shooting.
- Player shooting.
- Win condition: all enemies destroyed → STAGE_CLEAR.
- Lose condition: all lives lost → GAME_OVER.

### STAGE_CLEAR
- Brief celebration (flash screen or "STAGE CLEAR" text for 1.5s).
- If next stage is a challenging stage: transition to CHALLENGING_STAGE.
- Otherwise: STAGE_INTRO.

### GAME_OVER
- Show "GAME OVER" for 3 seconds.
- Show final score and hi-score.
- After 3 seconds (or press Enter), return to TITLE.

---

## Visual Style

Replicate the dark arcade aesthetic:
- **Background:** Pure black `#000`.
- **Starfield:** ~80 stars, small white/blue dots at varying brightness, slowly drifting downward at 0.3–1 px/frame (parallax optional with 2–3 layers).
- **All colors:** Bright saturated colors against black. No pastels.
- **Text:** Use `ctx.font = '16px monospace'` or similar. White or yellow for UI, red for "GAME OVER".
- **Flash effects:** When an enemy is hit, flash the grid cell white for 2 frames before disappearing.
- **Explosions:** On enemy death, draw an expanding circle or burst of 6–8 short lines radiating outward, animated over 20 frames, in the enemy's color. On player death, similar but larger (orange/red).

---

## Audio (Web Audio API)

Implement with `AudioContext`. Create sounds procedurally:

| Sound | How to Generate |
|---|---|
| Player shoot | Short sine burst: freq 880→220 Hz, 0.08s duration, quick envelope |
| Enemy shoot | Lower, buzzier: sawtooth wave 200→80 Hz, 0.12s |
| Enemy explosion (small) | White noise burst, 0.15s, quick decay |
| Enemy explosion (large/Boss) | White noise + low sine, 0.25s |
| Player explosion | White noise + pitched descent, 0.5s |
| Tractor beam | Looping sine LFO ~4 Hz on a 220 Hz carrier, active while beam on |
| Stage start jingle | Simple 4-note ascending sequence on square wave |
| Background "heartbeat" | A soft two-tone low pulse every 0.8s while in battle (iconic Galaga ambient beat) |

**Background beat:** The original Galaga has a 4-note looping low-frequency beat that speeds up as fewer enemies remain. Implement as a `setInterval` that fires 4 tones in sequence with decreasing interval as enemy count drops.

All audio is optional — wrap in try/catch and disable gracefully if `AudioContext` is unavailable.

---

## Input Handling

```javascript
const keys = {};
window.addEventListener('keydown', e => { keys[e.code] = true; e.preventDefault(); });
window.addEventListener('keyup',   e => { keys[e.code] = false; });
```

Read `keys` each frame in the game loop.

| Action | Key Codes |
|---|---|
| Move Left | `ArrowLeft`, `KeyA` |
| Move Right | `ArrowRight`, `KeyD` |
| Fire | `Space`, `KeyZ` |
| Start/Confirm | `Enter` |
| Pause (optional) | `KeyP`, `Escape` |

**Touch support (optional):** Add two touch zones (left half = move left, right half = move right) and a tap = fire.

---

## Architecture / Code Structure

Recommended structure within one HTML file:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Galaga</title>
  <style>/* center canvas, black bg */</style>
</head>
<body>
  <canvas id="c"></canvas>
  <script>
    // 1. Constants & config
    // 2. Game state variables
    // 3. Entity classes/objects: Player, Enemy, Bullet, Explosion, Star
    // 4. Formation logic
    // 5. Entry sequence logic
    // 6. Dive AI logic
    // 7. Collision detection
    // 8. Rendering functions
    // 9. Audio engine
    // 10. State machine (title, playing, gameover, etc.)
    // 11. Main game loop (requestAnimationFrame)
    // 12. Input setup
    // 13. Init & start
  </script>
</body>
</html>
```

### Entity Design

Use plain objects or ES6 classes. Suggested fields:

**Enemy:**
```javascript
{
  type: 'bee' | 'butterfly' | 'boss',
  col: 0-9,       // formation column
  row: 0-4,       // formation row
  x: Number,      // current world x
  y: Number,      // current world y
  state: 'entering' | 'inFormation' | 'diving' | 'returning' | 'dead',
  entryPath: [...waypoints],
  entryT: 0,       // progress along entry path
  divePath: [...bezierPoints],
  diveT: 0,
  alive: true,
  animFrame: 0,    // for wing animation
  capturedShip: false,  // for dual-boss
}
```

**Player:**
```javascript
{
  x: Number,
  y: 590,
  alive: true,
  invincible: false,
  invincibleTimer: 0,
  dualMode: false,
  x2: Number,   // second ship x offset in dual mode
}
```

**Bullet:**
```javascript
{
  x, y,
  vy: -10 (player) or +5 (enemy),
  owner: 'player' | 'enemy',
  alive: true,
}
```

---

## Entry Path Implementation (Detailed)

For each enemy group, precompute an array of waypoints. Enemies follow waypoints sequentially, lerping toward each one at fixed speed. When they arrive at a waypoint, they move to the next. When they arrive at the final waypoint (their formation slot), they enter `inFormation` state.

**Example: Bees entering from right**

Waypoints (screen coordinates):
1. `(440, 200)` — off-screen right, mid-height
2. `(320, 80)` — curve upward-left
3. `(60, 160)` — sweep left
4. `(formation slot x, formation slot y)` — home

Space ships within a group: stagger start by 15 frames between each ship.

For Boss Galaga and Butterfly entry, define similar but more dramatic paths (loops, tighter spirals).

**Curved movement:** If you want smooth curves rather than straight segments between waypoints, use quadratic Bézier interpolation:
```javascript
function bezierPoint(t, p0, p1, p2) {
  const mt = 1 - t;
  return mt*mt*p0 + 2*mt*t*p1 + t*t*p2;
}
```
Advance `t` by `speed / arcLength` each frame (approximate arc length for even pacing).

---

## Dive Path Implementation (Detailed)

On dive trigger:
1. Record enemy's current formation position as start point.
2. Choose a dive pattern based on enemy type and position. Example patterns:

**Pattern A (Basic swoop):**
- Control point 1: `(enemy.x + 80, enemy.y + 150)` (sweep right)
- Control point 2: `(player.x + 40, player.y - 200)` (aim toward player)
- End point: `(player.x, 700)` — exit bottom

Use cubic Bézier. After reaching end, wrap to top and return.

**Pattern B (Figure-eight):**
- Enemy loops around in a figure-eight before heading down.
- Implement as two sequential arc segments.

**Return path:**
- From bottom (y = 700+), reappear at top (y = -20) at x ≈ formation slot x ± 100.
- Follow a gentle arc back to formation slot.
- Return trip: re-enter as `returning` state, set `state = 'inFormation'` on arrival.

---

## Canvas Scaling

```javascript
const LOGICAL_W = 384;
const LOGICAL_H = 672;

function resize() {
  const scale = Math.min(window.innerWidth / LOGICAL_W, window.innerHeight / LOGICAL_H);
  canvas.style.width  = (LOGICAL_W * scale) + 'px';
  canvas.style.height = (LOGICAL_H * scale) + 'px';
  canvas.width  = LOGICAL_W;
  canvas.height = LOGICAL_H;
}
window.addEventListener('resize', resize);
resize();
```

Always render to logical coordinates. CSS scaling handles display.

---

## Formation Movement

The entire formation drifts horizontally:
```javascript
let formationX = 0;         // offset from center
let formationDir = 1;       // 1 = right, -1 = left
const FORMATION_SPEED = 0.5;
const FORMATION_BOUND = 40; // max drift in px

formationX += formationDir * FORMATION_SPEED;
if (Math.abs(formationX) > FORMATION_BOUND) formationDir *= -1;
```

Each enemy's display position when in formation:
```javascript
enemy.x = FORMATION_BASE_X + enemy.col * CELL_W + formationX;
enemy.y = FORMATION_BASE_Y + enemy.row * CELL_H;
```

Where `CELL_W = 32`, `CELL_H = 36`, `FORMATION_BASE_X = 32`, `FORMATION_BASE_Y = 80`.

Enemies that are diving or returning **ignore** formation position and use their own `x, y`.

---

## Wing Animation

Enemies alternate between two slightly different wing shapes every 8 frames (4 frames each):
```javascript
enemy.animFrame = (enemy.animFrame + 1) % 8;
const wingOpen = enemy.animFrame < 4;
```

Draw different polygon shapes based on `wingOpen`. This gives the classic flapping illusion.

---

## Pause

On press P or Escape:
- Set `paused = true`.
- Stop the game loop (or skip all updates, only render).
- Show "PAUSED" text overlay.
- On press again: resume.

---

## Edge Cases & Polish

1. **Last enemy:** When only one enemy remains, it dives immediately and continuously — no pause between dives. Speed bonus (faster dive) is classic behavior.

2. **All enemies dead mid-entry:** If player destroys enemies during entry sequence, handle gracefully. Stage clears when `enemies.filter(e => e.alive).length === 0`.

3. **Player death during dive return:** If player dies while a diving enemy is returning to formation, the enemy still returns normally.

4. **Score overflow:** Cap display at 999,990 or wrap around — your choice.

5. **Dual fighter:** In dual mode, display both ships ~24px apart. Both ships fire. If one is hit, it explodes and the other remains. Player doesn't lose a life for the dual ship — the dual ship is the captured one.

6. **Entry lockout:** During the entry sequence, enemies can't dive. Dives begin only after all living enemies are in formation (or 5 seconds after last enemy settles, whichever comes first).

7. **Boss Galaga escort:** Boss Galaga in formation always occupies the center-top row. When a Boss dives, it is sometimes accompanied by 2 "escort" bees that flank it. Escorts dive in formation with the Boss, same Bézier curve but offset ±30px horizontally. Escorts shoot independently.

---

## Minimal Viable Feature Checklist

Build in this order:

- [ ] Canvas setup, scaling, game loop
- [ ] Starfield
- [ ] Player ship draw + movement + shooting
- [ ] One enemy type (bee) that sits in formation
- [ ] Player bullet hits enemy (AABB), score
- [ ] Remaining enemies in formation drift
- [ ] Enemy dive (simple straight line first, then Bézier)
- [ ] Enemy shoots during dive
- [ ] Enemy bullet hits player (player death, respawn, lives)
- [ ] Entry sequence (waypoint following)
- [ ] All three enemy types
- [ ] Formation layout (all 44 enemies)
- [ ] Stage progression
- [ ] Boss Galaga tractor beam + capture
- [ ] Dual fighter mode
- [ ] Challenging stage
- [ ] Score, HI-SCORE, stage display
- [ ] Title screen + Game Over screen
- [ ] Audio
- [ ] Polish (explosions, flash, wing animation, pause)

---

## Numbers Reference Sheet

| Parameter | Value |
|---|---|
| Canvas logical size | 384 × 672 |
| Player Y | 590 |
| Player speed | 4 px/frame |
| Player bullet speed | 10 px/frame (upward) |
| Max player bullets | 1 |
| Enemy bullet speed | 5 px/frame (downward), +0.15/stage |
| Max enemy bullets on screen | 6 |
| Formation base X | 32 |
| Formation base Y | 80 |
| Formation cell W | 32 |
| Formation cell H | 36 |
| Formation drift speed | 0.5 px/frame |
| Formation drift bound | ±40 px |
| Dive speed | 3 px/frame base, +0.2/stage, cap 7 |
| Dive interval | 2–4s random, -0.1s/stage, floor 1s |
| Tractor beam width | 40–80 px (cone) |
| Tractor beam height | 120 px |
| Capture pull speed | 2 px/frame upward |
| Player hitbox | 18 × 14 |
| Bee hitbox | 12 × 12 |
| Butterfly hitbox | 14 × 14 |
| Boss hitbox | 16 × 16 |
| Enemy bullet hitbox | 3 × 6 |
| Invincibility after respawn | 120 frames (2s) |
| Explosion duration | 20 frames |
| Starting lives | 3 |
| Extra life threshold | 20,000 pts |
| Challenging stage frequency | Every 3 stages |
| Challenging stage enemies | ~40 |
| Bee formation count | 24 (rows 3–4) |
| Butterfly formation count | 16 (rows 1–2) |
| Boss Galaga count | 4 (row 0) |
| Total enemies per stage | 44 |

---

## What "Complete and Playable" Means

A complete implementation must have:
1. All 44 enemies in a recognizable formation that drifts
2. Three distinct enemy types, visually differentiated
3. Entry flight sequence at stage start
4. Enemy diving with Bézier curves and shooting
5. Player death and respawn with life counter
6. Score tracking and HI-SCORE
7. Stage progression with increasing difficulty
8. Boss Galaga tractor beam and ship capture
9. At least one challenging stage (Stage 3)
10. Title screen and game over screen

Dual fighter mode and audio are strongly recommended but secondary to the above.

---

Good luck. The key to making it feel authentic is the Bézier dive arcs — they need to feel swooping and threatening, not robotic. Spend time tuning the control points.
