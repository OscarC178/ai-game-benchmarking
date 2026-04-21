# Space Invaders — Complete Game Specification

## Overview

Space Invaders is a single-player fixed shooter. You control a cannon at the bottom of the screen, moving left and right. Rows of aliens descend from above, moving side-to-side and gradually advancing downward. Shoot all aliens before they reach the bottom or destroy your cannon. You have limited lives. Aliens shoot back. Shields provide temporary cover but degrade when hit. Clear all aliens to advance to the next wave.

---

## Game Elements

### The Arena

- **Canvas size:** 800×600 pixels
- **Background:** Solid black (#000000)
- **Boundaries:**
  - Left wall at x = 0
  - Right wall at x = 800
  - Top at y = 0
  - Bottom at y = 600 (player area)

### The Player Cannon

- **Size:** 50px wide × 30px tall
- **Position:** Horizontally centered, 20px from bottom of canvas (y ≈ 550)
- **Color:** White (#FFFFFF) or cyan (#00FFFF)
- **Shape:** Simple cannon/tank shape (rectangle with a small barrel on top, or pixel-art style)
- **Movement:** Horizontal only (left/right)
- **Speed:** 5 pixels per frame
- **Boundary constraints:** Cannot move beyond left/right walls (stay within canvas)
- **Shooting:** Fires one laser upward. Must wait for laser to hit something or leave screen before firing again.
- **Lives:** Starts with 3 lives

### The Aliens

**Layout:** 5 rows × 11 columns = 55 aliens total

**Rows (from top to bottom):**

| Row | Alien Type | Appearance | Points |
|-----|------------|------------|--------|
| 1 (top) | Type A | Small, squid-like | 30 points |
| 2 | Type A | Small, squid-like | 30 points |
| 3 | Type B | Medium, crab-like | 20 points |
| 4 | Type B | Medium, crab-like | 20 points |
| 5 (bottom) | Type C | Large, octopus-like | 10 points |

**Alien dimensions:**
- Type A (small): 30×20 px
- Type B (medium): 40×25 px
- Type C (large): 50×30 px

**Colors:**
- Type A: White or light green
- Type B: White or yellow
- Type C: White or red
- All aliens can be simple white shapes with distinct silhouettes

**Initial position:**
- First row starts 80px from top
- Columns span from approximately x = 80 to x = 720
- Horizontal spacing between aliens: ~15px
- Vertical spacing between rows: ~15px

### The Shields (Barriers)

**Count:** 4 shields, evenly spaced across the bottom half of the screen

**Position:**
- Each shield: 70px wide × 50px tall
- Centered vertically around y = 450
- Spaced horizontally: approximately at x = 100, 280, 460, 640

**Shape:** Arch/bunker shape — rectangular base with a semicircular or rectangular cutout at the bottom center (like an inverted U)

**Color:** Green (#00FF00) or white

**Destruction behavior:** Shields are pixel-based. When hit by any projectile (player or alien), the shield is damaged at that exact point. Small chunks are removed. Eventually, shields can be completely destroyed or carved through.

**Implementation:** Store each shield as a 2D array of pixels or use canvas pixel manipulation. When a projectile hits, remove a small circular area (radius 3-5 pixels) from the shield.

### Projectiles

#### Player Laser

- **Size:** 3px wide × 15px tall
- **Color:** White or yellow (#FFFF00)
- **Speed:** 8 pixels per frame (upward)
- **Behavior:** Travels straight up until hitting an alien, shield, or leaving the top of the screen
- **Fire rate:** Only one laser can be on screen at a time. Player must wait for it to hit something or leave before firing again.

#### Alien Bomb

- **Size:** 4×4 px (small square) or 3×6 px (small rectangle)
- **Color:** White or red (#FF0000)
- **Speed:** 3-4 pixels per frame (downward)
- **Fire pattern:** Random aliens in the bottom row of each column drop bombs at random intervals
- **Maximum on screen:** Typically 3-4 bombs at once

### The Mystery Ship (Bonus)

**Appearance:** A larger, different alien ship that flies across the top of the screen

- **Size:** 60×25 px
- **Color:** Red or white
- **Position:** Flies horizontally across the top of the screen (y ≈ 40)
- **Movement:** Appears randomly, moves from left to right (or right to left) at constant speed
- **Speed:** 3 pixels per frame
- **Points:** Random value from 50, 100, 150, or 300 points
- **Spawn:** Random chance (every 10-30 seconds) or triggered by certain conditions

---

## Alien Movement Pattern

### Horizontal Movement

The aliens move as a group, in a "step" pattern:

1. All aliens move right together (one step)
2. Continue moving right until the rightmost alien hits the right boundary
3. When an alien would go past the right wall, the entire group drops down one row AND reverses direction
4. Now all aliens move left together
5. Continue moving left until the leftmost alien hits the left boundary
6. Drop down one row, reverse direction, move right
7. Repeat

**Movement timing:** The aliens step at regular intervals. The interval decreases as fewer aliens remain.

| Aliens Remaining | Step Interval |
|------------------|---------------|
| 55-45 | 800ms |
| 44-35 | 600ms |
| 34-25 | 400ms |
| 24-15 | 300ms |
| 14-5 | 200ms |
| 4-1 | 100ms |

**Step distance:** Each horizontal step moves aliens 10-15 pixels. Each vertical drop is 15-20 pixels.

### Animation

Aliens have two animation frames that alternate with each step:

- **Frame 1:** "Arms down" position
- **Frame 2:** "Arms up" position

This creates a walking/marching effect.

### Collision with Bottom

If any alien reaches the player's row (y ≥ 500 or so), the game ends immediately — the aliens have invaded.

---

## Alien Shooting Behavior

### Which Aliens Can Shoot

Only aliens in the **bottom row of each column** can shoot. If an alien is destroyed, the alien above it can now shoot.

**Example:** In a column with aliens at y = 100, 130, 160, 190, 220, only the alien at y = 220 shoots. If that alien is destroyed, the alien at y = 190 can now shoot.

### Fire Rate

- Each bottom-row alien has a random chance to fire on each game tick
- Not every tick — there's a delay between shots
- Typical rate: each shooter alien attempts to fire every 1-3 seconds
- Maximum bombs on screen: 3-4 at a time

### Implementation

```
// For each bottom-row alien:
if (Math.random() < 0.002 && bombs.length < 4) { // Adjust probability as needed
  fireBomb(alien.x, alien.y + alien.height);
}
```

---

## Collision Detection

### Player Laser vs Alien

**Condition:** Laser rectangle intersects alien rectangle.

**On hit:**
1. Destroy the alien (remove from array or mark as dead)
2. Destroy the laser (remove from screen)
3. Add alien's point value to score
4. Play explosion effect (optional)

### Player Laser vs Shield

**Condition:** Laser intersects shield's remaining pixels.

**On hit:**
1. Destroy the laser
2. Remove a small chunk of the shield at the impact point

### Player Laser vs Mystery Ship

**Condition:** Laser intersects mystery ship rectangle.

**On hit:**
1. Destroy the mystery ship
2. Destroy the laser
3. Add random bonus points (50, 100, 150, or 300)
4. Display bonus score briefly at impact location

### Alien Bomb vs Player

**Condition:** Bomb rectangle intersects player cannon rectangle.

**On hit:**
1. Destroy the bomb
2. Player loses one life
3. Player cannon briefly disappears/explodes
4. Respawn player cannon at center after 1-2 seconds
5. If lives = 0, game over

### Alien Bomb vs Shield

**Condition:** Bomb intersects shield's remaining pixels.

**On hit:**
1. Destroy the bomb
2. Remove a small chunk of the shield at the impact point

### Alien vs Player (Collision)

**Condition:** An alien's y-position + height reaches or passes the player's y-position.

**On hit:**
1. Game over immediately (invasion)

### Alien vs Shield

**Condition:** Aliens descend low enough to collide with shields.

**On hit:**
1. The shield is destroyed / removed as aliens pass through it

---

## Score System

| Target | Points |
|--------|--------|
| Alien Type A (top 2 rows) | 30 |
| Alien Type B (middle 2 rows) | 20 |
| Alien Type C (bottom row) | 10 |
| Mystery Ship | 50, 100, 150, or 300 (random) |

**Score display:**
- Position: Top-left corner
- Format: "Score: [number]"
- Font: Monospace or sans-serif, 20px
- Color: White

**High score:**
- Can be stored in localStorage
- Displayed at top-center: "HI-SCORE: [number]"

---

## Lives System

- **Initial lives:** 3
- **Display:** Top-right corner, as "Lives: 3" or as small cannon icons
- **On death:** Player respawns at center after 1-2 seconds
- **On final death (lives = 0):** Game over
- **Life bonus:** Some implementations award an extra life at certain score thresholds (e.g., every 1000 points)

---

## Wave Progression

When all 55 aliens are destroyed:

1. Brief pause / victory fanfare
2. Reset alien formation to starting positions
3. Increase game difficulty:
   - Aliens start lower (closer to player)
   - Aliens move faster
   - Aliens shoot more frequently
4. Shields are NOT restored (remain damaged)
5. Score and lives carry over

**Wave counter:** Display current wave number (optional): "Wave 1", "Wave 2", etc.

---

## Controls

| Key | Action |
|-----|--------|
| ← or A | Move cannon left |
| → or D | Move cannon right |
| Space | Fire laser |
| P | Pause game |
| R | Restart game |
| Escape | Return to title screen |

**Control notes:**
- Player can hold left/right for continuous movement
- Player can only have ONE laser on screen at a time
- Must wait for laser to hit or exit before firing again
- Both arrow keys and WASD work

---

## Game States

### 1. Title Screen

**Display:**
- "SPACE INVADERS" in large text, centered
- Two rows of aliens (demo display)
- "Press SPACE to start"
- Controls: "← → to move, SPACE to fire"
- High score display

**Behavior:**
- No gameplay
- Pressing Space starts the game

### 2. Playing

**Display:**
- All game elements (player, aliens, shields, projectiles)
- Score, lives, high score at top

**Behavior:**
- Normal gameplay
- Aliens move and shoot
- Player moves and shoots
- Pressing P pauses the game

### 3. Paused

**Display:**
- Game frozen
- "PAUSED" centered
- "Press P to resume"
- Semi-transparent overlay

**Behavior:**
- Pressing P resumes
- Pressing R restarts

### 4. Player Death (Brief State)

**Display:**
- Explosion effect at player position
- All other action continues (aliens still move)

**Behavior:**
- Brief pause (1-2 seconds)
- Player respawns at center
- Return to Playing state
- If no lives remaining, go to Game Over

### 5. Game Over

**Display:**
- "GAME OVER" centered, large
- Final score
- "Press R to play again"
- Optional: New high score celebration

**Behavior:**
- Pressing R restarts with fresh state
- Pressing ESC returns to title screen

### 6. Wave Complete (Brief State)

**Display:**
- "WAVE [n] COMPLETE!" or similar
- Brief pause

**Behavior:**
- After 1-2 seconds, start next wave
- Reset aliens, increase difficulty

---

## Visual Polish

### Alien Animation

Aliens should have two animation frames (optional but classic):

- **Frame A:** Arms/legs in one position
- **Frame B:** Arms/legs in alternate position
- Toggle between frames on each step

This gives aliens a "marching" appearance as they move.

### Explosion Effects

When an alien is destroyed:

1. Show brief white flash (1-2 frames)
2. Or show small explosion particle effect (4-8 particles spreading outward)
3. Remove alien

Duration: 100-200ms

### Mystery Ship

- Display bonus score at destruction point: "+100" etc.
- Score floats upward briefly before fading

### Player Death

- Explosion effect (larger than alien explosion)
- Player disappears for 1-2 seconds
- Respawn at center with brief invincibility (optional)

---

## Technical Implementation Notes

### Alien Data Structure

Store aliens as a 2D array (rows and columns) or flat array:

```
aliens = [
  { x: 100, y: 80, type: 'A', width: 30, height: 20, alive: true },
  { x: 145, y: 80, type: 'A', width: 30, height: 20, alive: true },
  // ... 55 total
];
```

Or as a 2D array for easier position management:

```
aliens = [
  // Row 0 (top)
  [{type: 'A', alive: true}, {type: 'A', alive: true}, ...],
  // Row 1
  [{type: 'A', alive: true}, {type: 'A', alive: true}, ...],
  // ... 5 rows total, 11 columns each
];
```

### Alien Movement Timing

Use a timer or frame counter for alien steps:

```
let stepTimer = 0;
const baseStepInterval = 800; // ms
let currentStepInterval = baseStepInterval;

function update(deltaTime) {
  stepTimer += deltaTime;
  
  const aliensAlive = aliens.filter(a => a.alive).length;
  currentStepInterval = calculateInterval(aliensAlive);
  
  if (stepTimer >= currentStepInterval) {
    stepTimer = 0;
    moveAliens();
  }
}

function calculateInterval(aliensAlive) {
  // Faster as fewer aliens remain
  if (aliensAlive > 44) return 800;
  if (aliensAlive > 34) return 600;
  if (aliensAlive > 24) return 400;
  if (aliensAlive > 14) return 250;
  if (aliensAlive > 4) return 150;
  return 80; // Last few aliens move very fast
}
```

### Direction Reversal and Descent

```
let alienDirection = 1; // 1 = right, -1 = left
const alienStepSize = 10; // horizontal movement per step
const alienDropDistance = 20; // vertical drop when hitting wall

function moveAliens() {
  // Find boundaries
  let leftMost = 800, rightMost = 0;
  aliens.forEach(alien => {
    if (alien.alive) {
      leftMost = Math.min(leftMost, alien.x);
      rightMost = Math.max(rightMost, alien.x + alien.width);
    }
  });
  
  // Check if we need to reverse direction
  let shouldReverse = false;
  if (alienDirection === 1 && rightMost + alienStepSize > 780) {
    shouldReverse = true;
  } else if (alienDirection === -1 && leftMost - alienStepSize < 20) {
    shouldReverse = true;
  }
  
  // Move aliens
  aliens.forEach(alien => {
    if (alien.alive) {
      if (shouldReverse) {
        alien.y += alienDropDistance;
      } else {
        alien.x += alienStepSize * alienDirection;
      }
    }
  });
  
  if (shouldReverse) {
    alienDirection *= -1;
  }
}
```

### Shield Pixel System

Use a 2D array or canvas imageData for each shield:

```
// Simple approach: 2D boolean array
const shieldPixelWidth = 70;
const shieldPixelHeight = 50;
shield = []; // true = pixel exists, false = destroyed

for (let y = 0; y < shieldPixelHeight; y++) {
  shield[y] = [];
  for (let x = 0; x < shieldPixelWidth; x++) {
    // Define arch shape
    const isArch = y < 35 || (x < 25 || x > 45);
    shield[y][x] = isArch;
  }
}

// On collision:
function damageShield(shield, hitX, hitY) {
  const radius = 4;
  for (let dy = -radius; dy <= radius; dy++) {
    for (let dx = -radius; dx <= radius; dx++) {
      if (dx*dx + dy*dy <= radius*radius) {
        const px = hitX + dx;
        const py = hitY + dy;
        if (py >= 0 && py < shieldPixelHeight && 
            px >= 0 && px < shieldPixelWidth) {
          shield[py][px] = false;
        }
      }
    }
  }
}

// Render:
function renderShield(shield, offsetX, offsetY) {
  for (let y = 0; y < shieldPixelHeight; y++) {
    for (let x = 0; x < shieldPixelWidth; x++) {
      if (shield[y][x]) {
        ctx.fillStyle = '#00FF00';
        ctx.fillRect(offsetX + x, offsetY + y, 1, 1);
      }
    }
  }
}
```

### Single Laser Constraint

```
let playerLaser = null; // null = no laser on screen

function fireLaser() {
  if (playerLaser === null) {
    playerLaser = {
      x: player.x + player.width/2 - 1.5,
      y: player.y - 15,
      width: 3,
      height: 15
    };
  }
}

// In update:
if (playerLaser) {
  playerLaser.y -= 8; // Move up
  
  // Check for leaving screen
  if (playerLaser.y + playerLaser.height < 0) {
    playerLaser = null;
  }
  
  // Check for collisions...
  if (hitsAlien || hitsShield) {
    playerLaser = null;
  }
}
```

### Bottom-Row Shooting Aliens

```
function getShooterAliens() {
  const shooters = [];
  
  // For each column (0-10)
  for (let col = 0; col < 11; col++) {
    // Find the lowest (highest y) alive alien in this column
    let lowestAlien = null;
    for (let row = 4; row >= 0; row--) { // Start from bottom row
      const alien = aliens[row][col];
      if (alien.alive) {
        lowestAlien = alien;
        break;
      }
    }
    if (lowestAlien) {
      shooters.push(lowestAlien);
    }
  }
  
  return shooters;
}
```

---

## Common Bugs to Avoid

1. **Multiple lasers on screen:** Ensure only one player laser can exist at a time. Set laser to null after it hits something or leaves screen.

2. **Aliens overlap when descending:** When aliens reverse and drop, they shouldn't overlap. The drop distance should be greater than row height.

3. **Dead aliens still shoot:** Only check living aliens for shooting. Mark aliens as dead and filter them out of shooter calculations.

4. **Aliens jitter at boundaries:** When aliens hit the wall and reverse, make sure they don't oscillate. They should move down once, then continue in the opposite direction.

5. **Shields regenerated on respawn:** Shields should persist between waves. Only restore shields on full game restart.

6. **Player can fire while dead:** Disable firing during the death/respawn animation.

7. **Aliens shoot too fast:** Limit the number of bombs on screen and add delay between shots.

8. **Last alien moves too fast:** Cap the minimum step interval so the game remains playable even with 1-2 aliens.

---

## Minimum Viable Product Checklist

A complete Space Invaders implementation must have:

- [ ] Canvas rendering at 800×600
- [ ] Player cannon that moves left/right and fires upward
- [ ] 55 aliens in 5 rows × 11 columns, with 3 distinct types
- [ ] Aliens move side-to-side, descending when hitting walls
- [ ] Aliens shoot bombs downward at random intervals
- [ ] Player can only have one laser on screen at a time
- [ ] Collision detection: laser vs alien, bomb vs player, projectiles vs shields
- [ ] Score system with different points per alien type
- [ ] Lives system (3 lives, lose one when hit by bomb)
- [ ] 4 shields that degrade when hit by any projectile
- [ ] Game ends when all lives lost OR aliens reach the bottom
- [ ] Wave progression (aliens reset when all destroyed)
- [ ] Game states: Title → Playing → Paused → Game Over
- [ ] Pause (P) and Restart (R) functionality
- [ ] Aliens move faster as fewer remain
- [ ] No external dependencies (all code in one HTML file)

---

## Quick Reference

| Element | Value |
|---------|-------|
| Canvas | 800×600 px |
| Player cannon | 50×30 px |
| Alien Type A | 30×20 px, 30 pts |
| Alien Type B | 40×25 px, 20 pts |
| Alien Type C | 50×30 px, 10 pts |
| Aliens total | 55 (5 rows × 11 cols) |
| Shields | 4, each 70×50 px |
| Player laser | 3×15 px |
| Lives | 3 |
| Player speed | 5 px/frame |
| Laser speed | 8 px/frame (up) |
| Bomb speed | 3-4 px/frame (down) |
| Mystery ship | 60×25 px, 50-300 pts |

---

End of specification.
