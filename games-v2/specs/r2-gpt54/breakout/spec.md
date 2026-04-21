Build a classic Breakout-style arcade game as a single self-contained HTML file using HTML5 Canvas, with all CSS and JavaScript inline and no external assets, libraries, fonts, or network requests.

The developer should assume they have never seen Breakout before. The game is a paddle-and-ball brick-clearing game viewed from the side/front as a flat rectangular playfield. The player controls a horizontal paddle at the bottom of the screen. A ball bounces around the arena, breaking bricks near the top. The player must keep the ball from falling below the paddle. Clearing all bricks advances to the next level. Losing all lives ends the game.

The feel should be simple, crisp, readable, and arcade-clean. The fun comes from maintaining control of the ball, steering its reflection angle off the paddle, and methodically clearing the brick wall.

Core objective:
- Use the paddle to keep the ball in play.
- Bounce the ball upward into a grid of bricks.
- Each time the ball hits a brick, that brick disappears and the score increases.
- Clear all bricks to advance to the next level.
- Start with 3 lives.
- Lose a life whenever the ball falls below the bottom edge.
- Game over when lives reach 0.

Canvas and coordinate system:
- Canvas size: 800×600 pixels.
- Background: solid black.
- Coordinate origin: top-left.
- All gameplay uses this fixed internal resolution.
- The canvas may be scaled responsively in the browser, but aspect ratio and internal coordinates must remain unchanged.

Playfield layout:
- The paddle sits near the bottom.
- The ball begins attached above the paddle until launched.
- A wall of colored bricks occupies the upper portion of the screen.
- Left, right, and top edges are solid bounce walls.
- Bottom edge is an out-of-bounds fail zone, not a bounce wall.

Paddle:
- Size: 104×14 pixels.
- Color: white.
- Starting position: x=348, y=560.
- Movement: horizontal only.
- Speed: 520 px/s.
- Clamp fully inside screen bounds.
- Paddle should feel responsive and precise.
- No inertia needed; direct motion from held input is correct.

Ball:
- Shape: circle.
- Radius: 8 pixels.
- Color: white.
- Starting position before launch: centered above paddle at x=400, y=548.
- Initial state: attached to paddle until launch.
- On launch:
  - speed = 340 px/s
  - direction is upward with a random angle between 240° and 300° if using standard mathematical angles, or equivalently between upper-left and upper-right travel with no near-horizontal launch
  - the intent is: the ball must leave the paddle going upward, with a moderate horizontal component
- The ball should reflect off walls, paddle, and bricks cleanly.
- Ball speed increases by 20 px/s whenever the player advances to a new level.
- Maximum ball speed: 520 px/s.
- Keep speed constant during normal flight within a level unless design requires tiny adjustments for collision robustness.

Bricks:
- Layout: 10 columns × 6 rows.
- Brick size: 70×20 pixels.
- Top-left brick position: x=19, y=52.
- Horizontal spacing should make the 10 columns fit evenly with consistent gaps based on those dimensions and origin.
- Vertical spacing should be tidy and readable; a small gap between rows is recommended.
- Brick colors by row from top to bottom:
  1. red
  2. orange
  3. yellow
  4. green
  5. blue
  6. purple
- Bricks are single-hit: one ball impact removes the brick.
- No special bricks, powerups, or multi-hit variants unless kept extremely restrained; the baseline game should remain faithful and simple.

Controls:
- Left / Right arrows move paddle.
- Also support A / D.
- Space launches the ball when attached to the paddle.
- Enter starts a new game from title screen and restarts from game over.
- P pauses and unpauses.
- Optional: Enter may also launch if the ball is attached, but Space is the required launch control.

Game states:
1. Title screen
   - Visible on load.
   - Shows title “BREAKOUT”.
   - Shows controls/instructions briefly.
   - Shows “Press Enter to Start”.
2. Playing
   - Ball active or attached between lives.
   - Paddle controllable.
   - Bricks visible.
   - Score/lives/level visible.
3. Paused
   - Freeze gameplay and show pause text.
4. Life lost / ready state
   - When the ball falls below the screen:
     - decrement lives
     - if lives remain, reset paddle and attach a new ball above it
     - wait for launch input again
5. Level clear transition
   - When all bricks are destroyed:
     - increment level
     - rebuild brick wall
     - increase ball speed for the new level, up to cap
     - reset paddle and attached ball before relaunch
6. Game over
   - When lives reach 0.
   - Show “GAME OVER”, final score, and restart prompt.

Ball-paddle interaction:
- This is crucial to the feel of Breakout.
- The outgoing bounce angle should depend on where the ball hits the paddle:
  - center hit sends ball mostly straight upward
  - left edge sends ball up-left
  - right edge sends ball up-right
- The player should be able to intentionally aim the ball.
- Recommended approach:
  - compute hit offset from paddle center in range [-1, +1]
  - map that to an outgoing angle up to about 60° from vertical or equivalently about ±60° from straight up
- Ensure the resulting vertical direction is always upward after paddle collision.
- Reposition the ball above the paddle after collision to prevent sticking or double-collisions.
- Ignore paddle collision if ball is already moving upward away from paddle.

Wall collisions:
- Left wall: reflect x velocity.
- Right wall: reflect x velocity.
- Top wall: reflect y velocity.
- Bottom edge: lose life; no reflection.

