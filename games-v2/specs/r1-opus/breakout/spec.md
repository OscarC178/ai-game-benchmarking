# Game Spec: Breakout

## 1. Overview

Breakout (Atari, 1976 — designed by Wozniak and Jobs before they founded Apple). You have a paddle at the bottom of the screen. A ball bounces around above it. The top half of the screen is filled with rows of colored bricks. The ball destroys bricks on contact. Your job is to keep the ball alive by deflecting it with the paddle, and to clear every brick to complete the level. Miss the ball and you lose a life. Lose all lives and it's over.

The game's depth comes from one mechanic: where the ball hits the paddle determines the angle it returns at. Dead center sends it straight up. The paddle edges send it at steep angles. This gives the player full control over where the ball goes — turning what looks like a luck game into a precision aiming game. Everything else is secondary to getting this mechanic right.

## 2. Canvas & Layout

- **Canvas:** 780×600px
- **Background:** #0d0d0d
- **HUD:** Top 36px strip (y = 0–35). Score, high score, lives, level.
- **Play area:** 780px wide × 564px tall, from y = 36 to y = 600
- **Frame rate:** 60 FPS via `requestAnimationFrame` with delta-time
- **Coordinate system:** Origin top-left. x increases rightward, y increases downward.
- All rendering is geometric primitives — no images, no sprites, no external assets.

## 3. Game Objects

### Paddle

- **Size:** 104px wide × 12px tall (level 1). Shrinks by 8px per level (minimum 64px).
- **Color:** #ffffff
- **Corner radius:** 6px
- **Y position:** Fixed at y = 564 (24px above bottom of play area)
- **Starting X:** Centered horizontally (x = 338)
- **Movement:** Horizontal only. Two input methods, both active simultaneously:
  - **Keyboard:** Arrow Left / A moves left, Arrow Right / D moves right at 500px/s
  - **Mouse:** Paddle center tracks cursor x-position instantly (no smoothing — direct mapping feels most responsive)
- **Wall clamping:** Paddle left edge cannot go below x = 0, right edge cannot exceed x = 780.

### Ball

- **Shape:** Circle, radius 7px
- **Color:** #ffffff
- **Starting position:** Resting on top of paddle, centered — (paddleCenterX, 550)
- **Attached state:** Before launch, the ball sits on the paddle and moves with it. The player aims by positioning the paddle, then presses Space to release.
- **Initial speed:** 320px/s
- **Speed increment:** +12px/s each time the ball hits the paddle
- **Maximum speed:** 520px/s
- **Speed reset:** On life lost, speed resets to 320 + (level - 1) × 20 px/s. (Each level starts slightly faster than the last.)
- **Launch angle:** On Space press, the ball launches at an angle between 65° and 115° from the positive x-axis (so always predominantly upward, with slight left or right bias). If the player doesn't move the paddle before launching, default to a random angle in that range. If the paddle is moving at launch time, bias the angle slightly in the movement direction (±10°).

### Bricks

The brick field is the visual centerpiece and the gameplay target.

- **Brick dimensions:** 64px wide × 18px tall
- **Gaps:** 4px horizontal between bricks, 4px vertical between rows
- **Columns:** 11
- **Rows:** 8
- **Field position:** Centered horizontally. First brick starts at x = 18. First row starts at y = 62 (26px below HUD). Brick positions:
  - Column x: 18, 86, 154, 222, 290, 358, 426, 494, 562, 630, 698
  - Row y: 62, 84, 106, 128, 150, 172, 194, 216
- **Total brick count:** 88 per level

**Row colors and point values (top to bottom):**

| Row | Color | Hex | Points |
|-----|-------|-----|--------|
| 1 | Red | #e53935 | 7 |
| 2 | Red-orange | #f4511e | 7 |
| 3 | Orange | #fb8c00 | 5 |
| 4 | Amber | #ffb300 | 5 |
| 5 | Yellow | #fdd835 | 3 |
| 6 | Yellow-green | #c0ca33 | 3 |
| 7 | Green | #43a047 | 1 |
| 8 | Teal | #00897b | 1 |

Top rows are worth more because they're geometrically harder to reach — the ball must carve a path through lower rows first, or thread through existing gaps.

**Brick storage:** A flat array (or 2D array, 11×8) of objects:
```
{ alive: true, hp: 1, color: "#e53935", points: 7, x: 18, y: 62, w: 64, h: 18 }
```

When a brick is destroyed: set `alive = false`. Dead bricks are not rendered and not collision-checked.

