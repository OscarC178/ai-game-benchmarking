# Game Spec: Asteroids

## 1. Overview

Asteroids (Atari, 1979 — the first game to use vector graphics, the machine that dethroned Space Invaders). You are a small triangular ship adrift in space, surrounded by tumbling rocks. You can rotate, thrust forward, and shoot. The asteroids drift across the screen in random directions. Shoot a large asteroid and it splits into two medium ones. Shoot a medium and it splits into two smalls. Shoot a small and it's destroyed. Clear all asteroids to advance to the next wave, which adds more. Periodically, an alien UFO appears and shoots at you.

The defining mechanic is **Newtonian inertia**. The ship doesn't stop when you release thrust. It keeps drifting in whatever direction it was moving. Thrust doesn't set your velocity — it adds to it. You are always managing momentum: thrusting to dodge, counter-thrusting to brake, overshooting and correcting. The ship is simultaneously your weapon and your greatest danger. Most deaths in Asteroids come from drifting into something, not from failing to shoot it.

The visual style is **vector line art** — everything is drawn as connected lines on a black void. No fills, no sprites, no textures. Bright lines against black. This is not optional aesthetics; it IS Asteroids.

## 2. Canvas & Layout

- **Canvas:** 800×600px
- **Background:** #000000 (pure black, always)
- **HUD:** Score at top-left, high score at top-center, lives at top-left (below score as ship icons)
- **Play area:** The entire canvas. There are no walls, no borders. Objects that exit one edge reappear on the opposite edge (screen wrapping). The play area is a torus — everything wraps.
- **Frame rate:** 60 FPS via `requestAnimationFrame` with delta-time
- **Rendering style:** All game objects are drawn as stroked line paths, not filled shapes. Stroke color is #FFFFFF unless otherwise specified. Line width is 1.5px.

## 3. Core Physics

Every moving object in Asteroids (ship, bullets, asteroids, UFOs) has a position (x, y) and a velocity (vx, vy). Each frame:

```
x += vx × dt
y += vy × dt
```

Then apply screen wrapping: if x < 0, x += 800. If x > 800, x -= 800. Same for y with 600. This applies to all objects without exception. An asteroid drifting off the right side reappears on the left. A bullet exiting the top enters from the bottom.

**There is no friction.** Objects in motion stay in motion at constant velocity until acted upon. The ship can thrust to add velocity but there is no air resistance, no drag, no automatic deceleration. This is the entire feel of the game.

**Cap the ship's speed** at 400px/s (magnitude of velocity vector). When thrusting would exceed this, clamp the velocity vector to 400px/s magnitude while preserving direction. Without a cap, the ship becomes uncontrollable.

## 4. Game Objects

### Ship

- **Shape:** An isoceles triangle, point facing forward. Vertices relative to center, at rotation 0 (pointing up):
  ```
  nose:       ( 0, -18)
  left wing:  (-12, +12)
  right wing: (+12, +12)
  ```
  Total: roughly 24px wide × 30px tall. Draw as a closed path with 1.5px white stroke, no fill.

- **Thrust visual:** When the player holds thrust, draw a flickering flame behind the ship — a smaller triangle or chevron behind the base:
  ```
  flame left:   (-6, +14)
  flame tip:    ( 0, +22 + random(0,6))  // the random creates flicker
  flame right:  (+6, +14)
  ```
  Color: alternate between #FF8C00 (orange) and #FFD700 (gold) every 3 frames. Only render while thrust key is held.

- **Starting position:** Center of screen (400, 300), zero velocity, facing up (rotation angle = -π/2 or 270°).

- **Rotation speed:** 270°/s (4.712 rad/s). Rotation is continuous while the key is held.

- **Thrust acceleration:** 200px/s². Applied in the direction the ship is facing:
  ```
  vx += cos(angle) × 200 × dt
  vy += sin(angle) × 200 × dt
  ```
  (Where angle 0 = right, π/2 = down, etc. Adjust based on your coordinate convention.)

- **No brakes.** There is no dedicated reverse or brake control. To slow down, the player must rotate to face the opposite direction and thrust. This is the fundamental skill of Asteroids.

- **Collision hitbox:** A circle centered on the ship, radius 12px. Don't use the triangle for collision — circle is simpler, fairer, and standard.

