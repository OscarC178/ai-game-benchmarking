# Donkey Kong — Complete Game Specification

## Overview

Donkey Kong is a single-player platform game. You control Mario (originally Jumpman), a carpenter trying to rescue his girlfriend Pauline from the giant ape Donkey Kong. Navigate platforms, climb ladders, and avoid obstacles like rolling barrels and fireballs. Reach Pauline at the top to complete the level. Use hammers to temporarily destroy barrels. You have limited lives. The game cycles through multiple unique stages, each with different hazards. The game ends when all lives are lost.

---

## Game Elements

### The Arena

- **Canvas size:** 448×512 pixels (or scaled proportionally)
- **Cell/tile size:** 16×16 pixels (platforms align to grid)
- **Layout:** Multiple platforms arranged diagonally or horizontally, connected by ladders
- **Background:** Black (#000000)
- **Platform colors:** Blue or gray (#4444FF or #888888)
- **Ladder color:** Blue or cyan

### Mario (Player)

- **Size:** 14×20 pixels (approximately 1 tile wide, slightly taller)
- **Color:** Red cap and shirt (#FF0000), blue overalls (#0000FF), skin tone
- **Position:** Starts at bottom-left of the screen
- **Movement:**
  - Horizontal: 1.5-2 pixels per frame (walking)
  - Vertical on ladders: 1-1.5 pixels per frame (climbing)
- **Jump:**
  - Height: Approximately 40-50 pixels (3 tiles)
  - Horizontal distance: Can jump while moving
  - Duration: 15-20 frames
  - Can jump over barrels and gaps
- **Lives:** Starts with 3 lives
- **Death animation:** Brief flip or spin animation

### Donkey Kong

- **Size:** 48×48 pixels (large, 3 tiles wide)
- **Color:** Brown fur (#8B4513), tan face/chest
- **Position:** Top of the screen, near Pauline
- **Behavior:** 
  - Grabs barrels and throws them down
  - Animates throwing motion
  - Stomps and taunts periodically
- **Animation:** Arm raise → throw → arm down, repeat

### Pauline (Lady)

- **Size:** 16×24 pixels
- **Color:** Pink/red dress, dark hair
- **Position:** Top-right of the screen, on a platform
- **Animation:** Calls for help, moves slightly
- **Goal:** Reach her position to complete the level

### Barrels

- **Size:** 16×16 pixels (one tile)
- **Color:** Orange/brown (#FF6600 or #8B4513)
- **Behavior:**
  - Donkey Kong throws barrels periodically
  - Barrels roll down platforms
  - Follow platform angles (diagonal descent)
  - Bounce off walls and change direction
  - Can fall through gaps in platforms
  - Roll over ladders randomly or predictably
- **Speed:** 2-3 pixels per frame
- **Collision:** Touching Mario = death (unless jumping over or using hammer)

### Fireballs

- **Size:** 12×12 pixels
- **Color:** Red/orange with yellow highlights
- **Behavior:**
  - Spawn from oil drum at bottom
  - Climb ladders
  - Move horizontally on platforms
  - Chase Mario (basic AI)
- **Speed:** Slower than barrels, 1-2 pixels per frame
- **Collision:** Touching Mario = death

### Hammers

- **Size:** 24×16 pixels (handle + head)
- **Color:** Brown handle, gray head
- **Position:** Fixed locations on platforms (2-3 per level)
- **Behavior:**
  - Mario picks up by touching
  - Duration: 5-7 seconds
  - Effect: Mario can destroy barrels and fireballs by touching them
  - Cannot climb ladders while holding hammer
- **Animation:** Mario swings hammer continuously

### Oil Drum

- **Size:** 24×24 pixels
- **Color:** Blue or red drum with flame on top
- **Position:** Bottom-left of screen, near Mario's start position
- **Behavior:**
  - If a barrel touches it, spawns a fireball
  - Constantly emits flame (visual only)

### Springs

- **Size:** 16×16 pixels
- **Color:** Gray/silver
- **Behavior:** (Elevator stage)
  - Bounce up and down
  - Mario must avoid or time jumps
- **Appears on:** Stage 3 (Springs stage)

### Conveyor Belts

- **Appearance:** Horizontal platforms with moving texture
- **Behavior:** (Pie factory stage)
  - Move left or right
  - Carry Mario, barrels, and pies
  - Speed: 1-2 pixels per frame

---

## Stage Layouts

Donkey Kong features 4 distinct stages that cycle:

### Stage 1: Girders (25m)

Classic barrel-throwing stage.

**Layout:**
- 6-7 horizontal platforms arranged diagonally
- Platforms connected by ladders
- Donkey Kong at top-left
- Pauline at top-right
- Oil drum at bottom-left

**Hazards:**
- Rolling barrels (primary)
- Fireballs (spawned from oil drum)

**Barrel behavior:**
- Donkey Kong throws every 2-3 seconds
- Barrels roll down diagonal platforms
- 25% chance to roll down a ladder (or deterministic pattern)

**Goal:** Reach Pauline at top-right.

### Stage 2: Conveyor Belt Factory (50m)

**Layout:**
- Horizontal platforms with conveyor belts
- Ladders connecting platforms
- Pie-shaped hazards on conveyors
- Donkey Kong at top

**Hazards:**
- Pies/cement pans moving on conveyor belts
- Fireballs
- Conveyor belts affect Mario's movement

**Goal:** Reach Pauline.

### Stage 3: Elevators (75m)

**Layout:**
- Platforms connected by moving elevators
- Static ladders also present
- Springs bouncing up and down

**Hazards:**
- Springs bouncing vertically
- Falling off elevators
- Fireballs

**Elevator mechanics:**
- Two elevators moving in opposite directions
- Mario must time jumps to board
- Missing = fall to lower platform or death

**Goal:** Reach Pauline.

### Stage 4: Rivet Stage (100m)

Final stage of each cycle.

**Layout:**
- Horizontal platform at top with Donkey Kong and Pauline
- Platform supported by 8 rivets
- Ladders connect multiple levels

**Goal:** Remove all 8 rivets by touching them.

**Mechanic:**
- Touch each rivet to remove it
- Rivets flash and disappear
- When all rivets removed, Donkey Kong falls
- Pauline rescued
- Bonus points awarded

**After Stage 4:**
- Cycle repeats at higher difficulty
- Stage 1 starts again

---

## Movement and Physics

### Walking

Mario walks horizontally on platforms.

- **Speed:** 1.5-2 pixels per frame
- **Constraint:** Cannot walk through walls or off platform edges
- **Animation:** Walking cycle (2-3 frames)

### Jumping

Mario can jump to avoid obstacles or reach platforms.

- **Jump height:** 40-50 pixels (approximately 3 tiles)
- **Jump duration:** 15-20 frames
- **Horizontal movement during jump:** Can move left/right while airborne
- **Landing:** Must land on a platform or fall
- **Collision during jump:** Immune to barrels/fireballs while jumping OVER them (feet must clear hazard)

**Jump mechanics:**
```
// Jump is a fixed arc, not physics-based
jumpFrame = 0;

function updateJump() {
  if (jumping) {
    jumpFrame++;
    
    // Parabolic arc
    const jumpProgress = jumpFrame / totalJumpFrames;
    const jumpHeight = Math.sin(jumpProgress * Math.PI) * maxJumpHeight;
    
    mario.y = jumpStartY - jumpHeight;
    mario.x += horizontalSpeed * direction;
    
    if (jumpFrame >= totalJumpFrames) {
      jumping = false;
      jumpFrame = 0;
    }
  }
}
```

**Can jump over:**
- Barrels
- Fireballs
- Small gaps (not large gaps)

**Cannot jump over:**
- Springs (too large, must avoid)
- Falling off screen

### Climbing Ladders

Mario can climb up and down ladders when positioned at the ladder's base or top.

- **Speed:** 1-1.5 pixels per frame
- **Constraint:** Must be centered on ladder (within 4-6 pixels)
- **Cannot jump while on ladder**
- **Cannot use hammer while climbing**

**Ladder interaction:**
```
function canClimb(direction) {
  // Find ladder at Mario's position
  const ladder = findLadderAt(mario.x, mario.y);
  
  if (!ladder) return false;
  
  if (direction === 'up' && mario.y > ladder.topY) return true;
  if (direction === 'down' && mario.y < ladder.bottomY) return true;
  
  return false;
}
```

### Falling

If Mario walks off a platform edge or misses a jump:

- Falls straight down
- Falls until landing on a platform
- If falls below screen: death

**Fall damage:** None (classic Donkey Kong doesn't have fall damage, but falling off screen = death)

### Conveyor Belt Movement

On conveyor belt platforms, Mario is pushed:

```
mario.x += conveyorSpeed * conveyorDirection;
```

Mario can walk against the conveyor (slower net speed) or with it (faster).

---

## Barrel Behavior Details

### Throwing Pattern

Donkey Kong throws barrels at regular intervals:

- **Interval:** 2-3 seconds between throws
- **Throw animation:** 0.5 seconds
- **Initial velocity:** Barrel thrown slightly upward, then rolls

### Rolling Physics

Barrels roll according to platform angles:

```
// On diagonal platform (going down-left)
barrel.x += barrelSpeed * Math.cos(platformAngle);
barrel.y += barrelSpeed * Math.sin(platformAngle);

// On horizontal platform
barrel.x += barrelSpeed * direction;
```

### Ladder Interaction

When a barrel reaches a ladder:

- **Random chance:** 25% to roll down the ladder
- **Or:** Continue rolling horizontally

**Implementation:**
```
function barrelAtLadder(barrel, ladder) {
  // Check if barrel is at ladder position
  if (Math.abs(barrel.x - ladder.x) < 8) {
    // Random chance to go down ladder
    if (Math.random() < 0.25) {
      barrel.state = 'rolling_down_ladder';
      barrel.ladder = ladder;
    }
  }
}
```

### Bouncing

When a barrel hits a wall or platform edge:

- Reverses horizontal direction
- Continues rolling

### Falling Through Gaps

Some platforms have gaps. Barrels can fall through:

```
if (platformHasGap(barrel.x, barrel.y)) {
  barrel.state = 'falling';
  barrel.vy += gravity;
}
```

---

## Fireball Behavior

### Spawning

- Fireballs spawn from the oil drum when a barrel touches it
- Or at fixed intervals
- Maximum 1-2 fireballs on screen at once

### Movement

Fireballs move horizontally and climb ladders:

```
function updateFireball(fireball) {
  // Move horizontally
  fireball.x += fireball.speed * fireball.direction;
  
  // At ladder, randomly climb
  const ladder = findLadderAt(fireball.x, fireball.y);
  if (ladder && Math.random() < 0.1) {
    fireball.state = 'climbing';
    fireball.ladder = ladder;
  }
  
  // Reverse at walls
  if (hitWall(fireball)) {
    fireball.direction *= -1;
  }
}
```

---

## Hammer Mechanics

### Pickup

When Mario touches a hammer:

1. Hammer disappears from platform
2. Mario enters "hammer mode"
3. Timer starts (5-7 seconds)

### Hammer Mode

- Mario cannot climb ladders
- Mario cannot jump
- Mario walks and swings hammer continuously
- Collision with barrels or fireballs destroys them (points awarded)

### Destroying Enemies

```
function hammerCollision() {
  if (mario.hasHammer) {
    for (const enemy of enemies) {
      if (collision(mario, enemy)) {
        destroyEnemy(enemy);
        score += 500; // Points for hammer kill
      }
    }
  }
}
```

### Duration Display

- Visual timer bar or
- Hammer flashes near end of duration

---

## Scoring

### Points

| Action | Points |
|--------|--------|
| Jump over barrel | 100 |
| Destroy barrel with hammer | 500 |
| Destroy fireball with hammer | 500 |
| Remove rivet | 100 |
| Pick up item (bag, etc.) | varies |
| Complete stage | Bonus based on time |

### Time Bonus

Each stage has a time limit. Remaining time converts to bonus points:

- **Time limit:** 60-100 seconds per stage
- **Bonus:** Remaining seconds × bonus multiplier
- **Displayed:** Timer bar at top or bottom

**Implementation:**
```
function stageComplete() {
  const timeBonus = timeRemaining * 100;
  score += timeBonus;
  // Additional bonus for rivets, items, etc.
}
```

### Score Display

- **Position:** Top-right corner
- **Format:** "[number]"
- **Font:** Monospace or digital, 16-20px
- **Color:** White

**High score:**
- Position: Top-center
- Stored in localStorage

---

## Lives System

- **Initial lives:** 3
- **Display:** Mario icons at bottom-left
- **Death conditions:**
  - Collision with barrel (not jumping over)
  - Collision with fireball
  - Collision with spring
  - Falling off screen
  - Time runs out (some versions)

**On death:**
1. Death animation
2. Lose one life
3. Restart current stage from beginning
4. If no lives: game over

**Extra life:**
- Awarded at 7,000 and 20,000 points (configurable)

---

## Controls

| Key | Action |
|-----|--------|
| ← or A | Move left |
| → or D | Move right |
| ↑ or W | Climb ladder up |
| ↓ or S | Climb ladder down |
| Space | Jump |
| P or Escape | Pause game |
| R | Restart game |

**Control notes:**
- Both arrow keys and WASD work
- Jump can be pressed while moving
- Direction influences jump trajectory

---

## Game States

### 1. Title Screen / Attract Mode

**Display:**
- "DONKEY KONG" title
- Demo gameplay animation
- "Press SPACE to start"
- High score

**Behavior:**
- Pressing Space starts game

### 2. Stage Start

**Display:**
- Stage name/number ("25m", "50m", etc.)
- Brief pause
- Donkey Kong animation
- Mario at starting position

**Behavior:**
- After 2-3 seconds, gameplay begins

### 3. Playing

**Display:**
- Platforms, ladders
- Mario, Donkey Kong, Pauline
- Barrels, fireballs, hazards
- Score, lives, timer

**Behavior:**
- Normal gameplay
- Pressing P pauses

### 4. Paused

**Display:**
- Game frozen
- "PAUSED" centered
- "Press P to resume"

**Behavior:**
- Pressing P resumes
- Pressing R restarts

### 5. Mario Death

**Display:**
- Death animation (flip/spin)
- Hazards pause

**Behavior:**
- After animation, respawn or game over

### 6. Stage Complete

**Display:**
- Mario reaches Pauline
- Donkey Kong escapes (or falls on rivet stage)
- Bonus points displayed

**Behavior:**
- After 2-3 seconds, next stage begins

### 7. Game Over

**Display:**
- "GAME OVER" centered
- Final score
- "Press R to play again"

**Behavior:**
- Pressing R restarts
- Pressing Escape returns to title

---

## Stage-by-Stage Details

### Stage 1: Girders (25m)

**Platforms:**
```
Row 1 (bottom):    y = 450, x = 50 to 350 (left to right, slight diagonal)
Row 2:             y = 370, x = 100 to 400 (right to left diagonal)
Row 3:             y = 290, x = 50 to 350 (left to right diagonal)
Row 4:             y = 210, x = 100 to 400 (right to left diagonal)
Row 5 (top):       y = 130, x = 50 to 200 (horizontal, Donkey Kong area)
                    y = 100, x = 250 to 400 (horizontal, Pauline area)
```

**Ladders:** 
- 3-4 ladders connecting each platform level
- Ladders aligned with platform edges

**Hazards:**
- Barrels rolling down (primary)
- Oil drum spawns fireballs

**Hammer locations:** 2 hammers on platforms

**Strategy:** Jump over barrels, climb ladders, reach Pauline.

### Stage 2: Conveyor Factory (50m)

**Layout:**
- 5 horizontal platforms
- Conveyor belts moving left and right
- Pies/cement pans as hazards

**Hazards:**
- Pies moving on conveyors
- Fireballs
- Conveyor belts push Mario

**Conveyor directions:**
- Alternating left/right per level

### Stage 3: Elevators (75m)

**Layout:**
- Platforms connected by moving elevators
- Static ladders on sides
- Springs bouncing vertically

**Elevator mechanics:**
- Two elevators: one going up, one going down
- Elevators move at 1-2 pixels per frame
- Mario must time jumps to board

**Springs:**
- Bounce from bottom to top
- Return down
- Spawn from Donkey Kong's area

### Stage 4: Rivets (100m)

**Layout:**
- Top platform with 8 rivets (4 on left side, 4 on right side)
- Donkey Kong in center
- Pauline on right side
- Ladders connect lower rescue platforms

**Mechanic:**
- Touch each rivet to remove it
- Platform segment falls when both rivets removed
- Donkey Kong falls when all rivets gone

**Scoring:**
- Each rivet: 100 points
- Donkey Kong falls: 1000+ points

---

## Visual Design

### Mario Appearance

- Red cap with M logo
- Blue overalls
- Skin-tone face and hands
- Brown shoes
- 2-3 frame walking animation
- Jump pose (arms up)
- Hammer swing animation

### Donkey Kong Appearance

- Large brown gorilla
- Tan chest and face
- Black eyes
- Throwing animation
- Taunt animation

### Platform Appearance

- Gray or blue metal girders
- Visible rivets/connectors
- 16px height per platform

### Ladder Appearance

- Two vertical rails
- Horizontal rungs
- Blue or cyan color
- 8-12 pixels wide

### Barrel Appearance

- Orange/brown wooden barrel
- Metal bands (darker stripes)
- Rolling animation (spinning)

---

## Technical Implementation Notes

### Platform Collision Detection

```
function onPlatform(mario) {
  const feetY = mario.y + mario.height;
  
  for (const platform of platforms) {
    if (mario.x >= platform.x && 
        mario.x <= platform.x + platform.width) {
      if (Math.abs(feetY - platform.y) < 4) {
        return platform;
      }
    }
  }
  return null;
}

function applyGravity() {
  if (!jumping && !climbing) {
    const platform = onPlatform(mario);
    if (!platform) {
      mario.y += gravity; // Fall
    } else {
      mario.y = platform.y - mario.height; // Snap to platform
    }
  }
}
```

### Ladder Detection

```
function findLadderAt(x, y) {
  for (const ladder of ladders) {
    if (Math.abs(x - ladder.x) < 8 &&
        y >= ladder.topY - 10 &&
        y <= ladder.bottomY + 10) {
      return ladder;
    }
  }
  return null;
}
```

### Barrel Rolling on Diagonal Platforms

```
function updateBarrel(barrel) {
  const platform = getPlatformAt(barrel.x, barrel.y);
  
  if (platform && platform.angle !== 0) {
    // Diagonal platform - roll downward
    barrel.x += Math.cos(platform.angle) * barrel.speed;
    barrel.y += Math.sin(platform.angle) * barrel.speed;
  } else {
    // Horizontal platform
    barrel.x += barrel.direction * barrel.speed;
  }
  
  // Check for ladder
  const ladder = findLadderAt(barrel.x, barrel.y);
  if (ladder && Math.random() < 0.25) {
    barrel.state = 'descending_ladder';
    barrel.ladder = ladder;
  }
}
```

### Jump Arc

```
function jump(mario) {
  if (!mario.jumping && !mario.climbing) {
    mario.jumping = true;
    mario.jumpStartY = mario.y;
    mario.jumpFrame = 0;
    mario.jumpDirection = mario.facing; // Left or right
  }
}

function updateJump(mario) {
  if (mario.jumping) {
    mario.jumpFrame++;
    
    const progress = mario.jumpFrame / mario.jumpDuration;
    const height = Math.sin(progress * Math.PI) * mario.jumpHeight;
    
    mario.y = mario.jumpStartY - height;
    mario.x += mario.jumpDirection * mario.jumpSpeed;
    
    if (mario.jumpFrame >= mario.jumpDuration) {
      mario.jumping = false;
    }
  }
}
```

### Barrel Collision with Jumping Mario

```
function checkBarrelCollision(mario, barrel) {
  // Collision box
  if (rectsOverlap(mario, barrel)) {
    // Check if Mario is jumping OVER the barrel
    if (mario.jumping) {
      // Check if Mario's feet are above the barrel
      if (mario.y + mario.height < barrel.y + 8) {
        // Successfully jumping over
        score += 100;
        return 'jumped_over';
      }
    }
    return 'collision';
  }
  return 'no_collision';
}
```

### Rivet Removal

```
function checkRivet(mario, rivet) {
  if (!rivet.removed && rectsOverlap(mario, rivet)) {
    rivet.removed = true;
    score += 100;
    rivetsRemoved++;
    
    // Check if platform segment should fall
    checkPlatformIntegrity(rivet.platformSegment);
    
    if (rivetsRemoved === 8) {
      donkeyKongFalls();
    }
  }
}
```

---

## Difficulty Progression

After completing all 4 stages, the game loops with increased difficulty:

| Cycle | Barrel Speed | Barrel Frequency | Fireball Speed |
|-------|--------------|------------------|----------------|
| 1 | Normal | Normal | Normal |
| 2 | +15% | +15% | +15% |
| 3 | +25% | +25% | +25% |
| 4+ | +35% | +35% | +35% |

**Additional changes:**
- Fewer hammers in later cycles
- Shorter hammer duration
- Faster barrel throwing

---

## Common Bugs to Avoid

1. **Mario falls through platforms:** Ensure collision detection checks platform surface properly. Snap Mario to platform surface when landing.

2. **Cannot grab ladder:** Allow tolerance for ladder alignment (within 4-6 pixels). Players shouldn't need pixel-perfect positioning.

3. **Jump doesn't clear barrels:** Check collision carefully. Mario should be safe when feet are above the barrel.

4. **Barrels get stuck:** Ensure barrels continue rolling even at edges. Handle platform transitions smoothly.

5. **Hammer duration unclear:** Provide visual feedback (flashing, timer bar).

6. **Elevator timing impossible:** Ensure elevators are slow enough for players to board. Add visual timing cues.

7. **Rivets don't register:** Make rivet hitboxes slightly larger than visual size for better player experience.

8. **Diagonal platform physics wrong:** Calculate barrel rolling based on actual platform angle, not just horizontal movement.

9. **Conveyor belts affect jumping:** Mario should maintain horizontal position during jump, not be pushed by conveyors (unless landing on them).

10. **Ladder climbing interrupts jump:** Disable jump while on ladder, and prevent ladder interaction during jump.

---

## Minimum Viable Product Checklist

A complete Donkey Kong implementation must have:

- [ ] Canvas rendering with platform layout
- [ ] Mario with walking, jumping, and climbing animations
- [ ] Horizontal movement and ladder climbing
- [ ] Jump mechanic (parabolic arc)
- [ ] Platform collision detection
- [ ] Ladder detection and climbing
- [ ] Donkey Kong at top of screen
- [ ] Barrel throwing by Donkey Kong
- [ ] Barrels roll down platforms
- [ ] Barrels fall down ladders (random chance)
- [ ] Barrel collision = death (unless jumping over)
- [ ] Jump over barrels for points
- [ ] Hammers that can be picked up
- [ ] Hammer destroys barrels and fireballs
- [ ] Hammer duration with visual indicator
- [ ] Fireballs that spawn and move/climb
- [ ] Pauline at goal position
- [ ] Reach Pauline to complete stage
- [ ] Score system (jumping over barrels, hammer kills, stage completion)
- [ ] Lives system (3 lives)
- [ ] At least Stage 1 (Girders) fully playable
- [ ] Game states: Title → Playing → Paused → Game Over
- [ ] Pause and Restart functionality
- [ ] No external dependencies (all code in one HTML file)

---

## Quick Reference

| Element | Value |
|---------|-------|
| Canvas | 448×512 px |
| Tile size | 16×16 px |
| Mario size | 14×20 px |
| Mario walk speed | 1.5-2 px/frame |
| Jump height | 40-50 px |
| Jump duration | 15-20 frames |
| Donkey Kong size | 48×48 px |
| Barrel size | 16×16 px |
| Barrel speed | 2-3 px/frame |
| Fireball size | 12×12 px |
| Lives | 3 |
| Hammer duration | 5-7 seconds |
| Jump over barrel | 100 points |
| Hammer kill | 500 points |
| Rivet | 100 points |

---

End of specification.
