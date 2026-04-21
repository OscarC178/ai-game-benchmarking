Build a classic Frogger-style lane-crossing arcade game as a single self-contained HTML file using HTML5 Canvas, with all CSS and JavaScript inline and no external libraries, images, fonts, audio files, or network requests.

Assume the developer has never played Frogger. The game is a top-down lane-crossing survival/puzzle arcade game. The player controls a frog trying to travel from the bottom of the screen to safety homes at the top. To do this, the frog must first cross a road full of moving vehicles, then cross a river using moving logs and turtles as temporary platforms. The frog dies if hit by traffic, falls in water, or runs out of time. Reaching all home slots clears the level.

The essential feel is:
- discrete lane-by-lane movement
- readable moving hazards
- simple but tense timing
- a split-stage challenge: road first, river second
- precise, grid-snapped movement
- increasing pressure from a countdown timer

The game should feel immediately understandable, tightly controlled, and visually segmented into distinct horizontal zones.

Canvas and coordinate system:
- Canvas size: 600×700 pixels.
- Background: black or very dark.
- Coordinate origin: top-left.
- Internal game logic should use this fixed size even if displayed responsively.

Grid and movement structure:
- The game should be built around a visible lane grid.
- Recommended row height: 50 pixels.
- The frog moves in discrete single-lane jumps, not smooth walking.
- The frog should always occupy a lane-aligned position.
- Horizontal movement also occurs in fixed increments, typically one grid unit.
- The feel should be crisp and snapped, not analog.

A strong default layout:
- 12 vertical rows of 50 px each = 600 px
- Use remaining top/bottom space for HUD and margins, or fold HUD into the top area
- Alternatively, use 13 or 14 logical rows if keeping objects centered more comfortably, but the important part is consistent grid-snapped lanes

Core objective:
- Move the frog from the bottom starting area to one of several home bays at the top.
- After entering a home bay, that home becomes filled/safe.
- Continue until all home bays are filled.
- Then start a new level with increased difficulty.
- Avoid cars/trucks on the road.
- Avoid drowning in water unless standing on a floating object.
- Beat the countdown timer on each frog attempt.

Player frog:
- Approximate size: 30×30 px or slightly smaller than a lane cell.
- Starting position: horizontally centered near the bottom lane.
- Color: bright green, though palette is flexible.
- Movement:
  - Up = jump up one row
  - Down = jump down one row
  - Left = jump left one column step
  - Right = jump right one column step
- Use Arrow keys and also support WASD.
- The frog should hop instantly or with a very short animation, but the movement must remain grid-snapped and discrete.
- The frog should not move continuously while a key is held; each input should cause one hop.
- It is acceptable to use keydown with a brief lockout/debounce so a held key does not create uncontrollable rapid movement.

Controls:
- Arrow keys or W/A/S/D = hop
- Enter = start game from title screen and restart after game over
- P = pause / unpause
- Optional: Space may also start/restart, but Enter is required

Zone layout:
The playfield should clearly read from bottom to top as:

1. Bottom safe start zone
- A safe strip where the frog begins.
- No hazards.

2. Road section
- Several horizontal lanes with moving cars/trucks.
- Entering a vehicle’s occupied space kills the frog.

3. Middle safe strip
- A safe divider between road and river.

4. River section
- Several horizontal lanes containing moving logs and turtles.
- The frog survives only if standing on a floating object.
- If in river lanes and not on a valid platform, the frog drowns.

5. Top home row
- Multiple home bays that the frog must fill.
- Reaching an unfilled home bay scores and locks it as complete.
- Reaching a filled/invalid bay should count as death or failed landing depending on design; death is closer to classic feel.

Recommended lane composition:
Bottom to top:
- Safe start row
- 5 road lanes
- Safe middle row
- 5 river lanes
- Home row

That gives the classic structure and is strongly recommended.

Vehicles (road section):
Include multiple vehicle types with different sizes, colors, and speeds.
Each lane moves either left or right.

Suggested vehicle types:
- Small car: about 50×32 px
- Sedan / taxi: about 60×32 px
- Truck: about 90×36 px
- Bulldozer / heavy vehicle: about 70×34 px

Behavior:
- Vehicles move continuously across their lane.
- When exiting one side of the screen, they wrap and re-enter from the other with spacing preserved.
- Different lanes should have different speeds and directions.
- Vehicles should be easy to distinguish visually.

