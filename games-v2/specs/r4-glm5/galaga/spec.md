# Galaga — Complete Game Specification

## Overview

Galaga is a single-player fixed shooter. You control a starfighter at the bottom of the screen. Alien insects arrange in formation at the top and periodically dive-bomb toward you in attack patterns. Shoot them before they shoot or collide with you. Some enemies use tractor beams to capture your ship — rescue it for dual firepower. Clear all enemies to advance to the next stage. Bonus stages award points for shooting enemies without being attacked. The game ends when all lives are lost.

---

## Game Elements

### The Arena

- **Canvas size:** 480×640 pixels (portrait orientation, or scale to 600×800)
- **Background:** Solid black (#000000) with optional starfield (small white dots)
- **Boundaries:**
  - Left wall at x = 0
  - Right wall at canvas width
  - Top at y = 0
  - Player area at bottom
- **No wraparound:** Objects stay within bounds

### The Player Ship (Fighter)

- **Size:** 32px wide × 32px tall (approximate)
- **Position:** Horizontally centered, 50px from bottom of canvas
- **Shape:** Stylized starfighter (triangle with wings, or simple geometric shape)
- **Color:** White (#FFFFFF) or light blue
- **Movement:** Horizontal only (left/right)
- **Speed:** 5-6 pixels per frame
- **Boundary constraints:** Cannot move beyond left/right walls
- **Shooting:** Fires laser upward. Only two lasers can be on screen at a time.
- **Lives:** Starts with 3 lives
- **Dual mode:** When rescuing a captured ship, player controls two ships side-by-side with combined firepower (up to 4 lasers on screen)

### The Enemies

Three types of alien insects, each with distinct appearance and behavior.

#### Zako (Bee/Drone)

- **Appearance:** Bee-like, small wings, buzzing animation
- **Size:** 24×24 px
- **Color:** Yellow/orange when in formation, changes to white/blue during dive
- **Points:**
  - In formation: 50 points
  - During dive: 80 points
- **Rows:** Bottom 2 rows of formation
- **Behavior:** Common enemy, standard dive attacks

#### Goei (Butterfly)

- **Appearance:** Butterfly-like, larger wings, graceful movement
- **Size:** 28×28 px
- **Color:** Red/purple when in formation, changes during dive
- **Points:**
  - In formation: 80 points
  - During dive: 160 points
- **Rows:** Middle rows of formation
- **Behavior:** More aggressive dives, can use tractor beam (Goei Commander variant)

#### Boss Galaga (Boss)

- **Appearance:** Large moth/butterfly with prominent eyes, larger than others
- **Size:** 36×36 px
- **Color:** Green/blue with eye markings
- **Points:**
  - In formation: 150 points
  - During dive: 400 points
- **Rows:** Top row only (4 Boss Galagas)
- **Behavior:** Most aggressive, can use tractor beam to capture player ship
- **Vulnerability:** Takes 2 hits to destroy (first hit damages, second destroys) — OR — only vulnerable during certain animations

### Formation Layout

Enemies arrange in a specific pattern at the top of the screen:

```
[Boss]  [Boss]  [Boss]  [Boss]      ← Row 1: 4 Boss Galagas
  [Goei]  [Goei]  [Goei]  [Goei]    ← Row 2: 4 Goei (butterflies)
[Goei]  [Goei]  [Goei]  [Goei]      ← Row 3: 4 Goei
  [Zako]  [Zako]  [Zako]  [Zako]    ← Row 4: 4 Zako (bees)
[Zako]  [Zako]  [Zako]  [Zako]      ← Row 5: 4 Zako
```

**Total enemies:** 20 (4 Boss + 8 Goei + 8 Zako)

**Spacing:**
- Horizontal: ~50px between enemy centers (alternating rows offset by 25px)
- Vertical: ~35px between rows
- Formation starts 100px from top of canvas

### Projectiles

#### Player Laser

- **Size:** 3px wide × 12px tall
- **Color:** Yellow or white (#FFFF00)
- **Speed:** 8-10 pixels per frame (upward)
- **Maximum on screen:** 2 lasers (4 in dual-ship mode)
- **Behavior:** Travels straight up until hitting an enemy or leaving screen

#### Enemy Missile

- **Size:** 3×3 px (small dot) or 3×6 px (small rectangle)
- **Color:** Red or white
- **Speed:** 4-5 pixels per frame (downward)
- **Behavior:** Fired during dive attacks, aimed at player

### Tractor Beam

- **Appearance:** Yellow/orange beam extending from Boss Galaga
- **Shape:** Conical or rectangular beam
- **Duration:** Continuous while Boss hovers and attempts capture
- **Behavior:** If player ship touches beam, ship is captured and carried to top of screen

---

## Formation Behavior

### Entry Sequence

At the start of each stage (after stage 1), enemies enter the screen in orchestrated waves:

1. Groups of enemies fly in from the sides and top
2. They perform looping entrance patterns
3. They settle into formation positions
4. Player cannot shoot during entry (or can shoot for bonus points during entry)

**Stage 1 special:** Formation starts already in place.

### Formation Movement

While in formation, the entire group moves as a unit:

1. Drift horizontally left and right
2. Occasional forward "lunge" toward the player, then back
3. Individual enemies animate in place (wings flapping)

**Movement pattern:**
- Horizontal drift: 1-2 px/frame, reversing at screen edges
- Lunge frequency: Every 5-10 seconds
- Lunge distance: 50-100px toward player, then return

---

## Dive Attacks

### Triggering Dives

Periodically, enemies leave formation to attack:

- **Dive interval:** Every 2-5 seconds, an enemy begins a dive
- **Priority:** Goei and Boss dive more frequently than Zako
- **Simultaneous dives:** Up to 2-3 enemies can dive at once

### Dive Patterns

Enemies use various attack patterns when diving:

#### Pattern 1: Straight Dive

Enemy flies directly toward player's position, firing missiles, then arcs back up to formation or exits screen.

#### Pattern 2: Loop Dive

Enemy dives in a loop or spiral pattern, trying to hit player from unexpected angles.

#### Pattern 3: Tractor Beam Dive (Boss Galaga only)

1. Boss flies down and hovers near player's vertical position
2. Opens tractor beam
3. Attempts to capture player ship
4. If successful, carries ship to formation
5. If unsuccessful, returns to formation

### Dive Return

After diving:
- Enemy may return to its original formation position
- Or may continue attacking until destroyed
- Or may exit the screen (rare)

---

## Tractor Beam Capture and Rescue

### Capture Process

1. Boss Galaga descends with tractor beam active
2. Player ship touches tractor beam
3. Ship is captured (spins inside beam)
4. Boss carries ship to formation
5. Ship remains prisoner, attached to Boss in formation
6. Player respawns with a new ship (if lives remaining)

**Important:** Player loses one life when captured, but the captured ship remains in play (can be rescued).

### Rescue Process

1. Wait for Boss with captured ship to dive
2. Destroy the Boss (not the captured ship)
3. Captured ship falls and joins player's current ship
4. Player now controls two ships (dual mode)

**Dual mode characteristics:**
- Two ships move together, side by side
- Can fire up to 4 lasers on screen (2 per ship)
- If hit, only one ship is destroyed; player continues with remaining ship
- If both ships present, dual mode continues

**Double capture (rare):** If player is captured while in dual mode:
- Both ships can be captured separately
- Rescue grants combined triple power (3 ships) — this is extremely rare

---

## Stage Progression

### Regular Stages

**Stage start:**
1. Brief stage number display ("STAGE 5")
2. Enemies enter screen in waves (except Stage 1)
3. Formation assembles
4. Combat begins

**Stage clear condition:** All enemies destroyed

**Stage end:**
1. Brief pause
2. Stage clear message (optional)
3. Next stage begins

### Bonus Stages (Challenge Stages)

Every 4th stage (stages 4, 8, 12, 16, etc.) is a bonus stage.

**Bonus stage rules:**
- Enemies fly in predetermined patterns
- Enemies do not shoot or collide with player (player is invincible)
- Destroy as many enemies as possible for points
- "Perfect" bonus for destroying all enemies (extra 10,000 points)

**Scoring in bonus stages:**
- Each enemy destroyed: standard points
- Perfect clear: +10,000 bonus

---

## Scoring

### Regular Enemy Points

| Enemy | Formation Kill | Dive Kill |
|-------|---------------|-----------|
| Zako (Bee) | 50 | 80 |
| Goei (Butterfly) | 80 | 160 |
| Boss Galaga | 150 | 400 |

### Special Scoring

| Event | Points |
|-------|--------|
| Boss Galaga (2nd hit during dive) | 800 (combined) |
| Destroy Boss with captured ship | 500 + rescue |
| Bonus stage perfect clear | 10,000 |
| Dual mode starting bonus | — (no points, just firepower) |

**Note:** Points are higher for enemies killed during dive attacks (more risk = more reward).

### Score Display

- **Position:** Top-left corner
- **Format:** "[number]" or "SCORE: [number]"
- **Font:** Monospace or digital-style, 18-20px
- **Color:** White

**High score:**
- Position: Top-center
- Format: "HI: [number]"
- Stored in localStorage

---

## Lives System

- **Initial lives:** 3
- **Display:** Ships displayed in bottom-left or top-right as icons
- **Life loss conditions:**
  - Hit by enemy missile
  - Collision with enemy (during dive)
  - Captured by tractor beam (ship captured, lose one life, can rescue)
- **Extra life:** Some implementations award extra life at 20,000 and 70,000 points

**On death:**
1. Explosion effect
2. If lives remaining: respawn after 1-2 seconds
3. Brief invincibility after respawn (optional)
4. If dual mode: lose one ship, continue with remaining ship
5. If no lives: game over

---

## Controls

| Key | Action |
|-----|--------|
| ← or A | Move ship left |
| → or D | Move ship right |
| Space or Z | Fire laser |
| P or Escape | Pause game |
| R | Restart game |

**Control notes:**
- Movement is continuous while key held
- Fire can be held for auto-fire, or pressed repeatedly
- Maximum 2 lasers on screen (4 in dual mode)

---

## Game States

### 1. Title Screen

**Display:**
- "GALAGA" in large stylized text, centered
- Animated enemies flying
- "Press SPACE to start"
- Control instructions
- High score display

**Behavior:**
- Pressing Space starts game

### 2. Stage Start

**Display:**
- "STAGE [n]" centered
- Enemies entering screen

**Behavior:**
- Brief pause before combat
- Player can sometimes shoot during entry (bonus opportunity)

### 3. Playing

**Display:**
- Player ship(s)
- Enemy formation
- Projectiles
- Score and lives

**Behavior:**
- Normal gameplay
- Enemies dive periodically
- Pressing P pauses

### 4. Paused

**Display:**
- Game frozen
- "PAUSED" centered
- "Press P to resume"

**Behavior:**
- Pressing P resumes
- Pressing R restarts

### 5. Player Death

**Display:**
- Explosion at ship position
- Enemies continue

**Behavior:**
- Brief pause
- If lives remaining: respawn
- If no lives: game over

### 6. Stage Clear

**Display:**
- "STAGE CLEAR" or similar
- Brief pause

**Behavior:**
- After 1-2 seconds, next stage begins

### 7. Bonus Stage

**Display:**
- "CHALLENGING STAGE" or "BONUS STAGE"
- Enemies flying patterns

**Behavior:**
- Player is invincible
- Destroy enemies for points
- After all enemies pass, return to regular stage

### 8. Game Over

**Display:**
- "GAME OVER" centered, large
- Final score
- "Press R to play again"

**Behavior:**
- Pressing R restarts
- Pressing Escape returns to title

---

## Enemy AI Details

### Dive Selection

```
function selectDivingEnemy() {
  // Prefer Goei and Boss over Zako
  const candidates = enemies.filter(e => e.inFormation && !e.diving);
  
  // Weight selection by type
  const weighted = [];
  candidates.forEach(e => {
    if (e.type === 'boss') {
      weighted.push(e, e, e); // 3x chance
    } else if (e.type === 'goei') {
      weighted.push(e, e); // 2x chance
    } else {
      weighted.push(e); // 1x chance
    }
  });
  
  return weighted[Math.floor(Math.random() * weighted.length)];
}
```

### Dive Pattern Implementation

**Straight dive:**
```
function straightDive(enemy, player) {
  // Calculate direction to player
  const dx = player.x - enemy.x;
  const dy = player.y - enemy.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  
  // Set velocity toward player
  enemy.vx = (dx / distance) * enemy.diveSpeed;
  enemy.vy = (dy / distance) * enemy.diveSpeed;
  
  // Fire missiles periodically during dive
  if (Math.random() < 0.02) {
    fireMissile(enemy.x, enemy.y, player.x, player.y);
  }
}
```

**Loop dive:**
```
function loopDive(enemy, phase) {
  // Use parametric equations for loop pattern
  const t = enemy.diveTime;
  const loopRadius = 80;
  
  enemy.x = enemy.diveStartX + Math.sin(t * 0.1) * loopRadius;
  enemy.y = enemy.diveStartY + t * 2;
  
  enemy.diveTime++;
}
```

### Tractor Beam Behavior

```
function tractorBeamDive(boss, player) {
  if (boss.phase === 'descend') {
    // Move down to player's vertical level
    boss.y += 2;
    if (boss.y > canvas.height * 0.5) {
      boss.phase = 'hover';
      boss.tractorBeamActive = true;
    }
  } else if (boss.phase === 'hover') {
    // Move horizontally toward player
    if (boss.x < player.x) boss.x += 1;
    if (boss.x > player.x) boss.x -= 1;
    
    // Check for capture
    if (distance(boss, player) < 50 && player.tractorBeamActive) {
      capturePlayer(boss, player);
    }
    
    // Timeout and return to formation
    boss.hoverTime++;
    if (boss.hoverTime > 120) { // 2 seconds
      boss.phase = 'return';
      boss.tractorBeamActive = false;
    }
  } else if (boss.phase === 'return') {
    // Return to formation position
    returnToFormation(boss);
  }
}
```

---

## Visual Effects

### Enemy Animation

- **Wings flapping:** Cycle between 2-3 animation frames
- **Dive transformation:** Enemy changes color/appearance when diving
- **Formation pulse:** Subtle movement while in formation

### Explosion

- **Player ship:** Series of small particles flying outward
- **Enemy:** Flash and burst into small dots
- **Duration:** 200-400ms

### Tractor Beam Visual

- **Appearance:** Yellow/orange conical beam
- **Animation:** Pulsing or flickering effect
- **Captive ship:** Spins inside beam

### Dual Ship Visual

- **Formation:** Two ships side by side, ~20px apart
- **Movement:** Move together as one unit
- **Combined shots:** Fire alternating or simultaneously

---

## Technical Implementation Notes

### Enemy Data Structure

```
enemies = [
  {
    type: 'boss',        // 'zako', 'goei', or 'boss'
    x: 100,
    y: 120,
    formationX: 100,     // Home position in formation
    formationY: 120,
    inFormation: true,   // False when diving
    diving: false,
    divePattern: null,   // 'straight', 'loop', 'tractor'
    diveTime: 0,
    hasCapturedShip: false,
    capturedShip: null,
    hp: 2,               // Boss takes 2 hits
    points: 150,
    alive: true
  },
  // ... more enemies
];
```

### Formation Entry

```
function entryPattern(enemy, phase) {
  // Enemies enter in waves with looping paths
  const t = enemy.entryTime;
  
  if (enemy.entrySide === 'left') {
    enemy.x = -50 + t * 3 + Math.sin(t * 0.05) * 50;
    enemy.y = -50 + Math.abs(Math.sin(t * 0.03)) * 200;
  } else {
    enemy.x = canvas.width + 50 - t * 3 - Math.sin(t * 0.05) * 50;
    enemy.y = -50 + Math.abs(Math.sin(t * 0.03)) * 200;
  }
  
  enemy.entryTime++;
  
  // Check if reached formation position
  if (enemy.entryTime > 200) {
    enemy.x = enemy.formationX;
    enemy.y = enemy.formationY;
    enemy.inFormation = true;
  }
}
```

### Dual Ship Control

```
function movePlayer() {
  // Normal single ship
  if (keys.left) player.x -= playerSpeed;
  if (keys.right) player.x += playerSpeed;
  
  // Constrain to screen
  player.x = Math.max(20, Math.min(canvas.width - 20, player.x));
  
  // Dual ship: second ship mirrors first with offset
  if (player.dualMode) {
    player.ship2.x = player.x - 20;  // 20px left of main ship
    player.ship1.x = player.x + 20;  // 20px right of main ship
  }
}

function fireLaser() {
  const lasersOnScreen = lasers.filter(l => l.active).length;
  const maxLasers = player.dualMode ? 4 : 2;
  
  if (lasersOnScreen < maxLasers) {
    if (player.dualMode) {
      // Fire from both ships
      createLaser(player.ship1.x, player.ship1.y);
      createLaser(player.ship2.x, player.ship2.y);
    } else {
      createLaser(player.x, player.y);
    }
  }
}
```

### Rescue Logic

```
function destroyEnemy(enemy) {
  if (enemy.hasCapturedShip && enemy.capturedShip) {
    // Rescue the captured ship
    rescueShip(enemy.capturedShip);
    enemy.capturedShip = null;
    enemy.hasCapturedShip = false;
  }
  
  // Normal destruction
  createExplosion(enemy.x, enemy.y);
  addScore(enemy.points);
  enemy.alive = false;
}

function rescueShip(capturedShip) {
  // Captured ship falls and joins player
  capturedShip.falling = true;
  capturedShip.targetY = player.y;
}

function updateFallingShip(ship) {
  if (ship.falling) {
    ship.y += 3;
    
    if (ship.y >= ship.targetY) {
      // Join player as dual ship
      player.dualMode = true;
      ship.falling = false;
    }
  }
}
```

---

## Bonus Stage Implementation

```
function runBonusStage() {
  // Enemies fly in predetermined patterns
  // Player is invincible
  
  player.invincible = true;
  
  // Spawn enemy waves in patterns
  bonusWaveTimer++;
  
  if (bonusWaveTimer % 30 === 0) {
    spawnBonusEnemyWave();
  }
  
  // Standard collision detection (destroy enemies)
  // No player damage possible
  
  // Count destroyed enemies for perfect bonus
  if (enemiesDestroyed === totalEnemies) {
    score += 10000; // Perfect bonus
  }
}
```

---

## Common Bugs to Avoid

1. **Too many lasers on screen:** Enforce maximum laser count. Players should need to time shots.

2. **Enemies don't return to formation:** Ensure dive patterns have return logic, or enemies are destroyed after dive.

3. **Tractor beam captures during invincibility:** Player should be invulnerable during respawn, including capture.

4. **Dual ship hit detection issues:** Both ships should be independently hittable. If one is hit, only that ship is destroyed.

5. **Bonus stage enemies damage player:** Bonus stages must have invincibility or no collision damage.

6. **Formation movement looks jittery:** Formation should drift smoothly, with subtle individual animations.

7. **Boss takes only one hit:** Boss Galaga should take 2 hits (or be more vulnerable during specific phases).

8. **Captured ship rescued incorrectly:** Only the Boss with the captured ship should be targeted, not the captured ship itself.

---

## Minimum Viable Product Checklist

A complete Galaga implementation must have:

- [ ] Canvas rendering (portrait orientation recommended)
- [ ] Player ship that moves horizontally and fires upward
- [ ] 20 enemies in formation (4 Boss, 8 Goei, 8 Zako)
- [ ] Three distinct enemy types with different appearances and behaviors
- [ ] Formation movement (horizontal drift, occasional lunge)
- [ ] Dive attacks with multiple patterns
- [ ] Enemies shoot missiles during dives
- [ ] Tractor beam capture mechanic (Boss Galaga)
- [ ] Rescue mechanic (destroy Boss to rescue captured ship)
- [ ] Dual ship mode after rescue
- [ ] Score system with different points per enemy type
- [ ] Lives system (3 lives)
- [ ] Stage progression
- [ ] Bonus stages every 4 stages
- [ ] Game states: Title → Playing → Paused → Game Over
- [ ] Pause and Restart functionality
- [ ] No external dependencies (all code in one HTML file)

---

## Quick Reference

| Element | Value |
|--------|-------|
| Canvas | 480×640 px (portrait) |
| Player ship | 32×32 px |
| Player speed | 5-6 px/frame |
| Max lasers | 2 (4 in dual mode) |
| Zako (Bee) | 24×24, 50/80 pts |
| Goei (Butterfly) | 28×28, 80/160 pts |
| Boss Galaga | 36×36, 150/400 pts, 2 HP |
| Total enemies | 20 per stage |
| Lives | 3 |
| Bonus stages | Every 4 stages |

---

End of specification.
