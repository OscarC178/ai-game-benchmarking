Build a classic Pac-Man-style maze chase game as a single self-contained HTML file using HTML5 Canvas, with all CSS and JavaScript inline and no external libraries, images, fonts, audio files, or network requests.

Assume the developer has never played Pac-Man. The game is a top-down maze game. The player controls a circular yellow character that moves continuously through a maze, eating dots while being chased by four ghosts. The objective is to clear all pellets in the maze without losing all lives. Large power pellets temporarily let the player turn the tables and eat the ghosts for bonus points. The game’s identity comes from:
- a fixed maze filled with pellets
- continuous movement along corridors
- responsive buffered turning at intersections
- four ghosts with distinct personalities/targeting behaviors
- alternating chase/scatter pacing
- temporary frightened mode after power pellets
- wraparound tunnels on the left and right edges
- escalating tension as pellets disappear

This should feel like classic Pac-Man in spirit: readable, deliberate, and pattern-friendly, not a loose maze-action game.

Canvas and maze dimensions:
- Canvas size: 700×780 pixels.
- Background: black.
- Coordinate origin: top-left.
- Maze grid: 28 columns × 31 rows.
- Tile size: 24 pixels.
- Maze offset: x=14, y=30.
- This means the maze is drawn inside the canvas with modest padding around it for HUD and margins.
- Use the grid as the authoritative logic system. Movement, pellets, walls, intersections, and ghost navigation should all be based on tile coordinates plus smooth pixel movement between tile centers.

Core objective:
- Eat all regular pellets and power pellets in the maze to clear the board.
- Avoid contact with ghosts unless they are frightened.
- If the player eats a power pellet, ghosts become frightened for a limited time and can be eaten.
- Clearing all pellets advances to the next level.
- The game continues with slightly increased difficulty.
- The player starts with 3 lives.
- Game over occurs at 0 lives.

Player character (Pac-Man):
- Shape: yellow circular character with an animated wedge mouth.
- Radius: 10 pixels.
- Starting tile: column 14, row 23.
- Base movement speed: 120 px/s.
- Movement is continuous, not turn-by-turn, but constrained to the maze corridors.
- Direction choices:
  - Arrow keys
  - also support WASD
- Pac-Man should support buffered turning:
  - when the player presses a direction slightly before reaching an intersection, the turn should happen automatically as soon as the new path becomes valid
- Include a cornering assist / turn tolerance of about 4 pixels:
  - if near the centerline of the target corridor, snap into alignment so turning feels responsive rather than frustrating
- Pac-Man cannot move through walls.
- Pac-Man should align cleanly to the tile grid when moving along corridors.

Movement model:
- Pac-Man always moves in one of the four cardinal directions.
- If the player requests a valid new direction at an intersection, Pac-Man turns.
- If the requested direction is not currently valid, remember it as a queued direction.
- If the current direction becomes blocked by a wall and no queued turn is possible, Pac-Man stops until a valid direction is provided or available.
- This buffered-input turning behavior is one of the most important feel details.

Mouth animation:
- The mouth should open/close rhythmically while moving.
- Direction of the mouth wedge should match current movement direction.
- During death animation, the mouth can close down or the body can shrink / collapse.

Maze:
- Use a fixed classic-style maze structure.
- It must include:
  - walls
  - open corridors
  - a central ghost house area
  - left/right wrap tunnels
  - 240 total pellets including 4 power pellets
- The maze should visually resemble the iconic Pac-Man maze:
  - blue walls
  - black corridors
  - symmetrical structure
  - ghost house near the center
  - large power pellets near outer corners
- Exact tile art can be abstract, but the navigational structure must support authentic play.

Maze tiles should distinguish:
- wall
- empty path
- regular pellet
- power pellet
- ghost house door / restricted ghost gate if needed
- tunnel path

Pellets:
- Regular pellet:
  - small dot
  - score +10
- Power pellet:
  - larger blinking dot
  - there are exactly 4
  - score +50
  - triggers frightened mode for ghosts
- Total pellets in level: 240 including the 4 power pellets
- The level is cleared when all pellets and power pellets are eaten

Ghosts:
There are four ghosts, each with distinct color and target logic:
- Blinky: red
- Pinky: pink
- Inky: cyan
- Clyde: orange

Suggested colors:
- Blinky: #FF0000
- Pinky: #FFB8FF
- Inky: #00FFFF
- Clyde: #FFB852

Ghost starting area:
- Ghosts begin in or around the ghost house near the center of the maze.
- Blinky may start outside or ready to leave quickly.
- Pinky, Inky, and Clyde can start inside the house and be released over time or based on pellet count.
- Ghost “eyes” return to the house when eaten, then regenerate into normal ghosts.

Ghost movement speed:
- Normal speed: 110 px/s
- Frightened speed: 60 px/s
- Eyes-returning speed: 200 px/s
- These can be adjusted slightly for balance, but keep the relationships:
  - frightened slower than Pac-Man
  - eyes much faster
