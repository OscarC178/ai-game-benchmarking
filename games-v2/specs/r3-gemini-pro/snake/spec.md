# Game Specification: Snake

## 1. Core Concept & Gameplay Overview
Snake is a discrete, grid-based survival and growth game. The player controls a continuously moving line (the "Snake") that travels across a bounded 2D grid. The objective is to navigate the snake's head over consumable items ("Food" or "Apples") that appear one at a time on the grid. 

Each time the snake eats food, it grows in length by one grid cell. The snake cannot stop moving. The game ends immediately if the snake's head collides with the outer boundary walls of the grid or with any part of its own body. As the snake grows, navigating the shrinking available space without self-colliding becomes the primary challenge.

## 2. Technical Architecture & Constraints
- **Format:** A single, self-contained `index.html` file.
- **Assets:** Strict zero-dependency rule. No external CSS, JS, images, or audio files.
- **Rendering:** HTML5 `<canvas>` using the 2D context.
- **Timing & Physics:** Unlike continuous physics games, Snake operates on a "Tick" or "Sweep" basis. The game state should only update at fixed time intervals (e.g., every 100 milliseconds), while rendering can occur at the browser's native frame rate via `requestAnimationFrame`.

## 3. Visual Design & Grid System
- **Canvas Size:** 600px width by 600px height.
- **Grid System:** The canvas is divided into a strict grid.
  - Cell Size: 20px by 20px.
  - Columns: 30 (Canvas Width / Cell Size).
  - Rows: 30 (Canvas Height / Cell Size).
  - All game coordinates (`x`, `y`) must represent grid coordinates (0 to 29), not pixel coordinates. Multiply by cell size only during the render step.
- **Color Palette:** 
  - Background: Very dark green (`#0a140a`) or black (`#000000`).
  - Snake Head: Bright Yellow (`#FFFF00`) or Lime Green (`#00FF00`).
  - Snake Body: Medium Green (`#00CC00`).
  - Food: Bright Red (`#FF0000`).
  - Score/Text: White (`#FFFFFF`) monospace font.

## 4. Game Entities

### The Snake (Data Structure)
The snake must be represented as an array of coordinate objects, e.g., `[{x: 10, y: 15}, {x: 9, y: 15}, {x: 8, y: 15}]`.
- **Index 0** is always the Head.
- **Length:** Starts with a length of 3 or 4 segments.
- **Initial Position:** Centered on the grid, horizontal, facing Right.
- **Initial Direction:** Right.

### The Food
A single coordinate object on the grid, e.g., `{x: 20, y: 5}`.
- **Spawning Logic:** Whenever food is eaten (or upon game initialization), generate random `x` and `y` coordinates within the grid limits (0-29). 
- **Crucial Rule:** You must verify that the newly generated food coordinate does not overlap with *any* segment of the snake's current body array. If it does, reroll the random position until a valid empty space is found.

## 5. Movement algorithm (The Game Tick)
Every time the fixed interval timer (e.g., 100ms) elapses, execute exactly one logical "Tick":

1. **Calculate New Head Position:** Take the current head coordinate (index 0) and add the current direction vector (`dx`, `dy`) to create a new head object.
2. **Check Collisions (Fatal):**
   - *Wall Collision:* If the new head `x` < 0, `x` > 29, `y` < 0, or `y` > 29 -> GAME OVER.
   - *Self Collision:* If the new head coordinate matches ANY coordinate currently occupying the snake array -> GAME OVER.
3. **Move / Grow (Unshift & Pop):**
   - Insert the new head object at the beginning of the snake array (`unshift`).
   - Check if the new head coordinate matches the Food coordinate.
     - **If YES (Eating):** Do NOT remove the tail. Increase score by 10. Generate new Food. Optional: Slightly decrease the tick time (increase game speed) down to a capped minimum.
     - **If NO (Standard Move):** Remove the last element of the snake array (`pop`). This creates the illusion of forward locomotion.

## 6. Controls & Input Buffering
The player uses the Arrow Keys or W-A-S-D to change the snake's direction vector.
- Up translates to `{dx: 0, dy: -1}`
- Down translates to `{dx: 0, dy: 1}`
- Left translates to `{dx: -1, dy: 0}`
- Right translates to `{dx: 1, dy: 0}`

### The Input Queue / Reversal Prevention (CRITICAL)
A snake cannot reverse directly into itself (e.g., if moving Right, the Left command must be ignored). 
Furthermore, because human inputs can be faster than the game tick (e.g., 100ms), a player moving UP might press LEFT then DOWN in rapid succession before the next tick. If you only check against the *current* direction variable, the snake will illegally reverse into itself.
- **Solution:** Maintain a queue (array) of user inputs, or store the `lastProcessedDirection` executed in the previous tick. Only allow directional changes that are completely orthogonal (90 degrees) to the `lastProcessedDirection`, not just the most recently pressed key. Apply one input from the queue per tick.

## 7. Game States & Flow
- **START SCREEN:** Display "SNAKE". Below it, "Press Space to Start".
- **PLAYING STATE:** Main game loop active. Render score at the top left. Render the food, then render the snake array.
- **GAME OVER STATE:** Stop the game loop. Display "GAME OVER". Show the final score. Show "Press Space to Restart". Reset all variables (snake array, score, direction, tick speed, etc.) upon restart.

## 8. Audio (Web Audio API)
Implement an inline sound synthesizer using natively available `window.AudioContext`. Note: AudioContext should be initialized or `resumed()` only after a gesture (like pressing Space to start).
- **Eat Sound:** A short, high-pitched "blip" or rising sweep (e.g., using an oscillator starting at 400Hz sliding up to 800Hz extremely quickly over 0.1s).
- **Crash/Game Over Sound:** A harsh, low frequency noise or descending tone (e.g., a oscillator starting at 200Hz dropping to 50Hz over 0.4s).
