# Pac-Man — Complete Game Specification
### Target: Single self-contained HTML5 Canvas file, no external dependencies

---

## 1. Overview

Pac-Man (1980, Namco) is a top-down maze game. The player controls a circular character ("Pac-Man") who navigates a fixed maze, eating dots. Four enemy ghosts roam the same maze trying to catch Pac-Man. Eating a special "power pellet" temporarily makes the ghosts vulnerable (the player can eat them for bonus points). Clearing all dots advances to the next level. The game ends when Pac-Man loses all lives.

---

## 2. Canvas & Rendering

- **Canvas size:** 448 × 576 px (28 tiles wide × 36 tiles tall, each tile 16×16 px).
- The playfield maze occupies rows 3–33 (31 rows). Rows 0–2 are the score display; row 34 is lives/fruit display; rows 35–35 are padding.
- Coordinate origin (0,0) is top-left.
- Render at a fixed 60 fps using `requestAnimationFrame`.
- Use a black background (`#000000`) for the canvas.

---

## 3. Tile System

Each tile is **16×16 pixels**. Tiles are addressed as `(col, row)` where col ∈ [0,27] and row ∈ [0,35].

### Tile types
| ID | Name | Description |
|----|------|-------------|
| 0  | Empty | Black, walkable |
| 1  | Wall | Blue maze wall (see §4) |
| 2  | Dot | Small pellet (10 pts) |
| 3  | Power pellet | Large flashing pellet (50 pts) |
| 4  | Ghost house door | Horizontal bar; only ghosts may pass |
| 5  | Tunnel | Wraps left↔right (row 17) |

Pac-Man and ghosts move between tile centres. A character occupies exactly one tile at a time for collision/AI purposes, but visually interpolates between tiles for smooth movement.

---

## 4. Maze Layout

The maze is 28 columns × 31 rows of playfield tiles (rows 3–33 on the canvas).

Below is the authoritative tile map. Use `1`=wall, `2`=dot, `3`=power pellet, `0`=empty (inside ghost house or open corridors), `4`=ghost door, `T`=tunnel wrap tile.

```
Row  0: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
Row  1: 1 2 2 2 2 2 2 2 2 2 2 2 2 1 1 2 2 2 2 2 2 2 2 2 2 2 2 1
Row  2: 1 2 1 1 1 1 2 1 1 1 1 1 2 1 1 2 1 1 1 1 1 2 1 1 1 1 2 1
Row  3: 1 3 1 1 1 1 2 1 1 1 1 1 2 1 1 2 1 1 1 1 1 2 1 1 1 1 3 1
Row  4: 1 2 1 1 1 1 2 1 1 1 1 1 2 1 1 2 1 1 1 1 1 2 1 1 1 1 2 1
Row  5: 1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 1
Row  6: 1 2 1 1 1 1 2 1 1 2 1 1 1 1 1 1 1 1 2 1 1 2 1 1 1 1 2 1
Row  7: 1 2 1 1 1 1 2 1 1 2 1 1 1 1 1 1 1 1 2 1 1 2 1 1 1 1 2 1
Row  8: 1 2 2 2 2 2 2 1 1 2 2 2 2 1 1 2 2 2 2 1 1 2 2 2 2 2 2 1
Row  9: 1 1 1 1 1 1 2 1 1 1 1 1 0 1 1 0 1 1 1 1 1 2 1 1 1 1 1 1
Row 10: 1 1 1 1 1 1 2 1 1 1 1 1 0 1 1 0 1 1 1 1 1 2 1 1 1 1 1 1
Row 11: 1 1 1 1 1 1 2 1 1 0 0 0 0 0 0 0 0 0 0 1 1 2 1 1 1 1 1 1
Row 12: 1 1 1 1 1 1 2 1 1 0 1 1 1 4 4 1 1 1 0 1 1 2 1 1 1 1 1 1
Row 13: 1 1 1 1 1 1 2 1 1 0 1 0 0 0 0 0 0 1 0 1 1 2 1 1 1 1 1 1
T  14: T 0 0 0 0 0 2 0 0 0 1 0 0 0 0 0 0 1 0 0 0 2 0 0 0 0 0 T
Row 15: 1 1 1 1 1 1 2 1 1 0 1 0 0 0 0 0 0 1 0 1 1 2 1 1 1 1 1 1
Row 16: 1 1 1 1 1 1 2 1 1 0 1 1 1 1 1 1 1 1 0 1 1 2 1 1 1 1 1 1
Row 17: 1 1 1 1 1 1 2 1 1 0 0 0 0 0 0 0 0 0 0 1 1 2 1 1 1 1 1 1
Row 18: 1 1 1 1 1 1 2 1 1 0 1 1 1 1 1 1 1 1 0 1 1 2 1 1 1 1 1 1
Row 19: 1 2 2 2 2 2 2 2 2 2 2 2 2 1 1 2 2 2 2 2 2 2 2 2 2 2 2 1
Row 20: 1 2 1 1 1 1 2 1 1 1 1 1 2 1 1 2 1 1 1 1 1 2 1 1 1 1 2 1
Row 21: 1 2 1 1 1 1 2 1 1 1 1 1 2 1 1 2 1 1 1 1 1 2 1 1 1 1 2 1
Row 22: 1 3 2 2 1 1 2 2 2 2 2 2 2 0 0 2 2 2 2 2 2 2 1 1 2 2 3 1
Row 23: 1 1 1 2 1 1 2 1 1 2 1 1 1 1 1 1 1 1 2 1 1 2 1 1 2 1 1 1
Row 24: 1 1 1 2 1 1 2 1 1 2 1 1 1 1 1 1 1 1 2 1 1 2 1 1 2 1 1 1
Row 25: 1 2 2 2 2 2 2 1 1 2 2 2 2 1 1 2 2 2 2 1 1 2 2 2 2 2 2 1
Row 26: 1 2 1 1 1 1 1 1 1 1 1 1 2 1 1 2 1 1 1 1 1 1 1 1 1 1 2 1
Row 27: 1 2 1 1 1 1 1 1 1 1 1 1 2 1 1 2 1 1 1 1 1 1 1 1 1 1 2 1
Row 28: 1 2 2 2 2 2 2 2 2 2 2 2 2 2 0 2 2 2 2 2 2 2 2 2 2 2 2 1
Row 29: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
Row 30: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
```

