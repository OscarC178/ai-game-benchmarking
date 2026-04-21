Build a classic Galaga-style fixed-screen space shooter as a single self-contained HTML file using HTML5 Canvas, with all CSS and JavaScript inline and no external libraries, images, fonts, audio files, or network requests.

Assume the developer has never seen Galaga. The game is a vertically oriented fixed shooter. The player controls a small ship at the bottom of the screen and fires upward at enemy insects/aliens that begin arranged in a formation near the top. Unlike Space Invaders, the enemies do not only march as a block. In Galaga, enemies start in a neat formation, but individual enemies regularly break formation, dive in looping attack paths, fire at the player, and then either return to formation or continue threatening the player. The game’s identity comes from:
- a clearly staged enemy formation at the top
- dramatic individual dive attacks
- a strong sense of rhythm and wave choreography
- a player ship with tight left/right control
- enemies that feel more alive and aggressive than static invaders

The game should feel crisp, readable, slightly flashy, and more animated than Space Invaders, but still simple and arcade-clean.

Core objective:
- Control the player ship at the bottom of the screen.
- Shoot enemy aliens while dodging their shots and dive attacks.
- Destroy all enemies in the wave to advance to the next stage.
- Survive as long as possible with a small number of lives.
- Optionally implement the iconic capture/rescue mechanic; this is strongly recommended because it is central to Galaga’s identity.

Canvas and rendering:
- Canvas size: 800×600 pixels.
- Background: black.
- Coordinate system: origin top-left.
- Use fixed internal coordinates even if visually scaled responsively.
- Include a subtle scrolling or drifting starfield background if possible; it helps create the Galaga feel.
- All art may be simple vector shapes or small pixel-art-like drawings made directly in code. No external assets.

Player ship:
- Position: bottom center area, starting at x=400, y=540.
- Approximate size: 30–34 px wide, about 24 px tall.
- Movement: horizontal only.
- Movement speed: about 320 px/s.
- Clamp ship fully inside screen width.
- No inertia; movement should be immediate and precise.
- The ship should feel very responsive because survival depends on fine dodging.

Player controls:
- ArrowLeft / A = move left
- ArrowRight / D = move right
- Space = fire
- Enter = start from title screen and restart after game over
- P = pause / unpause

Player bullets:
- Travel straight upward.
- Speed: about 500 px/s.
- Thin white or bright-colored shots.
- Allow at most 2 player bullets on screen at once.
- This two-shot limit is important to classic feel.
- Destroy bullets when:
  - they hit an enemy
  - they hit a boss/captor beam object if implemented
  - they leave the top of the screen

Game states:
1. Title screen
   - Visible on load
   - Shows title “GALAGA”
   - Explains controls briefly
   - Explains the objective in plain language:
     - move left/right
     - shoot enemies
     - avoid dive attacks and bullets
     - clear the wave
   - Shows “Press Enter to Start”
2. Stage intro / wave start
   - Show “STAGE 1”, “STAGE 2”, etc. briefly
3. Playing
   - Main gameplay
4. Paused
   - Freeze all action and show “PAUSED”
5. Respawn / between-life state
   - Brief pause after losing a ship if lives remain
6. Game over
   - Show “GAME OVER”, final score, and restart prompt

Enemy composition:
Use a formation-based enemy wave with rows of enemies of different types.

Recommended starting wave composition:
- 5 rows total in formation
- 10 enemies per row is acceptable, but a more classic-feeling composition is around 40 enemies total
- Practical recommendation:
  - top rows: boss / captain type enemies (fewer, larger, tougher)
  - middle rows: butterfly-type enemies
  - lower rows: bee/grunt-type enemies

A clean starter composition:
- 4 boss/captor enemies
- 16 butterfly enemies
- 20 bee/grunt enemies

You do not have to match arcade counts exactly, but the wave should visibly contain:
- weaker common enemies
- medium enemies
- tougher boss/captor enemies

Formation behavior:
- Enemies do not begin already sitting perfectly in place.
- At the start of a stage, they should enter in short choreographed arcs or swoops from off-screen into formation if possible.
- This entrance choreography is strongly recommended because it is a big part of Galaga’s feel.
- If full entrance choreography is too complex, a simpler fallback is:
  - spawn enemies off-screen/top
  - animate them swooping into their assigned formation slots
- Once settled, enemies hover in formation near the top half of the screen.
- The formation should sway or oscillate gently left/right for life.
- Formation position should not be static and dead.

Enemy formation layout:
- Center the formation horizontally in the upper half of the screen.
- Rough slot spacing:
  - horizontal spacing: ~48 px between slot centers
  - vertical spacing: ~40 px between rows
- Formation top row should begin around y=80.
- Each enemy has a designated “formation slot” and may return to it after attacking.

Enemy types:
Use at least three enemy types with distinct visuals and score values.

