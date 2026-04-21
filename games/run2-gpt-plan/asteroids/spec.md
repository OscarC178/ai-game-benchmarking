# Game Spec: Asteroids

## 1. Overview
Asteroids — a late-1970s vector-style space shooter built around thrust, inertia, screen wrapping, and asteroid splitting. The game feels authentic when movement has momentum, hazards drift unpredictably, and each cleared wave escalates pressure without losing the minimalist arcade presentation.

## 2. Canvas & Rendering
- Canvas size: 800×600px
- Background color: #000000
- Frame rate: 60 FPS
- Coordinate system: origin top-left
- Visual style: vector outlines with minimal fills

## 3. Game Objects

### Player Ship
- **Shape/Sprite:** White outlined triangle with points at (0,-18), (-12,12), (12,12)
- **Size:** 24×30px overall footprint
- **Color:** #FFFFFF stroke, 2px line width
- **Starting position:** x=400, y=300
- **Movement:** Rotates left/right at 270°/s, thrusts forward at 200px/s², wraps at screen edges, max speed 350px/s

### Thrust Flame
- **Shape/Sprite:** Small rear triangle flicker behind ship
- **Size:** 8×12px
- **Color:** #FF9900
- **Starting position:** hidden until thrusting
- **Movement:** Matches ship position and rotation only while thrust is active

### Large Asteroid
- **Shape/Sprite:** Irregular 10–14 point polygon outline
- **Size:** radius 40px
- **Color:** #AAAAAA stroke
- **Starting position:** random, at least 150px from ship spawn
- **Movement:** Drifts in a random direction at 50–80px/s and wraps at edges

### Medium Asteroid
- **Shape/Sprite:** Irregular polygon outline
- **Size:** radius 20px
- **Color:** #AAAAAA stroke
- **Starting position:** created from large asteroid splits
- **Movement:** Drifts at 80–120px/s and wraps at edges

### Small Asteroid
- **Shape/Sprite:** Irregular polygon outline
- **Size:** radius 10px
- **Color:** #AAAAAA stroke
- **Starting position:** created from medium asteroid splits
- **Movement:** Drifts at 120–180px/s and wraps at edges

### Player Bullet
- **Shape/Sprite:** Filled circle
- **Size:** radius 2px
- **Color:** #FFFFFF
- **Starting position:** ship nose position
- **Movement:** Travels in ship facing direction at 500px/s, wraps at edges, expires after 0.8s, max 4 active

### UFO
- **Shape/Sprite:** Red saucer outline with lower body and dome
- **Size:** 32×12px body with 20×8px dome
- **Color:** #FF4444 stroke
- **Starting position:** enters from left or right edge around y=120–220
- **Movement:** Horizontal travel at 120px/s, occasionally spawning on a 20–30s timer

### UFO Bullet
- **Shape/Sprite:** Filled circle
- **Size:** radius 2px
- **Color:** #FF4444
- **Starting position:** UFO center
- **Movement:** Fired toward player at 350px/s, wraps at edges if still alive

## 4. Controls

| Key | Action |
|-----|--------|
| ArrowLeft / A | Rotate ship left |
| ArrowRight / D | Rotate ship right |
| ArrowUp / W | Thrust forward |
| Space | Fire bullet |
| Enter | Start / Restart |
| P | Pause / Unpause |

## 5. Game Rules & Logic

1. Ship movement uses inertia; releasing thrust does not stop instantly.
2. Ship, asteroids, bullets, and UFO wrap seamlessly at all screen edges.
3. Wave 1 starts with 4 large asteroids; each later wave adds 1 more large asteroid.
4. Large asteroids split into 2 medium asteroids when shot.
5. Medium asteroids split into 2 small asteroids when shot.
6. Small asteroids are destroyed completely when shot.
7. Player starts with 3 lives.
8. On ship death, respawn after 2 seconds only if the center region is safe.
9. Respawned ship is invulnerable for 2 seconds and blinks.
10. Extra life awarded at each 10,000-point threshold.
11. UFO appears periodically and can shoot at the player.
12. Game over occurs when lives reach 0.

## 6. Collision Detection