> **Implementation note:** The above is a close approximation of the canonical maze. For pixel-perfect accuracy, encode the maze as a 2D integer array in your JavaScript and draw walls procedurally. The visual style uses rounded corners / "pill-shaped" wall outlines — implement using `arc()` and `lineTo()` calls, or simply draw filled rectangles for walls with a 1 px inset gutter for the blue border effect.

### Canonical dot count
- **244 small dots** (each worth 10 pts)
- **4 power pellets** at corners: `(1,3)`, `(26,3)`, `(1,22)`, `(26,22)` — each worth 50 pts

### Ghost house (the "pen")
- Located roughly at columns 10–17, rows 13–16 of the playfield.
- The door tile(s) are at `(13,12)` and `(14,12)` — only ghosts can traverse this tile (Pac-Man cannot).
- Inside the house, ghosts bounce up and down until released.

### Tunnel
- Row 14 (playfield row 11) has openings at columns 0 and 27.
- When a character exits left (col < 0), it reappears at col 27, and vice versa.
- Speed is reduced to 40% of normal while in the tunnel (applies to ghosts; Pac-Man slows slightly too).

---

## 5. Pac-Man

### Appearance
- Yellow circle, radius ~7 px, centred on tile centre.
- Animated mouth: opens and closes at ~11° per frame (0°–46° half-angle). Draw as a filled arc: `arc(x, y, r, mouthAngle, 2π - mouthAngle)`, then `lineTo(x,y)`.
- Mouth faces the current direction of travel. If stopped, mouth is open.
- Death animation: Pac-Man spins, mouth fully opens to a full circle, shrinks to nothing over ~60 frames (1 second).

### Start position
- Column 13, row 23 of the playfield (tile centre), facing left.

### Movement
- Pac-Man moves continuously in the current direction at a tile-based speed.
- **Buffered input:** The player may press a new direction up to ~1 tile early; store it as "next direction". When Pac-Man reaches the next tile centre and the new direction is open, commit it. If blocked in the current direction, stop.
- **Turn corners:** Pac-Man rounds corners without stopping if the new direction was queued at the right time.
- Cannot enter wall tiles.
- Cannot enter ghost house door tiles.

### Speed (fraction of tile per frame at 60 fps)
See §11 (Level Progression) for per-level values. Default level 1: **0.80** (80% of tile/frame baseline, ~8 px/frame for 10 px tiles — scale appropriately).

