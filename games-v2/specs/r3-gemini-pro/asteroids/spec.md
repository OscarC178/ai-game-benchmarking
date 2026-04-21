# Game Specification: Asteroids

## 1. Core Concept & Gameplay Overview
Asteroids is a multi-directional shooter set in a wrap-around space environment. The player controls a triangular spaceship that can rotate, thrust forward, and fire projectiles. The objective is to survive and score points by destroying drifting asteroids. 

When a large asteroid is shot, it breaks into two medium asteroids. When a medium asteroid is shot, it breaks into two small asteroids. When a small asteroid is shot, it is destroyed. Occasionally, an enemy UFO (Flying Saucer) appears and traverses the screen, firing at the player. If the player collides with an asteroid or a UFO projectile, they lose a life. The playing field is toroidal—objects that move off one edge of the screen reappear on the opposite edge.

## 2. Technical Constraints
- **Format:** A single, self-contained `index.html` file.
- **Assets:** Strict zero external dependency rule. Render everything using Canvas API line drawing (`lineTo`, `stroke`). No external images, CSS, or audio files.
- **Rendering:** HTML5 `<canvas>` using the 2D context.
- **Physics:** Continuous 2D vector physics using `requestAnimationFrame` and delta time (`dt`). Vector math (velocity, acceleration, rotation) is critical.

## 3. Visual Design & Layout
- **Style:** Classic vector arcade aesthetics. Everything is drawn as outlines (wireframes). No fill colors.
- **Canvas Size:** 800px width by 600px height. Centered in the browser with a `#000000` (black) background.
- **Line Color:** Bright White (`#FFFFFF`).
- **Typography:** Standard sans-serif or monospace font, white text.

## 4. Game Entities

### The Player Ship
- **Shape:** An isosceles triangle. Drawn using lines relative to a center point.
- **Dimensions:** Approx 20px long (nose to base) and 14px wide at the base.
- **Position:** Starts dead center `(400, 300)`.
- **Movement (Inertia-based):**
  - **Rotation:** Left/Right keys rotate the ship's heading (angle in radians). Rotation speed: ~5 radians per second.
  - **Thrust:** Up key applies forward acceleration in the direction of the ship's heading.
  - **Velocity:** X and Y velocity persist after thrusting (inertia). Apply a very small amount of friction/drag (e.g., multiply velocity by `0.99` per frame) so the ship doesn't drift infinitely fast, capping maximum speed.
- **Thruster Effect:** When the thrust key is held, randomly draw a small jagged "flame" line extending from the base of the ship opposite the heading.

### Player Projectiles (Lasers)
- **Shape:** A small dot or very short line.
- **Behavior:** Fired from the nose of the ship in the direction of the current heading.
- **Limits:** Max 4-5 projectiles on screen at once.
- **Lifespan:** Projectiles do not travel forever. They expire after traveling a set distance (e.g., crossing roughly 80% of the screen width), ensuring players cannot spam bullets indefinitely.
- **Speed:** Very fast (e.g., 600 pixels per second).

### The Asteroids
- **Shape:** Jagged, irregular polygons. Generate these procedurally using a base radius and randomizing the vertex distances by +/- 20% to create craggy shapes.
- **Sizes (Radii):** 
  - Large: ~40px
  - Medium: ~20px
  - Small: ~10px
- **Movement:** Constant linear velocity. Drift in a random initial direction.
- **Fracturing Logic:**
  - Shooting a Large spawns two Mediums at the same coordinates, but with new, faster random velocities.
  - Shooting a Medium spawns two Smalls exactly the same way (even faster).
  - Shooting a Small destroys it entirely.
- **Screen Wrapping:** If an asteroid's center goes off-screen, it wraps to the other side.

### The UFOs (Saucers)
- **Shape:** A classic saucer shape (a wide hexagon with a smaller dome on top and a line through the middle).
- **Behavior:** Appears occasionally from either the left or right edge and travels horizontally across the screen in a slightly zigzag or wavy pattern.
- **Types:**
  - *Large UFO:* Fires randomly in any direction. Easier to hit.
  - *Small UFO:* Fires specifically aimed shots at the player's current position. Much harder to hit.

## 5. Wrapping Mechanics (The Torus)
Every moving object (Ship, Asteroids, UFOs, Projectiles) must wrap around the screen edges seamlessly.
- If `x < 0`, `x += canvas.width`
- If `x > canvas.width`, `x -= canvas.width`
- If `y < 0`, `y += canvas.height`
- If `y > canvas.height`, `y -= canvas.height`

## 6. Controls
- **ArrowLeft:** Rotate Left.
- **ArrowRight:** Rotate Right.
- **ArrowUp:** Thrust forward.
- **Spacebar:** Fire projectile.
- **Shift** (Optional but authentic): Hyperspace. Instantly teleports the ship to a random position on screen. Has a small chance (e.g., 1 in 6) of instantly destroying the ship upon re-entry.

## 7. Physics & Collisions
- **Collision Detection:** Simple circle-based collision detection (radii overlap) is mathematically sufficient and historically accurate for this game. Calculate distance between the centers of two entities. If `distance < (radiusA + radiusB)`, a collision occurred.
- **Check Pairs:** 
  - Player Projectile vs. Asteroids
  - Player Projectile vs. UFO
  - UFO Projectile vs. Player Ship
  - Asteroid vs. Player Ship
  - UFO vs. Player Ship
- *Note: Asteroids do NOT collide with other asteroids.*

## 8. State Flow, Scoring, and Levels
- **Lives:** Start with 3. Bonus life awarded every 10,000 points.
- **Scoring:**
  - Large Asteroid: 20 pts
  - Medium Asteroid: 50 pts
  - Small Asteroid: 100 pts
  - Large UFO: 200 pts
  - Small UFO: 1000 pts
- **Level Progression:**
  - Level 1 starts with 4 Large Asteroids drifting around the edges (away from the player).
  - When the screen is cleared of all asteroids and UFOs, pause briefly, then begin the next level.
  - Each new level spawns `4 + (Level Number)` Large Asteroids.
- **Death State:**
  - When the player is hit, draw the ship breaking apart into a few lines that drift away.
  - Delay for 2-3 seconds before respawning.
  - **Crucial:** Ensure the player respawns safely in the center. If an asteroid is currently occupying the center, wait until the center is clear before respawning (or grant 1 second of invulnerability).

## 9. Audio (Web Audio API)
Audio is crucial to the feel of Asteroids. Note browser autoplay rules (require interaction first).
- **Fire:** A sharp, descending "pew" (e.g., 800Hz dropping to 200Hz very quickly).
- **Thrust:** A low, rumbling white noise or harsh low-frequency oscillation (~50-100Hz) while the Up arrow is held.
- **Explosions (Asteroids/Ship):** A burst of noise. Lower pitch for large asteroids, higher pitch for small ones.
- **The "Beat":** A persistent, alternating two-note heartbeat (e.g., a low sine wave at 100Hz, then 105Hz) that plays in the background continuously. The tempo of the heartbeat accelerates as fewer asteroids remain on screen.
- **UFO Siren:** A continuous high-low wailing tone while the saucer is on screen.
