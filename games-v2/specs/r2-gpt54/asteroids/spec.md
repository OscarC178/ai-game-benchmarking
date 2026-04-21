Build a classic Asteroids-style arcade game as a single self-contained HTML file using HTML5 Canvas, with all CSS and JavaScript inline and no external libraries, images, fonts, audio files, or network requests.

Assume the developer has never played Asteroids. The game is a free-movement space survival shooter viewed from above. The player pilots a small ship in open space, rotates left/right, applies thrust in the direction it is facing, and fires projectiles to destroy drifting asteroids. The world wraps at the screen edges: objects exiting one side re-enter from the opposite side. Destroying large asteroids splits them into smaller ones. The player survives waves, earns points, and avoids collisions with asteroids and occasional enemy UFOs.

The essential feel is:
- sparse and clean
- vector-arcade style
- inertia-based movement
- precise rotation and thrust
- tension from drifting hazards and momentum management
- readable chaos, not clutter

Canvas and presentation:
- Canvas size: 800×600 pixels.
- Background: solid black.
- Coordinate system: origin at top-left.
- Internal simulation should use the fixed 800×600 space even if the canvas is visually scaled responsively.
- Visual style should be minimalist vector/line art:
  - white ship outlines
  - white bullets
  - light gray / white asteroid outlines
  - simple stars are optional but should stay subtle

Core objective:
- Control the ship in open space.
- Shoot and destroy all asteroids in the current wave.
- Avoid colliding with asteroids, UFOs, and enemy bullets.
- Clearing a wave starts the next wave with more pressure.
- Score increases for destroying threats.
- Lose when all lives are gone.

Ship:
- Shape: triangular vector ship.
- Approximate size: 28 px nose-to-tail, about 18 px wide.
- Spawn position: center of screen, x=400, y=300.
- Initial facing direction: upward or slightly rightward is acceptable, but upward is more iconic.
- Movement is inertial:
  - rotate left/right
  - thrust accelerates in facing direction
  - no immediate stop/brake button unless added as a hidden convenience (not recommended)
- Rotation speed: about 240 degrees/sec.
- Thrust acceleration: about 220 px/s².
- Optional max speed cap: around 320 px/s; acceptable and helpful for playability.
- When not thrusting, the ship continues drifting due to momentum.
- A tiny drag factor is acceptable for playability, but keep it very low; the game should still feel inertial rather than friction-heavy.

Controls:
- ArrowLeft / A = rotate left
- ArrowRight / D = rotate right
- ArrowUp / W = thrust
- Space = fire
- Enter = start from title screen and restart after game over
- P = pause / unpause
- Optional:
  - ArrowDown / S can be unused
  - hyperspace is optional and not required

Screen wrapping:
- The ship, asteroids, bullets, and UFOs should wrap around screen edges.
- If an object goes beyond one boundary, it reappears on the opposite side preserving velocity and direction.
- Wrap cleanly so objects do not vanish permanently.
- For rendering, consider drawing wrapped duplicates near edges when needed so large objects appear continuous.

Ship firing:
- Press Space to fire.
- Bullets travel straight in the direction the ship is facing at fire time.
- Bullet speed: about 420 px/s plus current ship velocity contribution if desired.
- Bullet lifetime: about 1.2 to 1.5 seconds.
- Fire rate should be limited, e.g. around 4 shots/sec max.
- Maximum simultaneous player bullets: around 4 on screen.
- Bullets are small bright points or tiny lines.
- Bullets disappear when lifetime expires or when they hit an asteroid/UFO.

Asteroids:
Use three asteroid sizes:
1. Large
   - Approx radius: 40 px
   - Slowest
   - On destruction splits into 2 medium asteroids
2. Medium
   - Approx radius: 24 px
   - Medium speed
   - On destruction splits into 2 small asteroids
3. Small
   - Approx radius: 14 px
   - Fastest
   - On destruction disappears

Asteroid behavior:
- Drift with constant linear velocity.
- Rotate slowly for visual effect.
- Have irregular polygonal outlines rather than perfect circles.
- Must wrap around screen edges.
- Large asteroid speed should be modest; small asteroids noticeably faster.
- Suggested speed ranges:
  - large: 20–55 px/s
  - medium: 40–85 px/s
  - small: 70–120 px/s
- Initial directions should be randomized.
- Spawn new wave asteroids away from the player spawn zone so the player is not immediately killed.