### Eating dots
- When Pac-Man's centre enters a dot tile: consume dot, add score, remove dot from map.
- Each dot consumes 1 game tick (Pac-Man pauses for 1 frame when eating a dot).
- Each power pellet consumes 3 game ticks.

---

## 6. Ghosts — Overview

There are four ghosts. Each has a **name**, a **colour**, a **personality** (targeting algorithm), and distinct **AI modes**.

| Name   | Nickname | Colour  | Hex     |
|--------|----------|---------|---------|
| Blinky | Shadow   | Red     | #FF0000 |
| Pinky  | Speedy   | Pink    | #FFB8FF |
| Inky   | Bashful  | Cyan    | #00FFFF |
| Clyde  | Pokey    | Orange  | #FFB847 |

### Ghost appearance
- Body: roughly a circle (top half) with a wavy bottom edge (3–4 bumps).
- Two white eyes with coloured pupils pointing in the direction of travel.
- **Frightened mode:** Dark blue body, no pupils visible.
- **Flashing (end of frightened):** Alternates blue ↔ white, ~4 times in last 2 seconds of frightened mode.
- **Eyes-only (eaten):** When a ghost is eaten, only the eyes remain and travel back to the ghost house at high speed.

### Ghost modes
Ghosts cycle through three primary modes; frightened is a special overlay.

| Mode    | Behaviour |
|---------|-----------|
| **Chase**   | Each ghost uses its unique targeting algorithm to chase Pac-Man |
| **Scatter** | Each ghost retreats to its designated home corner |
| **Frightened** | Ghosts move pseudo-randomly; Pac-Man can eat them |
| **Eyes (Eaten)** | Return to ghost house at full speed; not dangerous |

### Global mode timer (Chase / Scatter cycle)
Each level, the timer resets on each life:

| Phase | Level 1         | Levels 2–4      | Level 5+        |
|-------|-----------------|-----------------|-----------------|
| Scatter 1 | 7 s         | 7 s             | 5 s             |
| Chase 1   | 20 s        | 20 s            | 20 s            |
| Scatter 2 | 7 s         | 7 s             | 5 s             |
| Chase 2   | 20 s        | 20 s            | 20 s            |
| Scatter 3 | 5 s         | 5 s             | 5 s             |
| Chase 3   | 20 s        | 1033 s          | 1037 s          |
| Scatter 4 | 5 s         | 1/60 s (1 tick) | 1/60 s (1 tick) |
| Chase 4   | ∞            | ∞               | ∞               |

- Whenever the mode switches between Chase and Scatter, each ghost **reverses direction** (180°) immediately — except during Frightened mode (no reversal during that).
- When Frightened ends, the ghost resumes the current Chase/Scatter phase (do **not** restart the timer).

### Ghost speed
See §11. Summary: ghosts move slightly slower than Pac-Man in normal play; faster than Pac-Man when in eyes-only mode; much slower when frightened.

---

## 7. Individual Ghost AI

Ghosts decide their next direction at each tile centre (intersection). They **cannot reverse** direction (except on mode switch). At intersections, they choose the available direction that minimises Euclidean distance to their **target tile**.

If multiple directions are equally close to the target, prefer in this order: **up > left > down > right** (i.e., prefer upward movement first as a tiebreak).

Ghosts cannot turn up into the two "no-upward" zones: the two T-junctions above the ghost house at approximately `(12,14)` and `(15,14)` have a restriction — ghosts may **not** choose "up" at those specific intersections during Chase or Scatter (this prevents them from looping). Mark these tiles explicitly in your map data.

### 7.1 Blinky (Red) — "Shadow"

**Chase target:** Pac-Man's exact current tile.

**Scatter target:** Top-right corner, tile `(25, 0)`.

**Elroy modes (speed boost when dots are low):**
- When remaining dots ≤ `elroy1_dots` (level-dependent), Blinky enters "Elroy 1": speed increases slightly.
- When remaining dots ≤ `elroy2_dots`, Blinky enters "Elroy 2": speed increases more.
- Elroy mode is disabled (temporarily) when Pac-Man loses a life; resumes after the new life starts if the dot condition is still met.
- Example values for level 1: Elroy1 at ≤20 dots, Elroy2 at ≤10 dots.

### 7.2 Pinky — "Speedy"

**Chase target:** 4 tiles ahead of Pac-Man in Pac-Man's current direction of travel.