### Reinforced Bricks (Level 2+)

Starting at level 2, some bricks take 2 hits to destroy:

- **Level 2:** Top row (row 1) is reinforced
- **Level 3:** Top 2 rows reinforced
- **Level 4+:** Top 3 rows reinforced
- **Visual indicator:** Reinforced bricks have a lighter inner rectangle (8px inset from each edge, 20% brighter than the brick color). On first hit, the inner rectangle disappears and a hairline crack renders across the brick (a 1px diagonal white line at 30% opacity).
- **Points:** Awarded only on destruction (not per hit). Same point value as the row.

### Indestructible Bricks (Level 5+)

From level 5 onward, 3–5 bricks in the middle rows (rows 4–5) become indestructible:

- **Color:** #616161 (dark grey)
- **Visual:** Metallic sheen — render a 1px horizontal highlight at 20% white across the middle of the brick
- **Behavior:** Ball bounces off them normally. They never break. They do not count toward the level-clear total. The player must clear all *destructible* bricks to complete the level.

## 4. Controls

| Input | Action |
|-------|--------|
| Arrow Left / A | Move paddle left (keyboard) |
| Arrow Right / D | Move paddle right (keyboard) |
| Mouse movement | Paddle tracks cursor x |
| Space | Launch ball from paddle |
| Enter | Start game from title / Restart from game over |
| P or Escape | Pause / Unpause |

Keyboard input uses a held-key state map (keydown sets true, keyup sets false). Each frame, check the map and apply continuous movement. This prevents dropped and stuck input.

Mouse and keyboard operate simultaneously. If the mouse is being used, keyboard input is still accepted (and vice versa). No mode-switching needed.

## 5. Ball Physics

### Movement

Standard: `x += vx × dt`, `y += vy × dt`. Cap dt at 50ms (0.05s) to prevent tunneling after tab switches.

### Ball ↔ Ceiling

Ball top edge reaches y ≤ 36 (HUD bottom): reflect vy. Clamp ball y so top edge = 36.

### Ball ↔ Side Walls

Ball left edge reaches x ≤ 0 or right edge reaches x ≥ 780: reflect vx. Clamp.

### Ball ↔ Floor (Life Lost)

Ball center y > 610 (below canvas + margin): life is lost. The delay gives the ball time to visually exit the screen rather than vanishing at the exact edge.

### Ball ↔ Paddle

**This is the entire game.** The paddle collision dictates the return angle, and the return angle dictates where the ball goes. If this feels wrong, nothing else matters.

Detection: check if ball's bounding circle overlaps the paddle's bounding rectangle (expand the rectangle by ball radius on all sides for the circle test, or use circle-vs-rounded-rect). Only register a hit when the ball is moving downward (vy > 0) — this prevents the ball from re-triggering as it exits upward through the paddle.

On collision:

1. **Compute hit ratio** — where on the paddle the ball struck:
   ```
   hitRatio = (ball.x - paddleCenterX) / (paddleWidth / 2)
   clamp to [-1, 1]
   ```
   -1 = left edge, 0 = center, +1 = right edge.

2. **Map to angle.** The outgoing angle is measured from straight-up (negative y direction):
   ```
   maxAngle = 65°
   angle = hitRatio × maxAngle
   ```
   So center = 0° (straight up), left edge = -65° (sharply left-upward), right edge = +65° (sharply right-upward).

3. **Set velocity:**
   ```
   vx = speed × sin(angle)
   vy = -speed × cos(angle)    // always negative — ball always goes up
   ```
   The absolute speed (magnitude of velocity vector) is preserved. Only the direction changes.

4. **Ensure vy is meaningfully negative.** If `|vy|` < speed × 0.25, nudge it to `-speed × 0.25`. An almost-horizontal ball is tedious and feels like a bug.

5. **Increase speed** by 12px/s (cap at 520).

6. **Reposition ball** so its bottom edge sits exactly on top of the paddle. Prevents re-collision next frame.

### Ball ↔ Bricks

**For each alive brick, each frame:** test if the ball's circle overlaps the brick's rectangle.

On collision:

1. **Determine reflection axis.** Which face of the brick was hit — top, bottom, left, or right? The standard approach:
   - Compute the overlap penetration on each axis
   - The axis with the **smaller** overlap is the collision axis (the ball entered from that side)
   - Reflect velocity on that axis: if vertical collision, `vy = -vy`; if horizontal, `vx = -vx`

2. **Apply damage.** Decrement brick HP. If HP = 0: set `alive = false`, add points to score, spawn particles (section 9), play destruction sound. If HP > 0: play a "dink" sound, show damage visual.

