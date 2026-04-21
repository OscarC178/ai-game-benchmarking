# Game Spec: Snake

## 1. Overview

Snake (Nokia 6110, 1997 — descended from Blockade, 1976). A snake moves continuously across a walled grid. The player controls only its direction — it never stops. Eating food makes the snake one segment longer and awards points. Colliding with a wall or any part of the snake's own body ends the game. There is no way to win. The goal is to survive as long as possible while the snake's growing length steadily reduces the safe space on the board.

The critical design fact: Snake is a **discrete, tick-based** game, not a continuous-physics game. Every game tick, the snake jumps forward exactly one grid cell. The player's only action is choosing which direction the next jump goes. The rendering layer interpolates between ticks to create smooth animation, but the game logic underneath is a grid turn machine. Every design decision flows from this.

## 2. Canvas & Layout

- **Canvas:** 660×700px
- **HUD:** Top 40px (y = 0–39) — score, high score, speed indicator
- **Play area:** 620×620px, offset 20px from left and 40px from top — so the play area spans pixel (20, 40) to pixel (640, 660)
- **Below play area:** 20px padding to canvas bottom edge
- **Grid:** 20 columns × 20 rows, each cell 31×31px
- **Background:** #111111 (play area), #0a0a0a (outside play area and HUD)
- **Grid lines:** 1px #1a1a1a between cells — structural, not decorative. They help the player count cells and plan routes.
- **Play area border:** 2px #333333
- **Frame rate:** 60 FPS render loop. Game logic ticks at a separate, variable rate (see section 6).

## 3. Game Objects

### Snake

**Data structure:** An ordered list of grid coordinates. Index 0 is always the head. The final element is the tail tip. Starting state: 3 segments — head at (10, 10), body at (9, 10), tail at (8, 10), facing right.

**Rendering:**

- Each segment is a rounded rectangle, 27×27px (2px inset from each cell edge), corner radius 5px
- **Head:** #4caf50 (bright green). Two eyes on the leading face — each eye is a 5×5px white rounded square containing a 2×2px #1a1a1a pupil. Eyes sit at roughly 25% and 75% across the leading face, each 3px from the edge.
- **Body:** Alternates #388e3c and #2e7d32 per segment (index 1 gets the first color, index 2 the second, etc.). The stripe helps perceive length and movement.
- **Gap between segments:** The 2px inset per side creates a 4px visual gap between adjacent segments. Do not connect segments into a continuous band — the segmented look is iconic to Snake and helps the player see the body layout.

**Movement:** One cell per tick. The snake has a heading (up/down/left/right). Each tick, a new head cell is computed as currentHead + direction vector, and the tail cell is removed (unless the snake is growing). Between ticks, the renderer interpolates positions for smooth animation (see section 10).

**Growth:** When the snake eats food, it grows by 1 segment. Implementation: set a `growthPending` counter. Each tick, if `growthPending > 0`, skip the tail removal and decrement the counter. This naturally extends the snake from the tail end.

### Food

- **One food item** exists at all times
- **Appearance:** 12px-radius circle, #f44336 (red), centered within its grid cell
- **Glow:** Faint radial shadow behind the food — a 20px-radius circle at #f4433633. Subtle, but makes the food visible at a glance.
- **Spawning:** When eaten (or at game start), immediately pick a new random position from the set of all unoccupied cells. Do not use rejection sampling (random guess → check → retry). Build the set of empty cells, pick a random index. This is O(cells) and guaranteed, whereas rejection sampling degrades as the snake fills the grid.
- **Points:** 10

### Bonus Item

