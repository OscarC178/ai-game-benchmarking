# Game Spec: Pong

## 1. Overview

Pong (Atari, 1972) — the original arcade video game. Two paddles on opposite sides of the screen, one ball. Each player defends their edge. If the ball gets past your paddle, your opponent scores a point. First to 11 wins the match.

The game is mechanically trivial but the *feel* is everything. The ball must accelerate over rallies to build tension. Where you strike the ball on your paddle must control the return angle — this is the only skill expression in the game. Get these two things right and it's satisfying. Get them wrong and it's a screensaver.

## 2. Canvas & Rendering

- Canvas size: 858×525px
- Background: #000000
- Frame rate: 60 FPS via `requestAnimationFrame` with delta-time
- Coordinate system: origin top-left
- Everything is white on black. No gradients, no color, no anti-aliasing tricks. Pong's visual identity is stark monochrome.

## 3. Game Objects

### Court

- **Boundaries:** Full canvas area
- **Top wall:** y = 0 — ball bounces off
- **Bottom wall:** y = 525 — ball bounces off
- **Left edge:** x = 0 — if the ball crosses this, Player 2 scores
- **Right edge:** x = 858 — if the ball crosses this, Player 1 scores
- **Center line:** Vertical dashed line at x = 429. Rendered as a column of filled white rectangles, each 4px wide × 12px tall, spaced 12px apart (12px visible, 12px gap). Color: #FFFFFF

### Paddles

- **Dimensions:** 14px wide × 90px tall
- **Color:** #FFFFFF
- **Left paddle (P1):** Left edge at x = 30
- **Right paddle (P2/AI):** Right edge at x = 828 (left edge at x = 814)
- **Starting y:** Vertically centered — y = 217.5 (paddle midpoint at y = 262.5)
- **Movement speed:** 380px/s
- **Clamping:** Paddle top cannot go above y = 0; paddle bottom cannot go below y = 525. Clamp y to range [0, 435].

### Ball

- **Shape:** Square, 14×14px. Classic Pong used a square cathode-ray dot, not a circle.
- **Color:** #FFFFFF
- **Rest position:** Center of court (x = 422, y = 255.5)
- **Starting speed:** 280px/s
- **Speed increment:** +30px/s every time the ball strikes a paddle
- **Maximum speed:** 550px/s
- **Serve direction:** Toward the player who conceded the last point (random for the opening serve). Random vertical angle between −35° and +35° from the horizontal.

Velocity calculation on serve:
```
angle = random(-35°, +35°)
vx = speed × cos(angle) × horizontalDirection   // +1 = right, -1 = left
vy = speed × sin(angle)
```

## 4. Controls

| Key | Action |
|-----|--------|
| W | P1 paddle up |
| S | P1 paddle down |
| ArrowUp | P2 paddle up (two-player mode) |
| ArrowDown | P2 paddle down (two-player mode) |
| Enter | Start / Restart |
| 1 | Select one-player mode (title screen) |
| 2 | Select two-player mode (title screen) |
| P | Pause / Unpause |

Use a persistent key-state map (updated by `keydown`/`keyup` listeners). On every frame, check the map and apply movement. This prevents dropped or stuck inputs that plague event-driven movement.

Both players can hold their keys simultaneously without conflict.

## 5. Physics

### Ball ↔ Top/Bottom Walls

Reflect vy: `vy = -vy`. Clamp the ball back inside bounds so it doesn't sink into the wall on the next frame.

### Ball ↔ Paddles

This is the core mechanic. Every other collision is trivial — this one makes or breaks the game.

**Detection:** Each frame, check if the ball overlaps a paddle's bounding box. At high speeds, the ball can pass through a paddle in a single frame. To prevent this, use sweep detection: if the ball's x-velocity would carry it past the paddle's x-plane this frame, calculate where the ball *would* have been at the moment it crossed that plane and test against the paddle's y-range at that instant.

Concretely, for the left paddle:
```
if ball was right of paddle last frame AND ball is left of paddle this frame:
    t = (paddleRightEdge - ball.prevX) / (ball.x - ball.prevX)
    ballYAtCrossing = ball.prevY + t × (ball.y - ball.prevY)
    if ballYAtCrossing overlaps paddle y-range → collision
```

**Angle response on hit:**

1. Calculate where the ball hit the paddle as a ratio from −1 (top edge) to +1 (bottom edge):
   ```
   hitRatio = (ballCenterY - paddleCenterY) / (paddleHeight / 2)
   clamp to [-1, 1]
   ```

2. Map to an outgoing angle: `angle = hitRatio × 65°`. Hitting dead center returns flat, hitting the extreme edge returns at 65° from horizontal. The 65° ceiling prevents near-vertical shots that would take forever to cross the court.