- **Invulnerability on spawn:** 3 seconds after respawning (after death). During invulnerability, the ship blinks at 6Hz (toggle visibility every ~83ms). The ship cannot be hit but CAN still shoot. Invulnerability ends early if the player thrusts or shoots (this is authentic and prevents players from camping in safety).

### Bullets (Player)

- **Shape:** Small circle, 2px radius, filled #FFFFFF (this is the one exception to the "no fill" rule — bullets are dots).
- **Speed:** 500px/s in the direction the ship is facing at the moment of firing. Bullets have their own velocity; the ship's current velocity is NOT added.
- **Lifetime:** 0.9 seconds. After that, the bullet disappears. This limits the range — the player can't snipe from across the screen.
- **Maximum active:** 4 bullets on screen at once. If 4 are already active, further shots are suppressed. This paces the shooting and forces aiming.
- **Collision:** Circle with radius 2px. On hitting an asteroid or UFO, both the bullet and target are affected (asteroid splits/destroys, UFO destroys, bullet removed).
- **Screen wrapping:** Yes. Bullets wrap just like everything else.
- **Fire rate:** Maximum 1 bullet per 120ms (≈8 shots/second). Track last-fire time and suppress shots within the cooldown. Firing is edge-triggered on key press, not continuous on hold.

### Asteroids

The primary obstacle. They are irregular polygonal shapes that rotate slowly as they drift.

**Three sizes:**

| Size | Radius | Speed range | Points |
|------|--------|-------------|--------|
| Large | 40px | 30–80px/s | 20 |
| Medium | 20px | 50–120px/s | 50 |
| Small | 10px | 80–160px/s | 100 |

Note: smaller = faster = more points. This is intentional — small asteroids are harder to hit and more dangerous.

**Shape generation:** Each asteroid is a rough circle with randomized vertices. Generate each asteroid shape once on creation:

1. Decide vertex count: 9–14 (random).
2. Space vertices evenly around a circle of the asteroid's radius.
3. For each vertex, vary the radius by ±30% randomly: `r = baseRadius × (0.7 + Math.random() × 0.6)`.
4. Store the vertex list. This is the asteroid's unique shape for its lifetime.
5. Draw as a closed path, stroked #FFFFFF, no fill.

This produces the iconic lumpy, irregular asteroid shapes. Every asteroid looks slightly different.

**Rotation:** Each asteroid has a rotation speed (random, ±1.5 rad/s). The shape rotates visually each frame: `angle += rotationSpeed × dt`. This is cosmetic — the collision hitbox is a circle centered at the asteroid's position with the asteroid's radius.

**Splitting behavior:**
- Shot large asteroid → removed, 2 medium asteroids spawn at its position
- Shot medium asteroid → removed, 2 small asteroids spawn at its position
- Shot small asteroid → removed, nothing spawns (fully destroyed)

Spawned children inherit a random velocity within their size's speed range, directed randomly (but generally away from each other — offset each child's direction by ±30° to ±90° from the parent's direction of travel, or use random directions if simpler). Children also get new random shapes and rotation speeds.

**Starting asteroids per wave:**

| Wave | Large asteroids |
|------|----------------|
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |
| 4 | 7 |
| 5+ | 8 (cap) |

Asteroids spawn at the screen edges with random velocities directed generally inward (not aimed at the player, but not directed off-screen either). Ensure no asteroid spawns within 150px of the player's position — the player needs a safe zone at the start of each wave.

### UFO (Alien Saucer)

Two types. They appear periodically to pressure the player and prevent passive play (sitting still and waiting).

**Large UFO:**
- **Shape:** A classic flying saucer — draw it as: a horizontal ellipse-ish shape using lines. Specifically, two horizontal lines (top and bottom of the "disc"), connected by angled lines on each side, with a smaller dome on top. Roughly 30px wide × 15px tall. Stroke #FFFFFF 1.5px.
- **Speed:** 120px/s, horizontal. Enters from a random side (left or right) at a random y, crosses the screen. Makes small random vertical adjustments every 1–2 seconds (±30px/s vertical jolt) to bob unpredictably.
- **Shooting:** Fires bullets every 1.5–2.5 seconds (random interval). Bullets travel in a **random** direction at 250px/s. The large UFO shoots inaccurately.
- **Points:** 200.
- **Screen wrapping:** Yes, horizontally. If it exits the other side, it's gone (or it can wrap once — either behavior is fine).