- Ghosts also slow down in tunnels similarly to the classic feel if desired.

Ghost states:
Each ghost should support at least:
1. Normal active
   - either chase or scatter mode
2. Frightened
   - blue, vulnerable, slower, directionally less intelligent
3. Eyes / eaten
   - returns directly to ghost house, then respawns into normal cycle
4. House / leaving-house
   - for release behavior

Global ghost modes:
Classic Pac-Man alternates between scatter and chase.
You should implement a global schedule that affects all active ghosts (except frightened/eaten overrides):

Recommended schedule:
- Scatter: 7 seconds
- Chase: 20 seconds
- Scatter: 7 seconds
- Chase: 20 seconds
- Scatter: 5 seconds
- Chase: 20 seconds
- Scatter: 5 seconds
- Chase indefinitely

This does not need to be arcade-perfect frame data, but it should create the classic ebb and flow:
- scatter = ghosts retreat toward their personal corners
- chase = ghosts actively pursue using their individual logic

When frightened mode begins:
- it temporarily overrides scatter/chase
- ghosts reverse direction once when frightened starts
- after frightened ends, they resume the prior global mode behavior

Ghost AI:
This is central. Each ghost should feel different.

Blinky (red):
- Direct chaser.
- Target tile is Pac-Man’s current tile.
- In scatter mode, target top-right corner.

Pinky (pink):
- Ambusher.
- Target 4 tiles ahead of Pac-Man’s current direction.
- In scatter mode, target top-left corner.

Inky (cyan):
- More complex / erratic.
- Compute a point 2 tiles ahead of Pac-Man, then use the vector from Blinky to that point and double it to get Inky’s target.
- In scatter mode, target bottom-right corner.

Clyde (orange):
- Alternates between chasing and retreating.
- If farther than 8 tiles from Pac-Man, target Pac-Man like a chaser.
- If within 8 tiles, target bottom-left scatter corner instead.
- In scatter mode, also target bottom-left corner.

Path choice rules:
- Ghosts navigate tile intersections.
- At each decision point, choose the valid direction that minimizes distance to target tile.
- Typically, ghosts should not reverse direction unless:
  - frightened mode begins
  - forced by dead end
  - entering special transitions
- This “shortest-distance toward target, no reverse unless necessary” rule is sufficient to reproduce the essential Pac-Man feel.

Frightened mode:
Triggered by eating a power pellet.
Behavior:
- All currently active ghosts become frightened unless already eyes-only.
- Ghosts turn dark blue.
- They move slower.
- They choose directions randomly (or semi-randomly) at intersections instead of using chase/scatter targeting.
- Near the end of frightened duration, they should flash between blue and white to warn the player.
- If Pac-Man touches a frightened ghost:
  - Pac-Man eats the ghost
  - the ghost becomes eyes only
  - eyes return to ghost house
  - score awarded increases in sequence

Frightened scoring:
- First ghost eaten during one power-pellet phase: 200
- Second: 400
- Third: 800
- Fourth: 1600

Frightened duration:
- Level 1: 8 seconds
- Level 2: 6 seconds
- Higher levels: can reduce gradually, e.g. 4 seconds
- The exact curve is flexible, but frightened duration should shorten over later levels.

Ghost release behavior:
A simple but authentic release system:
- Blinky active immediately
- Pinky leaves immediately or very soon
- Inky released after around 30 pellets eaten
- Clyde released after around 60 pellets eaten
This is sufficient and easy to reason about.

Wrap tunnels:
- There must be left and right tunnel exits around the middle of the maze.
- If Pac-Man exits one side through the tunnel, he reappears on the opposite side.
- Ghosts should also be able to use the tunnel.
- Movement speed may be reduced in tunnels for ghosts, and optionally Pac-Man, if desired.

Fruit / bonus item:
Strongly recommended.
- After a certain number of pellets eaten (for example 70 and 170), spawn a bonus fruit in the center area below the ghost house.
- The fruit remains for a limited time (e.g. 10 seconds).
- If Pac-Man eats it, award bonus points (e.g. 100 on level 1).
- The fruit is optional but adds authenticity.

Lives:
- Start with 3 lives.
- Display lives in HUD, typically as small Pac-Man icons near the bottom.
- On collision with a normal ghost:
  - lose one life
  - play death animation
  - reset Pac-Man and ghosts to starting positions
  - preserve remaining pellets
- If lives reach 0:
  - game over

Level progression:
- When all 240 pellets are eaten:
  - level complete
  - increment level
  - rebuild pellets
  - reset Pac-Man and ghost positions
  - preserve score and lives
  - optionally increase ghost pressure slightly (e.g. shorter frightened duration, slightly faster normal ghost speed)

