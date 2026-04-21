Build a classic Pong-style game as a single self-contained HTML file using HTML5 Canvas with all CSS and JavaScript inline. No external libraries, assets, fonts, sounds, or network requests.

The goal is a polished, immediately understandable two-paddle arcade game that feels like the original: minimalist, fast, readable, and fair. The player controls the left paddle. The computer controls the right paddle.

Core concept:
- Two vertical paddles hit a ball back and forth across the screen.
- If the ball passes a paddle and exits the playfield on that side, the opposing side scores a point.
- After a point, play pauses briefly, then the ball is served again from center.
- First side to 7 points wins the match.
- The game should support a title/start state, active play, pause, and game-over/restart.

Canvas and presentation:
- Canvas size: 800×600 pixels.
- Background: solid black.
- Coordinate system: origin at top-left.
- Render everything with simple crisp shapes.
- Maintain a retro arcade look: white paddles, white ball, white score digits, center divider.
- Use requestAnimationFrame for rendering and simulation.
- The game should visually scale in the browser while preserving aspect ratio, but the internal simulation should use the fixed 800×600 coordinate system.

Playfield layout:
- Left paddle starting position: x=32, y=258.
- Right paddle starting position: x=756, y=258.
- Paddle size: width=12, height=84.
- Ball size: 12×12 square.
- Ball starting position before serve: x=394, y=294.
- Center divider:
  - centered vertically down the middle of the screen
  - 4 px wide
  - dashed look: each dash 16 px tall with 10 px gap
- Top and bottom screen edges are solid collision walls.
- Left and right edges are scoring boundaries, not bounce walls.

Controls:
- Player paddle:
  - ArrowUp and ArrowDown
  - Also support W and S as alternate controls
- Enter:
  - Start game from title screen
  - Restart from game-over screen
- P:
  - Pause and unpause during active play
- Optional:
  - Space may also start/restart, but Enter is required
- Input should feel responsive and continuous while held.

Game states:
1. Title / attract screen
   - Shown on initial load
   - Displays game title “PONG”
   - Displays brief controls
   - Displays “Press Enter to Start”
   - No active scoring during this state
2. Serve / round reset
   - After starting a match or after each point, place paddles at starting y positions and ball at center
   - Wait a short moment before ball movement begins (recommended: 0.75s to 1.2s)
   - Show a subtle “READY” or countdown indicator if desired
3. Playing
   - Ball moves and collides
   - Paddles can move
   - Score updates when a point is won
4. Paused
   - Freeze gameplay and ball movement
   - Show pause overlay or text
5. Game over
   - Trigger when either side reaches 7 points
   - Display winner: “PLAYER WINS” or “CPU WINS”
   - Show final score
   - Show “Press Enter to Restart”

Player paddle behavior:
- Moves vertically only.
- Speed: 420 px/s.
- Must remain fully inside the canvas bounds.
- Movement should stop cleanly at top and bottom edges.
- No acceleration needed; direct velocity from input is fine.

CPU paddle behavior:
- Moves vertically only.
- Speed: 320 px/s.
- Starts at the specified position.
- Must remain fully inside the canvas bounds.
- Should feel beatable but competent.
- The CPU should not perfectly track the ball.
- Use a simple reaction-limited AI:
  - It tracks the ball’s y-position with a reaction delay of about 80 ms.
  - It should aim for the ball’s center, but with slight imperfection so it is not unbeatable.
  - Good behavior: update its target periodically instead of every frame, or add a small prediction error / dead zone.
- The CPU should only meaningfully react when the ball is moving toward it. When the ball is moving away, it can drift back toward center or hold position.

Ball behavior:
- Ball is a 12×12 square.
- Initial served speed: 340 px/s.
- On each serve, choose a horizontal direction toward either player or CPU depending on design preference:
  - Recommended: after a point, serve toward the side that lost the point
  - Acceptable alternative: randomize left/right
- Vertical launch angle must be randomized between -28° and +28° relative to pure horizontal travel.
  - In practice: mostly horizontal motion with mild vertical variance.
