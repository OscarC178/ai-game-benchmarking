Build a classic Donkey Kong-style single-screen platform arcade game as a single self-contained HTML file using HTML5 Canvas, with all CSS and JavaScript inline and no external libraries, images, fonts, audio files, or network requests.

Assume the developer has never played Donkey Kong. The game is a fixed-screen platformer in which the player controls a small human character climbing a construction site made of sloped girders and ladders. At the top of the stage, a large ape throws rolling barrels down the structure. The player must run, jump, and climb upward through hazards to reach the captive character at the top. The game’s identity comes from:
- a single static stage layout with multiple sloped platforms
- ladders connecting levels
- barrels rolling downward along the sloped girders
- careful jump timing
- temporary hammer pickups that let the player smash barrels
- a ticking bonus timer pushing the player upward
- a clear top-of-stage rescue goal

This should feel like an early arcade platform game: readable, punishing but fair, highly legible, and mechanically simple.

Canvas and presentation:
- Canvas size: 700×800 pixels.
- Background: black.
- Coordinate origin: top-left.
- Use this fixed internal resolution even if the canvas is visually scaled responsively.
- The whole game takes place on a single screen with no camera movement.
- Visual style should be simple but vivid:
  - bright red/pink girders
  - blue ladders
  - dark background
  - small pixel-art or vector characters
- The layout should read clearly at a glance: bottom start area, stacked sloped girders, ladders, ape at top-left, captive at top-center/right.

Core objective:
- Control Mario (or “the player character”) from the lower-left starting area.
- Climb up the stage using girders and ladders.
- Avoid or survive rolling barrels.
- Optionally collect hammer pickups for temporary offense.
- Reach Pauline at the top platform to clear the stage.
- Score points by jumping over barrels, smashing barrels with hammer, and clearing the stage quickly.
- Lose a life when hit by a barrel or other hazard.
- Game over at 0 lives.

Stage layout:
The stage should be a single built-in map, not procedural.

Use a classic construction-site composition:
- six major girder platforms stacked vertically
- each girder around 12 px thick
- most girders slope alternately left-up/right-up as they ascend
- ladders connect levels, with a few broken ladders that can be climbed only partway or not at all
- ape is positioned on a top platform at upper-left
- captive / goal character is near upper-middle/right on the same top platform
- oil drum is near the bottom-left area
- player starts on the bottom girder near the left side

A good default stage layout:
- Bottom girder spanning nearly full width, sloping slightly upward from left to right
- Next girder above it sloping opposite direction
- Continue alternating slopes as the stage rises
- Top girder flatter or only slightly sloped
- Ladder network should force route choices but remain traversable

You do not need exact arcade geometry, but the stage must visually and mechanically support:
- running on sloped girders
- climbing between them
- barrels rolling “downhill” in believable directions
- a clear path from bottom to top

Stage objects and approximate placements:
Player character:
- Size: 24×32 px
- Start position: around x=80, y=710
- Colors: red shirt, blue overalls, skin-tone face/hands
- Must feel nimble but slightly weighty

Donkey Kong / ape:
- Size: about 64×56 px
- Start position: around x=100, y=80
- Mostly stationary on top platform
- Animates a barrel-throw loop

Pauline / captive:
- Size: about 20×32 px
- Position: around x=310, y=38
- Static at goal platform
- Blink “HELP!” text above or near her

Oil drum:
- Position: bottom-left near x=40, y=736
- Decorative but meaningful as the lower barrel destination area
- Optional small flame effect

Girders:
- Bright pink/red main beams with darker edge details
- Should visually show slope and rivets
- The player stands on their top surfaces

Ladders:
- Width: about 20 px
- Cyan/light-blue
- Several full ladders connecting levels
- Some broken ladders that cannot be fully climbed
- Ladder placement should create a recognizable climbing puzzle, not random stairs

Hammer pickups:
- Two pickups on mid-level platforms
- Visible as yellow hammer icons
- One on a lower-middle platform
- One on an upper-middle platform
- Collecting one grants temporary hammer mode

Controls:
- ArrowLeft / A = move left
- ArrowRight / D = move right
- ArrowUp / W = climb up ladder
- ArrowDown / S = climb down ladder
- Space = jump
- Enter = start from title screen and restart after game over
- P = pause / unpause

Player movement:
Running:
- Horizontal speed: 150 px/s
- Movement only along current girder surface when grounded
- Character should remain aligned to the sloped platform while walking

Jumping:
- Jump velocity: -340 px/s
- Gravity: 900 px/s²
- Jump arc should be short and committed, not floaty
- Player can jump only when grounded and not using hammer
- Jumping should allow:
  - clearing rolling barrels
  - traversing small gaps where appropriate
- No double jump