Scoring:
- Regular pellet: 10
- Power pellet: 50
- Ghosts during frightened: 200, 400, 800, 1600 chain
- Fruit: 100+ depending on level
- Level clear bonus is optional; classic Pac-Man mostly scores through pellets/ghosts/fruit
- High score persists in localStorage
- Display score top-left and high score top-right

HUD:
At minimum display:
- Score
- High score
- Lives
- Level
Suggested layout:
- Score top-left
- High score top-right
- Lives along bottom-left
- Level along bottom-right or near lower HUD area
Keep the maze visually dominant.

Game states:
1. Title / start screen
   - Visible on load
   - Show title “PAC-MAN”
   - Explain controls and objective:
     - eat all dots
     - avoid ghosts
     - power pellets let you eat ghosts temporarily
     - clear the maze
   - Show “Press Enter to Start”
2. Ready state
   - Brief “READY!” message at start of level / after life reset
3. Playing
4. Paused
   - Freeze all timers and movement
   - Show “PAUSED”
5. Death animation / life lost
6. Level clear transition
7. Game over
   - Show “GAME OVER”, final score, restart prompt

Collision rules:
Use a simple overlap / same-tile or close-distance collision test between Pac-Man and ghosts.
Since all actors move along the grid, collision can be based on distance between centers or shared tile occupancy.
Recommended:
- if center distance is below a threshold around 16–18 px, count as contact

Required collision pairs:
- Pac-Man ↔ regular pellet
  - remove pellet, +10
- Pac-Man ↔ power pellet
  - remove pellet, +50, frighten ghosts
- Pac-Man ↔ frightened ghost
  - ghost eaten, +chain score
- Pac-Man ↔ normal ghost
  - lose life
- Pac-Man ↔ fruit
  - fruit consumed, score bonus

Rendering guidance:
Maze walls:
- Draw in blue.
- Simple stroke outlines or tile-based corner/edge rendering are acceptable.
- The maze should be visually readable and attractive even if not pixel-perfect.

Pellets:
- Regular pellets small and numerous.
- Power pellets large and blinking.

Ghosts:
- Rounded top with scalloped lower edge is enough.
- White eyes with directional pupils.
- During frightened state, use blue body, and flashing near expiration.
- Eyes-only state can be just eyes moving back to the house.

Pac-Man:
- Yellow filled circle with animated mouth wedge.
- Directional rotation based on movement direction.

Audio:
- Optional but recommended.
- Use Web Audio API only.
- Suggested procedural sounds:
  - waka-waka pellet sound alternating pitch
  - power pellet tone
  - ghost eaten tone
  - death sequence descending tone
  - start jingle
- Audio must not be required and should only activate after user interaction.

Implementation guidance:
Use requestAnimationFrame with delta time.
Clamp large frame gaps after tab inactivity.
Separate update and render logic.

Recommended state:
- gameState
- maze grid
- pellets remaining count
- pacman { x, y, dir, queuedDir, speed, radius }
- ghosts[] each with:
  - type
  - x, y
  - dir
  - state
  - speed
  - target tile
  - frightened timer
  - release conditions
- globalModeSchedule
- globalModeTimer
- frightenedChainCount
- score / highScore / level / lives
- fruit state

Movement/pathing details:
- Positions should be pixel-based, but intersections and path validation come from tile centers.
- Actors move continuously along their current direction.
- Turning should usually only happen at or very near tile centers.
- Before entering a new tile, validate the target tile is traversable.
- Ghost house door can be treated as a special tile:
  - ghosts may cross it under specific states
  - Pac-Man may not

Important edge cases:
- Buffered turns must feel reliable.
- Pac-Man should not snag on corners.
- Ghosts should not jitter at intersections.
- Frightened mode should not affect eyes-returning ghosts.
- Eating a frightened ghost should not cancel frightened mode for others.
- Level reset after death must preserve eaten pellets.
- Full level reset only happens on new game or new level.
- Game over restart must fully reset score, lives, level, pellets, ghosts, timers, and fruit.

Title screen should make the game clear to someone who has never played:
- Navigate the maze.
- Eat every dot.
- Avoid ghosts.
- Large flashing dots let you eat ghosts briefly.
- Use tunnels to wrap side-to-side.
- Clear the maze to advance.

Acceptance checklist:
- On load, title screen is visible and readable.
- Pressing Enter starts the game.
- Pac-Man moves continuously through corridors with buffered turning.
- Maze contains 240 pellets including 4 power pellets.
- Eating pellets increments score correctly.
- Four ghosts exist with distinct targeting logic.
- Ghosts alternate between scatter and chase modes.
- Power pellets trigger frightened mode.
- Frightened ghosts can be eaten for escalating points.
- Left/right tunnel wrap works.
- Losing a life resets character positions but preserves remaining pellets.
- Clearing all pellets starts next level.
- Score, high score, lives, and level are displayed.
- High score persists via localStorage.
- P pauses and unpauses correctly.
- Entire implementation is contained in one self-contained HTML file with inline CSS/JS only and no external dependencies.