**Small UFO:**
- **Shape:** Same design but scaled to 60% (roughly 18px wide × 9px).
- **Speed:** 150px/s. Same movement pattern but with more frequent direction changes.
- **Shooting:** Fires every 1.0–1.5 seconds. Bullets are **aimed at the player** — the bullet velocity vector points from the UFO toward the player's current position, at 300px/s. The small UFO is a sniper and is genuinely dangerous.
- **Points:** 1000.

**Which UFO appears:**
- Score < 10,000: always the large UFO.
- Score ≥ 10,000: always the small UFO.
- Only one UFO on screen at a time.

**Spawn timing:**
- First UFO appears 15–20 seconds into the wave.
- After a UFO is destroyed or exits, the next one appears 15–25 seconds later.
- UFOs do NOT appear during the brief wave-transition pause.

**UFO bullets:**
- Shape: same as player bullets (2px circle).
- Speed: 250px/s (large UFO) or 300px/s (small UFO).
- Lifetime: 1.2 seconds.
- Maximum: 2 active UFO bullets at a time.
- UFO bullets can destroy asteroids (this is authentic and creates interesting chaos — a UFO bullet missing you might hit an asteroid and split it into your path).
- UFO bullets screen-wrap.

**Collision:**
- UFOs can be destroyed by player bullets (points awarded).
- UFOs can be destroyed by asteroid collision (no points — the asteroid did it, not you).
- UFO bullets kill the player.
- The player's ship colliding with a UFO kills the player (and destroys the UFO, no points).

### Debris Particles (Visual Only)

When anything is destroyed (asteroid, UFO, or player ship), spawn a burst of line fragments:

- **Asteroid explosion:** 6–10 small line segments (each 4–8px long), random directions, speed 40–120px/s, fade from 1.0 to 0.0 opacity over 0.8 seconds. Lines are #FFFFFF.
- **UFO explosion:** 8–12 line segments, same behavior, mixed sizes (4–12px).
- **Ship explosion:** The ship's triangle breaks into 3–4 line segments that drift apart (as if the ship physically broke into shards). Each shard is a line of roughly 12–15px, drifting outward from the center at 30–80px/s. Fade over 1.5 seconds. This is the death animation.
- Debris does NOT wrap (it drifts off-screen and is removed). Debris has no collision — it's purely visual.

## 5. Controls

| Input | Action |
|-------|--------|
| Arrow Left / A | Rotate counter-clockwise |
| Arrow Right / D | Rotate clockwise |
| Arrow Up / W | Thrust (accelerate forward) |
| Space | Shoot |
| Shift / Arrow Down | Hyperspace (emergency teleport) |
| Enter | Start / Restart |
| P or Escape | Pause / Unpause |

**Rotation and thrust** are continuous — they apply every frame while the key is held. Track via keydown/keyup state map.

**Shoot** is edge-triggered — one shot per press. No auto-fire on hold. Cooldown of 120ms between shots.

**Hyperspace:** An emergency escape. When pressed:
1. Ship instantly vanishes from its current position.
2. Reappears at a random position on the screen after 500ms.
3. There is a **20% chance** the ship explodes on reentry (instant death). This risk is what makes hyperspace a desperation move, not a strategy.
4. On successful reentry, the ship has zero velocity (momentum is killed) and a brief 1-second invulnerability (same blinking as respawn).
5. Hyperspace is edge-triggered and has a 3-second cooldown.

## 6. Screen Wrapping — Critical Details

Everything wraps: ship, bullets, asteroids, UFOs, UFO bullets.

**How to implement correctly:** When an object's position crosses a boundary, add or subtract the screen dimension:

```
if (x < 0) x += 800;
if (x > 800) x -= 800;
if (y < 0) y += 600;
if (y > 600) y -= 600;
```

**Rendering wrapping objects:** An asteroid near the right edge (e.g., x = 790, radius 40) extends past the edge visually. The player needs to see it partially appearing on the left side too. For every object within one radius of an edge, **render it a second time** at the wrapped position. For a large asteroid at x = 790:
- Render at (790, y) — the main position.
- Also render at (790 - 800, y) = (-10, y) — the wrapped ghost.

This means objects near corners might need to be rendered up to 4 times (main + 3 ghosts). The alternative is to only render at the primary position and accept visual popping at edges, but the double-rendering feels significantly better.

