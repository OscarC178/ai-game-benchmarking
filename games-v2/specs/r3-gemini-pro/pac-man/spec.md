# Game Specification: Pac-Man

## 1. Core Concept & Gameplay Overview
Pac-Man is a maze chase game. The player controls Pac-Man, navigating a complex maze to eat all the small dots (pellets) while avoiding four colorful ghosts. 

If a ghost touches Pac-Man, he loses a life. However, four large flashing "Power Pellets" are placed in the corners of the maze. Eating a Power Pellet temporarily turns all ghosts blue (Frightened mode) and makes them reverse direction. During this time, Pac-Man can eat the ghosts for bonus points. Eaten ghosts turn into floating eyes that retreat rapidly to the center "Ghost House" to regenerate. Clearing the entire maze of dots advances the player to the next, faster level.

## 2. Technical Constraints
- **Format:** A single, self-contained `index.html` file.
- **Assets:** Strict zero-dependency. Do not use external image sprites or CSS. Draw the maze, Pac-Man, and Ghosts using the Canvas 2D API (`arc`, `fill`, bezier curves for ghosts).
- **Architecture:** The game must rely on a discrete 2D grid matrix for pathfinding, alignment, and collisions, even though the visual rendering moves entities smoothly between grid cells using `dt` in `requestAnimationFrame`.

## 3. Visual Layout & The Maze
- **Canvas Size:** ~560px width by ~620px height.
- **Grid Size:** The classic maze is 28 columns by 31 rows. (Cell size e.g., 20x20 pixels).
- **Maze rendering:** Draw the maze walls as thick, rounded blue lines (`#1919A6`) on a black background (`#000000`).
- **The Ghost House:** A box in the center of the maze (roughly rows 12-16, columns 10-17) with a "gate" (pink line) at the top that only ghosts can pass through.
- **The Tunnel:** Horizontally wraps the screen on Row 14. If an entity walks off the left edge, they appear on the right edge, and vice versa.

## 4. Game Entities

### Pac-Man
- **Shape:** A yellow circle (`#FFFF00`) with a wedge missing (the mouth). Animate the mouth opening and closing rapidly while moving.
- **Movement:** Pac-Man moves smoothly but strictly along the grid lines. 
- **Cornering (Input Buffering):** This is critical. The player will press "Up" *before* reaching an intersection. You must store this "Queued Direction" and apply it exactly when Pac-Man's center aligns with the center of the intersection tile.

### The Pellets
- **Standard Pellets:** Small beige/pink squares/circles worth 10 points. Populate every traversable corridor tile.
- **Power Pellets:** Large flashing beige/pink circles worth 50 points. Located near the 4 corners of the maze.

### The Ghosts (Crucial AI Rules)
Ghosts have a strict state machine and distinct targeting logic.
- **Blinky (Red):** Targets Pac-Man's exact current grid tile. Very aggressive.
- **Pinky (Pink):** Targets the grid tile 4 spaces *ahead* of Pac-Man's current direction (trying to cut him off).
- **Inky (Cyan):** Targets a tile based on a vector from Blinky's position through the tile 2 spaces ahead of Pac-Man, doubling the length. (Erratic).
- **Clyde (Orange):** If further than 8 tiles from Pac-Man, targets Pac-Man exactly (like Blinky). If closer than 8 tiles, abandons the chase and targets his home corner in the bottom left.

## 5. Ghost State Machine

1. **Scatter Mode:** Ghosts periodically ignore Pac-Man and head toward their respective "home corners" (Blinky: Top Right, Pinky: Top Left, Inky: Bottom Right, Clyde: Bottom Left). This provides the player brief relief. (e.g., 7 seconds Scatter, 20 seconds Chase).
2. **Chase Mode:** Ghosts use their specific targeting logic to hunt Pac-Man.
3. **Frightened Mode:** Triggered by a Power Pellet. Ghosts turn dark blue, reduce speed by ~50%, and choose directions by pseudo-random generation at intersections. Eaten ghosts yield 200, 400, 800, 1600 points sequentially. Lasts for a set time (e.g., 6 seconds), flashing white briefly before ending.
4. **Eaten (Eyes) Mode:** Ghost becomes a pair of eyes and moves extremely fast back to the Ghost House. Once inside, they regenerate to their normal color and exit automatically.

## 6. Grid Movement & Pathfinding (The Intersection Rule)
Ghosts NEVER reverse direction (unless a mode change directly forces them to, e.g., when Frightened mode triggers, they immediately do a 180). 
When a ghost reaches the exact center of a grid tile, it evaluates its next move:
1. Identify all valid exits from the current tile (excluding the direction it just came from).
2. Calculate the straight-line distance (Euclidean metric) from each valid adjacent tile to its current Target Tile.
3. Pick the valid tile that yields the shortest distance to the target.

## 7. Controls
- **Arrow Keys:** Queue direction for Pac-Man.

## 8. Collisions
- Constantly check distance between Pac-Man's center and Ghost centers. If distance < ~14px (overlapping), resolve collision based on Ghost State.
- If Ghost State is Scatter/Chase -> Pac-Man dies. 
- If Ghost State is Frightened -> Ghost is eaten, switch to Eyes mode.

## 9. Game Flow & Escalation
- **Lives:** Start with 3.
- **Speed:** 
  - Pac-Man base speed: e.g., 100px/s. 
  - Ghosts base speed: e.g., 90px/s.
  - Tunnel speed constraint: Both player and ghosts move noticeably slower while inside the side tunnels.
- **Death:** Pause briefly. Play death animation (Pac-Man spins and shrinks). Reset Pac-Man and Ghosts to starting positions.
- **Next Level:** When the final pellet is eaten, flash the maze, reset the board full of pellets, and restart with higher base speeds and shorter Frightened Mode duration.

## 10. Audio (Web Audio API)
- **Waka-Waka:** A dual-tone alternating siren that loops continuously while Pac-Man moves and eats.
- **Eat Power Pellet/Frightened:** A continuous, low, pulsing drone plays in the background while ghosts are blue.
- **Eat Ghost:** A rapid, rising "slide whistle" synth effect.
- **Death:** A descending, discordant series of bloops.