Climbing:
- Vertical climb speed: 120 px/s
- Climbing is possible only when overlapping a climbable ladder and moving up/down
- While climbing:
  - horizontal running is disabled
  - gravity is effectively suspended
  - the character aligns to ladder center
- Exiting a ladder onto a platform should feel clean, not jittery
- Broken ladders should visually exist but not allow full traversal

Grounding and slopes:
This is crucial to the feel.
The player should stand on sloped girders and follow their surface naturally.
Implementation guidance:
- Treat each girder as a line segment with thickness
- Compute the top-surface y-position at the player’s x
- When grounded on that girder, snap player’s feet to the girder surface
- If the player walks off the horizontal bounds of a platform or jumps, gravity takes over
- Moving between girders should be consistent and stable

Ladder alignment:
- When the player begins climbing, snap x to ladder center
- Only allow entering a ladder when close enough horizontally and positioned near its usable span
- If using broken ladders:
  - they may have a visible top portion but only part of their vertical span is climbable
  - player cannot pass the broken gap

Barrels:
Barrels are the main moving hazard.

Appearance:
- Size: 18×18 px
- Brown/orange with hoop lines

Spawn behavior:
- Donkey Kong throws/spawns barrels periodically from the top platform
- Repeating timer between spawns, roughly every 2 to 4 seconds, getting a little faster on later stages
- Spawn point near DK’s hands on the top platform

Movement:
- Barrels roll along girders in the downhill direction of that platform
- When they reach edges or valid drop points, they can:
  - continue falling to the next platform
  - descend ladders in selected cases
- They should create believable classic pressure, not random teleports

A good simplified barrel model:
- Each barrel knows which platform it is currently on
- While rolling:
  - move horizontally according to that platform’s slope direction
  - vertically align to the platform surface
- At a platform edge:
  - fall to the next platform below and continue rolling
- Occasionally, if crossing a ladder, choose to descend that ladder instead of continuing across
- Remove barrels when they reach the bottom/oil drum area or leave valid play space

Recommended barrel behavior details:
- Roll speed: around 120 px/s initially
- Slightly increase with stage/level
- Ladder descent chance: low but noticeable, e.g. some percentage when passing designated ladders
- Barrel gravity while falling between platforms should be faster than player jumping gravity or at least visually decisive
- Barrels should remain one of the primary route-denial forces

Collision with barrels:
- If player touches a barrel and does not have hammer mode, lose a life
- If hammer mode is active, touching a barrel destroys the barrel and awards points
- Collisions should use AABB and be reliable

Jumping over barrels:
This is a key scoring mechanic.
If the player jumps cleanly over a rolling barrel:
- award +100 points
- only count once per barrel per jump
- easiest implementation:
  - while player is airborne descending or midair
  - if player horizontally passes above a barrel within a close range
  - and the barrel has not already awarded jump points for that jump
- The jump-over reward should feel deliberate and not trigger randomly from standing near a barrel

Hammer mode:
Strongly recommended. It is a defining Donkey Kong mechanic.

Pickup:
- Two hammer pickups placed on mid-level platforms
- When player touches one:
  - pickup disappears
  - player enters hammer mode for a limited duration, about 8 seconds

Behavior during hammer mode:
- Player swings hammer in an obvious animation
- Jumping is disabled during hammer mode
- Colliding with a barrel destroys the barrel instead of hurting the player
- Each smashed barrel awards +300 points
- Hammer mode expires automatically after timer ends

Visual:
- Hammer should orbit or swing above/beside player
- Animation can alternate between two positions

Stage goal:
At the top platform is Pauline, the rescue target.
To clear the stage:
- player reaches the goal zone near Pauline
- award stage-clear points, e.g. +1000
- also add remaining bonus timer value
- then start next stage / next level
- reset player, barrels, hammer pickups, and bonus timer
- preserve score and lives

Bonus timer:
A countdown bonus is essential to the feel.
- Start each stage with a bonus value, e.g. 5000
- Decrease over time during active play
- Display it prominently in HUD
- If player clears the stage, award remaining bonus
- If desired, reaching zero can simply continue at zero, or it can cost a life for extra pressure; either is acceptable, though a life loss at zero is a nice arcade touch
- Bonus timer encourages upward momentum instead of stalling

Lives:
- Start with 3 lives
- Display lives clearly in HUD
- Small player-head icons or numeric count is fine
- On death:
  - lose one life
  - reset player position to the bottom start
  - clear active barrels or at least reset dangerous local state
  - preserve score and current stage progress
- If lives reach 0:
  - game over

Game states:
1. Title screen
   - Visible on load
   - Show title “DONKEY KONG”
   - Explain the premise plainly:
     - climb the girders
     - avoid barrels
     - use hammers
     - reach the captive at the top
   - Show controls
   - Show “Press Enter to Start”
