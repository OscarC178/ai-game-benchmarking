# Tetris — Complete Game Specification

## Overview

Tetris is a single-player puzzle game. Tetrominoes (shapes made of 4 squares) fall from the top of a vertical well. You control where they land by moving them horizontally and rotating them. When pieces land, they become part of a stack at the bottom. Complete horizontal lines are cleared, earning points. The game speeds up as you progress. If the stack reaches the top of the well, the game ends.

---

## Game Elements

### The Well (Playfield)

- **Grid size:** 10 columns × 20 visible rows (standard Tetris dimensions)
- **Cell size:** 30×30 pixels
- **Canvas dimensions:** 300×600 pixels for the well, plus space for UI (score, next piece, etc.)
- **Total canvas:** Approximately 500×650 pixels (well + sidebar for UI)
- **Background:** Solid black (#000000) or very dark gray (#111111)
- **Grid lines:** Optional faint lines to show grid structure
  - Color: #222222 or similar
  - Line width: 1px

### The Tetrominoes (7 Shapes)

Each piece is made of 4 squares arranged in a specific pattern. Each piece has a distinct color.

| Piece | Name | Shape | Color | Standard Color Code |
|-------|------|-------|-------|---------------------|
| I | Straight | ████ (4 in a row) | Cyan | #00FFFF |
| O | Square | ██<br>██ (2×2 block) | Yellow | #FFFF00 |
| T | T-shape | ███<br>&nbsp;█ (T formation) | Purple | #AA00FF |
| S | S-shape | &nbsp;██<br>██&nbsp; (S curve) | Green | #00FF00 |
| Z | Z-shape | ██<nbsp;<br>&nbsp;██ (Z curve) | Red | #FF0000 |
| J | J-shape | █<br>███ (L mirrored) | Blue | #0000FF |
| L | L-shape | &nbsp;&nbsp;█<br>███ (L shape) | Orange | #FF8800 |

### Piece Representation

Each piece has a "home position" defined as a 4×4 grid, with cells marked as filled (1) or empty (0). This makes rotation math easier.

**I-piece:**
```
0 0 0 0
1 1 1 1
0 0 0 0
0 0 0 0
```

**O-piece:**
```
0 0 0 0
0 1 1 0
0 1 1 0
0 0 0 0
```

**T-piece:**
```
0 0 0 0
1 1 1 0
0 1 0 0
0 0 0 0
```

**S-piece:**
```
0 0 0 0
0 1 1 0
1 1 0 0
0 0 0 0
```

**Z-piece:**
```
0 0 0 0
1 1 0 0
0 1 1 0
0 0 0 0
```

**J-piece:**
```
0 0 0 0
1 0 0 0
1 1 1 0
0 0 0 0
```

**L-piece:**
```
0 0 0 0
0 0 1 0
1 1 1 0
0 0 0 0
```

### Piece Spawn Position

- **Horizontal:** Centered in the well (columns 3-6, or piece-specific centering)
- **Vertical:** Top of the well, row 0-1 (pieces spawn partially above the visible area is acceptable)
- **Standard spawn:** Piece appears with its top at row 0 (or row -1 for I-piece with its horizontal orientation)

---

## Controls

| Key | Action |
|-----|--------|
| ← or A | Move piece left |
| → or D | Move piece right |
| ↓ or S | Soft drop (accelerate downward) |
| ↑ or X | Rotate clockwise |
| Z or Ctrl | Rotate counter-clockwise |
| Space | Hard drop (instant drop) |
| C or Shift | Hold piece (swap with held piece) |
| P or Escape | Pause game |
| R | Restart game |

**Control details:**
- Left/Right movement: One cell per key press. If key is held, auto-repeat after initial delay (DAS — Delayed Auto Shift).
- DAS settings (recommended): 170ms initial delay, then 50ms between repeats.
- Soft drop: Piece falls faster while ↓ is held (typically 10-20× normal fall speed).
- Hard drop: Piece instantly falls to the lowest valid position and locks in place.
- Rotation: Both directions should be supported (180° rotation is optional but nice).

---

## Game Mechanics

### Falling

The active piece falls automatically at regular intervals.

**Fall speed by level:**

| Level | Frames per drop (60fps) | Seconds per drop |
|-------|------------------------|------------------|
| 1 | 48 | 0.8 |
| 2 | 43 | 0.72 |
| 3 | 38 | 0.63 |
| 4 | 33 | 0.55 |
| 5 | 28 | 0.47 |
| 6 | 23 | 0.38 |
| 7 | 18 | 0.30 |
| 8 | 13 | 0.22 |
| 9 | 8 | 0.13 |
| 10 | 6 | 0.10 |
| 11-12 | 5 | 0.08 |
| 13-15 | 4 | 0.07 |
| 16-18 | 3 | 0.05 |
| 19-28 | 2 | 0.03 |
| 29+ | 1 | 0.02 |

**Simplified progression:** Each level, decrease time per drop by ~10%, with a minimum of 1-2 frames.

### Locking

When a piece cannot fall any further (would collide with stack or floor), it locks in place after a brief delay.

**Lock delay:** 0.5 seconds (typical). During this delay:
- Player can still move and rotate the piece
- If the piece can fall again (after a move), reset the lock delay
- After lock delay expires, piece becomes part of the stack

**Simple alternative:** Piece locks immediately when it cannot fall further (classic behavior, less forgiving).

### Line Clearing

When a horizontal row becomes completely filled with blocks:
1. That row is marked for clearing
2. After a brief visual effect (flash, fade, or explosion), the row is removed
3. All rows above it shift down by one position
4. Multiple lines can clear simultaneously (up to 4 at once)

**Clear animation:** Lines flash white or brighten briefly (100-200ms) before disappearing.

### Scoring

Points are awarded based on lines cleared at once:

| Lines Cleared | Name | Points (base) |
|---------------|------|---------------|
| 1 | Single | 100 × level |
| 2 | Double | 300 × level |
| 3 | Triple | 500 × level |
| 4 | Tetris | 800 × level |

**Additional scoring:**
- Soft drop: 1 point per cell dropped
- Hard drop: 2 points per cell dropped

### Level Progression

**Standard rule:** Level increases every 10 lines cleared.

**Example:** Clear 10 lines → Level 2. Clear 20 total lines → Level 3. And so on.

Level affects fall speed (see Falling section above).

### Game Over

**Trigger:** If a new piece cannot spawn without overlapping existing blocks in the stack, the game ends.

This typically happens when the stack has built up near the top of the well.

---

## Piece Rotation System

### Wall Kicks (SRS — Super Rotation System)

When a piece rotates, it may collide with the wall or other blocks. The SRS system attempts to "kick" the piece to a valid position.

**Wall kick process:**
1. Try to rotate piece normally
2. If collision occurs, try alternative positions (offsets)
3. If any offset is valid, piece rotates to that position
4. If no offset is valid, rotation fails (piece doesn't rotate)

**Kick offsets vary by piece type and rotation state.** The general idea:

For J, L, S, T, Z pieces:
- If rotating from spawn (0) → right (R): Try (0,0), (-1,0), (-1,1), (0,-2), (-1,-2)
- If rotating from right (R) → spawn (0): Try (0,0), (1,0), (1,-1), (0,2), (1,2)
- And similar for other rotation states

For I-piece (special case, longer kick table):
- The I-piece has unique kick offsets due to its length

**Simplified alternative:** No wall kicks. If rotation would cause collision, don't rotate. This is simpler but less player-friendly.

### Rotation Point

Each piece rotates around a specific point (typically the center of the 4×4 bounding box).

**For 4×4 representation:** Rotation is simply transposing and reversing rows/columns of the shape matrix.

```
// Clockwise rotation
function rotateClockwise(matrix) {
  const size = matrix.length;
  const rotated = [];
  for (let i = 0; i < size; i++) {
    rotated[i] = [];
    for (let j = 0; j < size; j++) {
      rotated[i][j] = matrix[size - 1 - j][i];
    }
  }
  return rotated;
}

// Counter-clockwise rotation
function rotateCounterClockwise(matrix) {
  const size = matrix.length;
  const rotated = [];
  for (let i = 0; i < size; i++) {
    rotated[i] = [];
    for (let j = 0; j < size; j++) {
      rotated[i][j] = matrix[j][size - 1 - i];
    }
  }
  return rotated;
}
```

---

## Hold System (Optional but Standard)

**Mechanic:** The player can hold the current piece, swapping it with a previously held piece (if any).

**Rules:**
- Press Hold key (C or Shift) to swap current piece with held piece
- If no piece is held, current piece goes to hold and next piece spawns
- Can only hold once per piece — after holding, you cannot hold again until a new piece spawns
- Held piece is displayed in a "Hold" box on the side of the screen

**Implementation:**
```
let heldPiece = null;
let canHold = true;

function hold() {
  if (!canHold) return;
  
  canHold = false;
  const currentType = currentPiece.type;
  
  if (heldPiece === null) {
    // No piece held yet, put current in hold and spawn next
    heldPiece = currentType;
    spawnNextPiece();
  } else {
    // Swap current with held
    const temp = heldPiece;
    heldPiece = currentType;
    spawnPiece(temp);
  }
}
```

---

## Next Piece Preview

Display the next piece (and optionally the next 2-5 pieces) in a sidebar.

**Implementation:**
- Maintain a "bag" of all 7 pieces
- Randomly draw from bag without replacement until empty
- Refill bag when empty
- This ensures even distribution of pieces (no long droughts of any piece)

**Bag randomizer:**
```
let bag = [];

function getNextPiece() {
  if (bag.length === 0) {
    bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L'];
    shuffle(bag);
  }
  return bag.pop();
}
```

---

## Ghost Piece (Optional but Recommended)

A translucent outline showing where the piece would land if hard-dropped now.

**Implementation:**
- Calculate the lowest valid position for current piece (simulate dropping)
- Draw a faint outline at that position
- Update in real-time as piece moves or rotates

**Visual:** Same shape as current piece, but:
- Outline only (no fill) or
- Semi-transparent fill (alpha 0.3)

---

## Visual Elements

### The Well

- Draw the grid background
- Draw locked pieces (the stack) with their colors
- Draw grid lines (optional)

### The Stack

- Each locked cell should show its color
- Optional: Add a subtle 3D effect (lighter top edge, darker bottom edge)
- Optional: Show grid lines between cells

### Current Piece

- Draw the piece at its current position
- Distinct color for each piece type
- Draw ghost piece below (optional)

### UI Sidebar (positioned to the right of the well)

**Elements:**
- **Score:** Current score, label "Score: [number]"
- **Level:** Current level, label "Level: [number]"
- **Lines:** Total lines cleared, label "Lines: [number]"
- **Next Piece:** Preview of next piece (small 4×4 grid showing the piece)
- **Hold Piece:** Currently held piece (if hold system implemented)
- **Controls:** Optional control reminder

---

## Game States

### 1. Title Screen

**Display:**
- "TETRIS" in large text, centered
- "Press SPACE to start"
- Control summary
- High score display (if stored)

**Behavior:**
- Pressing Space starts the game

### 2. Playing

**Display:**
- Well with current piece, stack, ghost piece
- Score, level, lines
- Next piece preview
- Hold piece (if implemented)

**Behavior:**
- Piece falls automatically
- Player controls movement and rotation
- Lines clear when complete
- Level increases every 10 lines
- Speed increases with level
- Pressing P or Escape pauses

### 3. Paused

**Display:**
- Game frozen
- "PAUSED" centered
- "Press P to resume"
- Semi-transparent overlay

**Behavior:**
- Pressing P resumes
- Pressing R restarts

### 4. Game Over

**Display:**
- "GAME OVER" centered, large
- Final score
- Lines cleared
- Level reached
- "Press R to play again"
- Optional: New high score message

**Behavior:**
- Pressing R restarts game
- Pressing Escape returns to title screen

---

## Technical Implementation Notes

### Grid Representation

Use a 2D array to represent the well:

```
const COLS = 10;
const ROWS = 20;
const grid = [];

// Initialize empty grid
for (let y = 0; y < ROWS; y++) {
  grid[y] = [];
  for (let x = 0; x < COLS; x++) {
    grid[y][x] = null; // null = empty, or store color
  }
}
```

### Piece Representation

```
const PIECES = {
  I: {
    shape: [
      [0,0,0,0],
      [1,1,1,1],
      [0,0,0,0],
      [0,0,0,0]
    ],
    color: '#00FFFF'
  },
  O: {
    shape: [
      [0,0,0,0],
      [0,1,1,0],
      [0,1,1,0],
      [0,0,0,0]
    ],
    color: '#FFFF00'
  },
  // ... and so on for T, S, Z, J, L
};
```

### Collision Detection

```
function isValidPosition(piece, grid, offsetX, offsetY) {
  const shape = piece.shape;
  
  for (let y = 0; y < shape.length; y++) {
    for (let x = 0; x < shape[y].length; x++) {
      if (shape[y][x]) {
        const gridX = piece.x + x + offsetX;
        const gridY = piece.y + y + offsetY;
        
        // Check boundaries
        if (gridX < 0 || gridX >= COLS || gridY >= ROWS) {
          return false;
        }
        
        // Check collision with stack (only if gridY >= 0)
        if (gridY >= 0 && grid[gridY][gridX] !== null) {
          return false;
        }
      }
    }
  }
  
  return true;
}
```

### Locking Piece to Grid

```
function lockPiece(piece, grid) {
  const shape = piece.shape;
  
  for (let y = 0; y < shape.length; y++) {
    for (let x = 0; x < shape[y].length; x++) {
      if (shape[y][x]) {
        const gridY = piece.y + y;
        const gridX = piece.x + x;
        
        if (gridY >= 0) {
          grid[gridY][gridX] = piece.color;
        }
      }
    }
  }
}
```

### Line Clearing

```
function clearLines(grid) {
  let linesCleared = 0;
  
  for (let y = ROWS - 1; y >= 0; y--) {
    // Check if row is full
    let isFull = true;
    for (let x = 0; x < COLS; x++) {
      if (grid[y][x] === null) {
        isFull = false;
        break;
      }
    }
    
    if (isFull) {
      // Remove the row
      grid.splice(y, 1);
      // Add new empty row at top
      grid.unshift(new Array(COLS).fill(null));
      linesCleared++;
      y++; // Re-check this row index (everything shifted down)
    }
  }
  
  return linesCleared;
}
```

### Hard Drop

```
function hardDrop(piece, grid) {
  let dropDistance = 0;
  
  while (isValidPosition(piece, grid, 0, 1)) {
    piece.y++;
    dropDistance++;
  }
  
  // Lock the piece
  lockPiece(piece, grid);
  
  // Award points for hard drop
  score += dropDistance * 2;
  
  // Clear lines
  const lines = clearLines(grid);
  addLineScore(lines);
  
  // Spawn next piece
  spawnNextPiece();
}
```

### Game Loop

```
let lastDropTime = 0;
let dropInterval = 1000; // ms, varies by level

function gameLoop(timestamp) {
  requestAnimationFrame(gameLoop);
  
  // Handle input
  handleInput();
  
  // Check if it's time for auto-drop
  if (timestamp - lastDropTime >= dropInterval) {
    lastDropTime = timestamp;
    
    if (isValidPosition(currentPiece, grid, 0, 1)) {
      currentPiece.y++;
    } else {
      // Lock piece
      lockPiece(currentPiece, grid);
      clearLines(grid);
      spawnNextPiece();
      
      // Check game over
      if (!isValidPosition(currentPiece, grid, 0, 0)) {
        gameOver();
      }
    }
  }
  
  // Render
  render();
}
```

---

## Common Bugs to Avoid

1. **Piece can rotate into walls/stack:** Implement wall kicks or disallow rotation that causes collision.

2. **Lines clear in wrong order:** Clear from bottom to top, and adjust row indices when removing lines.

3. **Piece spawns overlapping stack:** Always check if spawn position is valid. If not, game over.

4. **Infinite lock delay:** If lock delay resets every time the player moves, they can slide infinitely. Implement a limit on lock delay resets.

5. **Uneven piece distribution:** Use the 7-bag randomizer to ensure fair piece distribution.

6. **DAS makes movement feel sluggish:** Tune the initial delay (DAS) and repeat rate (ARR) for responsive controls. Typical values: 170ms delay, 50ms repeat.

7. **Rotation feels wrong:** Rotation should be around a consistent pivot point. The 4×4 matrix rotation handles this naturally.

8. **Ghost piece shows incorrect position:** Calculate ghost by simulating a drop, not by calculating distance to floor.

---

## Minimum Viable Product Checklist

A complete Tetris implementation must have:

- [ ] Canvas rendering with 10×20 grid well
- [ ] All 7 tetromino shapes with correct colors
- [ ] Piece movement (left, right, soft drop)
- [ ] Piece rotation (clockwise minimum, counter-clockwise recommended)
- [ ] Collision detection with walls, floor, and stack
- [ ] Pieces lock when they can't fall further
- [ ] Line clearing when rows are complete
- [ ] Scoring system (different points for 1, 2, 3, 4 lines)
- [ ] Level system (increases every 10 lines)
- [ ] Fall speed increases with level
- [ ] Next piece preview
- [ ] Hard drop functionality
- [ ] Game over detection
- [ ] Game states: Title → Playing → Paused → Game Over
- [ ] Pause and Restart functionality
- [ ] No external dependencies (all code in one HTML file)

---

## Quick Reference

| Element | Value |
|---------|-------|
| Grid | 10 columns × 20 rows |
| Cell size | 30×30 px |
| Pieces | 7 (I, O, T, S, Z, J, L) |
| Level up | Every 10 lines |
| Lines per Tetris | 4 |
| Lock delay | ~0.5 seconds |
| DAS (initial delay) | ~170ms |
| ARR (repeat rate) | ~50ms |
| Level 1 drop interval | 0.8 seconds |
| Maximum speed | 1 frame per drop |

---

End of specification.
