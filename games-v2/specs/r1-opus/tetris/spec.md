# Game Spec: Tetris

## 1. Overview

Tetris (Alexey Pajitnov, 1984 — the most played video game in history). Geometric shapes made of four squares ("tetrominoes") fall one at a time from the top of a tall rectangular well. The player can move them left/right, rotate them, and accelerate their descent. When a tetromino lands, it locks into place. When an entire horizontal row of the well is filled with blocks — no gaps — that row is cleared and everything above it drops down. The game ends when new pieces can no longer enter the well because the stack has reached the top.

The genius is that every decision is a tradeoff. Flat pieces fill gaps but waste vertical space. Placing a piece safely now might block a better placement later. Leaving a column open for the long I-piece is high-reward but high-risk — if it doesn't come soon, the stack grows dangerously. Tetris is a game about managing imperfection under increasing time pressure.

The speed increases as the player clears more lines. There is no winning. You survive until you don't.

## 2. Canvas & Layout

- **Canvas:** 480×640px
- **Background:** #0a0a0a
- **Playfield (the well):** 10 columns × 20 visible rows. Each cell is 28×28px. Playfield dimensions: 280×560px. Positioned with its left edge at x=24, top edge at y=44. Outlined with a 2px #333333 border.
- **Above the visible field:** 2 additional hidden rows (rows 21–22 from the bottom, or rows -1 and -2 from the top) where new pieces spawn. These rows are not rendered. If blocks exist in these hidden rows when a piece locks, the game is over.
- **Playfield background:** #111111, with 1px #1a1a1a grid lines between cells.
- **Right panel:** x=320 to x=470, for Next piece preview, score, level, and lines.
- **Hold panel:** x=320, y=44, for the held piece display.
- **Frame rate:** 60 FPS via `requestAnimationFrame`.
- **Game logic:** Gravity tick on a timer (variable interval based on level). Input processing every frame.

## 3. The Seven Tetrominoes

Every piece in Tetris is composed of exactly four unit squares arranged in a specific shape. There are exactly seven, named by their resemblance to letters. Each has a fixed color:

```
I-piece (Cyan, #00F0F0):        O-piece (Yellow, #F0F000):
  . . . .                         . . . .
  X X X X                         . X X .
  . . . .                         . X X .
  . . . .                         . . . .

T-piece (Purple, #A000F0):      S-piece (Green, #00F000):
  . . . .                         . . . .
  . X . .                         . X X .
  X X X .                         X X . .
  . . . .                         . . . .

Z-piece (Red, #F00000):         J-piece (Blue, #0000F0):
  . . . .                         . . . .
  Z Z . .                         X . . .
  . Z Z .                         X X X .
  . . . .                         . . . .

L-piece (Orange, #F0A000):
  . . . .
  . . X .
  X X X .
  . . . .
```

Each piece is defined within a bounding grid for rotation purposes:
- **I-piece:** 4×4 bounding box
- **O-piece:** 4×4 bounding box (though it only uses a 2×2 area — it does NOT rotate)
- **All others (T, S, Z, J, L):** 3×3 bounding box (the 4×4 grids above use padding — internally store these as 3×3)

**Data representation:** Store each piece's rotations as arrays of filled cell offsets relative to an origin point (typically the piece's center of rotation). For example, the T-piece in spawn orientation has cells at [(0,0), (-1,0), (1,0), (0,-1)] relative to center.

Pre-compute all four rotation states for each piece (0°, 90°, 180°, 270° clockwise). The O-piece has one state (rotating it changes nothing).

## 4. Rotation System (SRS — Super Rotation System)

Rotation in Tetris is not simple. Pieces rotate around a center point, but if the rotated position overlaps a wall or existing block, the game attempts to "kick" the piece into a nearby valid position before giving up. This wall kick system is what makes rotation feel fluid instead of frustrating.

### Basic Rotation

Pieces rotate clockwise (primary) and counter-clockwise (secondary). The rotation states are numbered 0→1→2→3 (clockwise) and 0→3→2→1 (counter-clockwise).

For 3×3 pieces (T, S, Z, J, L), rotating 90° clockwise transforms each cell offset (x, y) to (y, -x) relative to the center. Counter-clockwise: (x, y) → (-y, x).