2. Playing
   - Main gameplay active
3. Paused
   - Freeze motion and show “PAUSED”
4. Death / respawn state
   - Brief player death animation or flash
5. Stage clear transition
   - Brief “STAGE CLEAR!” or equivalent before next stage
6. Game over
   - Show “GAME OVER”, final score, restart prompt

Scoring:
A solid classic-feeling system:
- Jump over barrel: +100
- Smash barrel with hammer: +300
- Reach Pauline / clear stage: +1000
- Add remaining bonus timer on stage clear
- High score should persist in localStorage

HUD:
Display at minimum:
- Score
- High score
- Lives
- Level / Stage
- Bonus timer

Suggested placement:
- Score: top-left
- High score: top-right
- Lives: upper-left/upper-right row or lower corner
- Bonus timer: top-center or just below top HUD
- Level: near HUD text
Keep the top portion readable without obscuring stage geometry.

Enemy / hazard pacing:
Donkey Kong should feel like a pressure game, not chaos.
- Early stage should start manageable
- Barrel cadence and movement should create route choices and force timing
- Higher stages can become more intense by:
  - faster barrel spawn rate
  - faster barrel roll speed
  - slightly less forgiving timer
Do not add too many enemy types unless you want extra polish; a solid barrel-focused stage is sufficient.

Optional extras if desired, but not required:
- fireball hazard emerging from oil drum
- jumping springs / pies in alternate stages
- animated DK pounding or laughing
- Pauline blinking / bouncing
- rivet details and decorative construction beams
These are nice, but the baseline game should focus on the main 25m-style barrel stage.

Visual style guidance:
- Use high-contrast arcade colors
- Girders should be bright and readable
- Ladders should stand out as climbable routes
- Barrels should be easy to track
- The player must always be visually distinct from hazards and background
- DK and Pauline should anchor the goal visually at the top

Audio:
- Optional but recommended
- Use Web Audio API only
- Suggested sounds:
  - jump tone
  - hammer rhythmic ticking
  - barrel smash hit
  - player death descending tone
  - stage clear jingle
- Audio must not be required and should only activate after user interaction

Implementation guidance:
Use requestAnimationFrame with delta time.
Clamp large frame gaps after tab inactivity.
Separate update and render logic clearly.

Recommended state/entities:
- gameState
- player
- barrels[]
- hammer pickups[]
- score
- highScore
- lives
- level/stage
- bonusTimer
- platforms[]
- ladders[]
- dk state (barrel spawn timer, throw anim)
- pauline state (blink/help text)

Recommended player state:
- x, y
- vx, vy
- width, height
- onGround
- currentPlatform
- climbing
- ladder
- facing
- hammerTime
- jumpId / jump scoring id

Recommended barrel state:
- x, y
- width, height
- platformId or current segment
- direction
- vertical velocity if falling
- state: rolling / falling / ladder
- set of jump-score flags if needed

Collision guidance:
Use AABB for player, barrels, pickups, and goal.
For grounding:
- use girder surface calculation instead of raw AABB standing checks
For ladders:
- treat ladder overlap with a small alignment threshold around center
For barrel jump scoring:
- detect one-time midair pass over a barrel using player and barrel relative positions plus a per-jump/per-barrel guard

Important behavior details:
- Player should not jitter when walking on slopes.
- Climbing transitions should be forgiving; being near a ladder should usually be enough.
- Barrels should not get stuck at platform edges.
- Hammer mode should be obvious and temporary.
- Stage reset after death should feel clean and not trap the player immediately.
- Clearing the stage should reset barrels and pickups.
- Restart after game over must fully reset score, lives, level, barrels, timer, and pickups.

Title screen should explain the game clearly because the developer has never played:
- You are climbing a construction site.
- Donkey Kong throws barrels from above.
- Jump over them or smash them with a hammer.
- Climb ladders and reach the captive at the top.
- You are racing the bonus timer.

Acceptance checklist:
- On load, title screen is visible and readable.
- Pressing Enter starts the game.
- Player can run left/right on sloped girders and jump.
- Player can climb ladders up and down without jitter.
- Donkey Kong repeatedly spawns barrels from the top platform.
- Barrels roll down the stage in believable downhill paths.
- Barrel collision causes life loss unless hammer mode is active.
- Hammer pickups grant temporary barrel-smashing ability.
- Jumping over barrels awards score.
- Reaching Pauline clears the stage and starts the next stage.
- Bonus timer counts down and contributes to stage-clear scoring.
- Score, high score, lives, level, and bonus timer are displayed.
- High score persists via localStorage.
- P pauses and unpauses correctly.
- Game over occurs at 0 lives.
- Entire implementation is contained in one self-contained HTML file with inline CSS/JS only and no external dependencies.