1. Bee / grunt
- Smallest / simplest enemy
- Most common
- Fast dive attacker
- Score:
  - 50 when shot in formation
  - 100 if shot during a dive

2. Butterfly / medium enemy
- Mid-sized
- Elegant curved dive paths
- Score:
  - 80 in formation
  - 160 during dive

3. Boss / captor
- Largest enemy
- May require 2 hits if not implementing detachable armor, or 1 hit if simplifying
- Responsible for capture beam attacks
- Score:
  - 150 in formation
  - 400 during dive
- If you want a simpler implementation, boss enemies may take 1 hit but should still be visually distinct and rarer.

These exact values are flexible, but scoring more for enemies during dive is strongly recommended because it captures the risk-reward of Galaga.

Dive attacks:
This is the heart of the game.

Enemies should periodically leave formation one at a time or in small groups and dive toward the player along curved paths.
The path should not be a straight downward line. It should feel theatrical and insect-like.

Recommended dive behavior:
- Select an eligible enemy from the formation.
- Temporarily detach it from formation behavior.
- Follow a predefined or parametric path:
  - small loop or corkscrew near top
  - then a descending curve toward player x-position
  - then continue off lower screen or arc back upward
- After the dive:
  - if still alive and not intended to remain out, return to its assigned formation slot
- Some enemies may fire during their dive.

Implementation approach:
- Use scripted spline-like or parametric paths for dives.
- A very workable method:
  - store a sequence of path waypoints/control points
  - move the enemy along a curve over time
- Simpler alternative:
  - state machine with phases:
    1. peel out from formation
    2. curved swoop left/right
    3. descend toward player
    4. return upward to formation
- The important thing is that dives are visibly curved and distinctive, not simple straight descents.

Enemy firing:
- Enemies may shoot while diving and optionally sometimes from formation.
- Bullet speed: about 220–280 px/s downward.
- Bullets should be visible but not enormous.
- Fire cadence should be threatening but fair.
- Dive attackers are the best source of bullets.
- Avoid bullet spam from every enemy simultaneously.

Enemy bullets:
- Destroy on leaving screen bottom or hitting player.
- Optional: allow player bullets to pass through enemy bullets without collision; this is fine and simpler.
- Bullet visuals may vary slightly by enemy type but do not need to.

Lives:
- Player starts with 3 lives.
- Display remaining lives clearly.
- On hit by enemy bullet or collision with diving enemy:
  - lose one ship
  - play explosion / death animation
  - pause briefly
  - respawn if lives remain
- If lives reach 0, game over.

Respawn:
- Respawn at bottom center after a brief delay.
- It is acceptable to give a very short invulnerability period (e.g. 1 second) if needed for fairness, but keep it subtle.
- Clear or avoid immediate unavoidable bullets on respawn.

Collision rules:
Use AABB or simple radial collision depending on your rendering style; either is fine if consistent.

Required collisions:
- player bullet ↔ enemy
  - destroy bullet
  - damage/destroy enemy
  - award score
- enemy bullet ↔ player
  - player dies
- diving enemy ↔ player
  - player dies
  - enemy may also be destroyed or survive depending on design; simplest is both are removed only if appropriate, but classic-feeling is player dies and enemy continues or is also lost depending on collision logic
- player ↔ capture beam / tractor beam (if implemented)
  - trigger capture sequence instead of normal death
- player bullet ↔ capture beam device / boss (optional if beam is its own object)

Stage progression:
- When all enemies in the wave are destroyed, stage clears.
- Show a brief stage clear / next stage message.
- Start the next stage with:
  - a fresh formation
  - slightly more aggressive dives and/or bullets
- Difficulty can increase via:
  - more frequent dives
  - slightly faster bullets
  - more simultaneous attackers
  - more boss/captor activity
- Preserve score and remaining lives across stages.

Capture / tractor beam mechanic:
This is strongly recommended. It is one of Galaga’s defining features.

Behavior:
- Certain boss/captor enemies, while diving, can stop above the player and emit a tractor beam downward.
- If the player remains under the beam, the player ship is captured instead of simply destroyed.
- The captured ship is then attached near the boss/captor in formation.
- Later, when that boss/captor returns and is shot, the player can rescue the captured ship.

Dual-ship reward:
- If the player rescues the captured ship without destroying it, the rescued ship rejoins the player.
- The player then temporarily or permanently has a dual-fighter:
  - two side-by-side ships
  - fires two bullets at once
- This is iconic Galaga and makes the game feel much more authentic.

If implementing capture/rescue, use this simplified workable version:
1. Boss enemy begins special dive.
2. It pauses near upper-middle screen and projects a vertical blue beam downward.
3. If player overlaps beam, player ship is “captured”:
   - remove active player
   - consume a life slot / treat as lost ship
   - boss returns to formation carrying captured ship marker