- If Pac-Man faces **up**, the target is 4 tiles up **and** 4 tiles to the left (this is a deliberate replication of an original overflow bug that defines Pinky's behaviour).
  - Specifically: target = `(pac_col - 4, pac_row - 4)` when facing up.
  - For all other directions: target = Pac-Man's tile + 4 in the travel direction.

**Scatter target:** Top-left corner, tile `(2, 0)`.

### 7.3 Inky (Cyan) — "Bashful"

**Chase target:** Computed using both Pac-Man and Blinky's positions:
1. Find the tile 2 ahead of Pac-Man in Pac-Man's facing direction. Call this point **P**.
   - Apply the same up-direction offset bug as Pinky (2 tiles up and 2 left when facing up).
2. Draw a vector from Blinky's tile to **P**.
3. Double that vector: `target = P + (P - blinky_tile)`.

This makes Inky try to flank from the opposite side of Blinky relative to Pac-Man.

**Scatter target:** Bottom-right corner, tile `(27, 30)`.

### 7.4 Clyde (Orange) — "Pokey"

**Chase target:**
- If the distance between Clyde and Pac-Man is **more than 8 tiles**: target is Pac-Man's tile (same as Blinky).
- If the distance is **8 tiles or less**: target is Clyde's own scatter corner (bottom-left, `(0, 30)`).

This makes Clyde seemingly charge at Pac-Man but shy away when close.

**Scatter target:** Bottom-left corner, tile `(0, 30)`.

---

## 8. Ghost Release (Leaving the Pen)

Ghosts start the level inside the ghost house (except Blinky, who starts outside above the door). They are released based on a **dot counter** and a **global timer**.

### Release order
1. **Blinky** — starts outside the pen immediately.
2. **Pinky** — released immediately at level start.
3. **Inky** — released when the player has eaten 30 dots (level 1); 0 dots (level 2+).
4. **Clyde** — released when the player has eaten 60 dots (level 1); 50 dots (level 2); 0 dots (level 3+).

### Per-ghost dot counters (alternative release method)
Each ghost also has an individual dot counter. When Pac-Man eats a dot, the counter for the currently-housed ghost increments. When the counter hits the threshold, the ghost is released.

| Ghost | Level 1 | Level 2 | Level 3+ |
|-------|---------|---------|----------|
| Pinky | 0       | 0       | 0        |
| Inky  | 30      | 0       | 0        |
| Clyde | 60      | 50      | 0        |

Use whichever counter (global or per-ghost) first triggers release.

### Global release timer
If Pac-Man doesn't eat a dot for 4 seconds (level 1) / 3 seconds (level 2+), the next unreleased ghost is forced out.

### Release behaviour
- A ghost inside the pen oscillates vertically (bounces up and down) until released.
- When released, the ghost moves to the door tile, exits upward, then moves left to tile `(13, 11)` before entering normal AI.
- Pinky starts at the centre of the pen and exits immediately.
- Inky starts left of centre; Clyde starts right of centre.

---

## 9. Frightened Mode

When Pac-Man eats a **power pellet**:
1. All ghosts (not in eyes mode) enter Frightened mode.
2. All ghosts reverse direction immediately.
3. The Chase/Scatter timer is **paused** for the duration.
4. Ghosts take random turns at each intersection (still cannot reverse).
5. Frightened duration (seconds) is level-dependent (see §11).

### Eating ghosts (ghost point values)
Ghost points reset each time a new power pellet is eaten:

| Ghosts eaten in succession | Points |
|----------------------------|--------|
| 1st                        | 200    |
| 2nd                        | 400    |
| 3rd                        | 800    |
| 4th                        | 1600   |

When Pac-Man eats a ghost:
- Display the point value briefly at the eaten ghost's location (~1 second).
- Pac-Man and all other characters **freeze** for ~0.5 seconds (brief pause).
- The eaten ghost becomes "eyes" and returns to the pen.
- Once in the pen, the ghost re-enters Frightened mode if it is still active, then resumes normal mode after Frightened ends.

If Frightened has 0 duration (high levels), ghosts turn blue for just a flicker (1 frame) then revert; they are still technically eat-able for that one frame.

---

## 10. Scoring

| Event | Points |
|-------|--------|
| Small dot | 10 |
| Power pellet | 50 |
| Ghost (1st per power pellet) | 200 |
| Ghost (2nd) | 400 |
| Ghost (3rd) | 800 |
| Ghost (4th) | 1600 |
| Eating bonus fruit | See table below |

### Bonus fruit
A bonus fruit/item appears twice per level:
- 1st appearance: when 70 dots have been eaten.
- 2nd appearance: when 170 dots have been eaten.
- It appears at tile `(13, 20)` (just below the ghost house) and disappears after 9–10 seconds.

| Level | Fruit      | Points |
|-------|------------|--------|
| 1     | Cherry     | 100    |
| 2     | Strawberry | 300    |
| 3–4   | Peach      | 500    |
| 5–6   | Apple      | 700    |
| 7–8   | Grapes     | 1000   |
| 9–10  | Galaxian   | 2000   |
| 11–12 | Bell       | 3000   |
| 13+   | Key        | 5000   |

Draw fruit as a simple geometric shape or emoji-like coloured circle/shape — it does not need to be photorealistic.

### Extra life
Award a **bonus life** when the player's score first reaches **10,000 points** (once only per game).

---

## 11. Level Progression

After all 244 dots are eaten, the level increments and a new maze appears (same layout, dots/power pellets reset, ghosts reset). Play an intermission animation between some levels (optional — can be skipped for a simpler implementation).

Speed values below are expressed as fractions of the **base speed** (1.0 = one tile per ~10 frames at 60 fps, i.e., 9.6 tiles/second). Adjust to taste for feel.

| Level | Pac speed (normal) | Pac speed (fright.) | Ghost speed (normal) | Ghost speed (fright.) | Ghost speed (tunnel) | Fright. duration (s) | Fright. flashes |
|-------|--------------------|---------------------|----------------------|-----------------------|----------------------|----------------------|-----------------|
| 1     | 0.80               | 0.90                | 0.75                 | 0.50                  | 0.40                 | 6                    | 5               |
| 2     | 0.90               | 0.95                | 0.85                 | 0.55                  | 0.45                 | 5                    | 5               |
| 3     | 0.90               | 0.95                | 0.85                 | 0.55                  | 0.45                 | 4                    | 5               |
| 4     | 0.90               | 0.95                | 0.85                 | 0.55                  | 0.45                 | 3                    | 5               |
| 5     | 1.00               | 1.00                | 0.95                 | 0.60                  | 0.50                 | 2                    | 5               |
| 6     | 1.00               | 1.00                | 0.95                 | 0.60                  | 0.50                 | 5                    | 5               |
| 7–8   | 1.00               | 1.00                | 0.95                 | 0.60                  | 0.50                 | 2                    | 5               |
| 9     | 1.00               | 1.00                | 0.95                 | 0.60                  | 0.50                 | 1                    | 3               |
| 10–11 | 1.00               | 1.00                | 0.95                 | 0.60                  | 0.50                 | 5                    | 5               |
| 12–14 | 1.00               | 1.00                | 0.95                 | 0.60                  | 0.50                 | 1                    | 3               |
| 15–18 | 1.00               | 1.00                | 0.95                 | 0.60                  | 0.50                 | 1                    | 3               |
| 19+   | 1.00               | 1.00                | 0.95                 | 0.60                  | 0.50                 | 0                    | 0               |

At level 19+, frightened duration is 0 — power pellets still exist and are worth 50 pts, but ghosts are **never** vulnerable.

---

## 12. Lives System

- **Start with 3 lives** (displayed as Pac-Man icons at the bottom of the screen).
- The current life is not shown in the icons; icons show remaining extra lives. So with 3 lives, show 2 icons.
- When Pac-Man is caught by a ghost (their bounding boxes overlap while a ghost is in Chase/Scatter mode):
  1. Play death animation (~2 seconds).
  2. All characters pause during animation.
  3. Decrement life count.
  4. If lives ≥ 1: Reset Pac-Man to start position, reset ghosts to start positions (do **not** reset dots or score). Brief pause before resuming play.
  5. If lives = 0: **Game over.**

### Collision detection
Use tile-based collision: Pac-Man and a ghost are in collision if they occupy the same tile, **or** if they are passing through each other (i.e., Pac-Man moves through a ghost's tile in the same frame — check both current and next tile).

Specifically: collision occurs when the Euclidean distance between Pac-Man's pixel centre and the ghost's pixel centre is < ~10 px.

---

## 13. UI Layout

### During gameplay
- **Top area (rows 0–2):**
  - `1UP` score (left), high score (centre), `2UP` label (right, grey if single player).
  - Current score rendered in white pixel-style font (`monospace` or a pixelated font).
- **Playfield:** Rows 3–33 (described above).
- **Bottom area (rows 34–35):**
  - Lives icons (left): Pac-Man icons, one per remaining extra life.
  - Fruit history (right): Up to 7 recent bonus fruits displayed as icons.

### Start screen
- Flash "PLAYER ONE READY!" text in the centre of the maze before level begins.
- Show "READY!" text in yellow just above Pac-Man's start position for ~2 seconds at the beginning of each life.

### Game over
- Display "GAME OVER" in red at the centre of the maze.
- After ~3 seconds, show a high-score entry prompt or return to attract mode (can be simplified: just show score and prompt to press Space/Enter to restart).

### Attract mode (optional, but recommended)
- If not in game, cycle through a simple demo: show the maze with ghosts chasing Pac-Man on a looped path, flashing the score table.

---

## 14. Controls

| Input | Action |
|-------|--------|
| Arrow Left / A | Move left |
| Arrow Right / D | Move right |
| Arrow Up / W | Move up |
| Arrow Down / S | Move down |
| Space / Enter | Start game / Confirm |
| P | Pause / Resume |

Implement input buffering: store the **last pressed direction**. At each tile boundary, attempt to apply the buffered direction. If it's valid, commit it; otherwise keep trying until Pac-Man reaches the next intersection.

---

## 15. Audio

Since no external dependencies are allowed, use the **Web Audio API** (`AudioContext`) to synthesise all sounds procedurally.

| Sound | Description |
|-------|-------------|
| Chomp | Alternating ~200 Hz / ~250 Hz square wave pulse, ~50 ms, triggered each dot eaten |
| Power pellet | Rising sweep 100→400 Hz, 200 ms |
| Ghost eaten | Descending sweep 800→200 Hz, 300 ms |
| Death | Multi-step descending chromatic scale, ~1.5 s |
| Extra life | Short ascending fanfare, ~0.5 s |
| Fruit | Quick arpeggio, ~200 ms |
| Siren (bg) | Looping low-frequency hum at ~120–180 Hz, pitch increases as fewer dots remain (5 speed levels) |
| Frightened siren | Irregular low warble, ~60–90 Hz pulse |
| Eyes returning | Rapid high tick, ~1000 Hz |

All audio is optional/degradable — if `AudioContext` is unavailable, the game should still run silently.

---

## 16. Visual Style Notes

### Wall rendering
The classic blue-on-black walls are drawn as **outlines** (hollow), not solid fills. Render walls by:
1. Flood-fill all wall tiles with black.
2. Draw the outline of wall regions in blue (`#2121DE` or `#0000FF`).
3. Use `roundedRect` or arc() for smooth corners — walls have rounded outer corners and rounded inner corners.

Alternatively, use a simpler approach: draw each wall tile as a blue rectangle, then overdraw corridor tiles in black. For a cleaner look, add 1 px blue border on corridor sides adjacent to walls.

### Dot rendering
- Small dot: white circle, radius 2 px, centred in tile.
- Power pellet: white circle, radius 5 px, flashes on/off every ~0.3 seconds (toggle visibility at 15-frame intervals).

### Ghost house door
Drawn as a thin horizontal white/pink line (2 px tall) spanning columns 13–14 of the ghost house row.

---

## 17. State Machine

Implement a top-level game state machine:

```
ATTRACT → PLAYING → DYING → LEVEL_COMPLETE → GAME_OVER
                ↑___________________________________|
```

- **ATTRACT:** Idle screen. Press Start to begin.
- **PLAYING:** Normal gameplay. Sub-states: READY (2-second pause at life start), NORMAL, FRIGHTENED.
- **DYING:** Death animation plays. Transitions to PLAYING (new life) or GAME_OVER.
- **LEVEL_COMPLETE:** Flash maze briefly (alternating blue/white walls ~8 times over ~2 seconds), then reset for next level.
- **GAME_OVER:** Show game-over message. Press Start to return to ATTRACT.

---

## 18. Tile-Based Movement Implementation Guide

Movement is the most complex part. Here's a recommended implementation:

### Representation
Each moving character has:
- `tileX, tileY` — current tile (integer)
- `pixelX, pixelY` — pixel coordinates for rendering (smooth interpolation)
- `direction` — current direction (enum: UP, DOWN, LEFT, RIGHT)
- `nextDirection` — buffered direction from input (Pac-Man only)
- `speed` — tiles per frame (e.g., 0.075 for 80% of ~11.2 px/frame at 16px tiles)

### Per-frame update
```
1. Compute movement delta = speed * deltaTime (or speed per fixed frame)
2. Move pixelX/pixelY in current direction by delta pixels.
3. If the character has crossed the centre of the *next* tile:
   a. (For Pac-Man) Try to apply nextDirection. If valid, commit + update tileX/tileY.
   b. If not valid (or ghost), continue in current direction if open; else stop/reverse.
   c. Snap pixelX/pixelY to new tile centre.
   d. Update tileX/tileY.
4. Handle tunnel wrap: if tileX < 0, set tileX = 27; if tileX > 27, set tileX = 0.
```

For ghosts, the "choose next direction" decision is made **one tile in advance**: when the ghost enters a new tile, it decides which direction to go at the *next* intersection (look-ahead). This avoids hesitation at intersections.

---

## 19. Reference Data Summary

### Starting positions (all in playfield tile coordinates, (col, row))
| Character | Tile     | Initial direction |
|-----------|----------|-------------------|
| Pac-Man   | (13, 23) | Left              |
| Blinky    | (13, 11) | Left              |
| Pinky     | (13, 14) | Down (bouncing)   |
| Inky      | (11, 14) | Down (bouncing)   |
| Clyde     | (15, 14) | Down (bouncing)   |

### Scatter corners (playfield)
| Ghost  | Corner tile |
|--------|-------------|
| Blinky | (25, 0)     |
| Pinky  | (2, 0)      |
| Inky   | (27, 30)    |
| Clyde  | (0, 30)     |

---

## 20. Implementation Checklist

- [ ] Maze tile map (28×31) with wall collision
- [ ] Pac-Man movement with input buffering and wall collision
- [ ] Dot/power pellet consumption + scoring
- [ ] Ghost house with oscillating pre-release ghosts
- [ ] Ghost release logic (dot counters + timer)
- [ ] Ghost AI: Chase (x4 unique algorithms), Scatter, Frightened (random), Eyes (return home)
- [ ] Chase/Scatter global mode timer with direction reversal
- [ ] Frightened mode: trigger on power pellet, duration timer, flashing, point multiplier
- [ ] Ghost eaten: freeze, point display, eyes-only return
- [ ] Tunnel wrap with speed reduction
- [ ] Blinky Elroy speed modes
- [ ] Collision detection (Pac-Man vs. ghost, Pac-Man vs. dots)
- [ ] Lives system: death animation, reset, game over
- [ ] Bonus fruit appearance/scoring
- [ ] Extra life at 10,000 pts
- [ ] Level progression: dots cleared → next level, speed table applied
- [ ] UI: score display, lives icons, fruit history
- [ ] Start/Ready screens
- [ ] Audio via Web Audio API (synthesised)
- [ ] Pause functionality
- [ ] High score (session memory, not persistent)
- [ ] State machine: ATTRACT → PLAYING → DYING → LEVEL_COMPLETE → GAME_OVER

---

## 21. Known Original Game Quirks (Replicate for Authenticity)

1. **Pinky's up-direction bug:** As described in §7.2 — target is (pac_col-4, pac_row-4) when Pac-Man faces up. This is intentional.
2. **Inky uses the same bug:** The 2-tile look-ahead for up also applies the left-offset.
3. **Pac-Man stops briefly on each dot:** 1-frame pause per small dot, 3-frame pause per power pellet. This is why eating many dots in a row feels slightly slower.
4. **No-upward zones:** Ghosts cannot turn upward at the two intersections flanking the ghost house. These are at approximately (12,14) and (15,14) on the playfield.
5. **Ghost house door:** Pac-Man cannot enter through the ghost house door, but ghosts can exit and return through it.
6. **Ghost speed in tunnel:** All ghosts slow to 40% base speed in the tunnel (this prevents ghosts from catching Pac-Man in the tunnel since Pac-Man also slows but less so).
7. **Elroy persists across modes:** Blinky in Elroy mode ignores Scatter (continues targeting Pac-Man even in Scatter phase).
8. **Score multiplier resets per power pellet:** Eating the 1st ghost after any power pellet = 200 pts. Each subsequent ghost (without eating another power pellet) doubles.

---

*End of specification. Total: ~244 dots, 4 power pellets, 4 ghosts, 13+ levels, one legendary maze.*
