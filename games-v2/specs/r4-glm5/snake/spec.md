# Snake — Complete Game Specification

## Overview

Snake is a single-player game where you control a growing snake on a grid. Eat food to grow longer. Avoid hitting the walls or your own body. The game ends when you collide with a wall or yourself. Your score is based on how much food you eat.

---

## Game Elements

### The Arena

- **Canvas size:** 600×600 pixels
- **Grid size:** 20×20 cells (each cell is 30×30 pixels)
- **Background:** Solid black (#000000) or very dark gray (#111111)
- **Grid lines (optional):** Faint grid pattern to help visualize cells
  - Color: #222222
  - Line width: 1px

### The Snake

- **Starting length:** 3 segments
- **Starting position:** Center of the grid (approximately cells 10, 10)
- **Starting direction:** Moving right
- **Segment size:** One grid cell (30×30 pixels)
- **Color:**
  - Head: Bright green (#00FF00) or slightly different shade (#44FF44)
  - Body: Green (#00CC00) or gradient from bright (near head) to darker (near tail)
- **Movement:** Moves one cell per game tick in the current direction
- **Growth:** When eating food, add one segment to the head. The tail does not advance on that tick, causing the snake to grow by one cell.

### The Food

- **Size:** One grid cell (30×30 pixels)
- **Color:** Red (#FF0000) or bright red (#FF3333)
- **Shape:** Filled square (matching snake segments) OR a filled circle
- **Position:** Randomly placed on any empty cell (not occupied by the snake)
- **Respawn:** When eaten, a new food appears immediately at a random empty location

### The Score

- **Position:** Top-left corner of the canvas
- **Format:** "Score: [number]"
- **Font:** Sans-serif, 24px, bold
- **Color:** White (#FFFFFF)
- **Initial value:** 0
- **Points per food:** 10 points

---

## Grid & Coordinate System

The game uses a logical grid for all game logic. Visual rendering translates grid coordinates to pixel positions.

- **Grid coordinates:** 0-indexed, from (0, 0) at top-left to (19, 19) at bottom-right
- **Pixel conversion:** `pixelX = gridX * cellSize`, `pixelY = gridY * cellSize`
- **Snake representation:** An array of grid coordinates, ordered from head to tail
  - Example: `snake = [{x: 10, y: 10}, {x: 9, y: 10}, {x: 8, y: 10}]`
  - First element is always the head
  - Last element is always the tail

---

## Movement Logic

### Direction

The snake always moves. It cannot stop. Valid directions are:

- **UP:** y decreases (moving toward top of screen)
- **DOWN:** y increases (moving toward bottom of screen)
- **LEFT:** x decreases (moving toward left of screen)
- **RIGHT:** x increases (moving toward right of screen)

### Changing Direction

The player can change direction by pressing arrow keys or WASD.

**Critical rule:** The snake cannot reverse direction into itself. 

- If moving UP, the player cannot change to DOWN
- If moving DOWN, the player cannot change to UP
- If moving LEFT, the player cannot change to RIGHT
- If moving RIGHT, the player cannot change to LEFT

**Implementation:** On key press, check if the new direction is opposite to current direction. If it is, ignore the input.

**Input buffering (recommended):** If the player presses two keys quickly between ticks (e.g., UP then LEFT while moving RIGHT), the second key may be ignored or misinterpreted. Solution: Buffer one pending direction change. Apply it on the next tick, then clear the buffer.

### The Move Tick

Every game tick (see Speed section), the snake moves:

1. **Calculate new head position:** Based on current direction
   ```
   newHead = {
     x: snake[0].x + direction.x,
     y: snake[0].y + direction.y
   }
   ```

2. **Check for collisions** (see Collision section)

3. **If no collision:**
   - Add new head to front of snake array: `snake.unshift(newHead)`
   - If food was eaten this tick: do NOT remove tail (snake grows)
   - If no food eaten: remove tail: `snake.pop()`

---

## Collision Detection

### Wall Collision

The snake dies if its head moves outside the grid boundaries.

**Death condition:**
- `head.x < 0` OR
- `head.x >= 20` OR
- `head.y < 0` OR
- `head.y >= 20`

### Self Collision

The snake dies if its head moves into any cell occupied by its own body.

**Death condition:** The new head position equals any body segment (excluding the current head, which will move).

**Implementation:**
```
for (let i = 0; i < snake.length; i++) {
  if (newHead.x === snake[i].x && newHead.y === snake[i].y) {
    // Collision! Game over.
  }
}
```

**Note:** The tail segment is about to move (unless eating), so technically the head can move into where the tail currently is. However, for simplicity and common convention, check against all segments. If you want the "tail is safe" behavior, exclude the last segment from the check.

### Food Collision

The snake eats food when its head moves into the cell containing food.

**On food collision:**
1. Increment score by 10
2. Do NOT remove the tail this tick (snake grows by 1)
3. Spawn new food at a random empty cell
4. Optionally increase game speed slightly

---

## Food Spawning

When food is eaten or at game start, spawn new food:

1. Create a list of all empty cells (not occupied by the snake)
2. If no empty cells exist, the player has won (entire grid filled)
3. Randomly select one empty cell from the list
4. Place food at that cell

**Implementation:**
```
function spawnFood() {
  const emptyCells = [];
  for (let x = 0; x < 20; x++) {
    for (let y = 0; y < 20; y++) {
      const isOccupied = snake.some(segment => segment.x === x && segment.y === y);
      if (!isOccupied) {
        emptyCells.push({x, y});
      }
    }
  }
  if (emptyCells.length === 0) {
    // Victory! Snake fills entire grid.
    return null;
  }
  const randomIndex = Math.floor(Math.random() * emptyCells.length);
  food = emptyCells[randomIndex];
}
```

---

## Speed & Difficulty

### Base Speed

The game runs at a fixed tick rate, not tied to frame rate.

- **Initial tick interval:** 150ms (approximately 6.7 moves per second)
- **Frame rate:** 60fps for smooth rendering (but snake only moves on ticks)

### Speed Increase (Optional)

The game can become progressively faster as the snake grows:

- Every 5 food eaten: decrease tick interval by 10ms
- Minimum tick interval: 60ms (don't go faster or game becomes unplayable)

**Alternative:** Keep speed constant. This makes for a more relaxed, casual game.

---

## Controls

| Key | Action |
|-----|--------|
| ↑ or W | Move up |
| ↓ or S | Move down |
| ← or A | Move left |
| → or D | Move right |
| Space | Pause / Resume |
| R | Restart game |
| Escape | Return to title screen |

**Key handling notes:**
- Both arrow keys and WASD should work
- Keys should be case-insensitive (W and w both work)
- Opposite direction inputs are ignored (snake can't reverse into itself)

---

## Game States

### 1. Title Screen

**Display:**
- "SNAKE" in large text, centered
- "Press SPACE to start"
- "Arrow keys or WASD to move"
- Optional: High score display

**Behavior:**
- No gameplay
- Pressing Space transitions to Playing state

### 2. Playing

**Display:**
- Snake moving on grid
- Food on grid
- Score at top-left
- Optional: current length or level

**Behavior:**
- Normal gameplay
- Game ticks at regular intervals
- Pressing Space pauses the game (transitions to Paused state)

### 3. Paused

**Display:**
- Game frozen in current state
- "PAUSED" text centered on screen
- "Press SPACE to resume"
- Background dimmed (semi-transparent black overlay)

**Behavior:**
- No movement, no game ticks
- Pressing Space returns to Playing state
- Pressing R restarts the game

### 4. Game Over

**Display:**
- "GAME OVER" text centered
- Final score: "Score: [number]"
- "Press R to play again"
- "Press ESC for title screen"
- Optional: "High Score: [number]" if this is a new high score

**Behavior:**
- No gameplay
- Pressing R restarts the game (resets score, snake length, position)
- Pressing ESC returns to Title Screen

### 5. Victory (Optional)

**Trigger:** Snake fills the entire 20×20 grid (400 segments)

**Display:**
- "YOU WIN!" or "PERFECT SCORE!"
- Final score: 4000 points (400 food × 10 points)
- "Press R to play again"

This is extremely difficult to achieve but provides a true win condition.

---

## Visual Polish (Recommended)

### Snake Rendering

1. **Rounded corners:** Each segment drawn with slightly rounded corners for a smoother appearance.

2. **Gradient body:** Body segments gradually darken from head to tail, creating depth.

3. **Head distinction:** The head has eyes or a slightly different shape to show direction.

   **Simple eye implementation:**
   - Draw two small dots on the head segment
   - Position based on direction:
     - Moving right: dots on the right side
     - Moving left: dots on the left side
     - Moving up: dots on the top side
     - Moving down: dots on the bottom side

4. **Smooth movement (advanced):** Instead of jumping cell-to-cell, interpolate position over multiple frames. This requires tracking both grid position and pixel position.

### Food Rendering

1. **Pulse animation:** Food slowly pulses (grows and shrinks slightly) to draw attention.

2. **Sparkle:** Small animated highlights on food.

### Death Animation

When the snake dies, briefly show the collision:
- Flash the snake red
- Or display a small explosion/particle effect at the collision point
- Delay 0.5 seconds before showing Game Over screen

---

## Technical Implementation Notes

### Game Loop Structure

Use `requestAnimationFrame` for rendering at 60fps. Use `setInterval` or timestamp comparison for game ticks.

```
let lastTickTime = 0;
const tickInterval = 150; // ms

function gameLoop(currentTime) {
  requestAnimationFrame(gameLoop);
  
  // Always render
  render();
  
  // Only update game logic on tick
  if (currentTime - lastTickTime >= tickInterval) {
    lastTickTime = currentTime;
    update();
  }
}
```

### Direction Storage

Store direction as an object with x and y components:

```
const directions = {
  UP:    { x: 0,  y: -1 },
  DOWN:  { x: 0,  y: 1  },
  LEFT:  { x: -1, y: 0  },
  RIGHT: { x: 1,  y: 0  }
};

let currentDirection = directions.RIGHT;
```

This makes movement calculation clean:
```
newHead.x = head.x + currentDirection.x;
newHead.y = head.y + currentDirection.y;
```

### Opposite Direction Check

```
function isOppositeDirection(newDir, currentDir) {
  return newDir.x === -currentDir.x && newDir.y === -currentDir.y;
}
```

### High Score Persistence (Optional)

Store high score in localStorage:

```
// Save
localStorage.setItem('snakeHighScore', highScore);

// Load
const saved = localStorage.getItem('snakeHighScore');
const highScore = saved ? parseInt(saved, 10) : 0;
```

---

## Common Bugs to Avoid

1. **Snake can reverse into itself:** If moving RIGHT and player presses LEFT quickly, the snake reverses. Prevent by checking if new direction is opposite to current direction.

2. **Food spawns on snake:** Food placement must check all snake segments. A naive random placement might occasionally overlap.

3. **Multiple direction inputs per tick:** If player presses UP then LEFT before a tick, the snake might try to go LEFT while moving DOWN (if UP was processed), causing an illegal reversal. Solution: Only buffer one pending direction change per tick.

4. **Game speed tied to frame rate:** If you move the snake every frame instead of on a fixed tick, the game speed will vary with the player's hardware. Use a timer or timestamp comparison.

5. **Self-collision on first move:** At game start with a 3-segment snake moving right, the head at x=10 can't move left anyway, but ensure your collision check doesn't flag the initial state.

6. **No victory condition:** Technically, if the snake fills the entire grid, there's nowhere to spawn food. Handle this edge case gracefully.

---

## Minimum Viable Product Checklist

A complete Snake implementation must have:

- [ ] Canvas rendering at 600×600
- [ ] 20×20 grid system
- [ ] Snake that starts at 3 segments, centered, moving right
- [ ] Arrow keys OR WASD controls (supporting both is better)
- [ ] Snake cannot reverse direction
- [ ] Food that spawns randomly on empty cells
- [ ] Snake grows when eating food
- [ ] Score display and tracking (10 points per food)
- [ ] Wall collision detection (game over)
- [ ] Self collision detection (game over)
- [ ] Game states: Title → Playing → Game Over
- [ ] Pause functionality (Space key)
- [ ] Restart functionality (R key)
- [ ] Fixed tick rate (not frame-dependent)
- [ ] No external dependencies (all code in one HTML file)

---

## Quick Reference

| Element | Value |
|---------|-------|
| Canvas | 600×600 px |
| Grid | 20×20 cells |
| Cell size | 30×30 px |
| Starting length | 3 segments |
| Starting position | Center, moving right |
| Points per food | 10 |
| Initial tick speed | 150ms |
| Colors | Snake: green, Food: red, Background: black |

---

End of specification.
