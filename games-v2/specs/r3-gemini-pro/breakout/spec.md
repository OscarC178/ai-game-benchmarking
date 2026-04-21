# Game Specification: Breakout

## 1. Core Concept & Gameplay Overview
Breakout is a single-player arcade game where the objective is to destroy a wall of bricks at the top of the screen. The player controls a paddle—a horizontal platform at the bottom of the screen—that can only move left and right. A ball bounces continuously around the screen. 

The player must use the paddle to intercept the ball and bounce it upwards into the bricks. When the ball strikes a brick, the brick is destroyed, the player earns points, and the ball deflects back. If the ball touches the bottom edge of the screen (missing the paddle), the player loses a life. The game is won when all bricks are destroyed, and lost when the player runs out of lives.

## 2. Technical Constraints
- **Format:** A single, self-contained `index.html` file.
- **Assets:** Strict zero external dependency rule. No external CSS, JS, images, or audio files. You must render everything procedurally.
- **Rendering:** HTML5 `<canvas>` using the 2D context (`getContext('2d')`).
- **Timing:** Use `requestAnimationFrame` for the game loop. Standardize movement using delta time (`dt`) so the game speed is independent of the monitor's refresh rate.

## 3. Visual Design & Layout
- **Canvas Size:** 800px width by 600px height. Position centered in the browser with `#000000` (black) body background.
- **Canvas Background:** Black (`#000000`).
- **Typography:** Standard monospace font for UI (Score, Lives, Messages). Color: `#FFFFFF`.

## 4. Game Entities

### The Paddle
- **Dimensions:** Width: 100px | Height: 15px.
- **Color:** Light Blue (`#00FFFF`) or White (`#FFFFFF`).
- **Starting Position:** Centered horizontally (`x = 350`), fixed near the bottom (`y = 550`).
- **Movement:** Restricted strictly to the X-axis. Movement is clamped so the paddle cannot partially or fully exit the left (`x < 0`) or right (`x > 800 - paddleWidth`) screen boundaries.
- **Speed:** 500 pixels per second.

### The Ball
- **Dimensions:** Radius of 8px (can be rendered as a circle or a 16x16 square).
- **Color:** White (`#FFFFFF`).
- **Initial State:** Resting on the center of the paddle before the player "serves", or immediately spawned moving upwards.
- **Speed:** Base speed of 400 pixels per second. Speed should increase slightly (e.g., +2%) every time a brick is destroyed to ramp up difficulty.

### The Bricks (The Wall)
- **Grid Setup:** 8 rows and 14 columns of bricks.
- **Dimensions:** Brick Width: 50px | Brick Height: 20px.
- **Spacing/Padding:** 5px between bricks, 5px from the top/left/right walls to center the grid perfectly (Calculate offsets carefully).
- **Placement Offsets:** Start drawing the grid 50px from the top of the canvas to leave room for the UI.
- **Colors by Row (Top to Bottom):**
  - Rows 0-1: Red (`#FF0000`) - 7 points each
  - Rows 2-3: Orange (`#FFA500`) - 5 points each
  - Rows 4-5: Yellow (`#FFFF00`) - 3 points each
  - Rows 6-7: Green (`#00FF00`) - 1 point each
- **Data Structure:** A 2D array or flat list of objects containing `x`, `y`, `status` (1 for active, 0 for broken), and `color`.

## 5. Controls
- **Keyboard:** Left Arrow (or 'A') moves paddle left. Right Arrow (or 'D') moves paddle right.
- **Mouse (Optional but recommended):** Moving the mouse horizontally maps the paddle's center to the cursor's X coordinate (clamped to screen boundaries).
- **Spacebar / Left Click:** "Serve" the ball to start the game or resume after a life is lost.

## 6. Physics & Collision Mechanics

### Wall Collisions
- **Left/Right Walls:** If the ball hits `x <= 0` or `x + radius >= 800`, invert its horizontal velocity (`vx = -vx`).
- **Top Wall:** If the ball hits `y <= 0`, invert its vertical velocity (`vy = -vy`).
- **Bottom Wall (Death):** If the ball goes below the paddle (`y >= 600`), the player loses a life. Do NOT bounce. Transition to the "Serve/Life Lost" state.

### Paddle Collision (CRITICAL GAMEPLAY MECHANIC)
Standard angle-of-reflection (`vy = -vy`) on the paddle creates a boring game where the ball follows the same paths forever. **You must give the player aiming control.**
1. When the ball intersects the paddle's Axis-Aligned Bounding Box (AABB), calculate the *relative intersection point*.
2. `hitPoint = ball.x - (paddle.x + paddle.width / 2)` (Distance from the center of the paddle).
3. Normalize this value from `-1.0` (hit the far left edge) to `1.0` (hit the far right edge).
4. Calculate the bounce angle. A maximum angle of 60 degrees (`Math.PI / 3` radians) is standard.
   `angle = hitPointNormalized * MAX_ANGLE`
5. Apply the new velocity using trigonometry (ensure the ball always goes UP, so Y is negative):
   - `ball.vx = ball.speed * Math.sin(angle)`
   - `ball.vy = -ball.speed * Math.cos(angle)`

### Brick Collisions
Use AABB overlap checks to see if the ball intersects an active brick.
1. If overlap occurs: Set brick `status = 0` (destroyed), update the score.
2. Deflection: To prevent the ball from ghosting through adjacent bricks, you must determine which side of the brick was hit based on the ball's previous frame position.
   - If the ball was historically above or below the brick, invert `vy`.
   - If the ball was historically to the left or right of the brick, invert `vx`.
3. Only process one brick collision per frame to avoid erratic multi-bounce physics.

## 7. Game Flow & States
- **Lives:** Start with 3 lives. Display in the top right.
- **Score:** Display in the top left.
- **STATE: START** -> Display "BREAKOUT" and "Press Space to Start". Ball rests on paddle.
- **STATE: PLAYING** -> Main loop actively updating physics and collisions.
- **STATE: WAITING/SERVE** -> After a life is lost, ball rests on the paddle, moving with it until the player presses Space to launch.
- **STATE: GAME OVER** -> Lives reach 0. Stop physics. Display "Game Over" and final score. "Press Space to Restart".
- **STATE: VICTORY** -> All bricks destroyed. Stop physics. Display "You Win!".

## 8. Audio (Web Audio API)
Browser security policies require audio to start only *after* a user interaction (like clicking or pressing Space to start). Implement a simple `AudioContext` synthesizer.
- **Paddle Hit:** Medium-high beep (e.g., 400Hz, square wave, 0.05 seconds).
- **Brick Destroyed:** High, short beep (e.g., 800Hz, square wave, 0.05 seconds). Higher rows can optionally have higher pitches.
- **Wall Hit:** Medium-low beep (e.g., 300Hz, square wave, 0.05 seconds).
- **Life Lost:** Descending "wa-wa-wa" tone or a low, long buzz (e.g., 150Hz dropping to 50Hz over 0.5s, sawtooth form).