For the I-piece (4×4), the center of rotation is between cells. The rotation offsets are irregular — define all four states explicitly rather than computing them:

```
I-piece rotation states (cells relative to piece origin):
State 0: (0,1), (1,1), (2,1), (3,1)   — horizontal, second row
State 1: (2,0), (2,1), (2,2), (2,3)   — vertical, third column
State 2: (0,2), (1,2), (2,2), (3,2)   — horizontal, third row
State 3: (1,0), (1,1), (1,2), (1,3)   — vertical, second column
```

### Wall Kicks

When a rotation would place the piece in an invalid position (overlapping walls or existing blocks), the game tries a series of alternative positions by shifting the piece. These shifts are called "kick offsets" and are attempted in order. If any offset results in a valid position, the rotation succeeds at that position. If none work, the rotation fails silently.

**Kick table for T, S, Z, J, L (standard SRS):**

| Rotation | Test 1 (offset) | Test 2 | Test 3 | Test 4 |
|----------|---------|--------|--------|--------|
| 0→1 | (-1, 0) | (-1, -1) | (0, +2) | (-1, +2) |
| 1→0 | (+1, 0) | (+1, +1) | (0, -2) | (+1, -2) |
| 1→2 | (+1, 0) | (+1, +1) | (0, -2) | (+1, -2) |
| 2→1 | (-1, 0) | (-1, -1) | (0, +2) | (-1, +2) |
| 2→3 | (+1, 0) | (+1, -1) | (0, +2) | (+1, +2) |
| 3→2 | (-1, 0) | (-1, +1) | (0, -2) | (-1, -2) |
| 3→0 | (-1, 0) | (-1, +1) | (0, -2) | (-1, -2) |
| 0→3 | (+1, 0) | (+1, -1) | (0, +2) | (+1, +2) |

Offsets are (x, y) where positive x = right, positive y = up (toward the top of the well — note this is the opposite of screen y direction).

**Kick table for I-piece (different from the others):**

| Rotation | Test 1 | Test 2 | Test 3 | Test 4 |
|----------|--------|--------|--------|--------|
| 0→1 | (-2, 0) | (+1, 0) | (-2, +1) | (+1, -2) |
| 1→0 | (+2, 0) | (-1, 0) | (+2, -1) | (-1, +2) |
| 1→2 | (-1, 0) | (+2, 0) | (-1, -2) | (+2, +1) |
| 2→1 | (+1, 0) | (-2, 0) | (+1, +2) | (-2, -1) |
| 2→3 | (+2, 0) | (-1, 0) | (+2, -1) | (-1, +2) |
| 3→2 | (-2, 0) | (+1, 0) | (-2, +1) | (+1, -2) |
| 3→0 | (+1, 0) | (-2, 0) | (+1, +2) | (-2, -1) |
| 0→3 | (-1, 0) | (+2, 0) | (-1, -2) | (+2, +1) |

The attempt order is: first try the raw rotation (no offset). If invalid, try Test 1 offset. Then Test 2, 3, 4. First valid position wins. If all five attempts fail, the rotation is rejected.

**Why this matters:** Without wall kicks, pieces near walls or in tight spaces will refuse to rotate, which feels broken. With SRS kicks, the I-piece can tuck into tight columns, the T-piece can execute "T-spins" (a celebrated advanced technique), and rotation generally feels forgiving and fluid. Implementing this table exactly is important for a game that feels correct.

## 5. Controls

| Input | Action |
|-------|--------|
| Arrow Left / A | Move piece one cell left |
| Arrow Right / D | Move piece one cell right |
| Arrow Down / S | Soft drop (accelerate descent) |
| Arrow Up / W | Rotate clockwise |
| Z / Ctrl | Rotate counter-clockwise |
| Space | Hard drop (instant drop + lock) |
| Shift / C | Hold piece |
| Enter | Start / Restart |
| P or Escape | Pause / Unpause |

### Input Handling Details

**DAS (Delayed Auto Shift) — horizontal movement:**

Left/Right does NOT simply repeat every frame while held. That would be too fast and uncontrollable. Instead:

