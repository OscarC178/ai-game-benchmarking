Build a classic Space Invaders-style arcade shooter as a single self-contained HTML file using HTML5 Canvas, with all CSS and JavaScript inline and no external libraries, images, audio files, fonts, or network requests.

Assume the developer has never seen Space Invaders. The game is a fixed-screen defense shooter. The player controls a small cannon/ship at the bottom of the screen and fires upward at descending alien formations. The enemies move as a coordinated block, sweeping horizontally, reversing direction when they hit a screen edge, and dropping lower each time they reverse. The player must destroy all aliens before they descend too far or before being shot too many times. The essential feeling is mounting pressure: the fewer aliens remain, the more dangerous and urgent the formation becomes.

The game should feel crisp, readable, tense, and unmistakably arcade-like. Minimal graphics are fine; the important part is clear rules, good pacing, and faithful behavior.

Canvas and presentation:
- Canvas size: 800×600 pixels.
- Background: solid black (#000000).
- Coordinate system: origin at top-left.
- Use a fixed internal resolution even if displayed responsively in the browser.
- Rendering style should be minimalist, geometric, and high-contrast.
- All sprites may be drawn with simple rectangles, vector silhouettes, or tiny pixel-art shapes created directly in canvas code.

Core objective:
- Control the player ship at the bottom of the screen.
- Shoot upward to destroy all aliens.
- Avoid alien bullets.
- Use shields for temporary cover.
- Clear a wave to start the next wave.
- Lose if the player runs out of lives or if the aliens descend to the player line / invader defeat threshold.

Player ship:
- Size: 40×32 pixels.
- Color: bright green (#00FF00).
- Starting position: x=380, y=550.
- Movement: horizontal only.
- Movement speed: 300 px/s.
- Clamp fully inside screen bounds.
- No inertia required; direct responsive movement is correct.
- Ship should feel precise and predictable.

Player controls:
- ArrowLeft / A = move left
- ArrowRight / D = move right
- Space = fire
- Enter = start from title screen and restart after game over
- P = pause / unpause
- Optional: Enter may also start a new wave after title or game over, but Space remains the fire button

Player bullet:
- Shape: vertical rectangle.
- Size: 3×12 pixels.
- Color: white (#FFFFFF).
- Spawn point: center-top of player ship.
- Speed: 500 px/s upward.
- Only one player bullet may exist at a time.
- If the player presses fire while a bullet is already active, do nothing.
- Bullet is destroyed on:
  - hitting an alien
  - hitting a shield cell
  - leaving the top of the screen
  - colliding with an alien bullet (optional but recommended)

Alien formation:
- 11 columns × 5 rows.
- The formation is a coordinated block, not independent free-moving enemies.
- Use three alien silhouette types:
  - top row: small type, 24×16 px, red (#FF0000)
  - middle rows: medium type, 28×20 px, yellow (#FFCC00)
  - bottom rows: wide type, 32×20 px, cyan (#00CCFF)
- First alien center position: x=120, y=80.
- Horizontal spacing between alien centers: 50 px.
- Vertical spacing between alien centers: 40 px.
- Formation movement:
  - move horizontally as a group at 30 px/s initially
  - when any alive alien would cross a horizontal boundary, the entire formation:
    - reverses direction
    - drops downward by 20 px
- As aliens are destroyed, the movement should feel faster / more urgent.
  - This can be implemented either by increasing horizontal speed as alien count decreases or by shortening step intervals if using classic stepped movement.
  - The important outcome is: fewer aliens = more dangerous formation.
- The formation should remain easy to read as a single moving wall of enemies.

Alien movement style:
Two implementations are acceptable:
1. Smooth continuous movement of the formation with synchronized animation and discrete edge-drop reversals.
2. Classic stepped movement where the formation advances in small horizontal steps at a cadence that accelerates as aliens die.

Either is fine, but the formation must clearly:
- behave as a group
- reverse at edges
- drop lower after each edge hit
- become more threatening as numbers thin out

Alien bullets:
- Shape: vertical rectangle.
- Size: 3×12 pixels.
- Color: red-tinted (#FF4444) or similar.
- Speed: 250 px/s downward.
- Maximum simultaneous alien bullets: 3.
- Bullets are fired from the bottom-most alive alien in a chosen column.
- Only columns containing living aliens may fire.
- Fire cadence should feel threatening but fair.
- Multiple alien bullets on screen at once are important to the game feel.
- Alien bullets are destroyed on:
  - hitting player
  - hitting shield cells
  - leaving the bottom of the screen
  - colliding with player bullet (optional but recommended)

Enemy firing behavior:
- At intervals, select one or more valid columns from alive alien columns.
- For each shot, use the bottom-most alive alien in that column as the origin.
- Bullets should emerge from the alien body and travel straight downward.
- Fire rate can scale gently by wave or by remaining alien count.
- Avoid overwhelming chaos; the player should feel pressured, not helpless.

Shields:
- 4 destructible shield bunkers.
- Position them roughly above the player area at x origins:
  - 140
  - 300
  - 460
  - 620
- y origin: 480
- Approximate shield footprint: 80×64 px each.
- Construct shields from a grid of small destructible cells, e.g. 4×4 px blocks.
- Each shield should resemble a chunky bunker with an arch/cutout at the bottom center.
- Bullets remove cells they hit.
- Repeated hits should progressively chew holes through the shields.
- Both player and alien bullets damage shields.
- Shields are one of the key tactical elements and should visibly degrade over time.

Mystery ship:
- A red saucer-like bonus ship occasionally travels across the very top of the screen.
- Size: 48×16 px.
- Color: red.
- It should enter from one side and move horizontally across the top, then exit the other side.
- Appears occasionally, not constantly.
- Destroying it awards bonus points.
- Good bonus range: 50 / 100 / 150 / 300, or just a fixed 100 if simplifying.
- This feature is strongly recommended because it is part of the classic feel.

Lives:
- Player starts with 3 lives.
- Display lives in HUD.
- On player hit:
  - remove one life
  - destroy active alien bullets (recommended)
  - briefly reset the player ship to a safe neutral position
  - optionally pause the action briefly before resuming
- If lives reach 0, game over.
- Optional invulnerability window after respawn is acceptable if brief and visually obvious.

Wave progression:
- A wave ends when all aliens are destroyed.
- Starting a new wave should:
  - rebuild the full 11×5 formation
  - optionally preserve partially damaged shields or rebuild them; either is acceptable, but rebuilding each wave is simpler and more forgiving
  - increase difficulty slightly
- Difficulty increase options:
  - slightly faster formation
  - slightly faster or more frequent alien bullets
  - slightly more aggressive mystery ship cadence
- Preserve score and remaining lives across waves.

Lose conditions:
The player loses if either:
- lives reach zero
- the alien formation descends too low
  - a good rule: if any alien reaches the player’s y zone or passes a defeat line above the shields / near the player
- Optionally, touching the player directly also causes immediate defeat, but in practice this is covered by descent threshold

Scoring:
Use a simple classic-feeling scoring system:
- Top-row aliens: 40 points
- Middle-row aliens: 20 points
- Bottom-row aliens: 10 points
- Mystery ship: bonus points
These exact values are not mandatory, but differential scoring by alien row is strongly preferred.
Start score at 0.
High score should persist in localStorage.
Display score top-left, high score top-right.

HUD:
At minimum display:
- current score
- high score
- lives
- wave number
All should be readable but unobtrusive.
Suggested layout:
- score top-left
- lives near bottom-left or top-center
- wave near top-center
- high score top-right

Game states:
1. Title screen
   - Visible on initial load
   - Show title “SPACE INVADERS”
   - Explain the objective briefly:
     - move left/right
     - fire upward
     - destroy all aliens
     - avoid bullets
     - shields absorb damage
   - Show controls
   - Show “Press Enter to Start”
2. Playing
   - Main gameplay active
3. Paused
   - Freeze all simulation
   - Show centered “PAUSED”
4. Between-life reset / respawn moment
   - Brief, readable reset after player hit if lives remain
5. Wave clear transition
   - Brief display such as “WAVE 2”
6. Game over
   - Show “GAME OVER”
   - Show final score
   - Show restart prompt

Collision rules:
Use AABB or simple rectangle-based collision for all gameplay objects.

Required collision pairs:
- player bullet ↔ alien
  - destroy bullet
  - destroy alien
  - award score
- player bullet ↔ mystery ship
  - destroy bullet
  - destroy mystery ship
  - award bonus
- player bullet ↔ shield
  - destroy bullet
  - remove struck shield cells
- alien bullet ↔ shield
  - destroy bullet
  - remove struck shield cells
- alien bullet ↔ player
  - destroy bullet
  - lose life / trigger hit
- alien ↔ player defeat line
  - trigger defeat
- optional but recommended:
  - player bullet ↔ alien bullet
    - destroy both on contact

Alien sprite behavior:
- You may animate aliens with a two-frame wobble / pose swap to mimic the classic look.
- This is optional but recommended.
- The animation can toggle on each movement step or on a short timer.
- Even simple geometric silhouettes are acceptable as long as row types are visually distinct.

Player ship rendering:
- A simple classic cannon shape is sufficient:
  - flat base
  - rising center
  - maybe two side blocks
- Use solid green and perhaps a darker accent if desired.
- It should be instantly readable against the black background.

Shield rendering:
- Shields should visibly erode cell-by-cell.
- This degradation is important. A static shield sprite that merely disappears when “dead” is not enough.
- Represent shields as boolean/health cells in a small grid mask and carve them away on hits.

Recommended timing / difficulty feel:
- Initial wave should be manageable, not instantly oppressive.
- Alien bullets should be regular but not spammy.
- Formation descent should create pressure even for players who survive a long time.
- By the end of a wave, one or two remaining aliens should feel noticeably tense because of increased speed.
- The game should reward accuracy and steady movement rather than frantic randomness.

Audio:
- Optional but recommended.
- Use Web Audio API only; no external files.
- Suggested sounds:
  - short shot sound for player fire
  - hit sound for alien destruction
  - lower tone for player death
  - marching beat tied to alien movement cadence
  - distinct tone for mystery ship
- If using sound, keep it simple and procedural.
- Audio should only start after user interaction to satisfy browser rules.

Implementation guidance:
- Use requestAnimationFrame for rendering.
- Use delta time in seconds and clamp large frame gaps.
- Separate update and render cleanly.
- Maintain clear entity/state structures, for example:
  - player
  - playerBullet
  - alien grid / formation data
  - alienBullets[]
  - shields
  - mysteryShip
  - score/lives/wave/state
- For formation logic, avoid updating each alien as a fully independent mover if that makes classic behavior harder. It is often easier to:
  - store alive/dead state in a grid
  - maintain a formation offset
  - compute living alien positions from base grid + formation offset
  - detect leftmost/rightmost alive alien for edge collision
- This better matches classic coordinated movement.

Recommended formation model:
- Store aliens in rows/columns with alive flags and type metadata.
- Maintain:
  - formationOffsetX
  - formationOffsetY
  - direction (1 or -1)
  - movementSpeed or stepTimer
- Alive alien position = basePosition + formation offsets.
- To check screen-edge reversal:
  - find leftmost and rightmost alive alien bounds
  - if moving right and rightmost would cross right boundary, reverse and drop
  - if moving left and leftmost would cross left boundary, reverse and drop

Boundaries:
- Keep aliens within visible screen width during sweeps.
- Maintain some padding so the formation does not clip the screen edge.
- Player must remain fully visible at all times.

Polish expectations:
- The game should feel complete, not like a prototype.
- It should be obvious when a wave starts, when the player is hit, and when the game ends.
- There should be no stuck bullets, invisible hits, or jittering enemies.
- Screen readability matters more than visual flourish.
- If any effect threatens clarity, simplify it.

Acceptance checklist:
- On load, title screen is visible and readable.
- Pressing Enter starts the game.
- Player ship moves left/right smoothly with Arrow keys and A/D.
- Space fires a single upward bullet; only one player bullet can exist at once.
- Aliens appear in an 11×5 formation and move as a coordinated group.
- Formation reverses at edges and drops lower.
- Aliens can be destroyed by player bullets.
- Alien bullets fire from valid living aliens and move downward.
- Player loses a life when hit by an alien bullet.
- Four destructible shields protect the player and visibly erode under fire.
- Clearing all aliens starts a new wave.
- Mystery ship occasionally crosses the top and awards bonus points when destroyed.
- Score, high score, lives, and wave are displayed.
- High score persists via localStorage.
- Game over occurs when lives reach 0 or aliens descend too far.
- P pauses and unpauses correctly.
- Entire implementation is a single self-contained HTML file with inline CSS/JS only and no external dependencies.