Brick collisions:
- Use straightforward AABB / circle-vs-rect collision handling.
- Determine whether the collision should invert horizontal or vertical velocity based on overlap depth or previous position.
- Remove exactly one brick per collision unless you intentionally implement robust multi-hit-through behavior; simplest correct behavior is one brick removed per contact.
- Score increases when a brick is destroyed.
- Recommended score values:
  - Top rows worth more than lower rows, or
  - Flat score per brick.
- If you want a classic-feeling scheme, row values are a nice touch:
  - red: 70
  - orange: 50
  - yellow: 40
  - green: 30
  - blue: 20
  - purple: 10
- Flat +10 or +50 per brick is also acceptable if consistent, but row-based scoring better reflects arcade feel.

Lives:
- Start with 3.
- Display lives clearly in HUD.
- Losing a ball subtracts one life.
- If lives remain, reset to attached-ball state.
- If no lives remain, transition to game over.

Level progression:
- Level starts at 1.
- Clearing all bricks advances to next level.
- Recreate the same brick layout for each level.
- Increase ball speed by 20 px/s per level, capped at 520 px/s.
- Optionally make visuals slightly more energetic per level, but keep rules simple.
- Preserve score and remaining lives across levels.

Scoring:
- Start at 0.
- Increase score when bricks are destroyed.
- Display score at top-left.
- Display high score at top-right and persist it using localStorage.
- Update high score whenever surpassed.
- Optionally award a modest bonus for clearing a level, but this is not required.

HUD:
At minimum display:
- Score
- High score
- Lives
- Level

Suggested placement:
- Score: top-left
- High score: top-right
- Lives and Level: near top center or beneath score/high score
Keep everything readable but not distracting from the playfield.

Visual style:
- Minimalist retro arcade.
- Black background, white paddle/ball, brightly colored bricks.
- Optional subtle brick outlines or shine.
- Optional faint particle flash or tiny screen shake on brick hit, but do not overcomplicate.
- The player should instantly understand:
  - where the paddle is
  - where the ball is
  - which bricks remain
  - whether the ball is attached or active

Title screen should explain the game in plain terms because the developer has not played it:
- “Bounce the ball with the paddle.”
- “Break all bricks to clear the level.”
- “Don’t let the ball fall.”
- Controls.
- Start prompt.

Attached-ball behavior:
- At the beginning of a game and after losing a life, the ball should rest centered above the paddle.
- While attached, it moves horizontally along with the paddle.
- The game waits for Space to launch.
- This state should be obvious visually, either via a small “Press Space” prompt or just the visible attached ball on the paddle.

Pause behavior:
- P toggles pause during active play and attached-ball state.
- While paused:
  - no ball movement
  - no paddle movement updates unless you intentionally allow paddle movement while paused (better not to)
  - no timers advance
  - show pause overlay

Audio:
- Optional but recommended.
- If included, generate with Web Audio API only.
- Suggested sounds:
  - short blip on wall hit
  - distinct blip on paddle hit
  - sharper pop on brick break
  - lower tone on life lost
  - short success phrase on level clear
- Audio must be optional and must not block gameplay.
- Audio context should begin only after user interaction.

Implementation guidance:
- Use requestAnimationFrame.
- Use delta time in seconds.
- Clamp large frame deltas to avoid giant jumps after tab switching.
- Separate update and render logic cleanly.
- Keep entities simple:
  - paddle
  - ball
  - brick array/grid
  - score/lives/level/state
- For the attached-ball state, ball x should track paddle center and ball y should sit just above paddle.

Collision robustness:
- Ball should not tunnel through thin bricks at high speed.
- Since speeds are moderate, careful per-frame collision is usually sufficient, but still implement sensible collision resolution.
- Reposition the ball after collisions so it does not remain embedded in bricks or walls.
- If overlap is ambiguous, choose a stable resolution rather than a visually noisy one.
- The game should never let the ball get stuck bouncing inside a brick or paddle.
- Consider using previous ball position to help infer collision side.

Recommended update order:
1. Handle input / paddle movement
2. If ball is attached, update ball position relative to paddle
3. If ball is active:
   - advance ball by velocity * dt
   - resolve wall collisions
   - resolve paddle collision
   - resolve brick collision(s)
   - check bottom out-of-bounds
4. Check level clear
5. Update HUD/high score state

Important details for feel:
- Paddle movement should be precise enough that the player feels in control of ball angle.
- Ball launch should never be too vertical or too horizontal.
- The first few seconds of a game should be easy to read.
- Brick spacing and color should make progress visually satisfying.
- Losing a life should be clear and calm, not confusing.
- Restarting should fully reset score, level, lives, bricks, paddle, and ball state.

Suggested acceptance checklist:
- On load, title screen is visible and readable.
- Pressing Enter starts the game.
- Paddle moves smoothly left/right with arrows and A/D.
- Ball begins attached above paddle.
- Pressing Space launches the ball upward.
- Ball bounces off top/left/right walls correctly.
- Ball bounces off paddle and angle changes based on hit position.
- Ball destroys bricks on contact.
- Score increases correctly.
- Losing the ball decreases lives and resets to attached-ball state if lives remain.
- Clearing all bricks advances to next level and increases ball speed.
- Game over occurs at 0 lives.
- Enter restarts after game over.
- High score persists via localStorage.
- Entire implementation is contained in one self-contained HTML file with inline CSS/JS only and no external dependencies.