Recommended road lane behavior:
- 5 lanes total
- Alternate directions by lane for readability
- Speeds roughly 60–160 px/s depending on lane
- Faster lanes should generally have slightly wider spacing
- Lane difficulty should vary; some lanes sparse but fast, others denser but slower

River section:
This is the other essential half of Frogger.

The frog cannot survive by standing directly in water.
Instead it must ride floating objects:
- logs
- turtles

Logs:
- Platforms of varying lengths
- Move horizontally
- Carry the frog with them if the frog is standing on them
- Wrap at screen edges and re-enter continuously

Turtles:
- Smaller floating platforms, often grouped
- Also move horizontally and carry the frog
- Some turtles should periodically dive underwater
- If the frog is on a turtle that submerges, the frog dies

Recommended river object types:
- Short log: ~90 px
- Medium log: ~130 px
- Long log: ~170 px
- Turtle group: ~70–100 px total
- Use a mix across lanes

Recommended river lane behavior:
- 5 lanes total
- Alternate directions across lanes
- Speeds roughly 50–140 px/s
- Some lanes have long safer logs
- Some lanes have shorter/more difficult turtles
- At least one lane should feature diving turtles for classic flavor

Carrying the frog:
When the frog is on a log or turtle:
- The frog’s x position should move along with that platform each frame
- The frog still remains conceptually lane-aligned vertically
- Horizontal carrying is continuous, not snapped
- If the carried frog moves completely off-screen, it dies
- This carried motion is a key part of Frogger feel

Home row:
At the top of the screen there should be 5 home bays.
These are the goals for the level.

Behavior:
- Each bay can be filled once.
- The frog must land inside an unfilled valid home bay to claim it.
- On success:
  - mark bay filled
  - award points
  - reset frog to start position
  - reset the per-life timer
- If frog lands in a gap between bays or in a filled bay, treat it as death.
- Once all 5 bays are filled:
  - award level-complete bonus
  - start next level
  - clear home occupancy
  - increase difficulty slightly

Time limit:
A countdown timer is essential.
Each individual frog attempt should have a limited amount of time to reach a home.

Recommended time:
- 45–60 seconds per frog attempt
- 50 seconds is a good default

Behavior:
- Timer decreases only during active play
- Timer resets when:
  - frog dies and respawns
  - frog successfully reaches a home bay
- If timer reaches zero before success, frog dies

Lives:
- Start with 3 lives.
- Each death removes one life.
- When lives remain:
  - reset frog to bottom start position
  - reset timer
- When lives reach 0:
  - game over
- Display lives clearly in HUD

Death conditions:
The frog dies if any of the following occur:
- collides with a vehicle
- enters a water lane and is not standing on a floating object
- rides a submerged turtle
- is carried off-screen in river lanes
- timer reaches zero
- lands in an invalid top-row location
- optionally: tries to enter an already occupied home bay

Game states:
1. Title screen
   - Visible on load
   - Show title “FROGGER”
   - Explain the objective plainly:
     - cross the road
     - ride logs/turtles across the river
     - reach all home slots
     - avoid traffic and water
   - Show controls
   - Show “Press Enter to Start”
2. Playing
   - Main gameplay
3. Paused
   - Freeze game and show “PAUSED”
4. Frog death / respawn moment
   - Brief pause or animation after death
5. Level clear transition
   - Brief message when all homes are filled
6. Game over
   - Show “GAME OVER”, score, and restart prompt

Scoring:
Use a simple classic-feeling scoring system:
- Successful hop upward: +10 points (optional but very traditional)
- Reaching a home bay: +50 or +100 points
- Bonus for remaining time when reaching home: add remaining timer value or a scaled bonus
- Completing all homes in level: bonus score
- High score persists in localStorage

A good readable system:
- +10 for each new forward row reached during a life
- +100 for reaching a home
- +remaining time bonus on home arrival
- +500 for clearing all 5 homes
This is flexible, but rewarding forward progress and home completions is important.

HUD:
At minimum display:
- Score
- High score
- Lives
- Level
- Timer
Suggested placement:
- Score top-left
- High score top-right
- Lives and Level near upper center
- Timer as a horizontal bar or number near top/bottom

A visible timer bar is strongly recommended because it communicates pressure at a glance.

Movement/input details:
- The frog should move one step per key press.
- Grid step size horizontally should align to lane logic and home bays.
- If using a 50 px row height, horizontal step can be 40 or 50 px depending on layout.
- The frog should not drift except when carried by logs/turtles.
- Prevent multi-hop chaos from key repeat by adding a small hop cooldown (e.g. 80–120 ms) or animating a hop over a very short duration.

