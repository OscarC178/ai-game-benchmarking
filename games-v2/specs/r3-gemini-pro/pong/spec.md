# Game Specification: Pong

## 1. Core Concept & Gameplay Overview
Pong is a minimalist 2D simulation of table tennis. The game consists of two paddles (vertical rectangles) on the left and right sides of the screen, and a ball (a small square) bouncing between them. 
The player controls the left paddle, moving it exclusively up and down to intercept the ball. The right paddle is controlled by the computer (AI). 
If the ball moves past a paddle off the left or right edge of the screen, the opposing side scores a point. The first side to reach 10 points wins the game.

## 2. Technical Constraints
- **Format:** A single, self-contained `index.html` file.
- **Assets:** NO external assets (no images, no CSS files, no sound files, no CDN links).
- **Rendering:** HTML5 `<canvas>` using the 2D context.
- **State Management:** Use `requestAnimationFrame` for the game loop, utilizing delta time (`dt`) for frame-rate-independent physics.
- **Audio:** Use the native Web Audio API (`AudioContext`) to synthesize simple beeps.

## 3. Visual Design & Layout
- **Canvas Size:** 800px width by 600px height. Positioned centrally in the browser window with a `#000000` (black) background.
- **Color Palette:** Strictly black (`#000000`) for the background, and white (`#FFFFFF`) for all game elements, text, and lines.
- **Net:** A dashed vertical line running down the exact center of the screen (x = 400).
- **Typography:** Use a standard monospace font (e.g., `font-family: 'Courier New', monospace;`).

## 4. Game Objects

### The Paddles
- **Dimensions:** Width: 15px | Height: 100px.
- **Positions:** 
  - Player (Left): x = 30, y = centered vertically.
  - AI (Right): x = 755 (800 - 30 margin - 15 width), y = centered vertically.
- **Movement:** Restricted to the Y-axis. Paddles CANNOT move beyond the top (y=0) or bottom (y=600) boundaries of the canvas.
- **Speed:** 400 pixels per second.

### The Ball
- **Dimensions:** Width: 15px | Height: 15px (rendered as a square).
- **Starting Position:** Exact center of the canvas (x = 392.5, y = 292.5).
- **Base Speed:** 400 pixels per second.
- **Max Speed:** 1000 pixels per second.

## 5. Controls
- **W Key (or Up Arrow):** Move the left paddle UP.
- **S Key (or Down Arrow):** Move the left paddle DOWN.
- **Spacebar / Enter:** Start the game from the title screen, or serve the ball after a point is scored.

## 6. AI Opponent (Right Paddle)
The computer controls the right paddle with a simple tracking algorithm.
- The AI paddle should attempt to match its center Y coordinate with the ball's center Y coordinate.
- **Crucial Limitation:** The AI must have a maximum movement speed (e.g., 350 pixels per second) that is slightly slower than the maximum speed of the ball. This ensures the AI is not unbeatable.
- The AI only needs to track the ball when the ball is moving towards the right side of the screen. When moving left, the AI can slowly return to the center.

## 7. Physics & Collision Mechanics

### Wall Collisions
- If the ball touches the top boundary (y <= 0) or bottom boundary (y + size >= 600), its Y-velocity inverts (`vy = -vy`).

### Score Triggers (Left & Right Boundaries)
- If the ball's X position goes below 0: The AI (Right) scores 1 point.
- If the ball's X position goes above 800: The Player (Left) scores 1 point.

### Paddle Collisions (CRITICAL GAMEPLAY MECHANIC)
Standard physics (angle of incidence = angle of reflection) makes the game boring. Instead, the bounce angle must be determined by **where the ball hits the paddle**.
1. **Intersection Detection:** Use basic AABB (Axis-Aligned Bounding Box) collision to check if the ball overlaps a paddle.
2. **Relative Intersection Point:** When a collision occurs, calculate where on the paddle the ball hit.
   - `intersectY = (paddle.y + (paddle.height / 2)) - (ball.y + (ball.height / 2))`
3. **Normalize Intersection:** Divide `intersectY` by half the paddle height.
   - `normalizedIntersectY = intersectY / (paddle.height / 2)`
   - This gives a value from `-1.0` (top of paddle) to `1.0` (bottom of paddle). It is `0` at the exact center.
4. **Calculate Bounce Angle:** Multiply the normalized value by a maximum bounce angle (e.g., 45 degrees, which is `PI / 4` radians).
   - `bounceAngle = normalizedIntersectY * MAX_BOUNCE_ANGLE`
5. **Apply New Velocity:**
   - Direction factor equals `1` if bouncing off the left paddle, and `-1` if bouncing off the right paddle.
   - `ball.vx = speed * Math.cos(bounceAngle) * direction`
   - `ball.vy = speed * -Math.sin(bounceAngle)`
6. **Speed Increase:** Every time the ball hits a paddle, increase the ball's `speed` by 5%, up to the `Max Speed`.

## 8. Game Flow & States

- **START SCREEN:** Display "PONG" in large text. Below it, "Press Space to Start".
- **SERVE STATE:** Once started, or after a point is scored, the ball rests in the center. Wait for the player to press Space. Upon serving, the ball moves toward the player who just conceded the point. (If it's the first serve, pick a random direction).
- **PLAYING STATE:** Main game loop active. Render dashed center line, scores, paddles, and ball. Update physics.
- **GAME OVER STATE:** Triggered when either Left or Right score reaches 10. Display "PLAYER WINS!" or "COMPUTER WINS!" based on the victor. Show "Press Space to Restart".

## 9. Audio Synth (Requirements)
Implement a simple `generateBeep(frequency, duration)` function using the Web Audio API. 
- **Paddle Hit:** High pitched beep (e.g., 600Hz, square wave, 0.1 seconds).
- **Wall Hit:** Medium pitched beep (e.g., 300Hz, square wave, 0.1 seconds).
- **Score:** Low, long tone (e.g., 150Hz, sawtooth wave, 0.5 seconds). 

*Note: Ensure the AudioContext is only initialized/resumed after the user's first interaction (e.g., pressing Space to start) to comply with browser autoplay policies.*