- **Spawn trigger:** Every 5th regular food eaten (after eating food #5, #10, #15, etc.)
- **Appearance:** A diamond shape (rotated square), 10×10px, #ffd740 (gold), centered in a random unoccupied cell that is also not the regular food's cell
- **Duration:** 8 seconds, then it vanishes
- **Visual countdown:** A thin (2px) ring around the diamond starts as a full circle (radius 14px) and shrinks linearly to radius 0 over 8 seconds. During the last 2 seconds, the diamond also blinks at 6Hz.
- **Points:** 50
- **Timer behavior:** The bonus timer pauses when the game is paused. Track it as remaining milliseconds, only decrementing during active play.

## 4. Controls

| Input | Action |
|-------|--------|
| Arrow Up / W | Face north |
| Arrow Down / S | Face south |
| Arrow Left / A | Face west |
| Arrow Right / D | Face east |
| Enter | Start / Restart |
| P or Escape | Pause / Unpause |

### The Three Input Laws

These are non-negotiable. Violating any one of them creates a game that frustrates or kills the player unfairly.

**Law 1 — No 180° reversal.** If the snake faces right, pressing left is silently discarded. If it faces up, pressing down is discarded. Only 90° turns (perpendicular to current heading) are accepted. Rationale: a reversal would instantly drive the head into the neck (segment index 1), killing the player from a single misdirected keypress.

**Law 2 — Maximum one direction change per tick.** Even if the player presses two keys between ticks, only one direction change applies per tick. Without this constraint, two rapid inputs within a single tick can create an illegal state: for example, a snake moving right receives Up then Left in one tick — Up is perpendicular (valid), and Left is now perpendicular to Up (valid) — but the combined result reverses the snake. The one-change-per-tick rule prevents this.

**Law 3 — Input queue of depth 2.** Buffer up to 2 pending directions. Each tick consumes at most one entry from the queue. This solves the problem of fast L-shaped turns: if the player wants to go from right → up → left (a U-turn via two perpendicular turns across two ticks), they'll press Up and Left in rapid succession. Without a buffer, the Left press is lost if it arrives during the same frame as the Up press. With the buffer, Up applies on tick N and Left applies on tick N+1.

**Implementation:**

```
directionQueue = []   // max length 2

onKeyDown(key):
    newDir = keyToDirection(key)
    if directionQueue.length >= 2: return
    // validate against the last queued direction (or current heading if queue empty)
    referenceDir = directionQueue.length > 0 ? directionQueue[last] : currentHeading
    if newDir is not the opposite of referenceDir:
        directionQueue.push(newDir)

onTick():
    if directionQueue.length > 0:
        candidate = directionQueue.shift()
        if candidate is not opposite of currentHeading:  // double-check
            currentHeading = candidate
```

## 5. Collision Rules

Processed each tick **after** computing the new head position but **before** moving the snake.

### Wall Collision

If the new head position is outside the 20×20 grid (x < 0, x ≥ 20, y < 0, y ≥ 20) → death.

### Self-Collision

If the new head position matches any segment currently in the snake's body → death.

**Critical exception — the tail chase rule:** If the snake is NOT growing this tick (i.e., the tail will be removed in the movement step), exclude the very last segment from the collision check. That segment is about to vacate its cell. The head can legally enter it. Without this exception, the player cannot follow their own tail in a tight spiral, which is a core survival technique in endgame Snake. Every player who has played Snake expects this to work.

**If the snake IS growing** (tail won't be removed), the last segment stays — so the full body is checked and the exception does not apply.

### Food Collision

If the new head position matches the food's cell → +10 points, increment `growthPending`, increment `foodEaten` counter, spawn new food, check bonus spawn trigger.

### Bonus Collision

If the new head position matches the bonus item's cell (and it exists) → +50 points, remove the bonus.

## 6. Tick Rate & Difficulty

| Level | Score to reach | Ticks/sec | Tick interval |
|-------|---------------|-----------|---------------|
| 1 | 0 | 7 | 143ms |
| 2 | 50 | 8 | 125ms |
| 3 | 100 | 9 | 111ms |
| 4 | 180 | 10 | 100ms |
| 5 | 280 | 11 | 91ms |
| 6 | 420 | 12 | 83ms |
| 7 | 600 | 13 | 77ms |
| 8 | 800 | 14 | 71ms |
| 9 (max) | 1100 | 15 | 67ms |

Speed never decreases. The tick rate is the primary difficulty lever — combined with increasing body length, the game becomes dramatically harder. At level 1 the player has ~143ms to think per move. At level 9 they have ~67ms.

## 7. Scoring & High Score

| Event | Points |
|-------|--------|
| Regular food | 10 |
| Bonus pickup | 50 |

**High score:** Persist in `localStorage` under key `"snake_best"`. Load on page init (default to 0 if absent). Update whenever the current score exceeds the stored best, at the moment it happens (not only at game over). Display in HUD at all times.

## 8. Game States

```
TITLE → COUNTDOWN → PLAYING → DYING → GAME_OVER → TITLE
                       ↕
                    PAUSED
```

### TITLE

- Dark grid visible (dimmed — draw the grid at 30% opacity)
- **Demo snake:** A 5-segment snake running autonomously on the grid, eating food, growing. AI logic: target the food greedily — choose the direction toward food that doesn't immediately collide with a wall or itself. If all directions are lethal, it dies. On death, respawn a fresh 3-segment demo snake after 1 second. This is ambient ambiance, not a tutorial.
- "SNAKE" centered in the play area at roughly y=250 (canvas coords), 48px bold monospace, #4caf50
- "Press Enter" at y≈400, 18px monospace, #888888, opacity pulsing smoothly from 0.3 to 1.0 (sinusoidal, 2s period)
- "Best: {N}" at y≈440, 15px monospace, #555555
- Enter → COUNTDOWN

### COUNTDOWN

- Grid, starting snake (3 segments at center, facing right), and first food all render fully
- Centered sequence: **"3"** → **"2"** → **"1"** at 650ms each, then **"GO!"** for 450ms
- Numbers: 60px monospace, #ffffff, with a scale animation — each number appears at 120% size and eases down to 100% over its display window
- "GO!": same size, #4caf50
- **Input is accepted and buffered during countdown.** The player can pre-select a starting direction. The snake doesn't move until countdown ends.
- After "GO!" → PLAYING

### PLAYING

- Tick logic runs. Rendering runs. All collisions active.
- P or Escape → PAUSED

### PAUSED

- Tick accumulator freezes. Bonus timer freezes.
- #000000 at 70% opacity overlay on the play area
- "PAUSED" centered, 36px monospace, #ffffff
- "P to resume" below, 14px, #888888
- HUD remains fully visible above overlay
- P or Escape → PLAYING (timers resume seamlessly)

### DYING

- Duration: ~0.8 seconds total
- Phase 1 (0–500ms): Segments turn #f44336 (red) one at a time, head to tail. Interval = 500ms / segmentCount. Each segment transitions via a quick 50ms color cross-fade, not an instant swap.
- Phase 2 (500–600ms): All segments flash #ffffff for 100ms
- Phase 3 (600–800ms): All segments fade to #444444 over 200ms
- No player input accepted.
- After animation → GAME_OVER

### GAME_OVER

- Dead snake visible (grey segments, #444444)
- Food and bonus removed from display
- "GAME OVER" centered at y≈270, 38px monospace, #f44336
- "Score: {N}" at y≈320, 22px monospace, #ffffff
- If new high score: "NEW BEST!" at y≈350, 16px monospace, #ffd740, opacity pulsing (sine, 0.5–1.0, period 1s)
- "Length: {N}" at y≈380, 14px monospace, #888888
- "Enter to play again" at y≈430, 14px monospace, #666666, blinking at 2Hz
- Enter → TITLE

## 9. HUD

The 40px strip at the top of the canvas.

| Element | Position | Style |
|---------|----------|-------|
| Score | Left-aligned, x=24, y=27 | "Score: {N}", 17px monospace, #ffffff |
| High score | Right-aligned, x=636 (right edge), y=27 | "Best: {N}", 17px monospace, #555555 |
| Speed indicator | Centered horizontally, y=27 | 9 dots (3px radius circles) spaced 12px apart. Filled dots = #4caf50 (current level), unfilled = #2a2a2a |

1px #222222 horizontal line at y=39 as a divider.

## 10. Visual Interpolation

At level 1 (7 ticks/sec), the snake advances one 31px cell every 143ms. Without interpolation, the snake appears to teleport from cell to cell — 7 jumps per second looks awful, like a slideshow.

**Solution:** Decouple rendering from tick logic. Each tick, store every segment's **previous** grid position and **current** grid position. During rendering, compute:

```
tickProgress = timeAccumulator / tickInterval    // 0.0 to ~1.0

for each segment:
    renderX = lerp(segment.prevGridX, segment.currGridX, tickProgress) × cellSize + areaOffsetX
    renderY = lerp(segment.prevGridY, segment.currGridY, tickProgress) × cellSize + areaOffsetY
```

This slides each segment smoothly from its old cell to its new cell between ticks.

**Tail retraction:** When the snake isn't growing, the old tail position should visually shrink/fade out. Render the departing tail cell at `(1 - tickProgress)` opacity, so it smoothly disappears rather than popping out of existence.

**Direction changes and corners:** When the snake turns, the head's previous and current positions form an L-shape, not a straight line. Linear interpolation between them produces a diagonal shortcut through a wall cell. **Simplest fix:** for the head segment only, when a direction change occurred this tick, skip interpolation and snap the head to its current position. The 1-frame snap is imperceptible at 60fps and avoids rendering artifacts. Advanced alternative: interpolate along the L-path (move along old direction first, then new direction), but this significantly increases complexity for minimal visual gain.

## 11. Audio

Generate all sounds programmatically with the Web Audio API. Instantiate `AudioContext` on the first user interaction (the Enter key on the title screen).

| Event | Sound | Implementation |
|-------|-------|----------------|
| Eat regular food | Quick chirp | 600Hz square wave, 55ms, gain 0.2 |
| Eat bonus | Rising triple note | 600Hz→800Hz→1050Hz, 45ms each, 5ms silent gap between, gain 0.2 |
| Change direction | Subtle tick | 140Hz triangle wave, 12ms, gain 0.06 (barely perceptible — tactile, not musical) |
| Level up (speed increase) | Rising sweep | 350Hz sawtooth, bending up to 700Hz over 200ms, gain 0.18 |
| Death | Descending crunch | 200Hz square wave, 450ms, bending down to 55Hz, gain 0.3 |
| New high score jingle | Victory arpeggio | C5 (523Hz) → E5 (659Hz) → G5 (784Hz) → C6 (1047Hz), 65ms each, gain 0.2 |

Every sound is optional. If Web Audio is unavailable or throws an error, catch it and continue silently. No sound should ever block gameplay.

## 12. Implementation Notes

1. **Use an accumulator for tick timing, not `setInterval`.** Inside `requestAnimationFrame`:
   ```
   dt = Math.min(now - lastFrameTime, 500)   // cap at 500ms to handle tab-switch
   accumulator += dt
   while (accumulator >= tickInterval) {
       gameTick()
       accumulator -= tickInterval
   }
   tickProgress = accumulator / tickInterval
   render(tickProgress)
   ```
   The `while` loop handles the case where one render frame spans multiple ticks (shouldn't happen in normal play, but does after a tab switch). Cap the `while` to a maximum of 2 iterations to prevent the snake from teleporting dozens of cells at once.

2. **Grid ↔ Pixel coordinate mapping:**
   ```
   pixelX = gridX × 31 + 20    // 31px cell + 20px area offset
   pixelY = gridY × 31 + 40    // 31px cell + 40px HUD offset
   ```

3. **Rounded rectangles:** `ctx.roundRect()` is available in modern browsers. If targeting broader compatibility, implement manually:
   ```
   function roundRect(ctx, x, y, w, h, r) {
       ctx.beginPath()
       ctx.moveTo(x + r, y)
       ctx.arcTo(x + w, y, x + w, y + h, r)
       ctx.arcTo(x + w, y + h, x, y + h, r)
       ctx.arcTo(x, y + h, x, y, r)
       ctx.arcTo(x, y, x + w, y, r)
       ctx.closePath()
   }
   ```
   If this causes any issues, plain rectangles are acceptable. Gameplay over cosmetics.

4. **Empty cell selection for food spawn:** Maintain the snake as an array and the food/bonus positions. To find empty cells:
   ```
   occupied = new Set(snake.map(s => s.x + ',' + s.y))
   if (food) occupied.add(food.x + ',' + food.y)
   if (bonus) occupied.add(bonus.x + ',' + bonus.y)
   empty = []
   for (x = 0; x < 20; x++)
       for (y = 0; y < 20; y++)
           if (!occupied.has(x + ',' + y)) empty.push({x, y})
   return empty[Math.floor(Math.random() * empty.length)]
   ```

5. **The demo snake on the title screen** should use dumb-but-functional AI: compute direction toward food; if that direction is immediately lethal (wall or own body in the next cell), try turning 90° one way, then the other, then continue straight. If all options are lethal, it dies. Respawn after a 1-second delay with a new 3-segment snake. Don't invest complexity here — it's ambiance.

6. **State cleanup on restart.** When transitioning from GAME_OVER → TITLE → COUNTDOWN → PLAYING, ensure *all* game state resets: snake array, food position, bonus state (position, timer, null it out), score, food-eaten counter, growth counter, direction queue, tick accumulator, speed level. A stale bonus timer from the previous game leaking into a new game is the kind of bug that takes forever to find.

## 13. Acceptance Criteria

- [ ] Loads in a browser with no console errors
- [ ] Title screen shows game name, high score, and demo snake
- [ ] Countdown (3-2-1-GO) before play begins
- [ ] Snake moves one cell per tick, continuously, in a cardinal direction
- [ ] Arrow keys and WASD change direction (perpendicular turns only)
- [ ] 180° reversals are silently ignored
- [ ] Two rapid inputs in one tick don't cause self-collision (one-per-tick rule)
- [ ] Quick L-shaped turn sequences work correctly (input buffer)
- [ ] Food spawns on a random empty cell; eating it grows the snake by 1 and awards 10 points
- [ ] Bonus item appears every 5th food, visible for 8 seconds, worth 50 points
- [ ] Bonus timer pauses when the game is paused
- [ ] Wall collision → death
- [ ] Self-collision → death
- [ ] Tail chase is legal (head enters the cell the tail is leaving)
- [ ] Speed increases through 9 levels at defined score thresholds
- [ ] Movement looks smooth at all speeds (interpolated rendering)
- [ ] Death animation plays (red cascade → flash → fade)
- [ ] High score saved to localStorage, persists across reloads
- [ ] Pause freezes all timers and gameplay
- [ ] Restart from game over fully resets state

## 14. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML scaffold | DOCTYPE, 660×700 canvas, inline CSS (`#0a0a0a` bg, centered, no margins), empty `<script>` block | Opens with dark canvas, no errors |
| T02 | Render loop & tick system | `requestAnimationFrame` at 60fps. Tick accumulator with configurable interval (starting 143ms). Delta-time capped at 500ms. Max 2 ticks per frame. | Smooth frame loop; tick fires at expected rate |
| T03 | Input handling | Key-state map via keydown/keyup. Direction queue (max depth 2). Reversal rejection. One dequeue per tick. Validate against current heading. | Keys register; queue fills and drains correctly |
| T04 | State machine | TITLE, COUNTDOWN, PLAYING, PAUSED, DYING, GAME_OVER with correct transitions. Enter starts, P/Esc pauses. | All states reachable and transitions work |
| T05 | Grid & HUD | Draw 20×20 grid (31px cells, subtle gridlines, 2px border). 40px HUD with score, best, speed dots, divider. | Play area and HUD render with correct geometry |
| T06 | Snake: render & move | Snake as array of grid coords. 3 initial segments. Head in bright green with eyes, body in striped darker greens. Rounded 27×27px segments. Advance one cell per tick. | Snake visible and moves across grid |
| T07 | Direction control | Dequeue input each tick. Apply if perpendicular. Buffer allows L-turns across ticks. Two inputs in same tick don't fold snake. | Turning responsive; fast turns work; no unfair deaths |
| T08 | Wall & self collision | Head outside grid → DYING. Head on body segment → DYING. Tail-chase exception: exclude last segment when not growing. | Walls kill; self-collision kills; tail chase is safe |
| T09 | Food, eating, growth | Spawn food on random empty cell (set-based, not rejection). Eating: +10 pts, growthPending++, respawn food instantly. | Food spawns correctly; snake grows; score updates |
| T10 | Smooth interpolation | Store prev/curr grid position per segment. Compute tickProgress. Lerp render positions. Tail fade-out. Head snap on direction change. | Movement visually smooth; no choppy cell-jumping |
| T11 | Speed progression | 9 levels (7→15 ticks/sec). Check thresholds on score change. Update tick interval. Speed dots in HUD. | Speed increases perceptibly; dots update |
| T12 | Bonus pickup | Gold diamond every 5th food. 8-second timer with shrinking ring. Blinks last 2s at 6Hz. +50 pts. Timer pauses when paused. Vanishes on expiry. | Bonus spawns, counts down, blinks, collects/vanishes correctly |
| T13 | Scoring & persistence | Score in HUD. High score from localStorage. Update best on beat. Display in HUD, title, game over. | Scores correct; high score persists across reloads |
| T14 | Title screen | "SNAKE" title, demo snake AI, pulsing "Press Enter", high score. | Title renders; demo snake is alive and eating |
| T15 | Countdown | 3-2-1-GO over starting snake/food. Scale animation on numbers. Direction input buffered during countdown. | Countdown plays; pre-selected direction works on first tick |
| T16 | Death animation | Red cascade head→tail (500ms), white flash (100ms), grey fade (200ms). No input. → GAME_OVER. | Full animation plays; clean transition |
| T17 | Game over & pause screens | Game over: score, length, new-best callout, restart prompt. Pause: overlay, text, resume instruction. | Both screens correct; restart fully resets state |
| T18 | Audio | WebAudio: eat chirp, bonus arpeggio, turn tick, level-up sweep, death tone, high-score jingle. AudioContext on first Enter. Graceful failure. | Sounds play correctly; game works if audio fails |
| T19 | Polish & edge cases | Full acceptance criteria pass. Test: long snake near-fill, tab-switch recovery, rapid restart, pause during bonus, pause during countdown, direction input during death. | All criteria met; no bugs in edge cases |
