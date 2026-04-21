# Game Spec: Pac-Man

## 1. Overview
Pac-Man — a maze chase game from the golden age of arcades where the player clears pellets, evades ghosts, uses power pellets to reverse the hunt, and advances through increasingly fast boards. It feels authentic when the maze is structured, cornering is smooth, ghost personalities are distinct, and frightened/eaten modes are clearly readable.

## 2. Canvas & Rendering
- Canvas size: 700×780px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left
- Maze grid: 28 columns × 31 rows, 24×24px cells, maze offset x=14, y=30

## 3. Game Objects

### Pac-Man
- **Shape/Sprite:** Yellow circle with animated wedge mouth
- **Size:** radius 10px
- **Color:** #FFFF00
- **Starting position:** tile column 14, row 23
- **Movement:** 120px/s with queued turning and 4px cornering assist

### Blinky
- **Shape/Sprite:** Rounded-top ghost with wavy bottom and eyes
- **Size:** 20×20px
- **Color:** #FF0000
- **Starting position:** ghost house upper slot near column 14, row 11–14 area
- **Movement:** 110px/s normally, 60px/s frightened, 200px/s as eyes returning home

### Pinky
- **Shape/Sprite:** Ghost body
- **Size:** 20×20px
- **Color:** #FFB8FF
- **Starting position:** ghost house
- **Movement:** same speed rules as other ghosts

### Inky
- **Shape/Sprite:** Ghost body
- **Size:** 20×20px
- **Color:** #00FFFF
- **Starting position:** ghost house
- **Movement:** same speed rules as other ghosts

### Clyde
- **Shape/Sprite:** Ghost body
- **Size:** 20×20px
- **Color:** #FFB852
- **Starting position:** ghost house
- **Movement:** same speed rules as other ghosts

### Pellets
- **Shape/Sprite:** Small filled dots
- **Size:** 4px diameter
- **Color:** #FFCC99
- **Starting position:** placed through walkable maze corridors, total 240 including 4 power pellets
- **Movement:** static

### Power Pellets
- **Shape/Sprite:** Large blinking dots
- **Size:** 10px diameter
- **Color:** #FFCC99
- **Starting position:** tiles (1,3), (26,3), (1,23), (26,23)
- **Movement:** static, blinking visibility

### Fruit Bonus
- **Shape/Sprite:** Cherry icon or simple red fruit graphic
- **Size:** 16×16px
- **Color:** #FF0000
- **Starting position:** tile column 14, row 17
- **Movement:** static while active, despawns after 10 seconds

### Ghost House Gate
- **Shape/Sprite:** Horizontal bar
- **Size:** approximately 24×4px spanning the house opening
- **Color:** #FFB8FF
- **Starting position:** centered above ghost house doorway
- **Movement:** static, blocks Pac-Man but allows ghost state logic to use it as needed

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Queue left |
| ArrowRight / D | Queue right |
| ArrowUp / W | Queue up |
| ArrowDown / S | Queue down |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Pac-Man moves through walkable maze corridors and cannot pass through walls.
2. Direction inputs are queued and applied at the next legal tile center.
3. Normal pellets are cleared on contact and reduce remaining pellet count.
4. Power pellets trigger frightened mode for all active ghosts.
5. Frightened ghosts reverse direction immediately and can be eaten by Pac-Man.
6. Eaten ghosts become eyes and return to the ghost house at 200px/s.
7. Maze tunnels on row 14 wrap Pac-Man and ghosts from one side to the other.
8. Movement through tunnels is reduced to 60% speed.
9. Fruit appears after 70 pellets eaten and again after 170 pellets eaten.
10. Clearing all pellets advances to the next level.
11. Player starts with 3 lives.
12. Collision with a non-frightened ghost costs a life.
13. Game over occurs at 0 lives.

## 6. Collision Detection

- Pac-Man ↔ Pellet: remove pellet and award points
- Pac-Man ↔ Power Pellet: remove pellet and trigger frightened mode
- Pac-Man ↔ Fruit: remove fruit and award bonus points
- Pac-Man ↔ Ghost (normal/scatter/chase): lose a life
- Pac-Man ↔ Ghost (frightened): eat ghost, award ghost points, send ghost eyes home
- Entity ↔ Wall: movement blocked at maze boundaries
- Entity ↔ Tunnel edge: wrap to opposite side

Use AABB based on tile centers and entity radii for corridor checks.

## 7. Scoring