- Ball must always have meaningful horizontal velocity. Avoid near-vertical launches.
- On paddle hit:
  - Reverse horizontal direction.
  - Increase speed by 22 px/s.
  - Cap total speed at 620 px/s.
  - Adjust bounce angle based on where the ball hit the paddle:
    - Hits near paddle center produce shallow angles.
    - Hits near paddle ends produce steeper angles.
  - Preserve constant ball speed after recalculating direction.
- On top/bottom wall hit:
  - Reflect vertical velocity.
  - Clamp ball position so it does not stick into the wall.
- Prevent repeated multi-hit jitter when ball overlaps a paddle:
  - Reposition the ball just outside the paddle on collision.
  - Track last-hit side if needed.

Paddle-ball collision rules:
- Use AABB collision detection.
- Treat paddle collision only when the ball is moving toward that paddle.
- Compute bounce using impact offset:
  - Find relative hit position from -1 at top edge to +1 at bottom edge.
  - Convert that into an outgoing angle.
  - Recommended maximum bounce angle: around 60° from horizontal.
- Left paddle should always send ball rightward.
- Right paddle should always send ball leftward.
- Ball speed scaling after each paddle collision should preserve game difficulty ramp.

Scoring:
- Player score displayed on left side of the upper HUD area.
- CPU score displayed on right side of the upper HUD area.
- Start at 0–0.
- When ball exits left edge, CPU gains 1 point.
- When ball exits right edge, Player gains 1 point.
- After a point:
  - freeze ball
  - reset paddles to starting positions
  - center ball
  - start next serve after short delay
- First to 7 points wins immediately.
- Once game over begins, stop further movement and ignore score changes.

HUD / text:
- Title screen:
  - prominent game title
  - controls
  - start prompt
- In-game:
  - player score and CPU score clearly visible
  - optional small paused/help text
- Pause screen:
  - centered “PAUSED”
- Game-over screen:
  - centered win/lose message
  - final score
  - restart prompt
- Use a simple pixel-ish or monospace fallback stack already available in browser, but do not load fonts externally.

Audio:
- Optional but recommended.
- If included, generate sound procedurally with Web Audio API only.
- Suggested sounds:
  - short blip on paddle hit
  - different blip on wall hit
  - slightly lower tone on scoring
  - optional win/lose tones
- Audio must not be required for gameplay.
- Respect browser gesture requirements before starting audio context.

Polish expectations:
- The game should feel finished, not like a bare physics demo.
- Add subtle polish such as:
  - brief flash or delay after score
  - clear start and restart flow
  - stable motion using delta time
  - no clipping or jitter
- Keep visuals simple and readable rather than overdesigned.

Implementation guidance:
- Use requestAnimationFrame.
- Use delta time in seconds, clamped to avoid giant jumps after tab inactivity.
- Separate update and render logic.
- Recommended entities:
  - player paddle
  - cpu paddle
  - ball
  - score state
  - game state
- Keep all values in pixels and px/s or px/s² where relevant.
- Use deterministic logic where possible.
- Avoid frame-rate-dependent movement.

Edge cases to handle:
- Ball must not get stuck inside paddles or walls.
- Ball must not spawn moving almost straight up/down.
- Repeated key presses should not be required for paddle motion.
- Pause should truly freeze gameplay state.
- Restart should fully reset scores, paddles, ball, and state.
- Canvas should render cleanly even before the first game starts.
- CPU should not leave the play area.
- Player paddle should not drift when no input is held.

Acceptance checklist:
- On load, title screen is visible and readable.
- Pressing Enter starts a new match.
- Player can move paddle smoothly with Arrow keys and W/S.
- CPU paddle moves automatically and is beatable.
- Ball launches from center after a short serve delay.
- Ball bounces off paddles and top/bottom walls correctly.
- Paddle impact position changes bounce angle.
- Ball speeds up gradually with each paddle hit and caps correctly.
- Scoring works when ball exits left/right boundaries.
- Match ends when either side reaches 7.
- Pause works with P.
- Enter restarts from game over.
- Entire game exists in one HTML file with inline CSS/JS only and no external dependencies.