1. First press: move one cell immediately.
2. If the key remains held: wait **170ms** (the DAS delay).
3. After the delay: auto-repeat movement at **50ms intervals** (the ARR — auto-repeat rate), moving one cell per interval.

This two-phase system (initial move, pause, then rapid repeat) lets the player tap for precise single-cell movements or hold for fast traversal. Track the held duration per key.

**Soft drop (Down arrow):**

While held, the piece drops at 20× the current gravity speed (or a minimum of 1 cell per 50ms, whichever is faster). Each cell dropped by soft-drop awards 1 point (the original NES Tetris did this — it rewards aggressive play).

**Hard drop (Space):**

The piece instantly teleports to the lowest valid position directly below its current location (the position shown by the ghost piece) and locks immediately. No lock delay. Awards 2 points per cell dropped. This is the fast-paced player's primary tool.

**Rotation (Up / Z):**

Edge-triggered — one rotation per keypress. Holding the key does NOT auto-repeat rotation. The player must release and press again.

**Hold (Shift / C):**

The player can store the current falling piece in a "hold slot" and receive the next piece from the queue instead (or swap with the currently held piece). Rules:
- Hold can be used **once per piece.** After holding, the player cannot hold again until the next piece naturally spawns. This prevents infinite hold-swapping.
- When a piece is held, it resets to its spawn orientation (rotation state 0) and spawn position.
- The held piece is displayed in the Hold panel.
- First hold (nothing stored): current piece goes to hold, next piece from queue spawns immediately.
- Subsequent holds: current piece goes to hold, previously held piece spawns.

## 6. Gravity & Drop Speed

The active piece falls downward automatically. The speed depends on the current level.

| Level | Frames per cell (at 60fps) | Approximate interval |
|-------|---------------------------|---------------------|
| 0 | 48 | 800ms |
| 1 | 43 | 717ms |
| 2 | 38 | 633ms |
| 3 | 33 | 550ms |
| 4 | 28 | 467ms |
| 5 | 23 | 383ms |
| 6 | 18 | 300ms |
| 7 | 13 | 217ms |
| 8 | 8 | 133ms |
| 9 | 6 | 100ms |
| 10–12 | 5 | 83ms |
| 13–15 | 4 | 67ms |
| 16–18 | 3 | 50ms |
| 19–28 | 2 | 33ms |
| 29+ | 1 | 17ms (1 cell per frame — "kill screen") |

Use an accumulator: each frame, add `dt` to a gravity timer. When the timer exceeds the current level's interval, move the piece down one cell and subtract the interval. If the piece can't move down (a surface is below it), begin the lock delay (section 7).

**Starting level:** The player starts at level 0 by default. Optionally allow level selection on the title screen (0–19).

**Level advancement:** The level increases by 1 for every 10 lines cleared. A player starting at level 0 who clears 10 lines reaches level 1. At 20 lines, level 2. And so on. If the player starts at a higher level, they still advance every 10 lines from that point.

## 7. Lock Delay

When a piece comes to rest on a surface (another block or the floor) and cannot fall further, it does NOT lock instantly. There is a **500ms lock delay** — a window where the player can still move or rotate the piece before it commits.

**Lock delay rules:**

