# Game Spec: Galaga

## 1. Overview
Galaga (Namco, 1981) — a fixed-shooter evolution of Galaxian. Enemies form a grid at the top, then dive-bomb the player in swooping attack patterns. Features a dual-ship mechanic where the player can rescue a captured ship for double firepower. Colorful enemies against a starfield background.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left
- Starfield: 80 small white dots (1–2px) at random positions, scrolling downward at 20px/s, wrapping

## 3. Game Objects

### Player Ship
- **Shape:** Arrow/fighter shape — draw as a 5-point polygon: tip (0,−16), upper-left (−8,−4), lower-left (−14,14), lower-right (14,14), upper-right (8,−4)
- **Size:** 28×30px bounding box
- **Color:** #FFFFFF fill
- **Starting position:** x=400, y=550
- **Movement:** Horizontal only at 350px/s, clamped to canvas

### Enemy Formation (Grid)
- **Layout:** 10 columns × 5 rows = 50 enemies
- **Spacing:** 48px horizontal, 40px vertical between centers
- **Grid center:** x=400, y=160
- **Row types (top to bottom):**
  - Row 1: Boss Galaga (2 per position width), #00CC00, 28×24px, takes 2 hits
  - Row 2: Butterfly, #FF4444, 24×20px
  - Rows 3–4: Bee, #FFCC00, 20×18px
  - Row 5: Bee variant, #00BBFF, 20×18px
- **Idle animation:** formation sways left-right ±20px at 0.5Hz

### Diving Enemies
- **Behavior:** 1–3 random enemies break from formation every 2–3 seconds. They follow a curved swoop path (Bezier or sine-wave) toward the player, then loop back to formation or exit bottom and re-enter from top.
- **Dive speed:** 250px/s along path
- **Firing:** Diving enemies fire 1–2 bullets during dive

### Player Bullets
- **Shape:** Rectangle 3×14px
- **Color:** #FFFFFF
- **Speed:** 550px/s upward
- **Limit:** 2 on screen (dual ship: 4)

### Enemy Bullets
- **Shape:** Rectangle 3×10px
- **Color:** #FF6666
- **Speed:** 300px/s downward