3. **Corner hits.** When the ball sits at the exact meeting point of two adjacent bricks and overlaps both: destroy (or damage) both, and reverse both vx and vy. Detect by checking all alive bricks for overlap, not stopping after the first hit. Process up to 3 brick collisions per frame to handle corners and tight clusters, but no more (prevents infinite bounce loops in degenerate cases).

4. **Push ball out of brick.** After reflecting, nudge the ball so it no longer overlaps the hit brick. Move it along the reflection axis by the penetration depth. This prevents the ball from getting stuck inside a brick.

**High-speed tunneling prevention:** At 520px/s, the ball moves ~8.7px per frame. Bricks are 18px tall. Standard overlap detection will work for bricks at this speed range. However, for the paddle (12px tall), you should also check the ball's trajectory between frames:
```
if ball was above paddle last frame AND is now below paddle:
    interpolate to find the crossing point
    check paddle coverage at that point
```
This sweep test prevents the ball from phasing through the paddle at maximum speed.

## 6. Scoring

| Target | Points |
|--------|--------|
| Green / Teal brick (rows 7–8) | 1 |
| Yellow / Yellow-green brick (rows 5–6) | 3 |
| Orange / Amber brick (rows 3–4) | 5 |
| Red / Red-orange brick (rows 1–2) | 7 |
| Reinforced (any row) | Same as row (on destruction) |
| Indestructible | N/A (cannot be destroyed) |

**Full clear bonus:** If the player clears all destructible bricks with 0 balls lost that level, award a 100-point bonus. Display "PERFECT!" in gold text for 1.5 seconds.

**High score:** `localStorage` key `"breakout_best"`. Loaded on page init (default 0). Updated whenever the current score exceeds it.

