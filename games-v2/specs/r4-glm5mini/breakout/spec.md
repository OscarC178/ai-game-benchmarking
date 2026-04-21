# Breakout — Complete Game Specification

## Overview

Breakout is a single-player game where you control a paddle at the bottom of the screen. Use the paddle to bounce a ball upward to destroy rows of bricks. Clear all bricks to win. Lose the ball (let it fall below the paddle) and you lose a life. Clear all bricks or lose all lives to end the game.

---

## Game Elements

### The Arena

- **Canvas size:** 800×600 pixels
- **Background:** Solid black (#000000) or very dark (#111111)
- **Wall boundaries:** The top, left, and right edges of the canvas are solid walls. The ball bounces off them. The bottom edge is open — if the ball passes below the canvas, it's lost.

### The Paddle

- **Dimensions:** 120px wide × 15px tall
- **Color:** White (#FFFFFF) or light gray (#CCCCCC)
- **Position:** Horizontally centered, 30px from the bottom of the canvas
- **Movement:** Horizontal only (left/right)
- **Speed:** 8 pixels per frame (when key held)
- **Boundary constraints:** Paddle cannot leave the canvas
  - Left edge: `paddle.x >= 0`
  - Right edge: `paddle.x + paddle.width <= 800`
- **Collision:** Ball bounces off the top surface of the paddle

### The Ball

- **Size:** 12×12 pixel square (classic) OR 10px radius circle (modern)
- **Color:** White (#FFFFFF)
- **Initial position:** Centered horizontally, just above the paddle (approximately y = 530)
- **Initial velocity:** Launched upward at an angle
  - Speed: 6 pixels per frame
  - Angle: Between 45° and 60° from horizontal, randomly left or right
- **Maximum speed:** 10 pixels per frame
- **Minimum speed:** 4 pixels per frame (ball should never move too slowly)

### The Bricks

- **Individual brick size:** 75px wide × 25px tall
- **Total brick layout:** 10 columns × 6 rows = 60 bricks
- **Positioning:**
  - First brick row starts 50px from the top of the canvas
  - Bricks span horizontally from x = 25 to x = 775 (with small gaps)
  - No gaps between bricks in a row (touching), OR small 2-3px gaps for visual separation
- **Colors by row (top to bottom):**
  - Row 1: Red (#FF0000) — 70 points
  - Row 2: Orange (#FF8800) — 60 points
  - Row 3: Yellow (#FFFF00) — 50 points
  - Row 4: Green (#00FF00) — 40 points
  - Row 5: Blue (#0088FF) — 30 points
  - Row 6: Purple (#8800FF) — 20 points
- **Hit behavior:** Most bricks are destroyed in one hit. Optionally, some bricks require multiple hits (see Advanced Variations).
- **Spacing (if using gaps):** 2-3 pixels between bricks horizontally and vertically

### The Score

- **Position:** Top-left corner
- **Format:** "Score: [number]"
- **Font:** Sans-serif, 20px
- **Color:** White (#FFFFFF)
- **Points:** Based on brick color destroyed (see brick colors above)

### Lives

- **Initial lives:** 3
- **Display:** Top-right corner, shown as text "Lives: 3" or as graphical icons (small paddle shapes or hearts)
- **Loss condition:** Ball falls below the paddle (passes y = 600)
- **On life loss:**
  - Reset ball to starting position above paddle
  - Reset paddle to center
  - Brief pause before ball can be launched again

---

## Controls

| Key | Action |
|-----|--------|
| ← or A | Move paddle left |
| → or D | Move paddle right |
| Space | Launch ball / Pause game |
| R | Restart game |
| Escape | Return to title screen |

**Control details:**
- Paddle moves smoothly while key is held
- Both arrow keys and WASD work
- At game start and after losing a life, the ball sits on the paddle. Press Space to launch it.
- Space during gameplay pauses the game

---

## Ball Physics

### Wall Collisions

- **Top wall (y = 0):** Ball reflects. Vertical velocity reverses. `ball.vy = -ball.vy`
- **Left wall (x = 0):** Ball reflects. Horizontal velocity reverses. `ball.vx = -ball.vx`
- **Right wall (x = 800):** Ball reflects. Horizontal velocity reverses.

**Position correction:** After reflection, ensure the ball isn't stuck inside the wall:
- If hit left wall: `ball.x = 0`
- If hit right wall: `ball.x = 800 - ball.width` (or `800 - ball.radius * 2`)
- If hit top wall: `ball.y = 0`

### Paddle Collision

The ball bounces off the top surface of the paddle.

**Collision condition:** Ball's bottom edge intersects paddle's top edge, and ball is within paddle's horizontal bounds.

**Reflection behavior:** The angle of reflection depends on where the ball hits the paddle.

- **Center hit:** Ball bounces straight up (vertical)
- **Left edge hit:** Ball bounces sharply to the left
- **Right edge hit:** Ball bounces sharply to the right
- **Gradual angle:** Angle varies smoothly based on hit position

**Implementation:**
1. Calculate hit position as a ratio from -1 (leftmost) to +1 (rightmost):
   ```
   hitRatio = ((ball.x + ball.width/2) - paddle.x) / paddle.width;
   hitRatio = hitRatio * 2 - 1; // Convert 0-1 to -1 to +1
   ```

2. Clamp hitRatio to [-1, 1] (in case ball hits edge)

3. Calculate new angle:
   ```
   // Maximum deflection angle: 60° from vertical
   maxAngle = Math.PI / 3; // 60° in radians
   angle = hitRatio * maxAngle;
   ```

4. Set new velocity:
   ```
   speed = Math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy);
   ball.vx = Math.sin(angle) * speed;
   ball.vy = -Math.cos(angle) * speed; // Always upward (negative)
   ```

**Position correction:** Move ball above paddle to prevent sticking:
```
ball.y = paddle.y - ball.height; // or paddle.y - ball.radius * 2
```

### Brick Collisions

**Detection:** AABB collision between ball and each brick.

**Determine collision side:** Figure out which side of the brick the ball hit, to bounce correctly.

**Simplified approach:** Check ball velocity direction:
- If ball is moving primarily horizontally (`|vx| > |vy|`), reverse horizontal velocity
- If ball is moving primarily vertically, reverse vertical velocity

**Better approach (recommended):** Calculate penetration depth on each axis and bounce on the axis with smaller penetration.

```
// Calculate overlap on each axis
overlapLeft = (ball.x + ball.width) - brick.x;
overlapRight = (brick.x + brick.width) - ball.x;
overlapTop = (ball.y + ball.height) - brick.y;
overlapBottom = (brick.y + brick.height) - ball.y;

// Find minimum overlap
minOverlapX = Math.min(overlapLeft, overlapRight);
minOverlapY = Math.min(overlapTop, overlapBottom);

if (minOverlapX < minOverlapY) {
  // Horizontal collision - reverse vx
  ball.vx = -ball.vx;
  // Position correction
  if (overlapLeft < overlapRight) {
    ball.x = brick.x - ball.width;
  } else {
    ball.x = brick.x + brick.width;
  }
} else {
  // Vertical collision - reverse vy
  ball.vy = -ball.vy;
  // Position correction
  if (overlapTop < overlapBottom) {
    ball.y = brick.y - ball.height;
  } else {
    ball.y = brick.y + brick.height;
  }
}
```

**On brick hit:**
1. Destroy the brick (remove from array)
2. Add brick's point value to score
3. Reverse ball velocity based on collision side
4. Apply position correction

### Speed Increase

The ball can gradually speed up to maintain challenge:

- **Per brick hit:** Increase speed by 0.5%, up to maximum
- **Per paddle hit:** Optional small speed increase
- **Maximum speed:** 10 pixels per frame

```
speed = Math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy);
if (speed < maxSpeed) {
  newSpeed = speed * 1.005;
  ratio = newSpeed / speed;
  ball.vx *= ratio;
  ball.vy *= ratio;
}
```

---

## Brick Layout Details

### Standard Layout (60 bricks)

```
Row 1 (y=50):  10 red bricks    - 70 pts each
Row 2 (y=75):  10 orange bricks - 60 pts each
Row 3 (y=100): 10 yellow bricks - 50 pts each
Row 4 (y=125): 10 green bricks  - 40 pts each
Row 5 (y=150): 10 blue bricks   - 30 pts each
Row 6 (y=175): 10 purple bricks - 20 pts each
```

### Brick Data Structure

Store bricks as an array of objects:

```
bricks = [
  { x: 25, y: 50, width: 75, height: 25, color: "#FF0000", points: 70, alive: true },
  { x: 102, y: 50, width: 75, height: 25, color: "#FF0000", points: 70, alive: true },
  // ... and so on
];
```

Or as a 2D array (row, column) for easier layout management.

### Generating Brick Positions

```
const brickRows = 6;
const brickCols = 10;
const brickWidth = 75;
const brickHeight = 25;
const brickPadding = 0; // or 2-3 for gaps
const offsetTop = 50;
const offsetLeft = 25;

const brickColors = [
  { color: "#FF0000", points: 70 },
  { color: "#FF8800", points: 60 },
  { color: "#FFFF00", points: 50 },
  { color: "#00FF00", points: 40 },
  { color: "#0088FF", points: 30 },
  { color: "#8800FF", points: 20 }
];

bricks = [];
for (let row = 0; row < brickRows; row++) {
  for (let col = 0; col < brickCols; col++) {
    bricks.push({
      x: offsetLeft + col * (brickWidth + brickPadding),
      y: offsetTop + row * (brickHeight + brickPadding),
      width: brickWidth,
      height: brickHeight,
      color: brickColors[row].color,
      points: brickColors[row].points,
      alive: true
    });
  }
}
```

---

## Game States

### 1. Title Screen

**Display:**
- "BREAKOUT" in large text, centered
- "Press SPACE to start"
- "← → or A D to move paddle"
- Optional: High score

**Behavior:**
- No gameplay
- Pressing Space starts the game

### 2. Playing — Ball on Paddle

After game start or losing a life, the ball sits on the paddle.

**Display:**
- Paddle at center bottom
- Ball positioned just above paddle center
- Score and lives displayed
- Bricks displayed

**Behavior:**
- Paddle can move left/right
- Ball follows paddle horizontally (ball.x = paddle.x + paddle.width/2 - ball.width/2)
- Pressing Space launches the ball upward

### 3. Playing — Ball in Motion

**Display:**
- Same as above, ball moving

**Behavior:**
- Ball bounces off walls, paddle, and bricks
- Normal gameplay
- Pressing Space pauses the game

### 4. Paused

**Display:**
- Game frozen
- "PAUSED" text centered
- "Press SPACE to resume"
- Semi-transparent black overlay

**Behavior:**
- Pressing Space resumes game
- Pressing R restarts

### 5. Game Over

**Trigger:** Lives reach 0

**Display:**
- "GAME OVER" centered
- Final score: "Score: [number]"
- "Press R to play again"
- Optional: "High Score: [number]"

**Behavior:**
- Pressing R restarts game
- Pressing ESC returns to title screen

### 6. Victory

**Trigger:** All bricks destroyed

**Display:**
- "YOU WIN!" or "ALL BRICKS CLEARED!"
- Final score
- "Press R to play again"

**Behavior:**
- Same as game over

---

## Advanced Variations (Optional)

### Multi-Hit Bricks

Some bricks require multiple hits to destroy:

- **Silver bricks:** 2 hits to destroy, appear in row 2
- **Gold bricks:** 3 hits to destroy, appear in row 1
- **Implementation:** Add `hitsRemaining` property to brick object

### Power-Ups

Occasionally, destroying a brick releases a power-up that falls downward:

| Power-up | Effect | Duration |
|----------|--------|----------|
| Expand | Paddle becomes wider (180px) | 20 seconds or until lost |
| Shrink | Paddle becomes narrower (60px) | 15 seconds |
| Slow | Ball moves at half speed | 10 seconds |
| Multi-ball | Spawn 2 additional balls | Until all balls lost |
| Extra life | +1 life | Permanent |

**Power-up implementation:**
- Random chance (5-10%) to spawn when brick destroyed
- Falls at 3 pixels per frame
- Caught if paddle touches it
- Missed if it falls below screen

### Level Progression

After clearing all bricks, advance to a new level with:

- Different brick patterns
- More bricks
- Faster ball speed
- Harder brick types (more multi-hit bricks)

---

## Technical Implementation Notes

### Game Loop

```
function gameLoop(timestamp) {
  requestAnimationFrame(gameLoop);
  
  update();
  render();
}
```

### Input Handling

```
const keys = { left: false, right: false };

document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') keys.left = true;
  if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') keys.right = true;
  if (e.key === ' ') handleSpace();
});

document.addEventListener('keyup', (e) => {
  if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') keys.left = false;
  if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') keys.right = false;
});

// In update():
if (keys.left) paddle.x -= paddleSpeed;
if (keys.right) paddle.x += paddleSpeed;
```

### Collision Detection Optimization

With 60 bricks, checking every brick every frame is fine. For larger brick counts, use spatial partitioning or only check bricks near the ball.

### Ball-Paddle Collision (Detailed)

```
function checkPaddleCollision() {
  if (ball.y + ball.height >= paddle.y &&
      ball.y <= paddle.y + paddle.height &&
      ball.x + ball.width >= paddle.x &&
      ball.x <= paddle.x + paddle.width &&
      ball.vy > 0) { // Only if ball moving downward
    
    // Calculate hit position (-1 to +1)
    const hitPos = ((ball.x + ball.width/2) - (paddle.x + paddle.width/2)) / (paddle.width/2);
    
    // Calculate angle (max 60° from vertical)
    const maxAngle = Math.PI / 3;
    const angle = hitPos * maxAngle;
    
    // Set new velocity
    const speed = Math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy);
    ball.vx = Math.sin(angle) * speed;
    ball.vy = -Math.abs(Math.cos(angle) * speed); // Always upward
    
    // Position correction
    ball.y = paddle.y - ball.height;
  }
}
```

---

## Common Bugs to Avoid

1. **Ball stuck in paddle:** If ball penetrates paddle before collision check, it may get stuck. Always do position correction after bounce.

2. **Ball passes through bricks at high speed:** At high speeds, ball may "tunnel" through thin bricks. Solution: Check for collision along the ball's path, not just at its final position. Or cap ball speed.

3. **Double brick destruction:** If collision check runs twice before ball leaves brick area, brick might be destroyed twice (causing errors). Check `brick.alive` before processing collision, set to false immediately.

4. **Ball bounces incorrectly off brick corners:** The penetration-depth approach handles this correctly. Simple velocity reversal can cause wrong bounces.

5. **Paddle can leave screen:** Clamp paddle position to canvas bounds every frame.

6. **Ball moves before player launches:** Ensure ball is in "on paddle" state and only launches when Space is pressed.

---

## Minimum Viable Product Checklist

A complete Breakout implementation must have:

- [ ] Canvas rendering at 800×600
- [ ] Controllable paddle (left/right movement, arrow keys or WASD)
- [ ] Ball that bounces off walls, paddle, and bricks
- [ ] Ball launches from paddle when Space pressed
- [ ] 60 bricks in 6 rows with different colors and point values
- [ ] Bricks destroyed on ball hit
- [ ] Score tracking and display
- [ ] Lives system (start with 3, lose one when ball falls)
- [ ] Ball angle varies based on paddle hit position
- [ ] Win condition (all bricks destroyed)
- [ ] Lose condition (all lives lost)
- [ ] Game states: Title → Playing → Paused → Game Over / Victory
- [ ] Pause (Space) and Restart (R) functionality
- [ ] No external dependencies (all code in one HTML file)

---

## Quick Reference

| Element | Value |
|---------|-------|
| Canvas | 800×600 px |
| Paddle | 120×15 px, 30px from bottom |
| Ball | 12×12 px square or 10px radius circle |
| Bricks | 75×25 px each, 10×6 grid |
| Total bricks | 60 |
| Lives | 3 |
| Ball initial speed | 6 px/frame |
| Ball max speed | 10 px/frame |
| Points per brick | 20-70 based on color |

---

End of specification.
