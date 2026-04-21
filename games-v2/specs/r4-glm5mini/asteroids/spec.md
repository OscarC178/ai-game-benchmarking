# Asteroids — Complete Game Specification

## Overview

Asteroids is a single-player space shooter. You control a triangular ship in a wraparound arena filled with floating asteroids. Shoot asteroids to break them into smaller pieces. Destroy all asteroids to advance to the next wave. Avoid collisions with asteroids and enemy saucers that periodically appear. You have limited lives. The game ends when all lives are lost.

---

## Game Elements

### The Arena

- **Canvas size:** 800×600 pixels
- **Background:** Solid black (#000000)
- **Wraparound:** The arena wraps around on all edges. Objects that move off one edge reappear on the opposite edge.
  - If x < 0, x becomes canvas width
  - If x > canvas width, x becomes 0
  - Same for y-axis

### The Ship (Player)

- **Shape:** Equilateral triangle, pointing upward (direction of movement)
- **Size:** Base ≈ 20px, height ≈ 25px
- **Color:** White (#FFFFFF)
- **Position:** Starts at center of screen (400, 300)
- **Rotation:** Rotates around its center point
- **Initial state:** Stationary, pointing upward (rotation = 0°)
- **Friction:** Ship gradually slows down when not thrusting (optional but classic)

### The Asteroids

- **Shape:** Irregular polygons (randomly generated, jagged rock shapes)
- **Colors:** White outline only (vector style, no fill) OR thin white stroke
- **Types by size:**

| Size | Name | Approx. Radius | Points When Destroyed |
|------|------|----------------|----------------------|
| Large | Big asteroid | 40-50 px | 20 |
| Medium | Medium asteroid | 20-25 px | 50 |
| Small | Small asteroid | 10-15 px | 100 |

**Initial spawn:** Each wave starts with 4 large asteroids in random positions (avoiding the player's starting area).

### Projectiles (Bullets)

- **Shape:** Small dot or short line
- **Size:** 2-3 px diameter or 2×8 px line
- **Color:** White (#FFFFFF)
- **Speed:** Fast, approximately 10-12 px per frame
- **Lifetime:** Limited range/duration — bullets disappear after traveling a certain distance or after ~1 second
- **Maximum on screen:** Typically 4 bullets at a time

### The Saucer (Enemy)

- **Shape:** Classic flying saucer shape (ellipse with dome)
- **Size:** 
  - Large saucer: 40px wide
  - Small saucer: 20px wide
- **Color:** White outline (vector style)
- **Behavior:** Appears periodically, flies across the screen horizontally, shoots at the player
- **Points:**
  - Large saucer: 200 points
  - Small saucer: 1000 points
- **Shooting:** Fires bullets at random angles (large) or aimed at player (small, more accurate)

---

## Controls

| Key | Action |
|-----|--------|
| ← or A | Rotate left (counter-clockwise) |
| → or D | Rotate right (clockwise) |
| ↑ or W | Thrust forward |
| Space | Fire bullet |
| ↓ or S | Hyperspace (teleport to random location, optional) |
| P or Escape | Pause game |
| R | Restart game |

**Control details:**

- **Rotation:** Ship rotates at a constant angular speed while key is held
  - Rotation speed: 3-5° per frame (180-300° per second at 60fps)
  
- **Thrust:** Applies acceleration in the direction the ship is facing
  - Acceleration: 0.1-0.15 pixels per frame squared
  - Maximum speed: Cap velocity to prevent excessive speeds (e.g., 8 px/frame)
  
- **Fire:** Press to shoot a bullet from the ship's nose
  - Bullet inherits ship's velocity plus its own speed in facing direction
  - Fire rate: Limited, typically 4 bullets max on screen
  
- **Hyperspace (optional):** Teleport to a random location
  - Risk: May teleport into an asteroid (death)
  - Use: Emergency escape

---

## Physics

### Ship Movement

The ship uses vector-based movement with momentum.

**Rotation:**
```
// On each frame when rotating:
if (rotatingLeft) ship.angle -= rotationSpeed; // in radians
if (rotatingRight) ship.angle += rotationSpeed;
```

**Thrust:**
```
// On each frame when thrusting:
ship.vx += Math.cos(ship.angle) * thrustPower;
ship.vy += Math.sin(ship.angle) * thrustPower;

// Cap speed:
const speed = Math.sqrt(ship.vx * ship.vx + ship.vy * ship.vy);
if (speed > maxSpeed) {
  ship.vx = (ship.vx / speed) * maxSpeed;
  ship.vy = (ship.vy / speed) * maxSpeed;
}
```

**Friction (optional):**
```
// Apply friction each frame (slows ship gradually)
ship.vx *= 0.99;
ship.vy *= 0.99;
```

**Position update:**
```
ship.x += ship.vx;
ship.y += ship.vy;

// Wraparound:
if (ship.x < 0) ship.x = canvas.width;
if (ship.x > canvas.width) ship.x = 0;
if (ship.y < 0) ship.y = canvas.height;
if (ship.y > canvas.height) ship.y = 0;
```

### Asteroid Movement

Asteroids float in straight lines at constant velocities.

- **Initial velocity:** Random speed (0.5-2 px/frame) and random direction
- **No friction:** Asteroids maintain velocity
- **Wraparound:** Same as ship
- **Rotation:** Asteroids can slowly rotate for visual effect (optional)

### Bullet Movement

Bullets travel in straight lines at constant velocity.

- **Initial velocity:** Ship's velocity + bullet speed in facing direction
- **Wraparound:** Same as other objects
- **Lifetime:** Count frames or distance traveled; destroy after limit

---

## Collision Detection

### Ship vs Asteroid

**Detection:** Circle collision (use ship's center point and approximate radius)

```
const dx = ship.x - asteroid.x;
const dy = ship.y - asteroid.y;
const distance = Math.sqrt(dx * dx + dy * dy);

if (distance < ship.radius + asteroid.radius) {
  // Collision!
  shipDestroyed();
}
```

**On collision:**
1. Ship explodes (visual effect)
2. Lose one life
3. Respawn ship at center after 2-3 seconds
4. Brief invincibility after respawn (ship flashes, collisions ignored for ~3 seconds)

### Ship vs Saucer

Same as asteroid collision. Saucer's bullet also destroys ship.

### Bullet vs Asteroid

**Detection:** Point vs circle collision

```
const dx = bullet.x - asteroid.x;
const dy = bullet.y - asteroid.y;
const distance = Math.sqrt(dx * dx + dy * dy);

if (distance < asteroid.radius) {
  // Hit!
  destroyAsteroid(asteroid);
  destroyBullet(bullet);
}
```

**On hit:**

1. Destroy the bullet
2. Break the asteroid:
   - **Large asteroid:** Splits into 2-3 medium asteroids
   - **Medium asteroid:** Splits into 2-3 small asteroids
   - **Small asteroid:** Destroyed completely
3. Add points based on asteroid size
4. Play explosion effect (optional)

### Bullet vs Saucer

Same as bullet vs asteroid. Saucer is destroyed in one hit.

---

## Asteroid Splitting

When a large or medium asteroid is destroyed, it splits into smaller asteroids.

**Split behavior:**

- **Large → Medium:** Spawns 2-3 medium asteroids
- **Medium → Small:** Spawns 2-3 small asteroids
- **Small → Nothing:** Completely destroyed

**New asteroid properties:**
- Position: Same as destroyed asteroid's position (with small random offset)
- Velocity: Random direction, speed slightly faster than parent
- Each spawned asteroid has a different random velocity

**Implementation:**
```
function splitAsteroid(asteroid) {
  const newAsteroids = [];
  
  if (asteroid.size === 'large') {
    for (let i = 0; i < 2 + Math.floor(Math.random() * 2); i++) {
      newAsteroids.push({
        x: asteroid.x + (Math.random() - 0.5) * 20,
        y: asteroid.y + (Math.random() - 0.5) * 20,
        vx: (Math.random() - 0.5) * 3,
        vy: (Math.random() - 0.5) * 3,
        radius: 25,
        size: 'medium',
        points: 50
      });
    }
  } else if (asteroid.size === 'medium') {
    // Similar, but spawn small asteroids
  }
  
  return newAsteroids;
}
```

---

## Asteroid Shape Generation

Asteroids are irregular polygons that look like jagged rocks.

**Generation method:**
1. Start with a circle
2. Divide into 8-12 points around the circumference
3. Randomly adjust each point's radius inward or outward
4. Connect points to form a polygon

```
function generateAsteroidShape(radius, numVertices = 10) {
  const vertices = [];
  
  for (let i = 0; i < numVertices; i++) {
    const angle = (i / numVertices) * Math.PI * 2;
    // Random radius variation: 70% to 130% of base radius
    const r = radius * (0.7 + Math.random() * 0.6);
    
    vertices.push({
      x: Math.cos(angle) * r,
      y: Math.sin(angle) * r
    });
  }
  
  return vertices;
}
```

**Rendering:**
```
function drawAsteroid(ctx, asteroid) {
  ctx.strokeStyle = '#FFFFFF';
  ctx.lineWidth = 2;
  ctx.beginPath();
  
  asteroid.vertices.forEach((v, i) => {
    const x = asteroid.x + v.x;
    const y = asteroid.y + v.y;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  
  ctx.closePath();
  ctx.stroke();
}
```

---

## The Saucer (Enemy)

### Spawn Behavior

- **Trigger:** Random chance every 15-30 seconds, or based on score/time
- **Entry:** Appears from left or right edge of screen, at random height
- **Exit:** Flies across and leaves the opposite edge, or is destroyed

### Movement

- **Horizontal:** Constant speed (2-3 px/frame), left-to-right or right-to-left
- **Vertical:** Occasional random direction changes (up or down)
- **Wraparound:** Can wrap like other objects, or simply leave the screen

### Shooting

- **Large saucer:** Shoots at random angles (inaccurate)
- **Small saucer:** Shoots aimed at the player (accurate)
- **Fire rate:** Every 1-2 seconds

**Aiming logic (small saucer):**
```
// Calculate angle to player
const dx = player.x - saucer.x;
const dy = player.y - saucer.y;
const angle = Math.atan2(dy, dx);

// Add some inaccuracy
const inaccuracy = (Math.random() - 0.5) * 0.3; // radians

fireBullet(saucer.x, saucer.y, angle + inaccuracy);
```

### Saucer Types

| Property | Large Saucer | Small Saucer |
|----------|--------------|--------------|
| Width | 40px | 20px |
| Speed | 2 px/frame | 3 px/frame |
| Accuracy | Random | Aimed (±15°) |
| Points | 200 | 1000 |
| Spawn chance | More common | Less common |

---

## Wave System

### Wave Start

- Clear screen of previous wave objects
- Spawn new set of asteroids
- Player ship respawns at center (if destroyed during wave transition)

**Asteroid count by wave:**

| Wave | Large Asteroids |
|------|-----------------|
| 1 | 4 |
| 2 | 4 |
| 3 | 5 |
| 4+ | 5-6 |

After wave 4, asteroid count stays at 5-6.

### Wave Completion

When all asteroids and saucers are destroyed:
1. Brief pause (1-2 seconds)
2. Display "Wave [n] Complete" or similar (optional)
3. Spawn next wave's asteroids
4. Continue play

---

## Scoring

| Target | Points |
|--------|--------|
| Large asteroid | 20 |
| Medium asteroid | 50 |
| Small asteroid | 100 |
| Large saucer | 200 |
| Small saucer | 1000 |

**Score display:**
- Position: Top-left corner
- Format: "[number]"
- Font: Monospace or sans-serif, 20-24px
- Color: White

**High score:**
- Can be stored in localStorage
- Displayed at top-center: "HI: [number]"

---

## Lives System

- **Initial lives:** 3
- **Display:** Ships displayed in top-right corner as small triangle icons, or text "Lives: 3"
- **On death:**
  1. Ship explodes (visual effect)
  2. If lives remaining: respawn at center after 2-3 seconds
  3. Brief invincibility after respawn (ship flashes, ~3 seconds)
  4. If no lives remaining: game over

**Extra life bonus:** Some implementations award an extra life at score milestones (e.g., every 10,000 points).

---

## Visual Effects

### Ship Thrust Flame

When thrusting, a flame appears behind the ship.

- **Shape:** Triangle or series of flickering lines behind the ship
- **Color:** Yellow/orange or white
- **Animation:** Flickers on/off rapidly to create flame effect

**Implementation:**
```
function drawFlame(ctx, ship) {
  if (!ship.thrusting) return;
  
  // Randomly skip some frames for flicker
  if (Math.random() < 0.3) return;
  
  const flameLength = 10 + Math.random() * 10;
  
  ctx.strokeStyle = '#FFA500'; // Orange
  ctx.lineWidth = 2;
  ctx.beginPath();
  
  // Draw flame from ship's rear
  const rearX = ship.x - Math.cos(ship.angle) * 15;
  const rearY = ship.y - Math.sin(ship.angle) * 15;
  const flameEndX = rearX - Math.cos(ship.angle) * flameLength;
  const flameEndY = rearY - Math.sin(ship.angle) * flameLength;
  
  ctx.moveTo(rearX - Math.cos(ship.angle + Math.PI/2) * 5, 
             rearY - Math.sin(ship.angle + Math.PI/2) * 5);
  ctx.lineTo(flameEndX, flameEndY);
  ctx.lineTo(rearX - Math.cos(ship.angle - Math.PI/2) * 5, 
             rearY - Math.sin(ship.angle - Math.PI/2) * 5);
  
  ctx.stroke();
}
```

### Explosion Effect

When ship or asteroid is destroyed:

- **Ship explosion:** Series of line fragments flying outward, fading quickly
- **Asteroid explosion:** Smaller debris particles flying outward

**Simple implementation:** Draw 5-10 short lines radiating from the explosion point, moving outward and fading over 0.5-1 seconds.

### Invincibility Flash

When ship respawns with invincibility:

- Ship alternates between visible and invisible every 3-5 frames
- Or ship drawn at 50% opacity

---

## Game States

### 1. Title Screen

**Display:**
- "ASTEROIDS" in large text, centered
- "Press SPACE to start"
- Control summary (arrow keys to rotate/thrust, space to fire)
- High score display

**Behavior:**
- Pressing Space starts the game

### 2. Playing

**Display:**
- Ship (if alive)
- Asteroids
- Bullets
- Saucer (if present)
- Score and lives

**Behavior:**
- Normal gameplay
- Pressing P or Escape pauses

### 3. Paused

**Display:**
- Game frozen
- "PAUSED" centered
- "Press P to resume"
- Semi-transparent overlay (optional)

**Behavior:**
- Pressing P resumes
- Pressing R restarts

### 4. Player Death (Brief State)

**Display:**
- Explosion at ship's position
- Remaining asteroids continue moving

**Behavior:**
- Brief pause (2-3 seconds)
- If lives remaining: respawn at center with invincibility
- If no lives: go to Game Over

### 5. Game Over

**Display:**
- "GAME OVER" centered, large
- Final score
- "Press R to play again"
- Optional: New high score message

**Behavior:**
- Pressing R restarts game
- Pressing Escape returns to title screen

---

## Technical Implementation Notes

### Ship Drawing (Triangle)

```
function drawShip(ctx, ship) {
  const size = 15; // Distance from center to vertex
  
  ctx.strokeStyle = '#FFFFFF';
  ctx.lineWidth = 2;
  
  ctx.save();
  ctx.translate(ship.x, ship.y);
  ctx.rotate(ship.angle);
  
  ctx.beginPath();
  // Triangle pointing right (will be rotated by angle)
  ctx.moveTo(size, 0);           // Nose
  ctx.lineTo(-size * 0.7, -size * 0.6);  // Bottom left
  ctx.lineTo(-size * 0.4, 0);    // Center back indent
  ctx.lineTo(-size * 0.7, size * 0.6);   // Top left
  ctx.closePath();
  
  ctx.stroke();
  ctx.restore();
}
```

### Wraparound Function

```
function wrapPosition(obj, canvasWidth, canvasHeight) {
  if (obj.x < -obj.radius) obj.x = canvasWidth + obj.radius;
  if (obj.x > canvasWidth + obj.radius) obj.x = -obj.radius;
  if (obj.y < -obj.radius) obj.y = canvasHeight + obj.radius;
  if (obj.y > canvasHeight + obj.radius) obj.y = -obj.radius;
}
```

### Bullet Lifetime

```
function updateBullets() {
  for (let i = bullets.length - 1; i >= 0; i--) {
    const bullet = bullets[i];
    bullet.x += bullet.vx;
    bullet.y += bullet.vy;
    bullet.age++;
    
    wrapPosition(bullet, canvas.width, canvas.height);
    
    // Remove old bullets (after ~60 frames = 1 second)
    if (bullet.age > 60) {
      bullets.splice(i, 1);
    }
  }
}
```

### Firing Bullets

```
function fireBullet() {
  if (bullets.length >= 4) return; // Max 4 bullets on screen
  
  const bulletSpeed = 10;
  
  bullets.push({
    x: ship.x + Math.cos(ship.angle) * 15, // From ship nose
    y: ship.y + Math.sin(ship.angle) * 15,
    vx: ship.vx + Math.cos(ship.angle) * bulletSpeed,
    vy: ship.vy + Math.sin(ship.angle) * bulletSpeed,
    age: 0
  });
}
```

### Saucer Spawn Logic

```
let lastSaucerTime = 0;
const saucerInterval = 15000 + Math.random() * 15000; // 15-30 seconds

function checkSaucerSpawn(currentTime) {
  if (saucer) return; // Saucer already exists
  
  if (currentTime - lastSaucerTime > saucerInterval) {
    spawnSaucer();
    lastSaucerTime = currentTime;
  }
}

function spawnSaucer() {
  const fromLeft = Math.random() < 0.5;
  const isSmall = Math.random() < 0.3; // 30% chance for small saucer
  
  saucer = {
    x: fromLeft ? -20 : canvas.width + 20,
    y: Math.random() * canvas.height,
    vx: fromLeft ? 2 : -2,
    vy: (Math.random() - 0.5) * 2,
    width: isSmall ? 20 : 40,
    isSmall: isSmall,
    lastShot: 0
  };
}
```

---

## Common Bugs to Avoid

1. **Ship goes too fast:** Cap maximum velocity. Without a speed limit, thrusting continuously makes the ship uncontrollable.

2. **Bullets wrap infinitely:** Give bullets a maximum age/distance so they don't persist forever.

3. **Asteroid splitting creates overlapping asteroids:** Add small random offsets to split positions.

4. **Player spawns inside an asteroid:** After death, clear a small area around spawn point or check for collisions before spawning.

5. **Saucer spawns off-screen and never enters:** Ensure saucer velocity is toward the play area.

6. **Collision detection at wraparound edge:** An object at x=5 and another at x=795 are actually close (15px apart due to wraparound). Handle this by checking distance both directly and across wrap boundary.

7. **Hyperspace lands player inside asteroid:** Either check for clear landing zone or accept it as game risk (classic behavior).

---

## Minimum Viable Product Checklist

A complete Asteroids implementation must have:

- [ ] Canvas rendering at 800×600
- [ ] Player ship as triangle, controllable (rotate, thrust, fire)
- [ ] Vector-based movement with momentum
- [ ] Wraparound screen edges
- [ ] Asteroids as irregular polygons
- [ ] Asteroids split when shot (large → medium → small)
- [ ] Bullets destroy asteroids
- [ ] Ship destroyed by asteroid collision
- [ ] Lives system (3 lives)
- [ ] Respawn at center after death
- [ ] Score system (different points per asteroid size)
- [ ] Wave progression (new asteroids when all destroyed)
- [ ] Enemy saucer that appears and shoots
- [ ] Game states: Title → Playing → Paused → Game Over
- [ ] Pause and Restart functionality
- [ ] No external dependencies (all code in one HTML file)

---

## Quick Reference

| Element | Value |
|---------|-------|
| Canvas | 800×600 px |
| Ship size | ~20px base triangle |
| Ship rotation speed | 3-5°/frame |
| Ship max speed | 8 px/frame |
| Thrust acceleration | 0.1-0.15 px/frame² |
| Bullet speed | 10-12 px/frame |
| Max bullets | 4 |
| Large asteroid | 40-50px radius, 20 pts |
| Medium asteroid | 20-25px radius, 50 pts |
| Small asteroid | 10-15px radius, 100 pts |
| Large saucer | 40px, 200 pts |
| Small saucer | 20px, 1000 pts |
| Lives | 3 |
| Initial asteroids | 4 large |

---

End of specification.