3. Apply to velocity:
   ```
   vx = speed × cos(angle) × direction   // direction = +1 heading right, -1 heading left
   vy = speed × sin(angle)
   ```

4. Increase speed by 30px/s (capped at 550).

5. Reposition the ball so it sits just outside the paddle face. This prevents double-triggering.

**Why this matters:** If you use simple geometric reflection (angle-in = angle-out), the player has zero control over the ball. The game becomes pure reaction speed — whoever is faster wins every time. The hit-position-based angle system means the player can *aim*. They can place the ball high, low, center. They can wrong-foot the opponent. This is Pong's entire skill ceiling.

### Ball Past Left/Right Edges (Scoring)

- Ball center passes x < −10: Player 2 scores
- Ball center passes x > 868: Player 1 scores

Use a small margin beyond the edge so the ball visually exits the screen before the point triggers. It feels wrong if the ball vanishes exactly at the boundary.

After a point:
1. Freeze for 1.2 seconds (both paddles and ball frozen, new score displayed)
2. Reset ball to center
3. Reset ball speed to 280px/s
4. Paddles remain where they are (do NOT reset to center — this punishes players who drift to one side)
5. Serve toward the player who was scored on

## 6. AI (Single-Player Mode)

The AI controls the right paddle. The design goal: an opponent that feels human-like — competent, sometimes brilliant, sometimes wrong. Not a perfect tracking robot.

