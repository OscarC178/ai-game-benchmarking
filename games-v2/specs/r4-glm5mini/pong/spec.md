# Pong — Complete Game Specification

## Overview

Pong is a two-player table tennis simulation. Each player controls a vertical paddle on opposite sides of the screen. A ball bounces between them. Miss the ball, your opponent scores. First to a set score wins.

---

## Game Elements

### The Arena

- **Canvas size:** 800×600 pixels
- **Background:** Solid black (#000000)
- **Center line:** A dashed vertical line down the center of the screen, dividing left and right territories
  - Color: White (#FFFFFF) at ~30% opacity or gray (#666666)
  - Pattern: 20px dash, 10px gap
  - Line width: 2px

### The Paddles

- **Dimensions:** 15px wide × 100px tall
- **Color:** White (#FFFFFF)
- **Positions:**
  - Left paddle: 30px from the left edge, vertically centered at start
  - Right paddle: 30px from the right edge, vertically centered at start
- **Movement:** Vertical only (up/down)
- **Speed:** 8 pixels per frame
- **Boundary constraints:** Paddle cannot leave the canvas. Its top edge cannot go above y=0, bottom edge cannot go below y=600.
- **Collision box:** Exact rectangle. Ball bounces off the front face (the side facing the arena center).

### The Ball

- **Size:** 15×15 pixel square (classic Pong used a square, not a circle)
- **Color:** White (#FFFFFF)
- **Initial position:** Exact center of canvas (400, 300)
- **Initial velocity:** 
  - Served diagonally toward one player at random
  - Speed: 5 pixels per frame
  - Angle: Between 30° and 60° from horizontal (randomly left or right, randomly up or down)
- **Maximum speed:** 12 pixels per frame (ball cannot accelerate beyond this)

### The Score

- **Position:** Centered horizontally at the top of the screen
- **Format:** "[left score]   [right score]" with significant spacing between
- **Font:** Monospace, bold, ~48px
- **Color:** White (#FFFFFF)
- **Location:** Approximately 40-50px from the top, positioned above the center line
- **Initial values:** 0-0

---

## Controls

### Player 1 (Left Side)

- **W** — Move paddle up
- **S** — Move paddle down
- Keys are not case-sensitive (W and w both work)

### Player 2 (Right Side)

- **↑ (Up Arrow)** — Move paddle up  
- **↓ (Down Arrow)** — Move paddle down

### Game State Controls

- **Spacebar** — Start game (from title screen) / Pause or resume (during play)
- **R** — Restart game (from game over screen or during play)
- **Escape** — Return to title screen

---

## Physics & Collision

### Ball-Wall Collision

- **Top wall (y=0):** Ball reflects. Its vertical velocity reverses. Horizontal velocity unchanged.
- **Bottom wall (y=600):** Same as top. Ball reflects, vertical velocity reverses.
- **Important:** The ball's position should be corrected so it doesn't appear to pass through the wall. If the ball would move past the wall, clamp its position to the wall boundary before reversing velocity.

### Ball-Paddle Collision

A collision occurs when the ball's rectangle intersects a paddle's rectangle.

**On collision:**

1. **Position correction:** Move the ball back so it's just touching the paddle surface (prevent "sticking" or tunneling through the paddle).

2. **Horizontal velocity:** Always reverses. Ball bounces back toward the other side.

3. **Vertical velocity:** Influenced by where the ball hits the paddle.
   - If ball hits the **exact center** of the paddle: vertical velocity stays the same (straight horizontal bounce)
   - If ball hits **above center**: ball bounces upward (add upward vertical component)
   - If ball hits **below center**: ball bounces downward (add downward vertical component)
   - **Implementation:** Calculate the offset from paddle center as a ratio (-1 to +1), multiply by a max deflection angle, and set the vertical velocity accordingly.

4. **Speed increase:** Each paddle hit increases ball speed by 3%, up to the maximum speed. This creates escalating tension as the rally continues.

**Edge case — ball hits corner of paddle:** Treat this as a paddle hit. The ball should bounce. Angle can be extreme.

### Ball-Goal Detection

- **Left goal (x < 0):** Player 2 (right) scores
- **Right goal (x > 800):** Player 1 (left) scores

When the ball passes beyond the canvas edge:

1. Increment the appropriate score
2. Reset ball to center
3. Pause briefly (0.5-1 second) before serving to the player who was just scored on
4. Serve with same initial velocity rules (random angle, toward the player who conceded)

---

## Scoring & Win Condition

- **Points per goal:** 1
- **Winning score:** 11 points
- **Win condition:** A player reaches exactly 11 points
- **Victory margin:** None required (win 11-10 is valid)
- **On win:** Display "PLAYER 1 WINS" or "PLAYER 2 WINS" centered on screen. Show restart prompt.

---

## Game States

### 1. Title Screen

- Display: "PONG" in large text, centered
- Display: "Press SPACE to start"
- Display: "W/S for Player 1, ↑/↓ for Player 2"
- No gameplay occurs. Ball and paddles are hidden or static.
- Pressing Space transitions to Playing state.

### 2. Playing

- Normal gameplay
- Score displayed at top
- Pressing Space pauses the game (transitions to Paused state)

### 3. Paused

- All motion stops
- Display: "PAUSED" centered on screen
- Display: "Press SPACE to resume"
- Background dims (optional: draw semi-transparent black rectangle over game)
- Pressing Space returns to Playing state
- Pressing R restarts the game (scores reset to 0-0, ball to center)

### 4. Game Over

- Display: "PLAYER [1/2] WINS!" centered
- Display: "Press R to play again"
- Display: "Press ESC for title screen"
- Scores remain visible showing final result
- Pressing R starts a new game (reset to 0-0, Playing state)
- Pressing ESC returns to Title Screen

---

## Visual Polish (Nice to Have)

These are not required but add quality:

1. **Paddle hit flash:** Paddle briefly changes color (e.g., to a brighter white or yellow) when ball strikes it. Duration: ~100ms.

2. **Ball trail:** Previous 3-5 ball positions drawn at decreasing opacity to create motion blur effect.

3. **Score animation:** Score pulses briefly when it changes.

4. **Wall hit particle:** Small white dots briefly appear at ball-wall collision point.

---

## Technical Implementation Notes

### Game Loop

Use `requestAnimationFrame` for smooth 60fps gameplay. Each frame:

1. Clear canvas
2. Process input (update paddle positions if keys pressed)
3. Update ball position (add velocity to position)
4. Check and resolve collisions
5. Check for scoring
6. Draw all elements (background, center line, paddles, ball, score)
7. Check win condition

### Input Handling

- Track key state in an object: `keys = { w: false, s: false, ArrowUp: false, ArrowDown: false }`
- On `keydown` event: set `keys[key] = true`
- On `keyup` event: set `keys[key] = false`
- During game update: if key is true, move paddle accordingly
- This allows smooth, continuous movement while key is held

### Collision Detection

Use Axis-Aligned Bounding Box (AABB) intersection:

```
ball.x < paddle.x + paddle.width &&
ball.x + ball.size > paddle.x &&
ball.y < paddle.y + paddle.height &&
ball.y + ball.size > paddle.y
```

### Ball Velocity and Angle

Store ball velocity as separate x and y components. To serve at an angle:

1. Pick a random angle between 30° and 60°
2. Pick a random direction (left or right, up or down)
3. Convert to velocity:
   - `ball.vx = Math.cos(angle) * speed * directionX`
   - `ball.vy = Math.sin(angle) * speed * directionY`

### Speed Increase Per Hit

```
currentSpeed = Math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy);
newSpeed = Math.min(currentSpeed * 1.03, maxSpeed);
ratio = newSpeed / currentSpeed;
ball.vx *= ratio;
ball.vy *= ratio;
```

### Position Correction on Collision

When the ball collides with a paddle, it may have partially entered the paddle's space. Before reflecting:

**For left paddle collision:**
```
ball.x = paddle.x + paddle.width; // Place ball at paddle's right edge
```

**For right paddle collision:**
```
ball.x = paddle.x - ball.size; // Place ball at paddle's left edge
```

This prevents the ball from getting "stuck" inside the paddle or tunneling through on high speeds.

---

## Common Bugs to Avoid

1. **Ball passes through paddle at high speed:** The ball moves fast enough that in one frame it's before the paddle, and in the next frame it's past it — never intersecting. Solution: Use continuous collision detection or cap speed, or use a "goalie" check: if ball crossed the paddle's x-plane this frame, check if its y-position was within the paddle's y-range at the crossing point.

2. **Ball gets stuck in paddle:** Position correction (see above) prevents this.

3. **Paddle can leave the screen:** Clamp paddle.y so `paddle.y >= 0` and `paddle.y + paddle.height <= canvas.height`.

4. **Keys "stick" when window loses focus:** Add a `blur` event listener to the window that resets all key states to false.

5. **Ball bounces at wrong angle after paddle hit:** Ensure you're calculating the hit position relative to the paddle's *center*, not its top edge. The math should be: `offset = (ball.y + ball.size/2) - (paddle.y + paddle.height/2)` which gives you -0.5 to +0.5 range (normalize to -1 to +1).

---

## Minimum Viable Product Checklist

A complete Pong implementation must have:

- [ ] Canvas rendering at 800×600
- [ ] Two controllable paddles with correct controls
- [ ] Ball that moves and bounces off walls and paddles
- [ ] Ball speed increases with each paddle hit
- [ ] Scoring system (displayed on screen)
- [ ] Win condition at 11 points
- [ ] Game states: Title → Playing → Paused → Game Over
- [ ] Space to start/pause, R to restart
- [ ] Ball served toward the player who was scored on
- [ ] No external dependencies (all code in one HTML file)

---

## Reference: Control Summary

| Key | Action |
|-----|--------|
| W | Player 1 paddle up |
| S | Player 1 paddle down |
| ↑ | Player 2 paddle up |
| ↓ | Player 2 paddle down |
| Space | Start / Pause / Resume |
| R | Restart game |
| Escape | Return to title |

---

End of specification.