### Dual Ship (Captured Rescue)
- **Mechanic:** Boss Galaga's tractor beam captures player ship. Destroying the boss while it holds a ship releases it, giving the player a double-wide ship with double fire rate (2 bullets per press, side by side).

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Move left |
| ArrowRight / D | Move right |
| Space | Fire |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Enemies start in formation and sway gently. Periodically (every 2–3s), 1–3 enemies dive-bomb the player along curved paths.
2. Diving enemies fire 1–2 bullets during their swoop, then return to formation or wrap from bottom to top.
3. Player fires up to 2 bullets at a time (4 if dual ship).
4. Boss Galaga (top row) takes 2 hits. On first hit it changes to a damaged state (#888888). Kill it = 150 pts in formation, 400 pts while diving.
5. Boss Galaga can perform a tractor beam attack: pauses above player, emits a #00FF00 beam downward. If player is caught, they lose that ship (stored as captured). Later, killing the boss with a captured ship releases the ship — it joins the player to form a dual-ship (wider hitbox, double fire).
6. If all enemies are destroyed, advance to next stage: more enemies dive, faster dive speed (+20px/s per stage), more bullets.
7. Player has 3 lives. Hit by enemy bullet or diving enemy = death.
8. Game over at 0 lives.

## 6. Collision Detection

- Player Bullet ↔ Enemy (in formation): destroy enemy (or damage boss), add score
- Player Bullet ↔ Diving Enemy: destroy, add score (higher than formation kill)
- Enemy Bullet ↔ Player: player dies
- Diving Enemy ↔ Player: both die
- Tractor Beam ↔ Player: capture player ship (if no dual ship active)

All AABB.

## 7. Scoring

- Starting score: 0
- Score display: top-left at (10, 24), #FFFFFF, 16px monospace
- Bee (in formation): 50 pts. Bee (diving): 100 pts.
- Butterfly (formation): 80 pts. Butterfly (diving): 160 pts.
- Boss (formation): 150 pts. Boss (diving): 400 pts.
- High score: localStorage, top-center

## 8. UI Elements

- **Score:** top-left "Score: {N}"
- **High Score:** top-center "High Score: {N}" 14px #AAAAAA
- **Lives:** bottom-left, small ship icons
- **Stage:** bottom-right "Stage {N}" 14px #AAAAAA
- **Game Over screen:** #000000CC overlay. "GAME OVER" 40px white centered. Score. "Press Enter to Restart."
- **Start screen:** "GALAGA" centered y=200, 56px #FFCC00 monospace. Starfield scrolling behind. Enemy type legend with point values. "Press Enter to Start" y=420, 20px #AAAAAA.
- **Pause:** "PAUSED" centered 36px white on #000000CC overlay.

## 9. Audio (Optional / Bonus)
- Player fire: 1200Hz square, 30ms
- Enemy hit: noise burst, 50ms
- Player death: descending 660→55Hz, 400ms
- Tractor beam: oscillating 220–440Hz while active
- Stage clear: short ascending arpeggio

## 10. Implementation Notes

1. Dive paths should be smooth curves — use quadratic Bezier or sinusoidal paths, not linear movement. Define 3–4 preset dive path templates.
2. Boss Galaga tractor beam is a simplified mechanic: if the beam rectangle overlaps the player for 1.5s, the ship is captured. Keep it simple — don't require pixel-perfect beam collision.
3. Dual-ship doubles the player's hitbox width (56px) but also doubles firepower. It's a risk-reward mechanic.
4. Formation sway is cosmetic — all enemies shift together by ±20px using sin(time × π).
5. Enemies that dive off the bottom of the screen should re-enter from the top and return to their grid position.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Player ship moves horizontally, fires up to 2 bullets
- [ ] Enemy formation renders and sways
- [ ] Enemies periodically dive-bomb in curved paths
- [ ] Enemies can be destroyed with correct point values
- [ ] Boss Galaga takes 2 hits
- [ ] Tractor beam mechanic captures and can rescue ship for dual-ship mode
- [ ] Stage advances when all enemies destroyed
- [ ] Starfield scrolls in background
- [ ] Game can be restarted after game over

## 12. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML5 scaffold | Create boilerplate: DOCTYPE, html/head/body, 800×600 canvas, inline style (black bg, centered), script tag | File opens in browser without errors |
| T02 | Game loop | Implement requestAnimationFrame loop with delta-time. Canvas clears to #000000 each frame. Render scrolling starfield (80 white dots, 1–2px, 20px/s downward, wrap). | Starfield scrolls; blank canvas renders at 60fps |
| T03 | Game state | Define state machine: IDLE → PLAYING → PAUSED → GAME_OVER. Enter starts/restarts. P pauses. | State transitions work correctly |
| T04 | Player ship | Draw 5-point fighter polygon (#FFFFFF fill) at y=550. Move with ArrowLeft/ArrowRight at 350px/s. Clamp to canvas. | Ship visible, moves horizontally, stays in bounds |
| T05 | Enemy formation | Create 10×5 grid centered at x=400 y=160, 48px/40px spacing. Row types: Boss (#00CC00 28×24, 2HP), Butterfly (#FF4444 24×20), Bee (#FFCC00 20×18), Bee variant (#00BBFF 20×18). Draw each as a colored rectangle. Track alive/dead/HP per enemy. Formation sways ±20px at 0.5Hz using sin(). | 50 enemies render in correct rows/colors; formation sways |
| T06 | Player bullets & combat | Space fires 3×14px white bullet upward at 550px/s. Max 2 on screen. Bullet ↔ enemy: destroy enemy (boss takes 2 hits, changes to #888888 on first). Score: 50/100 (bee), 80/160 (butterfly), 150/400 (boss) for formation/diving kills. | Bullets fire, hit enemies, correct scoring and boss 2-hit mechanic |
| T07 | Dive-bombing AI | Every 2–3s, 1–3 random enemies break from formation and follow a curved Bezier/sinusoidal path toward the player area. Speed 250px/s. Fire 1–2 #FF6666 3×10px bullets downward at 300px/s during dive. After dive, return to grid position or wrap from bottom to top. Define 3–4 preset path templates. | Enemies dive in smooth curves, fire during dive, return to formation |
| T08 | Enemy bullets & player death | Enemy bullets (3×10px #FF6666, 300px/s down). Bullet ↔ player or diving enemy ↔ player = death. Decrement life. Respawn at center after 1.5s. | Player dies on hit; respawns; lives decrement |
| T09 | Boss tractor beam | Boss Galaga can dive and pause above player, emit a #00FF00 vertical beam (40×200px). If beam overlaps player for 1.5s, ship is captured (stored). Later, killing that boss releases the ship → dual-ship mode: player width doubles to 56px, fires 4 bullets max (2 side-by-side per press). | Tractor beam captures ship; killing boss rescues it; dual-ship works |
| T10 | Stage progression | When all 50 enemies destroyed, advance stage. Reset formation with same layout. Increase dive speed +20px/s and dive frequency. Display "Stage {N}" bottom-right. | Stages advance; difficulty increases |
| T11 | Scoring & HUD | "Score: {N}" top-left 16px. "High Score: {N}" top-center 14px #AAAAAA (localStorage). Lives as ship icons bottom-left. Stage number bottom-right. | All HUD displays correctly; high score persists |
| T12 | Start & Game Over screens | Start: "GALAGA" y=200 56px #FFCC00, enemy legend, "Press Enter" y=420. Game Over: #000000CC overlay, "GAME OVER" 40px, score, restart. Starfield visible on start screen. | Screens show correctly; restart resets all state |
| T13 | Polish & debug | Fix remaining bugs. Ensure all acceptance criteria pass. Add metadata comment: `<!-- Galaga | spec:run1-opus-plan | built-by:{model} -->` | All section 11 criteria pass; comment header present |