**Extra life:** Awarded at 200 points. One-time only per game. Max 5 lives (extra life won't exceed this).

## 7. Lives & Level Progression

**Starting lives:** 3 (displayed as ball icons in HUD).

**On life lost:**
1. Ball has exited below the screen. Brief 0.8-second pause (everything frozen, let the player register the miss).
2. Lives counter decrements — flash the HUD lives display red for 0.3s.
3. If lives remain: ball reattaches to the paddle (attached state). Brick layout is **not** reset — damage persists. Speed resets to the level's base speed.
4. If 0 lives remain: → GAME_OVER.

**Level completion triggers when** every destructible brick is destroyed (alive = false for all bricks where `hp` was originally > 0). Indestructible bricks are excluded from this count.

**On level clear:**
1. Remaining ball freezes.
2. Brief screen flash — canvas background goes #ffffff for 60ms, then back to #0d0d0d.
3. "LEVEL {N} CLEAR!" centered in the play area, 32px monospace, #ffffff, for 2 seconds. Below it, the level score and any PERFECT bonus.
4. Next level loads: new brick field with updated parameters (reinforced rows, possible indestructibles), paddle width shrinks by 8px, base ball speed increases by 20px/s, ball reattaches to paddle.

**Difficulty scaling summary:**

| Level | Base ball speed | Paddle width | Reinforced rows | Indestructible bricks |
|-------|----------------|-------------|----------------|----------------------|
| 1 | 320 | 104 | 0 | 0 |
| 2 | 340 | 96 | 1 | 0 |
| 3 | 360 | 88 | 2 | 0 |
| 4 | 380 | 80 | 3 | 0 |
| 5 | 400 | 72 | 3 | 3 |
| 6 | 400 | 64 | 3 | 5 |
| 7+ | 400 | 64 | 3 | 5 |

Speed and paddle stop getting harder after level 6. By that point, the base speed + paddle hit acceleration makes the game sufficiently brutal.

## 8. Game States

```
TITLE → SERVE → PLAYING → (LIFE_LOST or LEVEL_CLEAR) → (SERVE or GAME_OVER)
                   ↕
                PAUSED
```

### TITLE

- Brick field from level 1 renders as a static backdrop, dimmed to 40% opacity
- A ball bounces around the play area autonomously — no paddle, just wall bounces and brick destruction (bricks respawn after all are cleared, with a 1-second delay). This is the attract mode — shows the game in action.
- **"BREAKOUT"** centered at y = 240, 52px bold monospace, #ffffff
- Ghost descriptions beneath: four colored squares (matching the row colors) with point values next to each, arranged horizontally. This subtly teaches scoring before the player starts.
- **"Press Enter"** at y = 430, 20px monospace, #888888, pulsing opacity (sine, 0.3→1.0, 2s period)
- **"Best: {N}"** at y = 470, 15px monospace, #555555
- **Controls hint:** "← → Move | Space Launch | P Pause" at y = 500, 13px, #333333
- Enter → SERVE (level 1)

### SERVE

- Full brick field rendered. Paddle rendered with ball attached on top.
- "READY" centered in the play area, 36px, #ffffff, displayed for 1.2 seconds. Fades out over the final 0.3s.
- Player can move the paddle during this phase to choose starting position.
- After "READY" disappears, a small aiming arrow appears above the ball — a thin 20px line pointing in the launch direction, rotating slightly as the paddle moves (previewing the launch angle). This helps the player aim.
- Space launches the ball. Arrow disappears.
- → PLAYING

### PLAYING

- All physics, collision, scoring active.
- P or Escape → PAUSED.

### PAUSED

- All movement and timers freeze.
- Overlay: #000000 at 60% opacity over the play area.
- "PAUSED" centered, 36px, #ffffff.
- "P to resume" below, 14px, #888888.
- HUD stays fully visible.
- P or Escape → PLAYING.

### LIFE_LOST

- 0.8s freeze after ball exits.
- Lives counter decrements (red flash on HUD).
- If lives > 0 → SERVE (ball reattaches to paddle, brick state preserved).
- If lives = 0 → GAME_OVER.

### LEVEL_CLEAR

- Screen flash (60ms white).
- "LEVEL N CLEAR!" for 2 seconds + perfect bonus if applicable.
- Load next level → SERVE.

### GAME_OVER

- Play area overlay: #000000 at 70%.
- Remaining bricks visible through the overlay (dimmed).
- "GAME OVER" centered at y = 240, 44px, #e53935.
- "Score: {N}" at y = 295, 26px, #ffffff.
- If new high score: **"NEW HIGH SCORE!"** at y = 330, 18px, #ffb300, pulsing.
- "Level reached: {N}" at y = 360, 16px, #888888.
- "Enter to play again" at y = 420, 16px, #666666, blinking at 2Hz.
- Enter → TITLE.

## 9. Visual Effects

### Brick Destruction Particles

When a brick is destroyed, emit 8 particles:
- Shape: small squares, 3×3px
- Color: same as the destroyed brick
- Starting position: brick center
- Velocity: random burst — vx in range [-120, 120], vy in range [-180, -40] (biased upward, creating a little explosion pop)
- Gravity: 400px/s² downward (particles arc and fall)
- Lifetime: 0.6 seconds, fading from full opacity to 0 linearly
- Cap total particles at 80. If exceeded, don't spawn new ones. Particles are cosmetic and expendable.

### Ball Trail

Store the ball's last 6 positions (one per frame, ring buffer). Render afterimages at each stored position with decreasing opacity: 0.4, 0.3, 0.22, 0.15, 0.1, 0.05. Same shape as the ball but shrinking slightly (radius 7, 6.5, 6, 5.5, 5, 4.5). This produces a comet-like trail that communicates speed and direction.

### Paddle Flash

On ball contact, the paddle flashes #4fc3f7 (light blue) for 50ms (3 frames), then returns to white. Quick visual confirmation of a successful deflection.

### Screen Flash on Level Clear

Fill the entire canvas with #ffffff for 60ms, then snap back to #0d0d0d. This is a punctuation mark — "you did the thing."

### Brick Damage Visual (Reinforced)

On first hit of a 2-HP brick: the brick's color darkens by 25%. Draw a 1px #ffffff33 diagonal crack from approximately (x + w×0.2, y) to (x + w×0.8, y + h). Subtle but reads as "damaged."

On first hit of a 3-HP brick (gold, if you add them): same crack, color darkens 15%. Second hit: two crossing cracks, color darkens another 20%.

### HUD Score Pop

When the score changes, briefly render the new score 10% larger for 4 frames, then ease back to normal size. Tiny bounce animation that draws the eye without demanding attention.

## 10. Audio

Web Audio API. Create `AudioContext` on first user interaction (Enter on title screen, or first mouse movement on canvas — whichever comes first).

| Event | Sound | Implementation |
|-------|-------|----------------|
| Paddle hit | Clean pop | 440Hz square, 40ms, gain 0.25 |
| Wall/ceiling bounce | Soft click | 280Hz square, 25ms, gain 0.15 |
| Brick destroy — green row | Low tone | 330Hz square, 50ms, gain 0.2 |
| Brick destroy — yellow row | Mid-low | 440Hz square, 50ms, gain 0.2 |
| Brick destroy — orange row | Mid-high | 550Hz square, 50ms, gain 0.2 |
| Brick destroy — red row | High bright | 660Hz square, 50ms, gain 0.2 |
| Brick damage (not destroyed) | Dull thud | 180Hz triangle, 35ms, gain 0.18 |
| Life lost | Descending buzz | 200Hz square, 350ms, pitch bend to 80Hz, gain 0.3 |
| Level clear | Ascending arpeggio | 523→659→784→1047Hz, 70ms each, square, gain 0.22 |
| Extra life | Chime | 880Hz then 1100Hz, 80ms each, sine, gain 0.2 |

The ascending pitch for brick destruction (low rows = low pitch, high rows = high pitch) creates a natural sonic reward for reaching the top of the field. It's instinctively satisfying.

All audio is gracefully optional. Wrap creation and playback in try/catch. If Web Audio is unavailable or throws, the game continues silently.

## 11. HUD

Top 36px bar. Background slightly lighter than play area (#141414) with a 1px #222222 divider at y = 35.

| Element | Position | Style |
|---------|----------|-------|
| "Score: {N}" | x = 16, y = 24 | 17px monospace, #ffffff |
| "Best: {N}" | x = 200, y = 24 | 17px monospace, #555555 |
| Lives | x = 500, y = 14 | Render (lives - 1) small circles (5px radius, #ffffff) spaced 16px apart. Don't show the "current" life — only remaining ones. |
| "Lv {N}" | Right-aligned, x = 750, y = 24 | 16px monospace, #aaaaaa |

Why `lives - 1` for the display: the "current" life is the ball in play. The dots represent how many more chances you have after this one. 3 lives = 2 dots displayed. More intuitive than counting the active ball as a "life."

## 12. Implementation Notes

1. **Delta-time everything.** `ball.x += ball.vx × dt`. Cap dt at 0.05. Never assume 16.67ms frames.

2. **Collision check order matters.** Each frame: (1) move the ball, (2) check ceiling + side walls, (3) check bricks, (4) check paddle, (5) check floor. This ordering means wall bounces resolve before brick/paddle checks, preventing corner-case phasing.

   Actually — better approach: move the ball, then check ALL collisions in a unified pass, resolving the earliest collision (smallest time-of-impact). This is more robust but more complex. The ordered approach works fine for Breakout's speed range. Use it unless you encounter phasing bugs.

3. **Prevent horizontal lock.** If `|vy|` drops below `speed × 0.2` after any collision, force it to `speed × 0.2` (preserving sign). A near-horizontal ball is uninteractable — it just bounces between side walls.

4. **Brick destruction count tracking.** Maintain a counter initialized to the number of destructible bricks at level start. Decrement on each brick destruction. Level clears when the counter reaches 0. This is simpler and faster than scanning the brick array every frame.

5. **Paddle width transition.** When the paddle shrinks at the start of a new level, animate it: lerp from old width to new width over 0.3 seconds during the SERVE state. Instantaneous resize is visually jarring.

6. **Ball attachment offset.** When the ball is attached to the paddle (SERVE state), its position is:
   ```
   ball.x = paddle.x + paddle.width / 2
   ball.y = paddle.y - ball.radius
   ```
   Update this every frame so the ball moves with the paddle.

7. **Mouse input without cursor interference.** Add `canvas.style.cursor = 'none'` during gameplay to hide the system cursor (it's distracting alongside the paddle). Restore it on pause and game over.

8. **Avoid `fillText` for the score if you want retro feel.** But honestly, `fillText` with a monospace font looks fine in Breakout. The chunky bitmap digits from Pong's era are iconic to Pong specifically. Breakout can use canvas text rendering without losing authenticity.

9. **Particle pooling.** Pre-allocate an array of 80 particle objects. Instead of creating/destroying, toggle an `active` flag and overwrite properties on spawn. This avoids garbage collection pressure during rapid brick destruction sequences.

## 13. Acceptance Criteria

- [ ] Loads with no console errors
- [ ] Title screen with attract-mode ball and brick field
- [ ] Enter starts the game; ball attached to paddle until Space is pressed
- [ ] Paddle moves with arrow keys / WASD (held input, not tap) and mouse
- [ ] Ball bounces off ceiling and side walls
- [ ] Ball bounces off paddle with angle determined by hit position (center = up, edges = angled)
- [ ] Ball speed increases with each paddle hit, resets on life lost
- [ ] Bricks break on contact; correct points per row color
- [ ] Ball reflects correctly off brick faces (top/bottom/left/right)
- [ ] Corner hits (two adjacent bricks) destroy both
- [ ] Missing the ball costs a life; bricks and score persist
- [ ] Level clears when all destructible bricks are destroyed
- [ ] Next level has faster ball, smaller paddle, reinforced bricks (level 2+), indestructible bricks (level 5+)
- [ ] Score, high score (localStorage), lives, and level display in HUD
- [ ] Extra life at 200 points (once, max 5)
- [ ] Pause works (P / Escape)
- [ ] Game over screen with score, high score callout, restart
- [ ] Particle effects on brick destruction
- [ ] Ball trail renders
- [ ] No ball tunneling through paddle at high speed

## 14. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML scaffold | DOCTYPE, 780×600 canvas, #0d0d0d background, centered, inline CSS, empty `<script>` | Dark canvas renders, no errors |
| T02 | Game loop & input | `requestAnimationFrame` with capped delta-time. Key-state map for arrows, WASD, Space, Enter, P, Escape. Mouse tracking for paddle x. | Loop runs smooth; inputs tracked |
| T03 | State machine | TITLE, SERVE, PLAYING, PAUSED, LIFE_LOST, LEVEL_CLEAR, GAME_OVER. Correct transitions on Enter, Space, P, game events. | All states reachable and transitions correct |
| T04 | HUD | Score, high score, lives (circle icons), level. 36px top bar, divider line. | HUD renders with placeholder values |
| T05 | Brick field | 11×8 grid, row colors per spec, stored as objects with alive/hp/color/points/position. | 88 bricks render in correct colors and positions |
| T06 | Paddle | White rounded rectangle at y=564. Keyboard movement at 500px/s, mouse tracking. Clamped to canvas. | Paddle moves smoothly with both input methods |
| T07 | Ball: attached & launch | Ball renders on paddle, tracks paddle position. Space launches at angled upward direction. Ball moves at 320px/s. Bounces off ceiling and side walls. | Ball launches and bounces off boundaries |
| T08 | Paddle collision & angle | Hit-position-based angle mapping (±65° from vertical). Speed +12px/s per hit (max 520). Ball nudged above paddle. vy minimum enforced. Sweep detection for high speed. | Angle varies with hit position; no tunneling |
| T09 | Brick collision | Per-frame overlap check against all alive bricks. Face detection (min-overlap axis). Reflect on correct axis. Damage/destroy brick. Corner multi-hit. Max 3 per frame. Push ball out. | Bricks break; ball reflects correctly; corners work |
| T10 | Scoring & high score | Points per row. Running score in HUD. High score from localStorage. Extra life at 200 (once, max 5). Score pop animation. | Points correct; high score persists; extra life works |
| T11 | Life system | Ball below y=610 → life lost. 0.8s freeze. Lives decrement. Ball reattaches. Speed resets to level base. 0 lives → GAME_OVER. | Lives track correctly; state transitions clean |
| T12 | Level progression | All destructible bricks cleared → level complete. Flash, "LEVEL N CLEAR!", load next level. Paddle shrinks, speed increases, reinforced/indestructible bricks per spec. | Levels advance; difficulty increases noticeably |
| T13 | Reinforced & indestructible bricks | 2-HP bricks (level 2+): visual damage on first hit, destroyed on second. Indestructible (level 5+): grey, never break, excluded from clear count. | Multi-hit bricks work; indestructibles bounce ball; level clears without them |
| T14 | Particles & visual effects | Brick destruction: 8 particles per brick, correct color, gravity, fade (0.6s). Ball trail: 6 afterimages. Paddle flash: blue 50ms. Screen flash on level clear. | Effects fire on correct events; enhance not distract |
| T15 | Game screens | Title: "BREAKOUT", attract ball, brick color legend, controls. Serve: "READY" + ball on paddle. Pause overlay. Game over: score, new-best, restart. | All screens display and transition cleanly |
| T16 | Audio | Web Audio: paddle pop, wall click, brick tones (pitch by row), damage thud, life-lost buzz, level-clear arpeggio, extra-life chime. Graceful failure. | Sounds play correctly; game works if audio fails |
| T17 | Polish & edge cases | Full acceptance criteria pass. Test: max speed ball, every brick type, rapid multi-brick hits, corner hits, tab-switch recovery, paddle at edges, mouse+keyboard simultaneously, perfect clear bonus. | All criteria met; no bugs under stress |
