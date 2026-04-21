Build a classic Tetris-style falling-block puzzle game as a single self-contained HTML file using HTML5 Canvas, with all CSS and JavaScript inline and no external libraries, images, sounds, fonts, or network requests.

Assume the developer has never played Tetris. The game is a real-time spatial puzzle played inside a tall rectangular well. One block shape at a time falls from the top. The player can move it left/right, rotate it, accelerate its fall, or instantly drop it. When the piece lands, it locks into the stack. If a horizontal row becomes completely filled with blocks, that row clears and everything above it drops down. The goal is to keep the stack low and survive as long as possible while scoring by clearing lines efficiently.

The most important qualities are:
- immediate readability
- tight, dependable controls
- clean grid alignment
- satisfying line clears
- steadily increasing pressure

This should feel like “classic modernized Tetris”: not a simulation of obscure arcade bugs, but a polished and familiar falling-block puzzle with standard essentials.

Canvas and presentation:
- Canvas size: 800×600 pixels.
- Background: dark gray / near-black, e.g. #111111.
- Coordinate origin: top-left.
- Use a fixed internal resolution even if visually scaled responsively.
- The central playfield should be the focus, with HUD panels around it.

Playfield:
- The main well is 10 columns wide and 20 visible rows high.
- Each cell is 28×28 pixels.
- Position the playfield at x=240, y=20.
- Therefore the visible well area is 280×560 pixels.
- Draw a clear border around the well.
- A subtle grid is recommended for readability.

Tetrominoes:
Use the seven standard tetrominoes:
- I
- O
- T
- S
- Z
- J
- L

Each piece consists of 4 square blocks aligned to the grid.

Recommended colors:
- I: cyan
- O: yellow
- T: purple
- S: green
- Z: red
- J: blue
- L: orange

These are conventional and make the game instantly legible.

Piece spawning:
- Pieces spawn centered near the top of the board.
- Spawn orientation should be the standard neutral orientation for each piece.
- It is acceptable to use hidden spawn rows above the visible field if needed for proper behavior.
- A piece must spawn in a position that gives it room to rotate and descend naturally.
- If a new piece overlaps occupied cells when spawning, the game ends immediately.

Randomization:
- Use a 7-bag randomizer.
- That means: shuffle all seven tetromino types, then deal them one by one until empty, then reshuffle a new bag.
- This avoids streaks of missing pieces and is standard modern behavior.

Next piece preview:
- Show exactly one upcoming piece in a preview box.
- Preview box size: 112×112 pixels.
- Position: x=560, y=60.
- Center the previewed piece cleanly in the box.
- Label it “NEXT”.

Controls:
- Left Arrow / A = move piece left
- Right Arrow / D = move piece right
- Up Arrow / W = rotate clockwise
- Down Arrow / S = soft drop
- Space = hard drop
- Enter = start from title screen, restart after game over
- P = pause / unpause

Optional quality-of-life behavior:
- Allow held left/right for repeated movement with DAS/ARR-like behavior, but this is not strictly required if repeated movement still feels good.
- Minimal input buffering is nice but not required beyond responsive basic controls.

Game states:
1. Title screen
   - Visible on load
   - Show title “TETRIS”
   - Show concise instructions
   - Show “Press Enter to Start”
2. Playing
   - Active falling piece, gravity, input, line clears, score progression
3. Paused
   - Freeze gameplay and show “PAUSED”
4. Game over
   - Trigger when a new piece cannot spawn
   - Show “GAME OVER”, score, and restart prompt

Core loop:
1. A piece spawns at the top.
2. Gravity pulls it downward at a rate determined by the current level.
3. Player may move or rotate it while it is falling.
4. When it contacts the stack/floor, it does not necessarily lock instantly:
   - use a lock delay
5. Once locked, its blocks become part of the board.
6. Any full rows clear.
7. Score/lines/level update.
8. Spawn the next piece.
9. Repeat until game over.