**Collision with wrapping:** When checking distance between two objects, use the minimum toroidal distance:
```
dx = abs(a.x - b.x)
if (dx > 400) dx = 800 - dx    // closer via wrap
dy = abs(a.y - b.y)
if (dy > 300) dy = 600 - dy
distance = sqrt(dx² + dy²)
```

All collision checks must use this toroidal distance. Otherwise, two objects on opposite edges won't collide even though they visually overlap.

## 7. Collision Detection

All collisions are **circle vs circle** (distance between centers < sum of radii).

| Object A | Object B | Result |
|----------|----------|--------|
| Player bullet | Large asteroid | Asteroid splits into 2 mediums + 20pts |
| Player bullet | Medium asteroid | Asteroid splits into 2 smalls + 50pts |
| Player bullet | Small asteroid | Asteroid destroyed + 100pts |
| Player bullet | Large UFO | UFO destroyed + 200pts |
| Player bullet | Small UFO | UFO destroyed + 1000pts |
| Ship | Any asteroid | Ship destroyed (lose life) |
| Ship | UFO | Both destroyed (lose life, no points) |
| Ship | UFO bullet | Ship destroyed (lose life) |
| UFO bullet | Any asteroid | Asteroid splits/destroyed (no points) |
| UFO | Any asteroid | UFO destroyed (no points) |

**Collision radii:**
| Object | Radius |
|--------|--------|
| Ship | 12px |
| Player bullet | 2px |
| Large asteroid | 40px |
| Medium asteroid | 20px |
| Small asteroid | 10px |
| Large UFO | 15px |
| Small UFO | 9px |
| UFO bullet | 2px |

Process all collisions each frame. Use the toroidal distance check from section 6.

## 8. Scoring

| Target | Points |
|--------|--------|
| Large asteroid | 20 |
| Medium asteroid | 50 |
| Small asteroid | 100 |
| Large UFO | 200 |
| Small UFO | 1000 |

**Extra life:** Every 10,000 points. Unlike most games in this spec, this is **repeating** — the player earns a life at 10k, 20k, 30k, etc. Asteroids is brutal enough to justify ongoing life rewards.

**High score:** `localStorage` key `"asteroids_best"`. Loaded on init, updated when exceeded.

## 9. Lives and Respawning

**Starting lives:** 3.

**On death:**
1. Ship explodes (shard debris animation — 1.5 seconds).
2. If lives remain: after the debris fades, the ship respawns at center (400, 300) with zero velocity, pointing up.
3. **Safe respawn:** The ship only respawns when the center area is clear — no asteroids within 120px of center. If the center is dangerous, wait until it clears. Check every frame. If it stays dangerous for more than 5 seconds, respawn anyway with extended invulnerability (5 seconds instead of 3). The player should never spawn into immediate death.
4. 3-second invulnerability on respawn (blinking). Ends early if the player thrusts or shoots.
5. If 0 lives remain: → GAME_OVER.

**Lives display:** Small ship icons at the top-left, below the score. One icon per remaining life (not counting the active life). Each icon is a miniature (~60% scale) of the ship triangle, stroked #FFFFFF.

## 10. Wave Progression

A "wave" begins with a set of large asteroids spawning at screen edges. The wave ends when all asteroids (large, medium, small) are destroyed. UFOs are independent of the wave count — killing a UFO doesn't progress the wave.

**Wave transition:**
1. Last asteroid of the wave is destroyed.
2. 2-second pause. Screen is empty except for the player (and possibly a UFO — if a UFO is alive, it stays until destroyed or exits).
3. New wave spawns. Large asteroid count increases per the table in section 4 (4, 5, 6, 7, 8 cap).
4. Player retains position and velocity across waves. They are NOT reset to center.

**Asteroid speed scaling:** Each wave beyond wave 3, increase the speed ranges by 10% (multiplicative). By wave 6, large asteroids move at roughly 40–105px/s instead of 30–80px/s. This compounds with the increasing count to create escalating pressure. Cap the multiplier at 2.0× (wave 10+).

## 11. Game States

```
TITLE → PLAYING → (DEATH → RESPAWN_WAIT → PLAYING) or GAME_OVER → TITLE
            ↕
         PAUSED
```

### TITLE

