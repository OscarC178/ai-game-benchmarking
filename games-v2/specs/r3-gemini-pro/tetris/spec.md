# Game Specification: Tetris

## 1. Core Concept & Gameplay Overview
Tetris is a tile-matching puzzle game. The game consists of a vertical rectangular playing field (the "Matrix"). Pieces formed of four square blocks (the "Tetrominoes") fall sequentially from the top of the Matrix to the bottom.

The player can move the falling piece horizontally and rotate it by 90 degrees to create a horizontal line of ten blocks without gaps. When such a line is created, it disappears, and any block above the deleted line will fall. The objective is to survive as long as possible and score points by clearing lines. As the player clears more lines, the level increases, causing the pieces to fall faster. The game ends when a new piece spawns but is immediately blocked by existing blocks (the stack reaches the top of the Matrix).

## 2. Technical Constraints
- **Format:** A single, self-contained `index.html` file.
- **Assets:** Strict zero-dependency rule. Render everything using Canvas API `fillRect` and `strokeRect`. No external images, CSS, or audio files.
- **Rendering:** HTML5 `<canvas>` using the 2D context.
- **Game Loop:** Typical physics continuous loops do not apply well to Tetris. The game operates on a "step" timer. The active piece drops one grid cell exactly every X milliseconds (gravity). However, player lateral movement and rotation inputs should execute instantaneously to feel responsive.

## 3. Visual Design & Matrix
- **Matrix Dimensions:** 10 columns by 20 rows. Visually, this is represented as a grid. (The standard implementation internally uses rows 0-1 for piece spawning above the visible area, so the internal grid is often 10x22, rendering only the bottom 20).
- **Cell Size:** e.g., 30px by 30px.
- **Canvas Size:** Large enough to hold the Matrix (width 300px, height 600px), plus UI side panels for "Next Piece", "Score", "Level", and "Lines". e.g., 500px width by 600px height total.
- **Background Palette:** Matrix background should be dark (e.g., `#111111`) with a faint grid overlay (`#333333`) to help read block positions.
- **Typography:** Standard sans-serif or monospace font, white text.

## 4. The Tetrominoes
There are exactly 7 distinct pieces, each made of 4 interconnected squares (blocks). Each piece has a specific color and a 4x4 or 3x3 bounding box used for rotation calculations.

*Note: For rotation, imagine the piece inside a small local 2D array. Rotating the piece means mathematically rotating this local array 90 degrees clockwise or counter-clockwise.*

1. **I Piece:** 4 blocks in a straight line. Color: Cyan (`#00FFFF`). (Needs a 4x4 matrix).
2. **J Piece:** A block with a tail of 3 blocks to the left. Color: Blue (`#0000FF`). (Needs a 3x3 matrix).
3. **L Piece:** A block with a tail of 3 blocks to the right. Color: Orange (`#FFA500`). (Needs a 3x3 matrix).
4. **O Piece:** A 2x2 square. Color: Yellow (`#FFFF00`). (Needs a 2x2 or 4x4 matrix, but rotation does practically nothing).
5. **S Piece:** A horizontal 'Z' shape. Color: Green (`#00FF00`). (Needs a 3x3 matrix).
6. **T Piece:** A 'T' shape. Color: Purple (`#800080`). (Needs a 3x3 matrix).
7. **Z Piece:** A horizontal 'S' shape. Color: Red (`#FF0000`). (Needs a 3x3 matrix).

### Block Visuals
For a polished look, blocks should not be flat colors. Render each block cell with a brighter border on the top and left, and a darker border on the bottom and right to create a 3D bevel/bevel effect.

## 5. Controls
- **ArrowLeft:** Move active piece 1 cell Left.
- **ArrowRight:** Move active piece 1 cell Right.
- **ArrowUp:** Rotate active piece 90 degrees Clockwise.
- **ArrowDown:** Soft Drop (accelerate gravity downward while held).
- **Spacebar:** Hard Drop (instantly move the piece straight down as far as it can go and lock it).
- **Enter:** Start / Restart game.

### Input Handling (DAS & ARR)
For the game to feel right, horizontal movement needs "Delayed Auto Shift" (DAS). When a player presses and holds Left or Right, move the piece 1 cell immediately. Then pause for a short delay (e.g., 150ms). If the key is still held, continue moving the piece rapidly (e.g., 1 cell every 50ms) until released.