- Player Bullet ↔ Asteroid: destroy bullet; split or destroy asteroid depending on size
- Player Bullet ↔ UFO: destroy both and award UFO score
- Ship ↔ Asteroid: lose life unless invulnerable
- Ship ↔ UFO Bullet: lose life unless invulnerable
- Ship ↔ UFO: lose life unless invulnerable
- UFO Bullet ↔ Asteroid: destroy bullet only

Use circular collision for bullets/asteroids/ship center checks.

## 7. Scoring

- Starting score: 0
- Large asteroid destroyed: +20 points
- Medium asteroid destroyed: +50 points
- Small asteroid destroyed: +100 points
- UFO destroyed: +200 points
- Score display: top-left, #FFFFFF, 18px monospace at y=30
- High score: top-right via localStorage

## 8. UI Elements

- **Score:** top-left in white monospace
- **Lives / Health:** small ship icons under the score area
- **Level indicator:** optional wave text near top-center in 16px #AAAAAA
- **Game Over screen:** centered text “GAME OVER”, final score, “Press Enter to restart”
- **Start screen:** “ASTEROIDS” centered at y=220 in 52px #FFFFFF monospace, start prompt at y=360
- **Pause:** P key toggles a #000000CC overlay with centered “PAUSED”

## 9. Audio (Optional / Bonus)
- Bullet fire: short 900Hz triangle blip
- Asteroid explosion: brief noise burst scaled by size
- Ship death: descending noisy sweep
- UFO hum: low oscillating tone while active

## 10. Implementation Notes

1. Asteroid polygon shapes should be generated once per asteroid and retained so each rock keeps a consistent silhouette.
2. Split asteroids should emerge at diverging angles instead of overlapping perfectly.
3. Respawn safety must prevent the ship from reappearing inside or immediately beside an asteroid.
4. Wrapping visuals should look seamless for large objects near screen edges.

## 11. Acceptance Criteria

- [ ] Game loads without console errors
- [ ] Player can start a new game with Enter
- [ ] Ship rotates, thrusts, coasts, and wraps correctly
- [ ] Bullets fire, wrap, and expire correctly
- [ ] Asteroids split into correct smaller sizes
- [ ] Ship death, respawn delay, and invulnerability work
- [ ] UFO appears and can be destroyed
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
| T05 | Ship inertia and wrapping | Add ship rotation, thrust acceleration, friction decay, speed cap, and edge wrapping for all sides. Draw thrust flame only while accelerating. | Ship can rotate, coast naturally, and re-enter smoothly from opposite edges |
| T06 | Asteroid wave setup | Spawn 4 large asteroids for wave 1 at random safe positions with irregular vector outlines and random drift velocities. | Four unique asteroids appear away from the ship spawn and drift independently |
| T07 | Bullet firing and lifetime | Implement player bullets from ship nose with 500px/s speed, 0.8s lifetime, edge wrapping, and a maximum of 4 active shots. | Bullets launch from the correct position, wrap, and disappear on timeout |
| T08 | Asteroid splitting | When bullets hit large asteroids, replace them with 2 medium asteroids; medium asteroids split into 2 small; small asteroids are removed entirely. | Destroying each asteroid size produces the correct next state |
| T09 | Death, respawn, and invulnerability | Remove a life on ship collision, delay respawn by 2 seconds, require a safe center-area spawn, and blink the ship for 2 seconds of invulnerability. | Death and respawn behavior are fair and repeatable |
| T10 | UFO enemy | Add periodic UFO spawns with horizontal motion and aimed red bullets at the player. Destroying the UFO awards 200 points. | UFO appears on schedule, attacks, and can be shot for score |
| T11 | Collision detection | Implement all collision pairs from spec section 6. AABB unless spec says otherwise. | Collisions trigger correct outcomes (log to console if needed) |
| T12 | Scoring | Implement score counter. Render score top-left, high score top-right (localStorage). | Score increments on correct events; persists on reload |
| T13 | Lives / health | Render lives/health indicator top-right per spec section 8. Decrement on hit. | Lives display correctly; game over triggers at 0 |
| T14 | Game Over screen | Render GAME OVER overlay with final score. Enter key restarts. | Overlay appears; restart resets all state |
| T15 | Start screen | Render title screen with game name and "Press Enter to Start". | Appears on load before game begins |
| T16 | Polish & debug | Fix any remaining bugs. Ensure all acceptance criteria from section 11 pass. Add the metadata comment header. | All section 11 criteria pass; comment header present |