**When the ball moves toward the AI (vx > 0):**
- Predict where the ball will arrive at the paddle's x-column, accounting for wall bounces (simulate the ball's trajectory forward, reflecting off top/bottom as needed, until it reaches the paddle's x)
- Add a random offset of ±35px to the predicted y-position. This offset is recalculated each time the ball is hit by the player (i.e., each time the AI needs to form a new prediction). Between recalculations, the AI commits to its (possibly wrong) prediction.
- Move toward the predicted y at 320px/s (slower than the human's 380px/s — this is the fairness lever)
- Dead zone: don't move if the target is within 8px of paddle center (prevents jitter)

**When the ball moves away (vx < 0):**
- Drift lazily toward vertical center (y = 217.5) at 100px/s
- This simulates a human relaxing between shots and creates windows of vulnerability after wide-angle serves

**Why 320px/s and not 380px/s:** The AI has perfect prediction (minus the random offset). If it also had equal speed, it would be nearly unbeatable. The speed deficit means the player can beat the AI by hitting sharp angles — the AI knows where the ball is going but sometimes can't get there in time. This creates a satisfying skill dynamic: hit the center of the paddle for safe returns, or risk the edges for winning shots.

## 7. Scoring

- **Points to win:** 11
- **Win by 2:** No. First to 11, period. (The original Pong used fixed-score victory.)
- **Score display:** Each player's score rendered as large retro-style segmented digits on their half of the court, above the center line area

### Retro Digit Rendering

Don't use `fillText` for scores. Render them as chunky bitmap digits for the authentic look.

Define each digit (0–9) as a 3×5 boolean grid. Each active cell is a filled 10×10px square with 3px gaps between cells. This produces a single digit roughly 36px wide × 62px tall.

```
0: ###    1: .#.    2: ###    3: ###    4: #.#    5: ###
   #.#       .#.       ..#       ..#       #.#       #..
   #.#       .#.       ###       ###       ###       ###
   #.#       .#.       #..       ..#       ..#       ..#
   ###       .#.       ###       ###       ..#       ###

6: ###    7: ###    8: ###    9: ###
   #..       ..#       #.#       #.#
   ###       ..#       ###       ###
   #.#       ..#       #.#       ..#
   ###       ..#       ###       ###
```

Player 1 score: centered at approximately x = 300, y = 40 (top area, left of center).
Player 2 score: centered at approximately x = 558, y = 40 (top area, right of center).

## 8. Game States

```
TITLE  →  SERVE  →  PLAYING  →  SCORED  →  SERVE (or MATCH_OVER)
                       ↕
                    PAUSED
MATCH_OVER → TITLE
```

### TITLE

- "PONG" displayed centered, y ≈ 160, 80px bold monospace, #FFFFFF
- Below: "1 PLAYER" and "2 PLAYERS" stacked, 26px, #CCCCCC. The currently highlighted option has a "▸" marker to its left. Press 1 or 2 (or Up/Down to toggle and Enter to confirm).
- Below: controls hint — "W/S and ↑/↓ to move paddles" — 14px, #555555
- **Attract mode:** Behind the text, a ball bounces around the court endlessly (no paddles, just wall bounces, purely decorative). Renders at 50% opacity so it doesn't compete with the text.
- The center net renders at full opacity. Scores show "0" and "0".

### SERVE

- Court, paddles, and net all render. Ball at center.
- "READY" displayed centered for 1.5 seconds, 36px, #FFFFFF
- Ball is then served automatically (no player input needed to serve). Transition to PLAYING.

### PLAYING

- All physics, input, and AI active
- P → PAUSED

### PAUSED

- Everything freezes (ball, paddles, timers)
- Overlay: #000000 at 50% opacity
- "PAUSED" centered, 40px, #FFFFFF
- P resumes

### SCORED

- Point awarded, score display updates immediately
- Ball disappears
- 1.2-second freeze
- If either player has 11 → MATCH_OVER
- Otherwise → SERVE

### MATCH_OVER

- Final scores remain displayed
- "PLAYER {1 or 2} WINS" centered, 40px, #FFFFFF
- If single-player: "YOU WIN" or "COMPUTER WINS" instead
- "Press Enter to play again" 20px, #AAAAAA, blinking at 2Hz
- Enter → TITLE

## 9. Audio

Generate all sounds via Web Audio API. Instantiate `AudioContext` on the first user interaction (to satisfy browser autoplay restrictions).

| Event | Sound | Implementation |
|-------|-------|----------------|
| Paddle hit | Sharp high blip | 480Hz square wave, 45ms, gain 0.3 |
| Wall bounce | Softer low blip | 240Hz square wave, 30ms, gain 0.2 |
| Point scored | Low punchy tone | 160Hz square wave, 250ms, gain 0.3 |
| Match won (winner) | Victory chime | Two notes ascending: 660Hz 70ms → 990Hz 100ms, gain 0.25 |
| Match won (loser) | Defeat tone | 140Hz square wave, 500ms, gain 0.25 |

These sounds are functional — they tell the player what happened without looking. The paddle hit should be distinct from the wall bounce. The score sound should be ominous. Keep it simple: square waves, short durations, no filters.

If audio implementation causes any issues, ship without sound. Audio is enhancement, not a gate.

## 10. Visual Polish

### Screen Flash on Score

When a point is scored, fill the entire canvas #FFFFFF for 2 frames (~33ms), then snap back to black. This is a visceral "something happened" signal that reads even in peripheral vision.

### Ball Trail

Store the ball's last 5 positions in a ring buffer. Each frame, render afterimages at those positions with decreasing opacity: 0.5, 0.35, 0.2, 0.1, 0.05. Same size as the ball (14×14). This gives a sense of speed and direction at no gameplay cost. At low speeds the trail is barely visible; at high speeds it fans out dramatically.

### Paddle Hit Stretch

When the ball hits a paddle, briefly stretch the ball by 2px in the x-direction for 3 frames (squash-and-stretch feedback). Return to normal size after. Subtle but adds physicality.

### Score Pop

When a score updates, render the new digit at 130% scale for 5 frames, then ease back to 100%. A small bounce animation that draws the eye.

## 11. Implementation Notes

1. **Delta-time is mandatory.** Every position update is `position += velocity × dt`. Cap dt at 0.05s (50ms) to prevent massive jumps after tab switches. If the frame took longer than 50ms, simulate 50ms of game time and discard the rest.

2. **The sweep collision in section 5 is essential.** At 550px/s, the ball moves ~9px per frame. The paddle is 14px wide. A standard overlap check will miss collisions roughly 40% of the time at max speed. If you skip sweep detection, high-speed rallies will have balls phasing through paddles.

3. **Ball speed resets on each point, not on each serve.** Speed is 280px/s at the start of every rally. The acceleration within a rally (30px/s per hit) is what creates tension — long rallies become frantic. If you carried speed across points, later rallies would start at an impossible pace.

4. **Do not use `setInterval` or `setTimeout` for the game loop.** Use `requestAnimationFrame` exclusively. It syncs to the monitor refresh rate, prevents tearing, and pauses automatically when the tab is backgrounded.

5. **The AI's wall-bounce prediction:** To predict where the ball will arrive at the paddle's x column, simulate a simple trajectory. Start at the ball's current position with its current velocity. Step forward until the x reaches the paddle's column. At each step, if the y goes below 0 or above 525 (canvas height), reflect it. The final y is the predicted arrival. This doesn't need to be frame-accurate — a coarse simulation (stepping in 50px increments) is fine.

6. **Prevent fully vertical ball.** If |vx| drops below 50px/s (due to floating-point drift or extreme paddle angles), clamp it to 50px/s in the original direction. A ball that bounces between top and bottom walls without horizontal progress is a soft lock.

7. **Key debouncing for mode select:** On the title screen, pressing 1 or 2 should start immediately. Don't require Enter as a separate step — but support it as an alternative (highlight 1P/2P with arrows, confirm with Enter). The 1/2 shortcut is for speed; the arrow+Enter path is for discoverability.

## 12. Acceptance Criteria

- [ ] Game loads with no console errors
- [ ] Title screen displays mode selection (1P / 2P)
- [ ] Ball serves from center after "READY" countdown
- [ ] Ball bounces off top and bottom walls
- [ ] Ball reflects off paddles with angle based on hit position (not simple geometric reflection)
- [ ] Ball speed increases every paddle hit, capped at 550px/s
- [ ] Missing the ball awards a point to the opponent
- [ ] Scores displayed as retro bitmap digits, update correctly
- [ ] First to 11 wins the match
- [ ] AI opponent is challenging but beatable in 1P mode
- [ ] 2P mode uses W/S for left paddle, arrows for right paddle
- [ ] Both players can move simultaneously without input conflict
- [ ] Pause works (P key)
- [ ] Match over screen shows winner and restart option
- [ ] Center net renders as dashed line
- [ ] Ball does not tunnel through paddles at high speed
- [ ] Score flash and ball trail render correctly

## 13. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML scaffold | DOCTYPE, head, body, canvas 858×525, inline CSS (black bg, centered, no margin), empty `<script>` | Opens in browser with black rectangle, no errors |
| T02 | Game loop & input | requestAnimationFrame loop with delta-time (capped 50ms). Key state map for W, S, ArrowUp, ArrowDown, Enter, P, 1, 2. Canvas clears #000000 each frame. | Smooth loop running; keys registered in state map |
| T03 | State machine | TITLE, SERVE, PLAYING, PAUSED, SCORED, MATCH_OVER. Transitions triggered by Enter, P, 1, 2, and game events. | Can navigate through every state with keyboard |
| T04 | Court rendering | Center net (dashed filled rectangles). Reserve areas for score digits. Static court visible each frame. | White dashed center line renders correctly |
| T05 | Paddles | Two white 14×90 rectangles at correct x-positions. P1 moves with W/S, P2 with ArrowUp/Down. 380px/s. Clamped to canvas. | Both paddles move smoothly, stop at edges, work simultaneously |
| T06 | Ball movement & walls | 14×14 white square. Starts at center, moves at 280px/s at a random angle (±35° from horizontal). Bounces off top/bottom walls. | Ball moves and bounces off ceiling/floor correctly |
| T07 | Paddle collision & angle | Sweep detection for high speeds. Hit-position-based angle response (−65° to +65°). Speed +30px/s per hit (max 550). Ball repositioned outside paddle. | Ball angle varies by hit position; no tunneling at max speed |
| T08 | Scoring & serve | Ball past left edge = P2 point. Past right edge = P1 point. 1.2s freeze. Ball resets to center, speed resets to 280, serve toward loser. First to 11 → MATCH_OVER. | Points track correctly; serve direction correct; match ends at 11 |
| T09 | Bitmap score display | Retro 3×5 grid digits (10×10px cells, 3px gaps). Render each player's score in their half of the court. | Scores display as chunky retro digits; update on each point |
| T10 | AI opponent | Right paddle AI in 1P mode. Predicts ball landing with wall-bounce simulation. ±35px error per prediction. 320px/s reaction speed. Drifts to center when ball away. 8px dead zone. | AI plays competently; beatable with angled shots |
| T11 | Title screen | "PONG" 80px centered. Mode selection (1P/2P) with highlight marker. Controls hint. Attract-mode ball bouncing in background at 50% opacity. | Title renders; mode select works with 1/2 keys and arrow+Enter |
| T12 | Game screens | SERVE: "READY" 1.5s then auto-serve. PAUSED: overlay + text. MATCH_OVER: winner text + restart prompt. | All screens display correctly; transitions smooth |
| T13 | Audio | Web Audio: paddle hit (480Hz 45ms), wall bounce (240Hz 30ms), score (160Hz 250ms), win/loss chimes. AudioContext on first interaction. | Sounds play on correct events; distinct and appropriate |
| T14 | Visual polish | Screen flash on score (2 frames white). Ball trail (5 afterimages). Score pop animation. | Visual effects enhance gameplay without distraction |
| T15 | Final testing | Verify all acceptance criteria. Stress-test: max-speed rallies, simultaneous inputs, tab-switch recovery, edge-case serves. Check for softlocks (stuck ball, infinite loops). | All criteria pass; game feels complete and tight |
