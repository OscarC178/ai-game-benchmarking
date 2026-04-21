# Game Specification: Frogger

## 1. Core Concept & Gameplay Overview
Frogger is a grid-based arcade action game where the objective is to guide a frog from the bottom of the screen to five specific "home" slots at the top. The player must navigate two distinct hazard zones:
1. **The Road:** The bottom half of the screen. Filled with cars, trucks, and bulldozers moving horizontally at various speeds. The frog must dodge these vehicles.
2. **The River:** The top half of the screen. In this zone, the water itself is lethal. The frog must cross by jumping onto moving platforms (logs and turtles).

To complete a level, the player must successfully guide a frog into all five home slots. The game is timed; if the player takes too long, they lose a life.

## 2. Technical Constraints
- **Format:** A single, self-contained `index.html` file.
- **Assets:** Strict zero external dependency rule. Draw all entities (frog, cars, logs, turtles) using Canvas API (`fillRect`, `arc`, paths) to create retro pixel-style sprites. No external images or CSS.
- **Grid System:** The game functions on a strict grid visually, but movement states can be handled fluidly or discretely. Player movement is discrete (hopping one tile at a time), while hazards move continuously via delta time (`dt`) in a `requestAnimationFrame` loop.

## 3. Visual Layout & Dimensions
- **Canvas Size:** 600px width by 650px height.
- **Grid:** Consider the play area as 13 rows tall. Each row/lane is approx 40px high.
- **Regions (Bottom to Top):**
  - UI/Bottom (Row 13): Start zone. Black or purple.
  - Road (Rows 8 to 12): 5 lanes of traffic. Gray or black background.
  - Median (Row 7): Safe zone halfway up. Green background.
  - River (Rows 2 to 6): 5 lanes of logs/turtles. Blue background (`#0000AA`).
  - Goal (Row 1): The riverbank with 5 indented "home" slots (coves) spaced evenly.
  - HUD (Row 0): Top bar for score, time, and lives.
- **Typography:** Arcade-style monospace font, bright colors.

## 4. Game Entities

### The Player (The Frog)
- **Size:** 30x30px (fits within a 40x40 lane).
- **Color:** Bright Green (`#00FF00`).
- **Movement (Discrete Hops):** The frog does not walk smoothly. Pressing a directional key makes the frog instantly (or very quickly) jump one full lane distance (e.g., 40px). 
- **Orientation:** Draw the frog facing the direction of the last jump.
- **Screen Bounds:** Cannot jump off the left, right, or bottom edges of the screen.
- **Riding Logic:** When the frog is overlapping a river object (log or turtle), the frog's X position must be continuously updated to match the velocity of that object. If the object carries the frog off the edge of the screen, the frog dies.

### Road Hazards (Cars & Trucks)
- **Rows 8-12.** Each lane has specific vehicle types moving right-to-left OR left-to-right.
- **Speed & Spacing:** Constant speed per lane. Spaced out so there are clear gaps. Speeds and densities should vary by lane (e.g., Lane 1 might have slow, long trucks; Lane 3 might have fast, small race cars).
- **Colors & Shapes:** Use contrasting colors (Yellow, Red, Purple, White) to distinguish vehicle types. Draw them as blocky rectangles.

### River Platforms (Logs & Turtles)
- **Rows 2-6.** Objects move right-to-left OR left-to-right.
- **Logs:** Brown (`#8B4513`). Come in short, medium, and long sizes. Always safe to stand on.
- **Turtles:** Red/Pink (`#FF4444`). Move in groups of 2 or 3. 
  - *Diving Turtles (Crucial Mechanic):* Some turtle groups periodically dive underwater and resurface. They switch between three states: Surfaced (safe), Submerging (safe but visually darker), and Submerged (invisible and lethal; if the frog is on them when they submerge, the frog drowns).

### The Homes (Goal Slots)
- 5 slots at the top.
- When the frog lands perfectly in an empty slot, they score points, that slot is filled (draw a frog permanently sitting there), and a new frog spawns at the bottom.
- Landing adjacent to a slot, or landing in an already-filled slot, kills the frog.

## 5. Controls
- **Arrow Keys (Up, Down, Left, Right):** Hop frog in the respective direction.
- **Input Debouncing:** Prevent holding a key from spamming jumps. One keypress = one hop. 

## 6. Collisions & Death Triggers
Use AABB overlap. A generous margin of error (hitboxes slightly smaller than the visual shapes) makes the game feel fair.

**Death occurs if the frog:**
1. Touches a vehicle in the road.
2. Is in the River area (Rows 2-6) BUT is NOT touching a safe log or surfaced turtle. (The water is lava).
3. Is carried off the left or right edge of the screen by a log or turtle.
4. Jumps into the Goal row but misses an empty slot (hits the bank or a filled slot).
5. The level timer runs out.

When death occurs: Play a discrete animation (e.g., a skull-and-crossbones sprite flash), pause briefly, reset the frog to the start, and lose 1 life.

## 7. Scoring and Progression
- +10 points for every *new* forward step (jumping backward doesn't award points, and jumping back up to a previously visited row doesn't grant points twice for the same row).
- +50 points for successfully reaching a home slot.
- +1000 points (and level advance) when all 5 slots are filled.
- Bonus points awarded based on the remaining time when a slot is filled.
- As levels increase, vehicles move faster, more turtles become diving turtles, and logs become shorter.

## 8. State Flow
- **Lives:** Start with 3.
- **Timer:** Usually represented as a visual colored bar taking up the bottom of the screen, shrinking continually over roughly 30-40 seconds.
- **STATE: START:** "FROGGER" title screen. "Press Space/Enter to Start".
- **STATE: PLAY:** Active game loop.
- **STATE: DEAD:** Briefly freeze, show death sprite, reset.
- **STATE: GAME OVER:** Lives = 0. Show text, wait for restart.

## 9. Audio (Web Audio API)
Audio requires a user interaction to unlock `AudioContext`.
- **Hop:** A short, distinctive "boing" (e.g., a fast rising synth pitch).
- **Death (Squash / Drown):** A discordant, descending noise.
- **Home:** A bright, rewarding chime.
- **Time Running Out:** A fast, high-pitched ticking that plays when the timer bar is critically low (e.g., last 5 seconds).