Wave setup:
- Start wave 1 with 4 large asteroids.
- Each new wave increases the number of large asteroids by 1, or ramps difficulty similarly.
- On wave start:
  - spawn asteroids around the edges or away from center
  - leave the central spawn area relatively safe
- When all asteroids are destroyed, start the next wave after a short transition.

Asteroid splitting:
- When a large asteroid is shot:
  - destroy it
  - spawn 2 medium asteroids at its position
  - inherit a bit of parent velocity plus diverging random velocities
- When a medium asteroid is shot:
  - destroy it
  - spawn 2 small asteroids
- When a small asteroid is shot:
  - destroy it with no children
- Splits should feel energetic but readable.

UFO enemy:
Include an occasional enemy UFO for authentic feel. It is strongly recommended.

UFO behavior:
- Periodically spawn a UFO entering from left or right edge.
- UFO size: about 32×16 px or similar simple saucer silhouette.
- It travels horizontally across the screen with slight vertical drift or course changes.
- It wraps or exits; either is acceptable, but crossing and exiting is simpler and classic-feeling.
- It occasionally fires bullets at the player.
- UFOs should be dangerous but infrequent.
- A simple system is fine:
  - spawn every 20–35 seconds if no UFO exists
  - move at 90–140 px/s
  - shoot every 1.0–2.0 seconds
- Optional two UFO types:
  - large inaccurate UFO
  - small more accurate UFO
  This is nice but not required. A single UFO type is enough.

UFO bullets:
- Travel in straight lines.
- Speed: about 220–280 px/s.
- Lifetime similar to player bullets.
- They can kill the player.
- Simple targeting is acceptable:
  - fire roughly toward player with mild aim error
- Perfect aim is not desirable; it should feel threatening but fair.

Lives:
- Player starts with 3 lives.
- Display remaining lives in HUD.
- On ship collision or being hit by enemy bullet:
  - lose one life
  - explode / hide ship briefly
  - clear immediate local danger if needed
  - respawn ship at center only if spawn area is safe
- If lives reach 0, game over.

Respawn logic:
- After death, do not instantly respawn into an asteroid.
- Wait for a safe respawn window or check a safe radius around the spawn point.
- On respawn, grant short invulnerability, around 2 seconds.
- During invulnerability, the ship can blink.
- If the center is not safe yet, delay respawn until it is.

Collision rules:
Use circle or approximate radial collision for most gameplay; this suits Asteroids better than AABB.

Required collisions:
- player bullet ↔ asteroid
  - destroy bullet
  - split or destroy asteroid
  - add score
- player bullet ↔ UFO
  - destroy bullet
  - destroy UFO
  - add score
- ship ↔ asteroid
  - player dies unless invulnerable
- ship ↔ UFO
  - player dies unless invulnerable
- UFO bullet ↔ ship
  - player dies unless invulnerable
- optional:
  - player bullet ↔ UFO bullet
  - bullets ↔ bullets
  These are not necessary.

Scoring:
Use classic-feeling score values:
- Large asteroid: 20 points
- Medium asteroid: 50 points
- Small asteroid: 100 points
- UFO: 200 points, or more if you differentiate UFO types
- Score starts at 0.
- High score persists in localStorage.
- Display score top-left and high score top-right.

HUD:
At minimum display:
- Score
- High score
- Lives
- Wave
Suggested layout:
- Score: top-left
- Wave: top-center
- High score: top-right
- Lives: bottom-left or near top-left as ship icons or numeric

Game states:
1. Title screen
   - Visible on load
   - Show title “ASTEROIDS”
   - Explain core rules briefly:
     - rotate
     - thrust
     - shoot asteroids
     - avoid collisions
   - Show controls
   - Show “Press Enter to Start”
2. Playing
   - Main gameplay active
3. Paused
   - Freeze all simulation
   - Show “PAUSED”
4. Respawning
   - Player temporarily absent or invulnerable after death
5. Wave transition
   - Brief “WAVE N” or “GET READY” overlay before next wave
6. Game over
   - Show “GAME OVER”, final score, and restart prompt

Ship death / explosion:
- When the ship is destroyed:
  - create a brief visual explosion using a few line fragments or particles
  - stop player control during the death moment
  - deduct one life
- Explosion effect can be simple:
  - several line segments flying outward and fading over 0.5–0.8 seconds

