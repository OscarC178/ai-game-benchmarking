Build a classic Snake game as a single self-contained HTML file using HTML5 Canvas, with all CSS and JavaScript inline and no external dependencies of any kind.

The developer should assume the player has never seen Snake before, so the game must teach itself through its layout and behavior. The core loop is simple: the player controls a growing snake moving around a grid. The snake automatically moves forward continuously. The player can only steer left, right, up, or down. Food appears on empty grid cells. Eating food makes the snake longer and increases score. Hitting the walls or the snake’s own body ends the run.

This should feel like the archetypal early Snake / Nokia / arcade-grid version: clean, readable, fast to understand, and increasingly tense as the snake grows.

Overall feel:
- Minimalist.
- Immediate readability.
- Crisp grid-based movement.
- No physics, no smooth turning arcs, no freeform motion.
- Every movement step should snap exactly from one grid cell to the next.
- Difficulty should come from increasing speed and growing length, not gimmicks.

Canvas and rendering:
- Canvas size: 600×600 pixels.
- Background: very dark gray or near-black, e.g. #111111.
- Use a visible 20×20 logical grid.
- Each cell is exactly 30×30 pixels.
- Keep all gameplay aligned strictly to this grid.
- The snake, food, HUD, overlays, and any visual effects must all render cleanly at this fixed resolution.
- If the canvas is visually scaled in the browser, preserve aspect ratio and internal 600×600 coordinate logic.

Core rules:
- The snake starts with length 3.
- It begins near the center of the board.
- Initial direction: moving right.
- The snake advances automatically at a fixed tick interval.
- The player may queue one direction change per movement step.
- Direct reversal is forbidden:
  - if moving right, pressing left should do nothing
  - if moving up, pressing down should do nothing
  - etc.
- Food spawns in a random unoccupied cell.
- When the snake’s head enters a food cell:
  - score increases
  - snake length increases by 1
  - a new food spawns in another free cell
  - movement speed increases slightly
- Game ends immediately when:
  - snake head exits the board bounds
  - snake head enters any occupied body cell
- If the snake fills the entire board, treat it as a completed perfect run / win state rather than a crash.

Board definition:
- 20 columns × 20 rows.
- Valid cell coordinates are 0..19 in both axes.
- Convert to pixel positions by multiplying by 30.
- The playfield is the whole canvas, unless you reserve a slim HUD band inside the same canvas. If you do add HUD, keep the playable area still clearly 20×20 and visually consistent.

Initial snake setup:
- Start with three cells in a horizontal line.
- Head at grid (10,10), body at (9,10) and (8,10) is a good default.
- Head should be visually distinguishable from body.
- Movement direction should be obvious from head design or eye placement if you choose to stylize it.

Controls:
- Arrow keys: up/down/left/right.
- Also support W/A/S/D.
- Enter:
  - start from title screen
  - restart from game-over or win screen
- P:
  - pause and unpause during active play
- Optional:
  - Space may also start/restart, but Enter is required

Movement model:
- The snake does not move every animation frame. It moves in discrete simulation ticks.
- Recommended starting speed: 8 ticks per second.
- Each tick:
  1. Apply any queued valid direction change.
  2. Compute next head cell.
  3. Check collisions.
  4. Add new head.
  5. If food was not eaten, remove tail.
- Allow at most one queued turn per tick window so fast key mashing does not create multiple same-step turns.
- This is important for fairness and for classic Snake feel.
- The snake should never “cut corners” or move diagonally.

Speed progression:
- Start at 8 ticks per second.
- Increase by 0.5 ticks per second for each food eaten.
- Cap at 15 ticks per second.
- This should make the game feel progressively more tense without becoming unplayable too quickly.
- The speed increase should happen immediately after eating food.

Food behavior:
- Exactly one food item on the board at a time.
- Food occupies one grid cell.
- Food must spawn only in free cells not occupied by the snake.
- Food should be visually obvious and attractive, e.g. a red apple-like square/circle or glowing pellet.
- Optional small pulse animation is fine, but keep it grid-centered and readable.
- If only one free cell remains, food must spawn there.
- If no free cells remain because the snake fills the board, trigger win state instead of attempting to spawn food.

Collision rules:
- Wall collision:
  - if next head x < 0 or > 19, game over
  - if next head y < 0 or > 19, game over
- Self collision:
  - if next head cell matches any snake segment cell, game over
- Tail nuance:
  - If moving into the cell currently occupied by the tail on a non-growth step, decide collision carefully based on update order.
  - Simplest robust approach: compute next head, then if not growing, allow the current tail cell to be considered vacated for that move.
  - This avoids false deaths in valid movement cases.

Game states:
1. Title screen
   - Visible on initial load.
   - Show game title “SNAKE”.
   - Show concise instructions:
     - move with arrows or WASD
     - eat food to grow
     - avoid walls and yourself
     - press Enter to start
2. Playing
   - Snake moves continuously on ticks.
   - Food present.
   - Score visible.
3. Paused
   - Freeze simulation.
   - Show centered “PAUSED”.