Gravity:
- Starting gravity: 1000 ms per row at level 1.
- As level increases, gravity becomes faster.
- A simple, readable progression is fine. For example:
  - level 1: 1000 ms/row
  - level 2: 850 ms/row
  - level 3: 700 ms/row
  - level 4: 550 ms/row
  - level 5: 420 ms/row
  - and continue decreasing to a sensible floor
- Exact curve is flexible, but the game should clearly get harder over time.

Level progression:
- Track total cleared lines.
- Increase level every 10 lines cleared.
- Display current level clearly.
- Gravity should depend on level.

Movement:
- Left/right movement shifts the active piece exactly one cell.
- Movement is blocked if the target cells are occupied or outside bounds.
- The piece must remain aligned to the grid at all times.

Rotation:
- Rotate clockwise only (per required controls).
- Use a practical wall-kick system so rotation feels forgiving near walls and stacks.
- It does not need to perfectly reproduce official SRS, but it should behave similarly enough that:
  - rotating near a wall often works
  - rotating near simple stack edges often works
  - rotation does not feel broken or arbitrarily blocked
- The O piece may visually rotate trivially with no meaningful footprint change.
- The I piece should have sensible kicks so it remains usable.

A good implementation approach:
- Define block coordinates for each rotation state.
- On rotate:
  1. Try the rotated orientation in place.
  2. If blocked, try small offset tests such as:
     - (0,0)
     - (-1,0)
     - (1,0)
     - (-2,0)
     - (2,0)
     - (0,-1)
  3. Accept the first valid placement.
- This is sufficient if consistent and reliable.

Soft drop:
- Holding Down / S should accelerate downward movement.
- Soft drop should not instantly lock the piece.
- It should simply make it fall faster while held.
- Optionally award 1 point per row soft-dropped.

Hard drop:
- Space instantly drops the piece to the lowest valid position.
- The piece should then lock immediately or nearly immediately.
- Optionally award 2 points per row hard-dropped.
- Hard drop should feel snappy and satisfying.

Ghost piece:
- Show a ghost projection of where the current piece would land if hard-dropped.
- Render it as a translucent or outline version of the current piece.
- This is strongly recommended because it greatly improves readability and planning.

Lock delay:
- When a falling piece first touches the stack or floor, do not lock it instantly.
- Use a lock delay of 500 ms.
- During this lock delay, the player may still move or rotate the piece if valid.
- If movement/rotation lifts or repositions the piece, the lock delay can reset, but only a limited number of times.
- Recommended rule:
  - allow up to 3 lock-delay reset extensions per piece
- This gives a modern, fair feel without allowing indefinite stalling.

Line clears:
- If a row becomes completely filled with occupied cells, clear it.
- Support clearing 1, 2, 3, or 4 lines at once.
- After clearing, rows above fall downward immediately.
- A short line-clear flash or animation is recommended but should be brief and not interfere with control flow.
- During the clear effect, you may briefly pause the next spawn for visual feedback.

Scoring:
Use a classic-ish line-clear scoring model scaled by level:
- Single line clear: 100 × level
- Double: 300 × level
- Triple: 500 × level
- Tetris (4 lines): 800 × level

Also optionally award:
- Soft drop: +1 per cell
- Hard drop: +2 per cell

Score starts at 0.
Display score prominently.
Persist high score in localStorage and display it as “BEST” or “HIGH SCORE”.

HUD:
At minimum display:
- Score
- High score
- Level
- Lines cleared
- Next piece preview

Suggested layout:
- Main board at x=240, y=20
- Next preview at right side, around x=560, y=60
- Score / Level / Lines stacked beneath or beside the preview
- Optional controls reminder on title screen only

Visual design:
- Use crisp, clean blocks with slight inset or border shading so stacked pieces are easy to read.
- Background should contrast well with blocks.
- Ghost piece should be visibly distinct but not distracting.
- The board grid can be subtle.
- Cleared lines should feel satisfying, even if the effect is minimal.
- Avoid excessive glow or particles if they harm readability.

