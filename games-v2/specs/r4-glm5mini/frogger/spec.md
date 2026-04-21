# Frogger — Complete Game Specification

## Overview

Frogger is a single-player action game. You control a frog trying to cross a busy road and a treacherous river to reach five home bays at the top of the screen. On the road, avoid cars and trucks. On the river, hop onto logs and turtles to cross — fall in the water and you die. Reach all five home bays to complete the level. You have limited lives and a time limit per frog. The game ends when all lives are lost.

---

## Game Elements

### The Arena

- **Canvas size:** 560×650 pixels (classic arcade proportions, or scale to fit)
- **Layout (from bottom to top):**
  - Row 0: Start zone (safe, grass)
  - Rows 1-5: Road (5 lanes of traffic)
  - Row 6: Median/safe zone (grass)
  - Rows 7-12: River (6 lanes of water with logs and turtles)
  - Row 13: Home bay area (5 goal positions)
- **Cell size:** 40×40 pixels (each row is 40px tall, frog occupies one cell)
- **Background:**
  - Grass: Green (#228B22 or similar)
  - Road: Dark gray (#333333) with white lane markings (optional)
  - River: Blue (#0000AA or #1E90FF)
  - Home bays: Blue water with green lily pads

### The Frog (Player)

- **Size:** 40×40 pixels (one cell)
- **Shape:** Stylized frog (circle or oval with eyes, or simple geometric frog shape)
- **Color:** Bright green (#00FF00)
- **Position:** Starts at bottom-center of screen
- **Movement:** Grid-based, moves one cell at a time
  - Up, Down, Left, Right
  - Each keypress = one cell hop
  - Movement is instant (teleports to new cell)
- **Orientation:** Frog faces the direction it just moved
- **Lives:** Starts with 3-5 frogs (displayed at bottom of screen)
- **Death animation:** Brief animation when dying (spinning, sinking, or squishing)

### Vehicles (Road Section)

Five lanes of traffic, each with vehicles moving at different speeds and directions.

| Lane | Vehicle Type | Size | Direction | Speed | Notes |
|------|--------------|------|-----------|-------|-------|
| 1 (bottom road lane) | Car | 40×40 | Left | 1-2 px/frame | Small, fast |
| 2 | Truck | 80×40 | Right | 0.5-1 px/frame | Long, slow |
| 3 | Car | 40×40 | Left | 2-3 px/frame | Fast |
| 4 | Truck | 120×40 | Right | 0.5 px/frame | Very long, slow |
| 5 (top road lane) | Car | 40×40 | Left | 1.5-2.5 px/frame | Medium speed |

**Vehicle colors:**
- Cars: Red, yellow, blue, white (variety)
- Trucks: Larger, often darker colors

**Vehicle spacing:** Multiple vehicles per lane, evenly spaced or with random gaps.

### Logs (River Section)

Floating logs that the frog can ride to cross the river.

| Lane | Log Size | Direction | Speed |
|------|----------|-----------|-------|
| 7 (bottom river lane) | Medium (80px) | Left | 1 px/frame |
| 8 | Long (120px) | Right | 0.5 px/frame |
| 9 | Short (40px) | Left | 2 px/frame |
| 10 | Medium (80px) | Right | 1 px/frame |
| 11 | Long (120px) | Left | 0.5 px/frame |
| 12 (top river lane) | Medium (80px) | Right | 1.5 px/frame |

**Log appearance:** Brown (#8B4513), rectangular with rounded ends, wood grain texture (optional).

### Turtles (River Section)

Turtles that surface and dive. The frog can ride them when surfaced.

| Lane | Turtle Group | Direction | Speed | Behavior |
|------|--------------|-----------|-------|----------|
| 7-12 (varies) | 3 turtles side-by-side | Left or Right | 0.5-1.5 px/frame | Cycle: surface → dive |

**Turtle appearance:**
- Surfaced: Green/brown, visible shell and head
- Diving: Animated sinking, eventually disappear underwater
- Diving duration: 2-3 seconds submerged, 4-5 seconds surfaced

**Turtle cycle:**
1. Surfaced (safe to land on)
2. Beginning to dive (still safe, visual warning)
3. Fully submerged (deadly — frog drowns if standing on diving turtle)

**Implementation:** Turtles alternate between safe and unsafe states with visual indicators.

### Home Bays (Goal)

Five home positions at the top of the screen.

- **Size:** Each bay is 40px wide × 40px tall
- **Spacing:** Spaced evenly across the top row with gaps between
- **Appearance:** Blue water with green lily pad or alcove
- **Goal:** Guide the frog into an empty bay
- **Completion:** All 5 bays filled = level complete

**Home bay hazards:**
- Some implementations have an alligator or otter that can occupy a bay temporarily
- If the bay is occupied by an enemy, the frog dies when entering

---

## Movement and Collision

### Frog Movement

The frog moves in discrete hops, one cell at a time.

**Movement rules:**
- Each keypress = one hop in that direction
- Movement is instantaneous (no sliding or walking)
- Frog visually "hops" with a quick animation
- After moving, frog faces the direction of movement

**Boundary constraints:**
- Cannot move beyond left/right screen edges
- Cannot move down past the starting row
- Can move up into home bays

### Road Collision

**Condition:** Frog occupies same cell as any part of a vehicle.

**On collision:**
1. Frog dies (squished)
2. Death animation
3. Lose one life
4. Respawn at starting position

### River Mechanics

The frog must ride logs and turtles to cross the river.

**Safe objects:** Logs and surfaced turtles
- When frog lands on a log/turtle, it moves WITH the object
- Frog inherits the object's velocity
- Frog can hop between logs/turtles

**Death conditions:**
- Falling into water (not on a log or turtle)
- Standing on a turtle when it dives
- Carried off-screen by a log or turtle (going past left/right edge)

**Riding mechanics:**
```
// Each frame, if frog is on a log or turtle:
frog.x += object.vx; // Move with the object

// Check if frog has been carried off screen:
if (frog.x < -20 || frog.x > canvas.width + 20) {
  frogDeath('drowned');
}
```

### Home Bay Success

**Condition:** Frog enters an unoccupied home bay.

**On success:**
1. Frog occupies the bay (visual confirmation)
2. Points awarded based on time remaining
3. New frog spawns at starting position
4. Bay is now filled (cannot be used again this level)

**Home bay failure:**
- If bay is occupied by enemy (alligator, otter): frog dies
- If frog misses the bay and lands in water: frog dies

---

## Timing

### Time Limit

Each frog has a limited time to reach a home bay.

- **Time limit:** 30-60 seconds per frog
- **Display:** Timer bar at bottom or side of screen
- **Visual:** Decreasing bar (green → yellow → red)
- **Time's up:** If timer runs out, frog dies

**Implementation:**
```
const timeLimit = 60; // seconds
let timeRemaining = timeLimit;

// Each frame:
timeRemaining -= deltaTime / 1000;

if (timeRemaining <= 0) {
  frogDeath('timeout');
}
```

### Time Bonus

Faster completion = more points.

**Bonus calculation:**
- Points = timeRemaining × bonusMultiplier
- Typical: 10-20 points per second remaining

---

## Scoring

### Points

| Action | Points |
|--------|--------|
| Forward hop | 10 points |
| Reaching home bay | 50 points |
| Time bonus | 10 pts per second remaining |
| Level completion bonus | 1000 points |
| Eating fly (optional) | 200 points |

**Note:** Points for forward hops encourage efficient routes.

**Score display:**
- Position: Top of screen
- Format: "SCORE: [number]"
- Font: Monospace or digital, 18-20px
- Color: White or yellow

**High score:**
- Stored in localStorage
- Displayed: "HIGH: [number]"

---

## Lives System

- **Initial lives:** 3-5 frogs (configurable, typically 3)
- **Display:** Frog icons at bottom of screen
- **Life loss conditions:**
  - Hit by vehicle
  - Fell in water
  - Standing on diving turtle
  - Carried off screen
  - Time ran out
  - Hit by enemy in home bay

**On death:**
1. Death animation (brief)
2. Lose one life
3. If lives remaining: respawn at start with full timer
4. If no lives: game over

---

## Controls

| Key | Action |
|-----|--------|
| ↑ or W | Hop forward (up) |
| ↓ or S | Hop backward (down) |
| ← or A | Hop left |
| → or D | Hop right |
| P or Escape | Pause game |
| R | Restart game |

**Control notes:**
- Only one movement per keypress
- Holding a key does NOT auto-repeat (must press each time)
- Both arrow keys and WASD work

---

## Level Progression

### Level Completion

When all 5 home bays are filled:
1. Brief victory display
2. Level complete bonus (1000 points)
3. Reset home bays (all empty again)
4. Increase difficulty:
   - Vehicles move faster
   - Logs/turtles move faster
   - Shorter time limit
   - More enemies in home bays

### Difficulty Scaling

| Level | Vehicle Speed | Log Speed | Time Limit | Notes |
|-------|---------------|-----------|------------|-------|
| 1 | Base | Base | 60 sec | Normal |
| 2 | +10% | +10% | 55 sec | |
| 3 | +20% | +20% | 50 sec | |
| 4+ | +30% | +30% | 45 sec | Snakes on logs |

**Level indicators:** Display "LEVEL [n]" at start of each level.

---

## Visual Design

### Frog Appearance

**Simple version:** Green circle with two white dots for eyes.

**Detailed version:**
- Oval body (green)
- Two bulging eyes (white with black pupils)
- Four legs (visible when hopping)
- Hop animation: stretch body vertically

**Orientation:** Frog faces the direction of last movement.

### Vehicle Appearance

- **Cars:** Rectangular with rounded corners, solid color, maybe wheels
- **Trucks:** Longer rectangles, different colors, maybe cab and trailer distinction

### Log Appearance

- Brown rectangle
- Rounded ends
- Optional: wood grain lines for texture

### Turtle Appearance

**Surfaced:**
- Three turtles in a row
- Each: green oval shell, small head
- Total width: 120px (3 × 40px)

**Diving animation:**
1. Turtles begin to lower into water
2. Animated submersion over 1-2 seconds
3. Fully underwater (not visible)
4. Resurface after 2-3 seconds

**Visual warning:** When turtles are about to dive, show animation (bubbles, turtles lowering).

### Home Bay Appearance

- Blue background (water)
- Green lily pad or grass alcove
- When occupied: Show frog sitting on lily pad

---

## Advanced Features (Optional)

### Enemies on Logs

**Snakes:** Appear on logs at higher levels
- Frog cannot land on log segment with snake
- Snake moves with log
- Contact with snake = death

### Home Bay Enemies

**Alligator:** Occasionally occupies a home bay
- Visual: Alligator head in the bay
- If frog enters bay with alligator: death
- Alligator leaves after a few seconds

**Otter:** Swims across river, can knock frog off log
- Contact = death

### Bonus Items

**Fly:** Appears occasionally on a log or in a bay
- Eating fly: +200 points
- Frog must reach the fly's location

**Lady frog:** Appears occasionally on a log
- Escorting lady frog to home bay: +200 bonus

---

## Game States

### 1. Title Screen

**Display:**
- "FROGGER" in large text, centered
- Animated frog hopping
- "Press SPACE to start"
- Control instructions
- High score

**Behavior:**
- Pressing Space starts game

### 2. Level Start

**Display:**
- "LEVEL [n]" centered
- Brief pause before gameplay

**Behavior:**
- After 1 second, begin gameplay

### 3. Playing

**Display:**
- Frog at starting position
- Vehicles moving on road
- Logs and turtles moving on river
- Home bays at top
- Score, lives, timer

**Behavior:**
- Normal gameplay
- Pressing P pauses

### 4. Frog Death

**Display:**
- Death animation at frog's position
- Other objects continue moving

**Behavior:**
- Brief pause (1 second)
- If lives remaining: spawn new frog
- If no lives: game over

### 5. Home Bay Reached

**Display:**
- Frog in home bay
- Points awarded (displayed briefly)
- Brief pause

**Behavior:**
- Spawn new frog at start
- If all 5 bays filled: level complete

### 6. Level Complete

**Display:**
- "LEVEL COMPLETE!" centered
- Bonus points displayed
- All bays filled with frogs

**Behavior:**
- After 2 seconds, start next level

### 7. Paused

**Display:**
- Game frozen
- "PAUSED" centered
- "Press P to resume"

**Behavior:**
- Pressing P resumes
- Pressing R restarts

### 8. Game Over

**Display:**
- "GAME OVER" centered, large
- Final score
- "Press R to play again"

**Behavior:**
- Pressing R restarts
- Pressing Escape returns to title

---

## Technical Implementation Notes

### Grid-Based Movement

```
const CELL_SIZE = 40;
const COLS = 14;  // 560 / 40
const ROWS = 16;  // 650 / 40 (approximately)

frog = {
  x: canvas.width / 2,      // Pixel position
  y: canvas.height - CELL_SIZE / 2, // Start at bottom
  gridX: Math.floor(COLS / 2),
  gridY: ROWS - 1,
  facing: 'up',
  alive: true
};

function moveFrog(direction) {
  if (!frog.alive) return;
  
  switch(direction) {
    case 'up':
      if (frog.gridY > 0) {
        frog.gridY--;
        frog.y -= CELL_SIZE;
        frog.facing = 'up';
        score += 10; // Points for forward movement
      }
      break;
    case 'down':
      if (frog.gridY < ROWS - 1) {
        frog.gridY++;
        frog.y += CELL_SIZE;
        frog.facing = 'down';
      }
      break;
    case 'left':
      if (frog.gridX > 0) {
        frog.gridX--;
        frog.x -= CELL_SIZE;
        frog.facing = 'left';
      }
      break;
    case 'right':
      if (frog.gridX < COLS - 1) {
        frog.gridX++;
        frog.x += CELL_SIZE;
        frog.facing = 'right';
      }
      break;
  }
}
```

### Vehicle Collision

```
function checkVehicleCollision() {
  const frogLeft = frog.x - CELL_SIZE/2;
  const frogRight = frog.x + CELL_SIZE/2;
  const frogTop = frog.y - CELL_SIZE/2;
  const frogBottom = frog.y + CELL_SIZE/2;
  
  for (const vehicle of vehicles) {
    // Check if frog overlaps with vehicle
    if (frogRight > vehicle.x &&
        frogLeft < vehicle.x + vehicle.width &&
        frogBottom > vehicle.y &&
        frogTop < vehicle.y + CELL_SIZE) {
      return true; // Collision
    }
  }
  return false;
}
```

### Log and Turtle Riding

```
function updateFrogOnRiver() {
  // Check if frog is in river area
  if (frog.gridY >= 7 && frog.gridY <= 12) {
    const frogRow = frog.gridY;
    
    // Find what's in this row at frog's position
    let onSomething = false;
    
    for (const obj of riverObjects) {
      if (obj.row === frogRow) {
        // Check if frog is on this object
        if (frog.x > obj.x && frog.x < obj.x + obj.width) {
          // Is it safe?
          if (obj.type === 'log' || (obj.type === 'turtle' && obj.surfaced)) {
            // Ride it!
            frog.x += obj.vx;
            onSomething = true;
          } else if (obj.type === 'turtle' && !obj.surfaced) {
            // Diving turtle - death!
            frogDeath('drowned');
            return;
          }
        }
      }
    }
    
    // If not on anything, frog drowns
    if (!onSomething) {
      frogDeath('drowned');
    }
    
    // Check if carried off screen
    if (frog.x < -CELL_SIZE/2 || frog.x > canvas.width + CELL_SIZE/2) {
      frogDeath('drowned');
    }
  }
}
```

### Turtle Diving Cycle

```
function updateTurtles() {
  for (const turtle of turtles) {
    // Move turtle
    turtle.x += turtle.vx;
    
    // Wrap around
    if (turtle.vx > 0 && turtle.x > canvas.width) {
      turtle.x = -turtle.width;
    } else if (turtle.vx < 0 && turtle.x + turtle.width < 0) {
      turtle.x = canvas.width;
    }
    
    // Diving cycle
    turtle.cycleTimer++;
    
    const cycleLength = 300; // frames
    const diveStart = 200;   // Start diving at frame 200
    const diveEnd = 280;     // Resurface at frame 280
    
    if (turtle.cycleTimer >= cycleLength) {
      turtle.cycleTimer = 0;
    }
    
    if (turtle.cycleTimer >= diveStart && turtle.cycleTimer < diveEnd) {
      turtle.surfaced = false;
    } else {
      turtle.surfaced = true;
    }
  }
}
```

### Home Bay Detection

```
const homeBays = [
  { x: 40, occupied: false },
  { x: 120, occupied: false },
  { x: 200, occupied: false },
  { x: 280, occupied: false },
  { x: 360, occupied: false }
];

function checkHomeBay() {
  if (frog.gridY === 0) { // Top row
    for (const bay of homeBays) {
      // Check if frog is at this bay
      if (Math.abs(frog.x - bay.x) < CELL_SIZE/2) {
        if (!bay.occupied) {
          // Success!
          bay.occupied = true;
          score += 50 + Math.floor(timeRemaining) * 10;
          respawnFrog();
          checkLevelComplete();
          return;
        } else {
          // Bay already occupied
          frogDeath('collision');
          return;
        }
      }
    }
    // Not in a bay - fell in water
    frogDeath('drowned');
  }
}

function checkLevelComplete() {
  if (homeBays.every(bay => bay.occupied)) {
    // Level complete!
    score += 1000;
    currentLevel++;
    resetLevel();
  }
}
```

---

## Row-by-Row Layout (Detailed)

From bottom (y = 0) to top (y = 650):

| Row | Y Position | Type | Contents |
|-----|------------|------|----------|
| 0 | 0-40 | Safe zone | Grass, starting area |
| 1 | 40-80 | Road | Cars, moving left, speed 1-2 |
| 2 | 80-120 | Road | Trucks, moving right, speed 0.5-1 |
| 3 | 120-160 | Road | Cars, moving left, speed 2-3 |
| 4 | 160-200 | Road | Long trucks, moving right, speed 0.5 |
| 5 | 200-240 | Road | Cars, moving left, speed 1.5-2.5 |
| 6 | 240-280 | Safe zone | Median, grass |
| 7 | 280-320 | River | Medium logs, left, speed 1 |
| 8 | 320-360 | River | Turtles (3), right, speed 0.5-1 |
| 9 | 360-400 | River | Long logs, left, speed 0.5 |
| 10 | 400-440 | River | Short logs, left, speed 2 |
| 11 | 440-480 | River | Turtles (3), right, speed 1 |
| 12 | 480-520 | River | Medium logs, right, speed 1.5 |
| 13 | 520-560 | River | Long logs, left, speed 0.5 |
| 14 | 560-600 | Safe zone | River bank (partial) |
| 15 | 600-640 | Home | 5 home bays with gaps |

---

## Common Bugs to Avoid

1. **Frog slides instead of hops:** Movement must be discrete, one cell per keypress. No smooth sliding.

2. **Frog drowns while on log:** Collision detection must be accurate. Frog should be safe when on any part of a log.

3. **Turtle dive not visible:** Provide clear visual warning before turtles dive (animation, bubbles).

4. **Frog carried off screen instantly:** Check screen boundaries and trigger death BEFORE frog completely exits.

5. **Multiple keypresses registered:** Ensure one keypress = one hop. Implement key debouncing.

6. **Home bay detection too strict:** Allow some tolerance for entering bays (within a cell width).

7. **Timer resets incorrectly on death:** Time should reset to full when new frog spawns.

8. **Objects overlap in wrong order:** Draw vehicles over road, logs over river, frog on top of everything.

---

## Minimum Viable Product Checklist

A complete Frogger implementation must have:

- [ ] Canvas rendering with proper dimensions
- [ ] Grid-based frog movement (up, down, left, right)
- [ ] 5 road lanes with moving vehicles
- [ ] Vehicle collision detection (frog dies on contact)
- [ ] 6 river lanes with moving logs
- [ ] Frog rides on logs (moves with log)
- [ ] Water death (frog not on log or turtle)
- [ ] Turtles that dive periodically
- [ ] Diving turtle death
- [ ] 5 home bays at top
- [ ] Home bay success and completion detection
- [ ] Score system
- [ ] Lives system (3 lives)
- [ ] Timer per frog
- [ ] Level progression (all 5 bays = next level)
- [ ] Game states: Title → Playing → Paused → Game Over
- [ ] Pause and Restart functionality
- [ ] No external dependencies (all code in one HTML file)

---

## Quick Reference

| Element | Value |
|---------|-------|
| Canvas | 560×650 px |
| Cell size | 40×40 px |
| Frog | 40×40 px, green |
| Lives | 3 |
| Time limit | 60 seconds per frog |
| Road lanes | 5 |
| River lanes | 6 |
| Home bays | 5 |
| Cars | 40×40 px |
| Trucks | 80-120×40 px |
| Logs | 40-120×40 px (various) |
| Turtles | 3 × 40 = 120 px wide groups |
| Forward hop points | 10 |
| Home bay points | 50 |
| Level bonus | 1000 |

---

End of specification.