## 6. Rules & Collisions

### Collision Detection
Before moving or rotating the active piece, the game must check if the *proposed* new state is valid.
1. Iterate over every block cell containing a value of `1` inside the piece's local matrix.
2. Translate local coordinate to global Matrix coordinate.
3. Check bounds: Is the global X < 0 or >= 10? Is the global Y >= 20? 
4. Check overlap: Does the global coordinate overlap a cell in the main Matrix grid that is already occupied by a previously locked block?
If ANY check fails, the move/rotation is invalid and the piece state remains unchanged.

### Locking
When the gravity timer ticks, the game attempts to move the piece down by 1 Y coordinate. 
- If gravity fails (the space below is blocked by the floor or stack), the piece doesn't move. 
- Instead, wait a brief "lock delay" (e.g., 500ms). If the piece is still blocked underneath when the lock delay expires, "Lock" the piece: write its color values permanently into the main Matrix grid structure.
- Spawn the next piece at the top middle of the grid.

### Rotation & "Wall Kicks" (Crucial for Playability)
A naive rotation simply turns the local array. If the piece is against a wall, a naive rotation will fail the collision overlap test, forcing the player to move away from the wall to rotate. 
- **Wall Kicks:** If a rotation fails collision, try "kicking" the piece by automatically shifting it 1 cell left, right, or up. If one of these shifted positions passes the collision test, accept the rotation at that new shifted position.

### Line Clearing (The Core Loop)
Immediately after a piece locks into the grid:
1. Scan the Matrix rows from bottom to top.
2. If a row is completely filled (no empty cells):
   - Mark the row for deletion.
   - Play a line clear sound.
   - Delete the row array and insert a new empty row array at the top (`y=0`) of the Matrix, effectively shifting all blocks above the deleted line down by 1 cell.
3. Count how many lines were cleared simultaneously in this step (1, 2, 3, or a "Tetris" = 4).

## 7. Scoring, Levels, and Gravity
The game requires escalation.

- **Lines:** Total number of lines cleared.
- **Level:** Starts at 1. Increases by 1 for every 10 lines cleared.
- **Gravity Scaling:** The interval between automatic downward drops must start slow (e.g., 1000ms at Level 1) and decrease exponentially as the Level increases (e.g., 800ms at Lvl 2, 600ms at Lvl 3, scaling down to a minimum of ~50ms).

### Standard Scoring Matrix
- Soft Drop: 1 point per cell dropped.
- Hard Drop: 2 points per cell dropped.
- Single Line Clear: 100 * Level.
- Double Clear: 300 * Level.
- Triple Clear: 500 * Level.
- Tetris Clear (4 lines): 800 * Level.

## 8. UI Elements
- **The Matrix:** The 10x20 playing field.
- **Next Piece Preview:** Display the next piece that will spawn in a side panel.
- **Score Display:** Current total points.
- **Level Display:** Current difficulty level.
- **Ghost Piece (Optional but expected):** Render a semi-transparent version of the active piece directly below it at the lowest possible valid Y coordinate. This indicates exactly where the piece will land on a Hard Drop.

## 9. Game Flow & States
- **STATE: STARTUP:** Display title "TETRIS" and "Press Enter to Start". 
- **STATE: PLAYING:** Manage gravity interval, process input, handle locking and line clearing. 
- **STATE: GAME OVER:** Triggered if a newly spawned piece immediately overlaps blocks in the Matrix. Display "GAME OVER". Allow restart.

## 10. Audio (Web Audio API)
- **Move:** Very fast, quiet, high-pitched tick (e.g., 1000Hz, 10ms length).
- **Rotate:** Fast, slightly longer tick.
- **Hard Drop/Lock:** A solid, low "thud" (e.g., quick slide from 200Hz to 50Hz noise).
- **Line Clear:** High-pitched, rewarding chime or arpeggio (e.g., 600Hz -> 800Hz -> 1000Hz).
- **Tetris (4 Line) Clear:** Longer, more dramatic triumphant chord.
- **Game Over:** Descending, somber tone.