- Black background
- **"ASTEROIDS"** centered at y≈180, 48px bold monospace, #FFFFFF. Draw each letter with slight position jitter (±1px random offset per letter, changing every 500ms) to evoke the vector display CRT wobble.
- Below: a handful of asteroids (4–5, mixed sizes) drifting across the screen, wrapping, slowly rotating. Purely cosmetic. No collisions, no splitting.
- The player ship sits centered at y≈300, slowly rotating in place (demonstrating what it looks like).
- **Point values display** at y≈360:
  ```
  Large asteroid shape .......... 20
  Medium asteroid shape ......... 50
  Small asteroid shape .......... 100
  Large UFO shape .............. 200
  Small UFO shape ............. 1000
  ```
  Draw each object at small scale next to its point value. This teaches scoring before playing.
- **"Press Enter to Start"** at y≈500, 18px, #888888, pulsing opacity
- **"Best: {N}"** at y≈540, 14px, #555555
- Enter → PLAYING

### PLAYING

- All game logic active: physics, collisions, wrapping, UFO spawning, wave progression.
- P or Escape → PAUSED.

### PAUSED

- All movement and timers freeze.
- Overlay: #000000 at 60% opacity (or simply freeze the frame and overlay text — since the background is already black, a semi-transparent overlay doesn't change much. Just render "PAUSED" over the frozen scene.)
- "PAUSED" centered, 36px, #FFFFFF.
- "P to resume" 14px, #888888.
- P or Escape → PLAYING.

### DEATH