- Starting score: 0
- Small pellet: +10 points
- Power pellet: +50 points
- Ghosts eaten during one frightened cycle: +200, +400, +800, +1600 points
- Fruit (level 1 cherry): +100 points
- Score display: top-left, white text, 16px monospace
- High score: stored in localStorage, display at top-right

## 8. UI Elements

- **Score:** top-left
- **Lives / Health:** bottom-left as small Pac-Man icons
- **Level indicator:** bottom-right or lower HUD text showing current level
- **Game Over screen:** centered text “GAME OVER”, score, “Press Enter to restart”
- **Start screen:** “PAC-MAN” centered near y=300 in 54px #FFFF00 monospace, “Press Enter to Start” below
- **Pause:** P key toggles pause overlay

## 9. Audio (Optional / Bonus)
- Pellet chomp: short alternating waka tones
- Power pellet: low pulsing tone during frightened mode
- Eat ghost: rising bonus tone
- Death: descending arcade jingle

## 10. Implementation Notes

1. Ghost AI must preserve distinct target logic for Blinky, Pinky, Inky, and Clyde.
2. Frightened, chase, scatter, and eaten/eyes-returning states must be visually and behaviorally distinct.
3. Pac-Man turning should feel forgiving using small cornering assist near tile centers.
4. Tunnel wrap and ghost house gate behavior are common failure points and must be handled explicitly.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Pac-Man moves smoothly through the maze and turns correctly
- [ ] Pellets, power pellets, and fruit award the correct points
- [ ] Ghosts have distinct behavior and frightened mode works
- [ ] Tunnel wrapping works for valid entities
- [ ] Clearing all pellets advances to the next level
- [ ] Score increments correctly
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

**THIS IS THE BUILDER'S WORK ORDER. Complete tasks in sequence. Do not skip ahead.**
**After completing each task, verify it works before moving to the next.**
**Mark each task complete in your output JSON (see results.json schema).**

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, canvas element, inline style (black bg), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame loop with delta-time tracking. Canvas clears each frame. | Console shows no errors; blank canvas renders at 60fps |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Enter key starts game. | State transitions logged to console |
| T04 | Player object | Draw player shape on canvas. Implement keyboard controls (per spec section 4). | Player visible, moves correctly, stays within bounds |
| T05 | Maze layout and pellet population | Build the 28×31 maze with walls, corridors, ghost house, gate, tunnel row, and all pellet placements including four power pellets in the exact corner positions. | Maze renders correctly and pellets populate only valid walkable tiles |
| T06 | Pac-Man movement and turning | Implement tile-based movement at 120px/s, queued turns, wall blocking, center alignment, and tunnel wrapping with reduced tunnel speed. | Pac-Man can navigate the maze smoothly and turn at intersections reliably |
| T07 | Ghost roster and house logic | Spawn Blinky, Pinky, Inky, and Clyde with their proper colors, starting house positions, release behavior, and movement speeds for normal, frightened, and eyes-returning states. | All four ghosts appear correctly and leave/return to the house as expected |
| T08 | Ghost AI modes | Implement scatter/chase cycling plus per-ghost chase targeting, immediate frightened reversals on power pellet use, and eaten-eye return behavior. | Ghost behavior clearly changes by mode and differs by ghost type |
| T09 | Pellet, power pellet, and fruit scoring | Remove pellets on contact, award points, trigger frightened mode from power pellets, and spawn fruit after 70 and 170 pellets eaten for 10 seconds at the center fruit tile. | Consumables appear and score correctly with correct spawn timing |
| T10 | Life loss and level progression | Detect fatal ghost contact, play death flow, reset board positions after life loss, and advance to the next level when all pellets are cleared while preserving score. | Death and board-clear progression both behave correctly |
| T11 | Collision detection | Implement all collision pairs from spec section 6. AABB unless spec says otherwise. | Collisions trigger correct outcomes (log to console if needed) |
| T12 | Scoring | Implement score counter. Render score top-left, high score top-right (localStorage). | Score increments on correct events; persists on reload |
| T13 | Lives / health | Render lives/health indicator top-right per spec section 8. Decrement on hit. | Lives display correctly; game over triggers at 0 |
| T14 | Game Over screen | Render GAME OVER overlay with final score. Enter key restarts. | Overlay appears; restart resets all state |
| T15 | Start screen | Render title screen with game name and "Press Enter to Start". | Appears on load before game begins |
| T16 | Polish & debug | Fix any remaining bugs. Ensure all acceptance criteria from section 11 pass. Add the metadata comment header. | All section 11 criteria pass; comment header present |