4. Later, if that boss is shot:
   - the captured ship is released
   - if the player is alive, the next respawn or immediate merge grants dual-ship mode
5. In dual-ship mode:
   - the player sprite is wider or rendered as two adjacent ships
   - pressing fire emits two bullets from the twin ships
6. If dual-ship player dies, revert to single ship

If capture is too complex to implement fully, at minimum include:
- boss enemies
- dive attacks
- a visually suggested beam attack
But the full capture/rescue mechanic is much better.

Scoring:
Track:
- current score
- high score (persist via localStorage)
- optionally stage bonus for clearing a wave without losing a ship, though not required

Display:
- score top-left
- high score top-right
- stage and lives near top center or lower HUD
- keep HUD readable and unobtrusive

Recommended score examples:
- bee/grunt:
  - 50 in formation
  - 100 diving
- butterfly:
  - 80 in formation
  - 160 diving
- boss:
  - 150 in formation
  - 400 diving
- captured-ship rescue bonus optional but nice

Visual style:
- Black starfield background strongly recommended.
- Enemies should be colorful and distinct by type.
- Player ship should be bright and easy to track.
- Explosions can be simple expanding particles or flashes.
- Formation sway and dive arcs matter more than sprite detail.
- A little animation goes a long way:
  - enemy wing flap / pose swap
  - starfield drift
  - slight formation sway

Suggested colors:
- Player ship: white or cyan with red accents
- Bee: yellow/red
- Butterfly: blue/purple
- Boss/captor: red/magenta with green accents
- Tractor beam: blue/cyan translucent
Exact palette is flexible, but enemies should be distinguishable at a glance.

Audio:
- Optional but recommended.
- Use Web Audio API only.
- Suggested sounds:
  - player shot
  - enemy hit/explosion
  - player death
  - dive swoop tone
  - tractor beam hum
  - stage start cue
- Audio must not be required and should only activate after user interaction.

Implementation guidance:
Use requestAnimationFrame with delta time.
Clamp large frame gaps after tab inactivity.
Separate update and render logic.

Recommended entity/state structures:
- gameState
- player
- playerBullets[]
- enemies[] where each enemy has:
  - type
  - formationSlotX / formationSlotY
  - x / y
  - state: entering, formation, diving, returning, capturing, dead
  - divePath / timer
  - alive
  - capturedShip flag for captor bosses
- enemyBullets[]
- particles[]
- stage / score / highScore / lives
- timers:
  - enemy launch timer
  - enemy fire timer
  - stage intro timer
  - respawn timer

Formation behavior implementation suggestion:
- Keep a formation anchor position that gently oscillates horizontally.
- Each enemy has a slot offset relative to that anchor.
- When in formation state, enemy position eases or snaps toward anchor + slot offset.
- When diving, it ignores formation anchor and follows its own path.
- When returning, guide it back to its slot and resume formation state.

Dive path implementation suggestion:
- Predefine a few dive templates:
  - left loop then descend
  - right loop then descend
  - shallow arc toward player
  - boss capture sweep
- Pick one based on enemy type and side of formation.
- This avoids needing fully procedural choreography while still feeling lively.

Important behavior details:
- Enemies should not all attack at once.
- The formation should remain legible while sending out attackers.
- The player should usually face one or a few active threats at a time, not total chaos.
- If a diving enemy survives, it should be able to return to formation if that slot still conceptually exists.
- If no formation remains, any surviving attackers may continue diving or exit before stage clear.

Pause behavior:
- P pauses and unpauses during active gameplay.
- Freeze all entities, timers, bullets, and animations.
- Show a visible “PAUSED” overlay.

Game over:
- Trigger when lives reach zero and no captured/active fallback remains.
- Show final score and restart prompt.
- Restart should fully reset stage, score, lives, formation, capture state, dual-ship state, timers, bullets, and particles.

Title screen must explain the game clearly:
- Enemies begin in formation and dive toward you.
- Shoot them before they shoot or collide with you.
- Bosses may try to capture your ship.
- Clearing all enemies advances to the next stage.
- Controls and start prompt.

Acceptance checklist:
- On load, title screen is visible and readable.
- Pressing Enter starts the game.
- Player ship moves left/right smoothly and fires upward with Space.
- Enemy wave appears in a clear formation near the top.
- Enemies occasionally break formation and dive in curved attack paths.
- Diving or formation enemies can fire bullets at the player.
- Player loses a life on collision or bullet hit.
- Destroying all enemies advances to the next stage.
- Score, high score, stage, and lives are displayed.
- High score persists via localStorage.
- P pauses and unpauses correctly.
- Game over occurs correctly at 0 lives.
- Strongly preferred: boss enemies can capture the player and rescuing the captured ship grants dual-ship fire.
- Entire implementation is in one self-contained HTML file with inline CSS/JS only and no external dependencies.