4. Game over
   - Trigger on wall or self collision.
   - Show “GAME OVER”.
   - Show final score and restart prompt.
5. Win / board-filled completion
   - Trigger when all 400 cells are occupied.
   - Show celebratory message such as “YOU WIN” or “BOARD CLEARED”.
   - Show final score and restart prompt.

Scoring:
- Start score at 0.
- Each food eaten: +10 points.
- Optional additional survival/time scoring is not necessary and should be avoided unless very restrained.
- High score should be stored in localStorage.
- Display current score and best score during play.
- After game over or win, preserve high score if exceeded.

UI and HUD:
- Keep HUD simple and always readable.
- At minimum display:
  - current score
  - best/high score
- Optional:
  - speed level or length
- The HUD may be drawn directly on the canvas at top or bottom, or overlaid cleanly in unused margin space, but it should not clutter the playfield.
- If using full 600×600 for the playfield only, score can appear in a subtle overlay at the edge, as long as gameplay remains clear.

Visual design guidance:
- Snake head: distinct from body.
- Snake body: clean repeated segments.
- Background grid lines are optional but recommended:
  - subtle, low-contrast lines help readability
  - do not overpower the game objects
- Food should contrast clearly against the snake and background.
- Title, pause, game-over, and win overlays should be centered and obvious.
- Retro arcade minimalism is preferred over decorative complexity.

Recommended visual proportions:
- Snake segments should not fill the entire 30×30 cell edge-to-edge.
- A slightly inset look works well:
  - e.g. 28×28 or 26×26 rectangles centered in each 30×30 cell
- This gives clean separation between cells and improves readability.
- Food can be smaller than a cell, e.g. 16–20 px, centered in its tile.

Animation and polish:
- Even though movement is tick-based, rendering still uses requestAnimationFrame.
- Use animation frames for:
  - smooth redraws
  - subtle food pulsing
  - overlays
  - possible head/body eye or tongue detail
- Do not interpolate snake position between cells unless done very carefully; classic Snake is happiest with discrete cell jumps.
- A small flash on eat or death is optional.
- Keep polish restrained and readable.

Audio:
- Optional but recommended.
- If used, generate procedurally with Web Audio API only.
- Suggested sounds:
  - short blip when food is eaten
  - harsher tone on death
  - optional pause/start tone
  - optional short celebratory tone on win
- Audio must not be required.
- It should activate only after user interaction per browser rules.

Implementation guidance:
- Use requestAnimationFrame for rendering.
- Accumulate delta time and advance the simulation in fixed snake-move ticks.
- Clamp very large frame gaps so tab switching does not cause wild jumps.
- Keep game logic separate from rendering.
- Use an array of snake segments ordered head-first or tail-first consistently.
- Store food as a single grid coordinate.
- Store current direction and next queued direction separately.
- Ensure only one valid turn is accepted per tick interval.

Important behavior details:
- The snake should begin stationary on the title screen, not moving in the background unless intentionally used as harmless decoration.
- Starting a new game should fully reset:
  - snake position
  - length
  - direction
  - queued input
  - score
  - food
  - speed
  - timers/overlays
- Pause should freeze the simulation without corrupting the accumulated tick timer.
- Restart from game over/win should behave exactly like a fresh run.
- Direction input during pause should not secretly queue up multiple turns.
- Key repeat should not break control. If using keydown events, handle them so held keys feel fine but repeated presses do not create illegal multiple queued turns.

Self-collision handling example:
- Suppose the snake is [head, ..., tail].
- Determine next head position.
- If food is not being eaten this turn, the tail will move away.
- Therefore, moving into the current tail cell should be allowed if that tail cell is the one that will be removed this same step.
- If food is being eaten, tail does not move, so that same move should count as collision.
- This distinction matters and should be implemented correctly.

Win condition:
- If snake length reaches 400 cells, the board is full.
- End the run as a win.
- Do not try to spawn new food after that.
- Show a clear win message.
- Preserve score and high score as usual.

Recommended structure:
- Constants:
  - canvas size
  - grid size
  - cell size
  - starting speed
  - max speed
- State:
  - gameState
  - snake array
  - direction
  - queuedDirection
  - hasQueuedTurn flag
  - food
  - score
  - highScore
  - tickRate
  - tickAccumulator
- Functions:
  - startGame()
  - resetGame()
  - spawnFood()
  - queueDirection()
  - updateTick()
  - checkCollision()
  - render()
  - drawSnake()
  - drawFood()
  - drawHUD()
  - drawOverlay()

Acceptance checklist:
- Game loads without console errors.
- Title screen appears on load.
- Enter starts a new game.
- Snake begins at length 3 and moves right automatically.
- Arrow keys and WASD steer correctly.
- Direct reverse turns are ignored.
- Only one turn can be queued per movement tick.
- Food always spawns in an empty cell.
- Eating food increases score, length, and speed.
- Wall collision causes game over.
- Self collision causes game over.
- Board-full condition triggers a win state.
- P pauses and unpauses correctly.
- High score persists across reloads via localStorage.
- Entire implementation is contained in one HTML file with inline CSS/JS only and no external dependencies.
