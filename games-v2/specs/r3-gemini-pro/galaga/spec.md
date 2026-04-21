# Game Specification: Galaga

## 1. Core Concept & Gameplay Overview
Galaga is a fixed-screen arcade shooter. The player controls a starfighter at the bottom of the screen, moving horizontally to shoot alien enemies. Unlike Space Invaders where enemies start in a grid, Galaga's enemies fly into the screen from the edges in looping, curving "convoy" formations before taking up their slotted positions in a grid at the top. 

Once in the grid, individual aliens or small groups continually break formation to "dive" or "swoop" down at the player while firing projectiles. The most iconic mechanic is the "Boss Galaga" which can lower a tractor beam to capture the player's fighter. If the player shoots the Boss holding their captured fighter, they retrieve it, creating a "Dual Fighter" (two ships side-by-side) that doubles their firepower.

## 2. Technical Constraints
- **Format:** A single, self-contained `index.html` file.
- **Assets:** Strict zero-dependency rule. Render all graphics using Canvas 2D API primitives. Implement simple pixel-art style sprites using `fillRect` or arrays. No external images, CSS, or audio files.
- **Game Loop:** Standard `requestAnimationFrame` with delta time (`dt`) for smooth physical movement.
- **State Machine:** The game requires a robust state machine to handle the distinct phases of enemy behavior (Entrance, Grid, Dive).

## 3. Visual Layout
- **Canvas Size:** Vertical orientation, e.g., 600px width by 800px height.
- **Background:** Black (`#000000`) with a vertically scrolling starfield (multiple layers of white/colored dots moving down at different speeds to create parallax depth).
- **Typography:** Bright, arcade-style monospace fonts (`#FF0000`, `#FFFF00`, `#00FFFF`).
- **UI:** Score and High Score at the top. Remaining lives (rendered as small ship icons) in the bottom-left corner. Stage markers (small badges/medals) in the bottom-right corner.

## 4. Game Entities

### The Player (Fighter)
- **Shape:** A sleek, pointed spaceship. Usually white with blue and red accents.
- **Size:** Approx 30x30 pixels.
- **Movement:** Strictly horizontal along the bottom. Speed: ~300 px/sec. 
- **Dual Fighter:** If the player rescues a captured ship, their bounding box and drawing logic doubles in width (two ships connected). They now fire two projectiles simultaneously.

### Player Projectiles
- **Shape:** Simple thin yellowish/white dashes (`#FFFFcc`).
- **Speed:** Fast (~800 px/sec) upwards.
- **Limits:** Exactly 2 projectiles allowed on screen at once per ship (so 4 if Dual Fighter).

### The Enemies (Galaga Forces)
The enemy fleet consists of 40 bugs arranged in a grid:
- **Boss Galagas (Top Row, 4 count):** Need 2 hits to destroy. (Hit 1 changes color/state). These are the only enemies that use the tractor beam.
- **Goeeies / Red Bugs (Rows 2 & 3, 16 count):** Standard divers.
- **Zako / Blue Bugs (Rows 4 & 5, 20 count):** Standard divers.

### Enemy Projectiles
- **Shape:** Small red or yellow teardrops/dots.
- **Speed:** Moderate (~250 px/sec) acting as area denial. Fired towards the general direction of the player.

## 5. Enemy Behavior States (Crucial System)

### Phase 1: The Entrance (Convoys)
- Enemies do not start in the grid. They fly into the screen from the top, bottom-left, and bottom-right corners in groups of 4 to 8.
- They follow predefined Bezier curves, looping arcs, or waypoints before flying up and settling into their assigned `gridX` and `gridY` slots.
- While flying in, they can shoot and dive at the player.
- The grid positions themselves slowly pulse left and right as a collective whole (the "breathing" grid).

### Phase 2: The Idle Grid
- Once all enemies have arrived, they idle in their grid positions, pulsing left and right.

### Phase 3: The Swoop / Dive
- Randomly, 1 to 3 enemies will break formation and dive toward the bottom of the screen.
- The dive path is usually a wide arc or loop (not a straight line). 
- If an enemy reaches the bottom of the screen, it loops back around and re-enters from the top to return to its grid slot.
- Boss Galagas usually dive with 2 Red Bug escorts.

## 6. The Tractor Beam Mechanic (The Core Gimmick)
1. A Boss Galaga dives and stops at a designated height (e.g., 2/3 down the screen).
2. It emits a cone-shaped "tractor beam" made of pulsing blue/white lines spanning downwards.
3. If the Player touches the beam, they lose control. The ship spins and is pulled up into the Boss Galaga.
4. The Boss returns to the grid with the captured Player ship red-tinted behind it. (The player uses up 1 life; if it was their last life, Game Over).
5. **Retrieval in subsequent play:**
   - If the player (on their next life) shoots the *Boss Galaga* while it is *diving*, the captured ship is freed, spins down, and docks next to the player, creating the Dual Fighter.
   - If the player shoots the Boss Galaga while it is *idle in the grid*, the captured ship turns hostile and attacks the player.

## 7. Controls
- **ArrowLeft:** Move Left.
- **ArrowRight:** Move Right.
- **Spacebar:** Fire.

## 8. Collisions and Logic
Use standard AABB (Axis-Aligned Bounding Box) or simple radius checks.
- Player Projectile vs. Enemy (during fly-in or grid or dive).
- Player vs. Enemy Body (fatal).
- Player vs. Enemy Projectile (fatal).
- Player vs. Tractor Beam (triggers capture sequence).
- Boss Galaga needs 2 hits to be destroyed. First hit changes its color palette to signify damage.

## 9. Scoring and Progression
- Points vary based on state. Enemies killed while diving (in formation) are worth roughly double the points of enemies killed while idling in the grid.
- Boss Galaga: 150 points (idle) / 400 points (diving).
- Escorts (Red/Blue): 50-80 points (idle) / 100-160 points (diving).
- After a level is cleared, display "STAGE [X]". 

## 10. Bonus Stages (Challenging Stages)
- Every few levels (e.g., Level 3, 7, 11), insert a "Challenging Stage".
- Enemies fly in predefined intricate looped paths and exit the screen without diving or shooting.
- The player must shoot as many as possible (usually out of 40). 
- No grid phase. No player death possible. 
- Award a significant score bonus based on the number destroyed (Special "PERFECT" bonus for all 40).

## 11. Audio (Web Audio API)
- **Fire:** A quick, electronic "pew".
- **Enemy Hit:** A sharp pop or explosion burst.
- **Player Death:** A drawn-out, descending series of explosion noises.
- **Tractor Beam:** A continuous, low, wobbly synth tone extending in pitch as it drags the player up.
- **Theme/Jingles:** Brief arpeggiated melodies using square waves for level starts, captures, and rescues. (Only play after user interaction to respect browser autoplay policies).