Recommended block rendering:
- Each occupied cell should fill most of its 28×28 area, with a small inset margin like 2 px.
- Use a darker border or inner highlight to make pieces distinct.
- Empty cells may show a faint grid line or remain plain.

Title screen instructions should explain the game clearly:
- pieces fall from the top
- fill complete horizontal lines to clear them
- prevent the stack from reaching the top
- controls
- start prompt

Pause behavior:
- P toggles pause during gameplay.
- While paused:
  - no gravity
  - no movement
  - no lock timer
  - no line clear timing
- Show clear “PAUSED” overlay.

Game over:
- Trigger when a new piece cannot spawn because its spawn area is blocked.
- Show “GAME OVER”.
- Show final score.
- Show restart prompt.
- Restart must fully reset board, score, level, lines, randomizer, next piece, timers, and state.

Implementation guidance:
Use requestAnimationFrame for rendering and time accumulation.

A robust structure would include:
- board[20][10] or board with hidden rows
- activePiece:
  - type
  - rotation
  - x
  - y
- nextPiece
- bag
- score
- bestScore
- lines
- level
- gravity timer
- lock timer
- lock reset count
- gameState

Recommended logic flow during play:
1. Handle input
2. Apply horizontal move attempts
3. Apply rotation attempt
4. Apply soft drop / gravity
5. Determine whether the piece is grounded
6. Update lock delay
7. Lock piece if needed
8. Clear lines if any
9. Spawn next piece
10. Render

Collision rules:
A placement is invalid if any block of the piece:
- is left of column 0
- is right of column 9
- is below row 19
- overlaps an occupied board cell
Hidden negative rows above the visible playfield are acceptable during spawn/rotation, but visible gameplay should remain consistent.

Line clear timing:
- A brief visual flash of around 80–150 ms is nice.
- It’s acceptable to clear immediately with no animation if the implementation is cleaner.
- If using animation, keep controls frozen only briefly.

Input feel:
- The game must feel reliable.
- Pressing rotate should rotate once.
- Pressing left/right should move exactly as expected.
- Hard drop should be immediate.
- Soft drop should feel faster but still controlled.
- No lost inputs, accidental double-rotations, or jitter.

Audio:
- Optional but recommended.
- Use Web Audio API only.
- Suggested procedural sounds:
  - subtle tick/click on move
  - slightly brighter chirp on rotate
  - low thud on lock
  - satisfying tone on line clear
  - stronger flourish on Tetris (4-line clear)
  - harsh short tone on game over
- Audio must not be required and should only activate after user interaction.

Important edge cases:
- Rotating near the wall should not feel unfairly blocked.
- Hard drop should not leave the piece hovering.
- Pieces should not lock prematurely when slight movement is still possible within lock delay.
- Clearing multiple rows at once must shift all rows above down correctly.
- Game over should happen only when spawn genuinely fails.
- Pausing must freeze timers cleanly.
- Restart must fully reset everything.

What the developer should aim for emotionally:
- The player should instantly understand that they are organizing falling shapes.
- The first minute should feel manageable and satisfying.
- As speed increases, the game should become tense but fair.
- Clearing four lines at once should feel especially rewarding.

Acceptance checklist:
- On load, title screen is visible and readable.
- Pressing Enter starts a new game.
- A 10×20 playfield is visible and functions correctly.
- Tetrominoes spawn one at a time using a 7-bag randomizer.
- Player can move left/right, rotate clockwise, soft drop, and hard drop.
- Pieces obey collision bounds and stack correctly.
- A ghost piece shows landing position.
- A next-piece preview is visible.
- Full horizontal lines clear correctly.
- Score, level, and line count update correctly.
- Level increases every 10 lines.
- Gravity speeds up as level increases.
- Lock delay feels fair and prevents instant locking on first contact.
- Game over occurs when a new piece cannot spawn.
- High score persists via localStorage.
- Entire implementation is in one self-contained HTML file with inline CSS/JS only and no external dependencies.