Visual style:
- Favor line-drawn shapes over filled sprites.
- Ship, asteroids, UFO, and bullets should contrast strongly with the black background.
- Optional starfield is fine but subtle.
- Thrust flame can appear behind the ship only while thrusting.
- Invulnerability blinking should be clear but not annoying.

Ship handling details:
- Rotation should feel immediate and smooth.
- Thrust should accelerate in the facing vector.
- Updating:
  - vx += cos(angle) * thrust * dt
  - vy += sin(angle) * thrust * dt
  or the equivalent based on chosen angle convention
- If using upward-facing ship by default, be consistent in angle math and sprite orientation.
- Low drag is acceptable, e.g. multiply velocity by 0.999–0.995 per frame equivalent, but keep it light.
- The player should feel like they are steering momentum, not a car.

Bullet handling details:
- Bullets should not be affected by drag.
- They can inherit ship velocity for a more authentic feel.
- Lifetime expiration is important to avoid endless wrapped bullets.
- Firing cadence should be rate-limited so holding Space does not create absurd spam unless you intentionally allow autofire at a controlled rate.

Wave pacing:
- The game should begin gently enough for a first-time player.
- Difficulty should increase through:
  - more large asteroids per wave
  - lingering small asteroid chaos from splits
  - occasional UFO pressure
- A short pause between waves helps readability.

Audio:
- Optional but recommended.
- Use Web Audio API only.
- Suggested procedural sounds:
  - laser shot
  - asteroid hit / break
  - UFO hum
  - ship explosion
  - wave start stinger
- Audio must be optional and activated only after user input per browser rules.

Implementation guidance:
Use requestAnimationFrame and delta time in seconds.
Clamp large frame deltas to avoid jumps after tab inactivity.
Separate update and render logic.

Recommended state/entities:
- gameState
- ship
- playerBullets[]
- asteroids[]
- ufo or null
- ufoBullets[]
- particles[]
- score / highScore / lives / wave
- timers:
  - fire cooldown
  - respawn timer
  - invulnerability timer
  - wave transition timer
  - UFO spawn timer

Recommended object structure:
- position x,y
- velocity vx,vy
- radius
- angle / rotation
- alive flag
- for asteroids: size, polygon points, spin
- for bullets: lifetime
- for particles: lifetime and fade

Spawning asteroids:
- New large asteroids should not spawn too close to ship spawn point.
- Good rule: require at least 150–200 px distance from center on wave start.
- Spawn positions near edges work well.

Asteroid shape generation:
- Create each asteroid as an irregular polygon:
  - 8–12 points
  - radius perturbed by random factor per point
- Rotate the polygon slowly over time for life.
- This gives classic rough rock silhouettes without external art.

Wrap rendering note:
- Since large objects can straddle screen edges, rendering wrapped duplicates when close to boundaries improves appearance.
- For each wrappable object, consider drawing it at its true position plus offset copies at ±width / ±height combinations if near edges.

Important edge cases:
- Ship must not respawn into guaranteed death.
- Bullets should not pass through asteroids too often; speeds are moderate, so careful frame updates should suffice.
- Splitting asteroids should not instantly collide-kill an invulnerable-less respawn.
- Clearing a wave should not leave stray bullets or UFOs in a confusing state; either clear them or handle transitions cleanly.
- Game over should fully stop action.
- Restart should fully reset all timers, waves, score, lives, entities, and effects.

Title screen should explain the concept clearly because the developer has not played the game:
- You are a ship drifting in space.
- Turn, thrust, and shoot.
- Asteroids split into smaller faster pieces when destroyed.
- Avoid hitting anything.
- Clear every wave.

Acceptance checklist:
- On load, title screen is visible and readable.
- Pressing Enter starts the game.
- Ship can rotate, thrust, and drift with inertia.
- Space fires bullets with a sensible cooldown.
- Ship, bullets, and asteroids wrap around screen edges.
- Large asteroids split into medium, medium into small, small disappear.
- Clearing all asteroids starts the next wave.
- Colliding with an asteroid kills the player.
- Player has 3 lives and game over occurs at 0.
- Respawn is safe and includes brief invulnerability.
- UFO occasionally appears and can shoot at the player.
- Score, high score, lives, and wave are displayed.
- High score persists via localStorage.
- P pauses and unpauses correctly.
- Entire implementation is contained in one self-contained HTML file with inline CSS/JS only and no external dependencies.