1. When the piece first touches a surface and gravity would push it down but can't, start a 500ms timer.
2. If the player moves or rotates the piece (any successful move/rotate), **reset the timer to 500ms.** This lets skilled players "slide" pieces along surfaces and rotate them into tight spots.
3. **Maximum resets: 15.** After 15 move/rotate resets, the piece locks on the next surface contact regardless. This prevents infinite stalling.
4. If the piece is moved off the surface (e.g., moved sideways so it's hovering over a gap), the lock timer pauses. It only ticks while the piece is resting on something.
5. On timer expiry: the piece locks. Its cells become part of the playfield. Check for line clears. Spawn the next piece.
6. **Hard drop bypasses lock delay entirely** — instant lock.

## 8. Piece Spawning & the Random Bag

### Spawn Position

New pieces appear at the top of the well, centered horizontally:
- **Spawn column:** Piece bounding box positioned so the piece is centered (columns 3–6 for 4-wide pieces, columns 3–5 for 3-wide pieces). The piece's cells occupy the top hidden rows (rows 20–21, counting from 0 at the bottom, or equivalently the two rows above the visible area).
- **Spawn orientation:** State 0 (the shapes shown in section 3).
- **Spawn gravity:** The piece immediately begins falling on the first gravity tick. It enters the visible area from above.

### Game Over Condition

If a newly spawned piece overlaps any existing blocks on the playfield (even in the hidden rows above the visible area), the game is over. This means the stack has reached the top and there's no room for new pieces.

### The 7-Bag Randomizer

Tetris does NOT use pure random piece selection. Pure random can produce long droughts of needed pieces (imagine needing an I-piece and not getting one for 30+ pieces). Instead, it uses the "7-bag" system:

1. Take all 7 piece types (I, O, T, S, Z, J, L). Put them in a bag. Shuffle randomly.
2. Deal them out one at a time in the shuffled order.
3. When the bag is empty, refill it with all 7, shuffle again, repeat.

This guarantees:
- Every piece type appears at least once in every 7 pieces.
- The maximum drought for any piece is 12 (last piece of one bag, first piece of the next bag is 6 other types before it repeats).
- The distribution is perfectly fair over time.

**Implementation:** Maintain an array. On init (and whenever the array runs low), concatenate a new shuffled set of 7 onto it. Always keep at least 7 pieces in the queue (so the "Next" preview can show upcoming pieces). Use Fisher-Yates shuffle for the randomization.

**Next piece preview:** Show the next 3 upcoming pieces in the right panel. More than 3 is noisy; fewer than 3 is stingy. Three is the standard modern Tetris count.

## 9. Line Clears

After a piece locks, scan every row of the playfield. Any row where all 10 cells are occupied is "cleared":

1. **Identify all full rows.** There can be 1, 2, 3, or 4 simultaneous clears (a 4-line clear is called a "Tetris" — it requires placing an I-piece into a 4-row-tall 1-wide gap and is the signature move of the game).
2. **Flash the full rows** white for 300ms (each cell briefly turns #FFFFFF).
3. **Remove the rows.** All cells in cleared rows are deleted.
4. **Collapse.** Every row above each cleared row drops down to fill the gap. Rows below cleared rows don't move. The result is equivalent to removing the cleared rows from the array and adding empty rows at the top.
5. **Award points** (see section 10).
6. **Update line count and level.**

The line clear animation (300ms flash + collapse) should feel snappy. Don't make the player wait.

## 10. Scoring

The modern Guideline scoring system:

### Line Clear Points

Points = base × level multiplier, where multiplier = (currentLevel + 1).

| Lines cleared | Name | Base points |
|---------------|------|-------------|
| 1 | Single | 100 |
| 2 | Double | 300 |
| 3 | Triple | 500 |
| 4 | Tetris | 800 |

Example: a Double at level 3 = 300 × 4 = 1,200 points.

### Back-to-Back Bonus

If the player clears a Tetris, and the **previous** line clear was also a Tetris (with no singles/doubles/triples in between), the second Tetris gets a 50% bonus: 800 × 1.5 = 1,200 base. Back-to-back chains continue at 1.5× as long as every clear is a Tetris.

### Soft Drop Points

+1 point per cell descended via soft drop (Down key held).

### Hard Drop Points

+2 points per cell descended via hard drop (Space).

### Combo System

Consecutive piece placements that each clear at least one line build a combo counter. Each successive clear in the combo awards an additional 50 × combo × (level + 1) points. The combo resets to 0 when a piece locks without clearing any lines.

```
Piece 1 clears lines: combo = 1 → +50 × 1 × (level+1)
Piece 2 clears lines: combo = 2 → +50 × 2 × (level+1)
Piece 3 clears lines: combo = 3 → +50 × 3 × (level+1)
Piece 4 does NOT clear: combo resets to 0
```

## 11. Ghost Piece

A translucent preview showing where the active piece will land if hard-dropped. This is essential for usability — without it, the player can't judge where the piece will end up, especially at high speeds.

- **Rendering:** Draw the piece's shape at the lowest valid position directly below its current location. Same cells, same position horizontally and rotation-wise, but projected down as far as possible.
- **Color:** Same hue as the active piece but at 20% opacity (or draw as an outline — 2px border in the piece's color, no fill, at 30% opacity). The ghost must be visible but must not be confused with the actual piece.
- **Calculation:** From the active piece's current position, move it down one cell at a time until it would collide with the floor or an existing block. The last valid position is the ghost position. Recalculate every frame (it changes every time the piece moves or rotates).

## 12. Playfield Data

The playfield is a 10×22 grid (10 wide, 20 visible rows + 2 hidden rows above). Store as a 2D array:

```
grid[row][col]  — row 0 is the bottom, row 21 is the top hidden row
                 — or row 0 is the top hidden row and row 21 is the bottom
                 (either convention works — pick one and be consistent)
```

Each cell is either empty (null/0) or contains a color value (indicating a locked block and its color for rendering). The active falling piece is NOT stored in the grid — it's tracked separately (piece type, rotation state, x, y position). It's only written into the grid when it locks.

## 13. Controls Recap & Timing

```
Left/Right:
  - Press: immediate 1-cell move
  - Hold: 170ms delay, then 50ms auto-repeat

Down:
  - Hold: 20× gravity speed (min 50ms per cell), +1 point per cell

Up / W:
  - Press: rotate CW (edge-triggered, no auto-repeat)

Z / Ctrl:
  - Press: rotate CCW (edge-triggered, no auto-repeat)

Space:
  - Press: hard drop (instant to ghost position, instant lock, +2 pts/cell)

Shift / C:
  - Press: hold piece (once per piece, edge-triggered)
```

## 14. Game States

```
TITLE → PLAYING → (LINE_CLEAR animation → PLAYING) or GAME_OVER → TITLE
           ↕
        PAUSED
```

### TITLE

- Dark playfield grid renders (empty, dimmed)
- **"TETRIS"** centered at y≈180, 48px bold monospace, #FFFFFF
- Below: the seven tetrominoes displayed in a row (or two rows), each in its color, like a character select screen. Rotate them slowly (one rotation per second) for visual interest.
- **"Press Enter to Start"** at y≈400, 20px, #AAAAAA, blinking at 2Hz
- **"Best: {N}"** at y≈440, 16px, #555555
- **Optional level select:** "← Level {N} →" with arrow keys to choose starting level (0–19). Display at y≈470, 16px, #888888.
- Enter → PLAYING

### PLAYING

- Active piece falling, player input processed, gravity ticking
- P or Escape → PAUSED

### PAUSED

- All timers freeze (gravity, lock delay, line clear animation)
- Overlay: #000000 at 70% opacity over the playfield
- "PAUSED" centered, 36px, #FFFFFF
- "P to resume" 14px, #888888
- Right panel (score/next/hold) remains visible
- P or Escape → PLAYING

### LINE_CLEAR (sub-state)

- 300ms: full rows flash white
- Rows collapse (animate: rows above slide down over 100ms)
- Score updates
- Next piece spawns
- → PLAYING

### GAME_OVER

- The stack freezes. Optionally: fill the playfield from bottom to top with grey blocks over 1 second (a curtain-drop effect). Or simply freeze in place.
- "GAME OVER" centered over the playfield, 36px, #FF0000
- "Score: {N}" below, 22px, #FFFFFF
- If new high score: "NEW BEST!" pulsing in #FFD740
- "Lines: {N}" and "Level: {N}" below, 16px, #AAAAAA
- "Enter to restart" 16px, #666666, blinking
- Enter → TITLE

## 15. UI Panels

### Right Panel Layout (x = 320–470)

**Hold box (top):**
- y = 44–110
- Label: "HOLD" in 13px monospace, #888888, at (320, 40)
- A 100×66px box with 1px #333333 border
- The held piece renders inside, centered, at 70% scale, in its natural color
- When hold is unavailable (already used this piece): dim the held piece to 30% opacity

**Next pieces (below hold):**
- y = 130–310
- Label: "NEXT" in 13px monospace, #888888
- Three preview slots, each 100×56px, stacked vertically with 4px gaps
- Each upcoming piece renders centered in its slot at 70% scale in its color
- The top slot is the immediate next piece

**Score area (below next):**
- "SCORE" label at y = 330, 12px, #888888
- Score value at y = 348, 18px, #FFFFFF
- "BEST" label at y = 378, 12px, #888888
- High score value at y = 396, 18px, #555555
- "LINES" label at y = 426, 12px, #888888
- Lines value at y = 444, 18px, #FFFFFF
- "LEVEL" label at y = 474, 12px, #888888
- Level value at y = 492, 18px, #FFFFFF

## 16. Visual Details

### Piece Colors (Repeated for Emphasis)

| Piece | Color | Hex |
|-------|-------|-----|
| I | Cyan | #00F0F0 |
| O | Yellow | #F0F000 |
| T | Purple | #A000F0 |
| S | Green | #00F000 |
| Z | Red | #F00000 |
| J | Blue | #0000F0 |
| L | Orange | #F0A000 |

### Block Rendering

Each cell of a locked or active piece renders as a 26×26px filled square (1px inset from cell edges for the gap), with:
- Base color: the piece's color
- A 2px lighter border on the top and left edges (highlight, piece color + 40% toward white)
- A 2px darker border on the bottom and right edges (shadow, piece color × 0.7)
- This faux-3D bevel makes each block look solid and stackable. It's the classic Tetris block look.

### Playfield Background

Alternate every other row with barely-different backgrounds (#111111 and #131313) to help the player count rows. Extremely subtle.

### Line Clear Flash

When rows are cleared, the cells in those rows flash #FFFFFF for 150ms, then collapse smoothly (rows above slide down over 150ms). Total animation: 300ms.

### Hard Drop Trail

When the player hard-drops, briefly render a translucent streak from the piece's original position to its landing position — a column of the piece's color at 15% opacity, visible for 100ms. This communicates the drop distance and adds punch.

### Level-Up Flash

When the level increases, the playfield border briefly flashes from #333333 to #FFFFFF over 200ms, then fades back. A subtle "something changed" cue.

## 17. Audio

Web Audio API. `AudioContext` on first interaction.

| Event | Sound | Implementation |
|-------|-------|----------------|
| Move (left/right) | Quiet tick | 200Hz square, 20ms, gain 0.08 |
| Rotate | Click | 400Hz square, 30ms, gain 0.12 |
| Soft drop (per cell) | Faint thud | 100Hz triangle, 15ms, gain 0.06 |
| Hard drop | Impact slam | 150Hz square, 80ms, gain 0.25, quick pitch bend to 80Hz |
| Lock (piece commits) | Solid click | 250Hz square, 40ms, gain 0.15 |
| Single line clear | Clean chime | 500Hz square, 100ms, gain 0.2 |
| Double | Higher chime | 600Hz, 120ms, gain 0.22 |
| Triple | Even higher | 700Hz, 140ms, gain 0.24 |
| Tetris (4 lines) | Triumphant! | Arpeggio: 523→659→784→1047Hz, 50ms each, gain 0.28 |
| Level up | Rising sweep | 400Hz→800Hz sawtooth, 250ms, gain 0.2 |
| Hold | Swap sound | 300Hz→500Hz, 40ms, gain 0.1 |
| Game over | Descending doom | 300Hz→60Hz square, 800ms, gain 0.3 |
| New high score | Fanfare | C5→E5→G5→C6, 80ms each, sine, gain 0.22 |

All audio gracefully optional.

## 18. Game State on Restart

When restarting (Enter from GAME_OVER → TITLE → Enter):
- Playfield: empty (all cells null)
- Score: 0
- Lines: 0
- Level: selected starting level (default 0)
- Hold: empty, hold available
- Piece queue: new shuffled bags
- Combo counter: 0
- DAS timers: reset
- Gravity timer: reset

## 19. Implementation Notes

1. **Separate the active piece from the grid.** The falling piece exists as its own object (type, rotation state, grid position). Only when it locks do you write its cells into the playfield array. This simplifies movement, rotation, and rendering — you never have to "erase" the piece from the grid to move it.

2. **Collision checking is used constantly.** Write a single function: `isValid(pieceType, rotationState, gridX, gridY)` that returns true if all four cells of the piece at that position are within bounds and don't overlap any occupied playfield cell. Use it for: left/right movement, gravity drop, rotation (including all kick tests), and ghost piece projection.

3. **DAS implementation:**
   ```
   For each direction (left, right):
     if key just pressed this frame:
       move once
       dasTimer = 0
       dasPhase = "delay"  // waiting for DAS threshold
     else if key held:
       dasTimer += dt
       if dasPhase == "delay" && dasTimer >= 170:
         dasPhase = "repeat"
         arrTimer = 0
       if dasPhase == "repeat":
         arrTimer += dt
         while arrTimer >= 50:
           move once
           arrTimer -= 50
     else:
       dasTimer = 0
       dasPhase = null
   ```

4. **Gravity accumulator:**
   ```
   gravityTimer += dt
   while (gravityTimer >= currentInterval):
       if canMoveDown(activePiece):
           activePiece.y += 1
       else:
           startOrContinueLockDelay()
       gravityTimer -= currentInterval
   ```
   Cap the `while` to avoid teleporting after a tab-switch (max 2–3 iterations).

5. **Line clear detection:** After locking a piece, iterate rows bottom to top. Collect indices of all full rows. Remove them, collapse, then spawn the next piece. Don't forget: the collapsed rows might create new full rows (they won't — collapsing only moves things down, never fills gaps — but verify your logic doesn't double-trigger).

6. **Ghost piece recalculation** depends on the active piece's current position and rotation. It must update after every move, rotate, or new piece spawn. It's just: clone the piece's position, drop it one row at a time until `isValid` fails, use the last valid position.

7. **Hold lockout:** Use a boolean `holdUsedThisTurn`. Set true when the player holds. Reset to false when a new piece spawns naturally (not via hold).

8. **The 7-bag should be pre-filled.** Always have at least 7 pieces in the queue. When the queue drops below 7, generate a new shuffled bag and append it. This ensures the Next preview always has enough to show.

9. **Key edge detection for rotation, hard drop, and hold:** Track a `keyWasDown` map. On each frame: if a key is down now and was NOT down last frame, it's an edge trigger. Update `keyWasDown` at end of frame. These actions should only fire on the edge, not continuously.

10. **Coordinate convention.** Pick one and document it in a comment:
    - Option A: row 0 = bottom of playfield, row 21 = top hidden row. y++ = up visually.
    - Option B: row 0 = top hidden row, row 21 = bottom. y++ = down visually (matches screen coords).
    - Option B is more natural for canvas rendering. Just be consistent.

## 20. Acceptance Criteria

- [ ] Loads with no console errors
- [ ] Title screen with piece showcase, high score, optional level select
- [ ] Seven distinct tetrominoes with correct shapes and colors
- [ ] Pieces spawn at top-center, fall at a speed determined by level
- [ ] Left/right movement with DAS (170ms delay, 50ms auto-repeat)
- [ ] Clockwise and counter-clockwise rotation with SRS wall kicks
- [ ] Soft drop accelerates the piece and awards 1 point per cell
- [ ] Hard drop instantly places the piece and awards 2 points per cell
- [ ] Ghost piece shows the landing position at all times
- [ ] Hold piece works (once per piece, swaps correctly, displays in panel)
- [ ] Pieces lock after 500ms on a surface (resettable up to 15 times by movement)
- [ ] Full rows are detected and cleared with a flash animation
- [ ] Rows above collapse downward after a clear
- [ ] Scoring follows Guideline: Singles 100, Doubles 300, Triples 500, Tetris 800 (× level+1)
- [ ] Back-to-back Tetris bonus (1.5×)
- [ ] Combo counter awards bonus points for consecutive clears
- [ ] 7-bag randomizer ensures fair piece distribution
- [ ] Next queue shows 3 upcoming pieces
- [ ] Level advances every 10 lines; gravity speed increases per the table
- [ ] Game over when a new piece can't spawn (stack reaches the top)
- [ ] Score, high score (localStorage), lines, and level display correctly
- [ ] Pause freezes all timers and hides the playfield (or overlays it)
- [ ] Restart fully resets all state

## 21. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML scaffold | DOCTYPE, 480×640 canvas, #0a0a0a background, centered, inline CSS, `<script>` | Dark canvas renders, no errors |
| T02 | Game loop & input | `requestAnimationFrame`, delta-time. Key-state map + edge detection for rotation/hard-drop/hold. DAS system for left/right. | Loop runs; keys tracked; DAS moves: tap = 1 cell, hold = delay then rapid |
| T03 | State machine | TITLE, PLAYING, PAUSED, LINE_CLEAR (sub-state), GAME_OVER. Transitions: Enter, P/Escape. | All states reachable; transitions correct |
| T04 | Playfield & rendering | 10×22 grid (20 visible). 28×28 cells. Grid lines, border. Beveled block rendering (highlight/shadow edges). | Empty playfield renders; blocks look solid and 3D |
| T05 | Piece definitions | All 7 tetrominoes: shapes, colors, all 4 rotation states pre-computed. O-piece single state. I-piece in 4×4, others in 3×3. | Each piece renders correctly in all rotation states |
| T06 | Piece spawning & 7-bag | 7-bag randomizer with Fisher-Yates. Queue pre-filled. Pieces spawn at top-center in state 0. Game over if spawn overlaps. | Pieces appear in fair distribution; no long droughts; game over triggers |
| T07 | Gravity & falling | Accumulator-based gravity at level-appropriate speed. Piece falls one cell per tick. | Piece descends at correct speed; speeds up at higher levels |
| T08 | Movement (left/right) | DAS: immediate move, 170ms delay, 50ms repeat. Collision checking against walls and locked blocks. | Tap = 1 cell; hold = delay then smooth repeat; stops at walls/blocks |
| T09 | Rotation + SRS kicks | CW (Up) and CCW (Z). Attempt basic rotation, then 4 kick offsets per SRS table. I-piece uses its own table. Edge-triggered. | Pieces rotate; wall kicks find valid positions; rotation near walls works |
| T10 | Lock delay | 500ms timer when piece rests on surface. Reset on move/rotate (max 15 resets). Piece locks when timer expires. Hard drop bypasses. | Piece locks after delay; movement resets timer; hard drop locks instantly |
| T11 | Soft drop & hard drop | Down = 20× gravity, +1 pt/cell. Space = instant drop to ghost + lock, +2 pts/cell. Hard drop trail visual. | Both drops work; points awarded; hard drop shows trail |
| T12 | Ghost piece | Translucent piece at lowest valid position below active piece. Updates on every move/rotate. | Ghost visible; accurately shows landing position |
| T13 | Line clears | Detect full rows after lock. Flash white (150ms), collapse (150ms). Remove rows, shift above down. Multiple simultaneous clears. | Lines clear with animation; playfield state correct after collapse |
| T14 | Scoring | Singles/Doubles/Triples/Tetris × (level+1). Back-to-back Tetris 1.5×. Soft/hard drop points. Combo bonus. | All scores calculate correctly per spec |
| T15 | Level progression | Level up every 10 lines. Gravity increases per speed table. Optional starting level select. | Level advances; speed noticeably increases; starting level works |
| T16 | Hold piece | Shift/C swaps active ↔ held. Once per turn. Held piece displays in panel. Reset rotation on hold. | Hold works; can't hold twice per piece; display correct |
| T17 | Next preview | Show next 3 pieces from queue in right panel, correct colors, centered in slots. | Preview shows 3 upcoming pieces; updates as pieces spawn |
| T18 | HUD panels | Hold box, Next box, Score/Best/Lines/Level — all positioned in right panel per spec. | All UI elements render with correct values |
| T19 | Title & game over | Title: "TETRIS" + piece showcase + level select + start prompt. Game over: score, new-best, stats, restart. | Screens display and transition correctly |
| T20 | Audio | Web Audio: move tick, rotate click, soft-drop thud, hard-drop slam, lock click, clear chimes (ascending by lines), Tetris arpeggio, level-up sweep, game over, high score fanfare. | Sounds trigger correctly; game works if audio fails |
| T21 | Polish & testing | Full acceptance criteria pass. Test: T-spin kicks, I-piece wall kicks, DAS consistency, hold edge cases, combo counting, back-to-back tracking, high-speed levels (19+), stack-to-top game over, tab-switch recovery. | All criteria met; game feels tight, responsive, and fair |