Collision logic:
Road:
- Frog vs vehicle: AABB collision.
- If overlap, frog dies immediately.

River:
- In water lanes, first determine whether frog overlaps any floating platform.
- If yes:
  - frog survives
  - frog is carried by that platform’s horizontal velocity
  - if the platform is a submerged turtle state, frog dies instead
- If no:
  - frog dies

Top homes:
- Define 5 valid home landing regions.
- If frog enters the home row, check:
  - if inside unfilled home region => success
  - else => death

Safe rows:
- Bottom start row and middle safe strip are always safe.
- Optionally, the top boundary outside actual home targets is unsafe.

Turtle diving behavior:
This is strongly recommended for authenticity.
A simple cycle works well:
- visible afloat
- warning / partial submerge
- fully submerged
- resurfacing
During fully submerged state:
- frog cannot stand on them
- if frog is on them, frog dies
Use a repeating timer per turtle group or lane, ideally staggered so the whole lane does not vanish at once.

Level progression:
On each new level, increase difficulty slightly. Recommended levers:
- slightly faster vehicles
- slightly faster river objects
- shorter timer or same timer but more aggressive motion
- more turtle diving frequency
Do not increase difficulty too sharply; Frogger should remain readable.

Visual design:
- The playfield should clearly separate road, safe strips, water, and home row by color.
Suggested palette:
- Road: dark gray
- Water: dark blue
- Safe strips: dark green or black with grass accents
- Home bays: top green band with bay cutouts
- Vehicles: bright varied colors
- Logs: brown
- Turtles: green/teal
- Frog: bright green

Readability matters more than decorative detail.

Rendering recommendations:
- Lane separators help a lot.
- Small repeating road stripes or water texture are optional.
- Home bays should be visibly distinct recessed target zones.
- Filled home bays can show a tiny frog icon or filled marker.
- The frog should be easy to track against every background.

Audio:
- Optional but recommended.
- Use Web Audio API only.
- Suggested procedural sounds:
  - hop sound
  - splat/crash on road death
  - splash on drowning
  - home success jingle
  - level clear sting
- Audio must not be required and should only start after user interaction.

Implementation guidance:
Use requestAnimationFrame with delta time.
Clamp large frame gaps after inactivity.
Separate update and render logic.

Recommended state:
- gameState
- frog { x, y, row, col?, alive, hopCooldown }
- vehicles by lane
- river platforms by lane
- homeSlots[]
- score
- highScore
- level
- lives
- timerRemaining
- deathTimer / levelClearTimer

Recommended update order during play:
1. Handle input / frog hops
2. Update vehicles
3. Update logs/turtles
4. If frog is in river lane, apply carrying motion from overlapping platform
5. Check collisions / drowning / home arrival
6. Update timer
7. Handle deaths / level completion
8. Render

Important details:
- The frog should reset to the exact bottom starting position after death or successful home arrival.
- Progress scoring for upward hops should only count the furthest row reached during the current frog attempt, to avoid exploitative back-and-forth scoring.
- If the frog reaches the top row, validate home placement immediately.
- Carried horizontal movement should happen before screen-off checks.
- If the frog is partly carried beyond the screen edge, treat as death.
- Pause must freeze object motion, timer, and animations cleanly.
- Restart must fully reset homes, score, level, lives, timer, and all entity positions.

Title screen should make the concept crystal clear because the developer has never played it:
- Cross the road without getting hit.
- Cross the river by riding logs and turtles.
- Reach all 5 homes at the top.
- You die in water unless on a floating platform.
- You are racing the clock.

Acceptance checklist:
- On load, title screen is visible and readable.
- Pressing Enter starts the game.
- Frog moves in crisp grid-snapped hops with Arrow keys and WASD.
- Road lanes contain moving traffic that kills on contact.
- River lanes contain moving logs/turtles that carry the frog.
- Frog drowns if in water without a platform.
- At least some turtles can dive underwater.
- Top row has 5 home bays that can be filled one by one.
- Reaching a home resets frog and timer.
- Filling all home bays advances to next level.
- Timer counts down and causes death at zero.
- Lives decrease correctly; game over occurs at 0.
- Score, high score, lives, level, and timer are displayed.
- High score persists via localStorage.
- P pauses and unpauses correctly.
- Entire implementation is contained in one self-contained HTML file with inline CSS/JS only and no external dependencies.