- Ship debris animation (1.5s). Asteroids and UFOs keep moving (they don't pause for your death — this is authentic and can lead to chain events where asteroids split from UFO bullets during your death, changing the battlefield).
- Decrement lives.
- If lives > 0 → RESPAWN_WAIT.
- If lives = 0 → GAME_OVER.

### RESPAWN_WAIT

- Wait for center area to be clear (120px radius around screen center free of asteroids).
- When clear: spawn ship at center, zero velocity, facing up, 3s invulnerability.
- → PLAYING.

### GAME_OVER

- Asteroids continue drifting (the world goes on without you). This is subtle but atmospheric.
- "GAME OVER" centered at y≈250, 40px, #FFFFFF.
- "Score: {N}" at y≈300, 24px, #FFFFFF.
- If new high score: "HIGH SCORE!" at y≈335, 18px, #FFFFFF, pulsing.
- "Wave reached: {N}" at y≈365, 16px, #888888.
- "Enter to play again" at y≈420, 16px, #666666, blinking.
- Enter → TITLE.

## 12. Audio

Web Audio API. `AudioContext` on first user interaction.

Asteroids has one of the most iconic soundscapes in gaming — a deep two-note heartbeat that accelerates as asteroids are destroyed.

### The Heartbeat

Two alternating bass notes, cycling continuously during gameplay:

```
Note A: 80Hz sine wave, 120ms duration, gain 0.3
Note B: 60Hz sine wave, 120ms duration, gain 0.3
```

Pattern: A ... B ... A ... B ... (alternating, with silence between)

The interval between notes depends on how many asteroids remain:

```
interval = 200 + (asteroidCount / maxAsteroidsInWave) × 600   // ms
```

So with a full wave of 12 asteroids (4 large = potentially 28 total if all split): interval ≈ 800ms (slow, ominous). As asteroids are destroyed and count drops: interval decreases. With 2 asteroids left: interval ≈ 250ms (frantic heartbeat). Minimum interval: 180ms.

This is the tension engine of the game. The player hears the pace increasing as they progress through the wave. It's also a status indicator — without looking at the screen, you know roughly how many asteroids are left by the beat speed.

### Other Sounds

| Event | Sound | Implementation |
|-------|-------|----------------|
| Thrust | Continuous low rumble | 60Hz sawtooth, gain 0.12, looping while thrust held. Apply slight gain oscillation (±0.03 at 5Hz) for texture. Stop on thrust release (fade out over 50ms to prevent click). |
| Fire | Sharp snap | 900Hz square → 300Hz over 50ms, gain 0.15 |
| Asteroid large destroy | Deep crunch | 120Hz square, 150ms, gain 0.25 |
| Asteroid medium destroy | Mid crunch | 180Hz square, 120ms, gain 0.22 |
| Asteroid small destroy | High crunch | 260Hz square, 80ms, gain 0.2 |
| UFO present (large) | Low warble | 200Hz sine, amplitude modulated at 4Hz, continuous while on screen, gain 0.15 |
| UFO present (small) | High warble | 400Hz sine, amplitude modulated at 7Hz, continuous while on screen, gain 0.15 |
| UFO destroyed | Descending burst | 600Hz → 100Hz sawtooth over 200ms, gain 0.2 |
| Player death | Explosion | White noise burst, 300ms, gain 0.3, with 100Hz sine undertone |
| Extra life | Chime | 880Hz→1100Hz sine, 80ms each, gain 0.18 |
| Hyperspace out | Whoosh down | 800Hz→200Hz sine, 200ms, gain 0.15 |
| Hyperspace in | Whoosh up | 200Hz→800Hz sine, 200ms, gain 0.15 |

All audio is optional. Graceful failure everywhere.

## 13. HUD

Minimal — Asteroids has very little UI. The vast majority of the screen is pure black gameplay space.

| Element | Position | Style |
|---------|----------|-------|
| Score | Top-left, x=20, y=28 | 22px monospace, #FFFFFF, stroked (not filled — keep the vector aesthetic if possible, or use fillText if stroked text looks bad) |
| High score | Top-center, x=400 (centered), y=28 | 18px monospace, #888888 |
| Lives | Top-left, x=20, y=56 | Miniature ship icons (12px tall triangles), 18px apart, #FFFFFF stroke |

No level/wave indicator (the original didn't have one). The player infers progress from the asteroid count and the heartbeat speed. If you want to add a small "Wave {N}" in the bottom-right at #333333, that's acceptable — just keep it unobtrusive.

## 14. Visual Style Notes

1. **Everything is stroked lines.** ctx.strokeStyle = '#FFFFFF'. ctx.lineWidth = 1.5. ctx.stroke(). Not ctx.fill(). The only exception is bullets (small filled circles) and the screen background. This line-art look is the soul of Asteroids.

2. **No anti-aliasing tricks needed.** Canvas anti-aliases by default, which actually makes the lines look clean. Don't disable it.

3. **Screen flicker (optional).** To evoke the CRT vector display, apply a very subtle full-screen effect: every frame, fill the canvas with #000000 at 92% opacity (instead of 100%). This creates a faint phosphor-trail afterglow — lines take a few frames to fully fade. Moving objects leave a barely-perceptible trail. This is subtle but immediately evokes the original hardware. If it causes performance issues or looks wrong, just clear to solid black.

4. **Rotation rendering.** Every object (ship, asteroids, UFOs) is defined as a set of vertices relative to center. To render at position (x, y) with rotation angle θ, transform each vertex:
   ```
   screenX = x + vertex.x × cos(θ) - vertex.y × sin(θ)
   screenY = y + vertex.x × sin(θ) + vertex.y × cos(θ)
   ```
   Or use `ctx.save()`, `ctx.translate(x, y)`, `ctx.rotate(θ)`, draw vertices at their local coordinates, `ctx.restore()`.

5. **Object color variation (optional):** The original was monochrome white. For a tasteful modern touch, you could tint asteroids very slightly grey (#CCCCCC), UFOs slightly (#FF4444 or keep white), and keep the player ship and bullets pure white. Or keep everything white. White-on-black is the canonical look.

## 15. Implementation Notes

1. **Delta-time all physics.** Every velocity integration, rotation update, and timer uses `dt`. Cap dt at 50ms. After tab-switch, clamp to one frame to prevent everything teleporting.

2. **Entity list pattern.** Maintain arrays: `asteroids[]`, `playerBullets[]`, `ufoBullets[]`, `debris[]`, one `ufo` object (or null), one `ship` object. Each frame: update everything, then check collisions, then remove dead entities, then render. Don't modify arrays while iterating — collect indices to remove, then splice in reverse order (or filter to a new array).

3. **Asteroid spawn at screen edges:** Pick a random edge (top/bottom/left/right). Place the asteroid at a random position along that edge. Give it a velocity directed generally inward (random angle within ±45° of the inward direction toward screen center, with speed in the size's range). Check distance to player — if < 150px, re-roll position.

4. **UFO pathing.** The large UFO enters from one side, moves horizontally. Every 1–2 seconds, it makes a small random vertical velocity change (vy = random(-30, 30)). The small UFO moves similarly but changes direction more frequently and can reverse horizontal direction once. Both exit the screen if they reach the opposite horizontal edge (or wrap once — pick one approach). They do wrap vertically if their vertical drift takes them off the top/bottom.

5. **UFO bullet aiming (small UFO):** Calculate the angle from UFO position to player position:
   ```
   angle = atan2(player.y - ufo.y, player.x - ufo.x)
   ```
   But use the **toroidal shortest path** — if the player is closer via wrapping, aim in the wrapped direction. Add a small random spread of ±5° for the small UFO (it's accurate but not perfect). The large UFO fires in a completely random direction.

6. **Hyperspace implementation:** On keypress, set ship state to "hyperspace_out" (invisible, no collision, 500ms timer). When timer expires: 20% chance → ship explodes (death). 80% chance → pick random position (ensure not within 80px of any asteroid or UFO), appear there with zero velocity, 1-second invulnerability.

7. **Invulnerability cancellation:** Track whether the player has pressed any action key (thrust, fire) since respawn. On first action input, set invulnerability timer to min(remaining, 500ms) — give a brief 500ms grace after the first action, then vulnerability begins. This is more forgiving than instant cancellation.

8. **Performance:** With up to 8 large asteroids that split into 16 mediums that split into 32 smalls, plus a UFO, bullets, and debris, the total entity count can reach ~60–80 objects. This is trivially fast for canvas. No spatial partitioning needed. Brute-force collision checking (O(n²) with n≈50) runs in microseconds.

9. **Wrap-aware rendering:** For each object, check if it's within its radius of any screen edge. If so, also render it at the wrapped position. Use a helper:
   ```
   function renderWrapped(obj, renderFn) {
       renderFn(obj.x, obj.y)
       if (obj.x - obj.radius < 0) renderFn(obj.x + 800, obj.y)
       if (obj.x + obj.radius > 800) renderFn(obj.x - 800, obj.y)
       if (obj.y - obj.radius < 0) renderFn(obj.x, obj.y + 600)
       if (obj.y + obj.radius > 600) renderFn(obj.x, obj.y - 600)
       // corners (rare but needed for large asteroids):
       // check x AND y combos too if feeling thorough
   }
   ```

10. **Wave clear detection:** After every asteroid destruction check, if `asteroids.length === 0`, start the 2-second wave transition timer. During this timer, no new asteroids exist (obviously), but UFOs can still be active.

## 16. Acceptance Criteria

- [ ] Loads with no console errors
- [ ] Title screen with asteroid showcase, point values, and start prompt
- [ ] Ship rotates, thrusts (with flame), and shoots
- [ ] Ship movement has Newtonian inertia — momentum persists without thrust
- [ ] Ship speed is capped at 400px/s
- [ ] Bullets have limited lifetime (disappear after 0.9s) and max 4 active
- [ ] Everything screen-wraps (ship, bullets, asteroids, UFOs)
- [ ] Objects render at wrapped positions when near edges (no visual popping)
- [ ] Large asteroids split into 2 mediums; mediums into 2 smalls; smalls are destroyed
- [ ] Correct points per asteroid size (20, 50, 100)
- [ ] Asteroids have randomized irregular polygon shapes and rotate
- [ ] UFOs appear periodically; large (random shots) at low scores, small (aimed shots) at high scores
- [ ] UFO bullets can destroy asteroids
- [ ] Hyperspace works with 20% death risk and cooldown
- [ ] Ship respawns at center when area is clear, with invulnerability
- [ ] Wave progression: more asteroids each wave, slightly faster
- [ ] Heartbeat audio accelerates as asteroid count decreases
- [ ] Score, high score (persisted), and lives display correctly
- [ ] Extra life every 10,000 points
- [ ] Pause freezes everything
- [ ] Game over screen with score and restart
- [ ] All rendering is vector/line-art style (stroked paths, not filled shapes)

## 17. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML scaffold | DOCTYPE, 800×600 canvas, #000000 background, centered, inline CSS, `<script>` | Black canvas, no errors |
| T02 | Game loop & input | `requestAnimationFrame` with delta-time (capped 50ms). Key state map for arrows, WASD, Space, Shift, Enter, P/Escape. Edge detection for fire/hyperspace. | Smooth loop; keys tracked; edge triggers work |
| T03 | State machine | TITLE, PLAYING (with DEATH and RESPAWN_WAIT sub-states), PAUSED, GAME_OVER. Transitions per spec. | All states reachable; transitions correct |
| T04 | Ship rendering & rotation | Triangle ship with stroked line art. Rotates 270°/s via left/right keys. Renders at position and angle. | Ship visible; rotates smoothly; vector-art look |
| T05 | Ship thrust & physics | Up key applies 200px/s² acceleration in facing direction. Momentum persists without thrust. Speed capped at 400px/s. Flame visual while thrusting. | Ship accelerates, drifts, feels Newtonian; flame flickers |
| T06 | Screen wrapping | All objects wrap position across edges. Render wrapped copies when near edges. Collision uses toroidal distance. | Ship wraps; no visual pop; collision across edges works |
| T07 | Bullets | Space fires bullet at 500px/s in ship's facing direction. Max 4 active, 120ms cooldown, 0.9s lifetime. Bullets wrap. Edge-triggered. | Bullets fire, travel, expire; max 4 enforced; wrapping works |
| T08 | Asteroids: rendering | Random irregular polygon shapes (9–14 vertices, ±30% radius variation). Three sizes (40/20/10 radius). Slow rotation. Stroked line art. | Asteroids look lumpy and unique; rotate visually |
| T09 | Asteroids: movement & spawning | Spawn at screen edges with inward velocities, not within 150px of player. Drift at size-appropriate speeds. Wrap. | Asteroids drift across screen; wrap; avoid player on spawn |
| T10 | Asteroid splitting | Bullet hits large → 2 mediums. Medium → 2 smalls. Small → destroyed. Children spawn at parent position with new random shapes/velocities. Correct points. | Splitting works; visual chain reaction satisfying; score updates |
| T11 | Ship collision & death | Ship-asteroid and ship-UFO-bullet collision (circle vs circle, toroidal). Death triggers shard debris animation (1.5s). Lives decrement. | Ship dies on contact; debris looks good; life decremented |
| T12 | Respawn | After death animation, wait for area clear (120px from center). Respawn at center, zero velocity, 3s invulnerability (blinking). Ends early on action. | Respawn waits for safety; invulnerability visible; cancels on action |
| T13 | Wave progression | All asteroids destroyed → 2s pause → new wave with +1 large asteroid (cap 8). Speed ranges increase 10%/wave (cap 2×). Player keeps position. | Waves advance; more and faster asteroids each wave |
| T14 | UFO (large) | Appears after 15–20s. Crosses horizontally at 120px/s with vertical bobbing. Fires random-direction bullets (max 2) every 1.5–2.5s. 200 pts. Score < 10k only. | Large UFO appears, moves, shoots randomly, can be destroyed |
| T15 | UFO (small) | Appears when score ≥ 10k. 150px/s, aimed bullets at player (toroidal aim, ±5° spread). 1000 pts. More frequent direction changes. | Small UFO appears at high score; bullets track player; very dangerous |
| T16 | Hyperspace | Shift/Down: ship vanishes, 500ms later reappears at random safe position. 20% death chance. Zero velocity on reentry. 1s invulnerability. 3s cooldown. | Hyperspace teleports; sometimes kills; safe positions chosen |
| T17 | Scoring & lives HUD | Score top-left, high score top-center, lives as ship icons. Extra life every 10k. High score in localStorage. | HUD renders; score correct; extra lives awarded; best persists |
| T18 | Audio: heartbeat | Two alternating bass notes (80Hz/60Hz). Interval decreases as asteroid count drops. Min 180ms. | Heartbeat plays; audibly accelerates as asteroids are killed |
| T19 | Audio: effects | Thrust rumble, fire snap, asteroid crunch (3 pitches by size), UFO warble (2 types), UFO destroy, player death, hyperspace whoosh in/out, extra life chime. | All sounds trigger correctly; thrust loops/stops cleanly |
| T20 | Title & game over screens | Title: "ASTEROIDS" + drifting asteroids + rotating ship + point legend + start prompt. Game over: score, high score, wave, restart. | Screens display; attract mode has drifting asteroids |
| T21 | Debris & visual polish | Explosion line fragments on all destructions. Ship shard animation on death. Optional CRT phosphor fade. Ensure all rendering is line-art. | Explosions look good; consistent vector aesthetic throughout |
| T22 | Full testing | All acceptance criteria pass. Edge cases: wrapping collisions, UFO bullet hitting asteroid near edge, hyperspace into asteroid cluster, max asteroid count (all mediums split into smalls = 32 on screen), rapid fire at cooldown limit, tab-switch recovery. | All criteria met; stable at high entity counts |
