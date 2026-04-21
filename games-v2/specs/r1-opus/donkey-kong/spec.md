# Game Spec: Donkey Kong

## 1. Overview

Donkey Kong (Nintendo, 1981 — the game that introduced Mario and Shigeru Miyamoto to the world). A giant ape has kidnapped a woman and carried her to the top of a construction site. You play as a small carpenter (Jumpman/Mario) who must climb from the bottom to the top of a series of sloped platforms while the ape hurls barrels down at you. Jump over the barrels, climb ladders, and reach the top to rescue the damsel.

This is a **platformer** — the first important one. Mario walks left and right, climbs ladders, and jumps. Gravity pulls him down. He has momentum but not much — this isn't a physics sandbox, it's a precision gauntlet. The platforms are sloped (tilted), so barrels roll downhill naturally. The level is a single static screen (no scrolling), viewed from the side.

The game has a distinctive rhythm: barrels come in waves, rolling down the sloped girders, sometimes taking ladders down to lower levels, sometimes rolling straight off edges. The player must read the barrel patterns, time their jumps, and race to the top. It's a game about reading chaos and finding safe paths through it.

## 2. Canvas & Layout

- **Canvas:** 672×768px
- **Background:** #000000
- **HUD top bar:** y = 0–36. Score, high score, level.
- **Play area:** y = 36–732. The construction-site level.
- **HUD bottom bar:** y = 732–768. Lives display.
- **Frame rate:** 60 FPS via `requestAnimationFrame` with delta-time.
- **Coordinate system:** Origin top-left. x increases right, y increases down.
- **No scrolling.** The entire level is visible at once, like looking at a cross-section of a building.

## 3. Level Layout — The Girder Map

Donkey Kong's iconic first stage (also known as "25m" or "Ramps") consists of six horizontal girders connected by ladders, with the platforms sloped at slight angles. Donkey Kong sits at the top-left. Pauline (the damsel) stands at the very top on a short platform above DK. Mario starts at the bottom.

### Girder Definitions

Each girder is a platform the player can walk on. They are sloped — the left end is at a different y than the right end. Barrels roll downhill along them.

Define girders as line segments with start and end points. The player's feet y-position follows the girder's slope when standing on it.

```
Girder 1 (bottom):    (40, 620) → (632, 592)    slope: rises left-to-right (left is lower... 
```

Actually, let me describe the classic layout properly. In the original, the girders alternate slope direction so barrels zigzag down:

```
Platform 6 (top):     Small platform at top — Pauline's perch
                      Girder: (200, 100) → (472, 100)  [flat, short]
                      Pauline stands at center (~336, 80)

Platform 5 (DK's):   Donkey Kong's platform  
                      Girder: (56, 172) → (512, 186)   [slight downward slope to right]
                      DK sits at left end (~100, 140)

Platform 4:           Girder: (104, 266) → (616, 240)  [slopes down-left]
                      (Right side is higher)

Platform 3:           Girder: (56, 358) → (568, 332)   [slopes down-left]
                      (Left side is lower)

Platform 2:           Girder: (104, 452) → (616, 426)  [slopes down-left... ]
```

Let me reconsider and describe the canonical layout more carefully. The original Donkey Kong 25m has this structure when viewed on screen:

- **Top:** A short flat platform where Pauline stands, centered, with "HELP!" text.
- **Below that:** DK's platform — a girder that slopes gently. DK is at the left side.
- **Six main girders** below that, each spanning most of the screen width, alternating which end is higher. The key pattern: the topmost walkable girder slopes so its left end is lower (barrels roll left), the next one slopes so its right end is lower (barrels roll right), alternating all the way down. This creates the zigzag barrel path.
- **Bottom:** The lowest girder where Mario starts, relatively flat.

Here is a precise layout:

```
                    [PAULINE]
              ═══════════════════            y ≈ 98
        [DK]                                 
    ══════════════════════════════════       y ≈ 174 left, 188 right  (slopes right)
              ║         ║       ║
         ══════════════════════════════     y ≈ 268 right, 282 left  (slopes left)
              ║    ║         ║
    ══════════════════════════════════      y ≈ 362 left, 376 right  (slopes right)
              ║         ║       ║
         ══════════════════════════════    y ≈ 456 right, 470 left   (slopes left)
              ║    ║         ║
    ══════════════════════════════════     y ≈ 550 left, 564 right   (slopes right)
         ║    ║         ║
         ══════════════════════════════   y ≈ 630 right, 640 left    (slopes left, gentle)
                                          Mario starts here
```

### Precise Girder Data

Each girder is defined by: left-x, right-x, left-y, right-y. The player walks along the top surface. The girder itself is 8px tall (rendered as a stack of red-orange segments).

| Girder | Left x | Right x | Left y | Right y | Slope direction | Notes |
|--------|--------|---------|--------|---------|-----------------|-------|
| G1 (bottom) | 56 | 616 | 640 | 628 | Down-right to up-right | Mario starts here, right side |
| G2 | 56 | 616 | 544 | 556 | Down-left to up-left | Barrels roll right → left |
| G3 | 56 | 616 | 460 | 448 | Down-right to up-right | Barrels roll left → right |
| G4 | 56 | 616 | 364 | 376 | Down-left to up-left | Barrels roll right → left |
| G5 | 56 | 616 | 280 | 268 | Down-right to up-right | Barrels roll left → right |
| G6 (DK's) | 56 | 456 | 188 | 180 | Slight down-right | DK stands here |
| G7 (Pauline) | 220 | 452 | 98 | 98 | Flat | Pauline's platform |

**Girder rendering:** Each girder is a series of small ~16×8px blocks (like construction I-beams), colored in an alternating pattern of #CC4400 (red-orange) and #FF6600 (brighter orange). Draw them as a filled polygon from (leftX, leftY) to (rightX, rightY) to (rightX, rightY+8) to (leftX, leftY+8). Then overprint the block segments.

**Walking on a girder:** When Mario's feet are on a girder, his y-position follows the linear interpolation between leftY and rightY based on his x-position:
```
t = (mario.x - girder.leftX) / (girder.rightX - girder.leftX)
girderY = girder.leftY + t × (girder.rightY - girder.leftY)
mario.feetY = girderY
```

### Broken Girder Detail

The top-left section of girder G6 (DK's platform) has a piece missing or broken — this is where DK sits, and the gap prevents the player from simply walking up to DK's level from the left. The player must reach the top via the ladder on the right side of G6 up to G7.

## 4. Ladders

Ladders connect girders vertically. Mario can climb up or down ladders. Some ladders are complete (always usable), some are broken (only the top or bottom half exists — climbable from one direction only).

**Ladder rendering:** Two vertical parallel lines 12px apart, with horizontal rungs every 10px. Color: #66CCFF (cyan-blue). Broken ladders render only their existing half.

**Ladder data:** Each ladder specifies its x-position (center), the girder it connects from (bottom), the girder it connects to (top), and whether it's full or broken.

| Ladder | Center x | Bottom girder | Top girder | Type |
|--------|----------|--------------|------------|------|
| L1 | 120 | G1 | G2 | Full |
| L2 | 320 | G1 | G2 | Broken (top half only — climb from G2 down only) |
| L3 | 540 | G2 | G3 | Full |
| L4 | 200 | G2 | G3 | Broken (bottom half only — climb from G2 up) |
| L5 | 120 | G3 | G4 | Full |
| L6 | 420 | G3 | G4 | Full |
| L7 | 540 | G4 | G5 | Full |
| L8 | 280 | G4 | G5 | Broken (top half) |
| L9 | 120 | G5 | G6 | Full |
| L10 | 400 | G6 | G7 | Full (this is the final ladder to reach Pauline) |

**Broken ladder behavior:**
- A broken ladder with only the **top half** exists from the top girder downward to the midpoint. Mario can descend from the top girder onto this ladder (climbing down to the midpoint, then he drops or the ladder simply doesn't continue — he can't reach the bottom girder via this ladder). He also cannot climb up from the bottom girder.
- A broken ladder with only the **bottom half** exists from the bottom girder upward to the midpoint. Mario can climb from the bottom up to the midpoint, but the ladder doesn't continue to the top girder. He drops back if he reaches the top of the fragment.

Actually, in the original game, broken ladders are simpler — they are ladders that are only sometimes accessible (they retract and extend). Let me simplify:

**Revised: broken ladders** are ladders that alternate between present and absent on a timer (every 3–4 seconds they retract for 2 seconds, then extend again). When retracted, they are not rendered and not climbable. This creates timing challenges — the player must reach the ladder while it's extended.

Use 3 broken ladders among the full set. They toggle on a shared timer (all retract/extend simultaneously, or staggered for more challenge — stagger by 1.5 seconds).

## 5. Game Objects

### Mario (Player)

- **Size:** 24×32px (standing), 24×28px (jumping)
- **Shape:** A small humanoid figure. Draw as a filled shape: blue overalls body (#0000AA), red shirt/hat (#CC0000), skin-colored face (#FFAA77), hands and feet. OR, for simplicity: a rounded rectangle body in #0000AA (16×22px), a red rectangle for the hat (16×6px), small feet (two 6×4px rectangles), and a skin circle for the head (10×10px). Two animation frames for walking (legs alternating — swap feet positions).
- **Starting position:** Right side of G1 (bottom girder), approximately (560, 620).
- **Movement speed:** 100px/s horizontal.
- **Climbing speed:** 80px/s vertical.
- **Jump:** Mario can jump. Jump velocity: 280px/s upward (initial), affected by gravity (see section 6). Mario can jump while walking (in which case he travels in an arc) or from a standstill (straight up). Jump height: approximately 50px at peak.
- **Collision hitbox:** Rectangle, 18×28px, centered on Mario.

**Mario animation frames:**
- Standing: static pose, facing left or right
- Walking: 2 frames alternating at 8Hz (legs swap)
- Jumping: distinct pose — arms up, legs tucked
- Climbing: 2 frames alternating at 6Hz (arms swap on ladder)
- Death: spinning/tumbling (see section 10)

### Donkey Kong

- **Size:** 64×64px
- **Position:** Top-left of G6, approximately (80, 124). He sits on/above the girder.
- **Shape:** A large brown ape. Draw as: a large #8B4513 (brown) rounded body, lighter #CD853F chest, two arms at the sides (arced shapes), two short legs. A darkened face oval with #FFD700 (gold/yellow) eyes/mouth area. It doesn't need to be beautiful — it needs to be recognizably a big ape.
- **Animation:** DK has three states:
  1. **Idle:** Beats chest — two frames alternating every 500ms (arms in, arms spread).
  2. **Throwing:** Grabs a barrel, lifts it overhead (200ms), throws it toward the first girder slope (300ms). Returns to idle.
  3. **Defeated (level clear):** Carried upward off-screen (end-of-level animation).
- **DK is NOT a collision target.** Mario cannot interact with DK directly. DK is a hazard generator (he throws barrels) and a set piece.

### Pauline (Damsel)

- **Size:** 20×32px
- **Position:** Center of G7 (top platform), approximately (336, 66).
- **Shape:** A simple feminine figure: #FF69B4 (pink) dress, #FFAA77 skin, #FF0000 or #8B0000 hair. Two alternating frames — she shifts weight or waves for help (toggle every 600ms).
- **"HELP!" text:** Rendered above Pauline in alternating #FF69B4 and #00FFFF, toggling every 500ms. Small text, 12px.
- **Pauline has no gameplay function beyond being the goal.** Reaching her platform (G7) completes the level.

### Barrels

The primary hazard. DK throws them, they roll down the girders.

- **Size:** 20×16px for rolling barrel, 16×20px when falling.
- **Shape:** A wooden barrel — small rounded rectangle, #CD853F (light brown) with #8B4513 (dark brown) horizontal bands (two stripes across the barrel). Two animation frames: the barrel rotates as it rolls (swap the band position or rotate the graphic by 90° per animation step, toggling at a rate proportional to speed).
- **Rolling speed:** 80–120px/s (varies per barrel — random within range). Difficulty multiplier applies per level.
- **Rolling behavior:** Barrels follow the slope of the current girder, rolling downhill. At the end of a girder, they either:
  1. **Fall to the next girder below** (80% chance) — the barrel drops off the edge and lands on the girder below, continuing to roll in the new direction (down the new slope).
  2. **Take a ladder down** (20% chance) — if there's a ladder at or near the girder's edge, the barrel rolls down the ladder to the next girder. Only possible at positions where ladders connect.
  
- **Falling barrels:** When a barrel falls off a girder edge, it drops straight down with gravity (400px/s²) until it lands on the next girder below. While falling, the barrel has slight horizontal drift (continuing its previous horizontal momentum, but much slower — roughly 30% of its rolling speed). On landing, it resumes rolling downhill on the new girder.

- **Barrel on ladders:** When a barrel decides to take a ladder, it moves downward at ~100px/s. At the bottom of the ladder, it deposits onto the lower girder and rolls in the appropriate direction. Barrels going down ladders are lethal — Mario can't share a ladder with a barrel.

- **Destruction:** Barrels that roll off the bottom of the screen (below G1) are removed. Barrels are also destroyed if Mario jumps over them (for scoring — see section 8) but they remain physics objects. They are destroyed by the hammer (see section 5 — Hammer).

- **Collision with Mario:** Barrel hitbox is 16×14px. Contact with Mario → death (unless Mario has the hammer, which destroys the barrel).

### Blue/Wild Barrels (Level 2+)

Starting at level 2, DK occasionally throws a "wild" barrel — colored #4488FF (blue). These barrels behave identically to normal barrels on slopes but have one difference: at ladder intersections, they ALWAYS take the ladder down (100% chance instead of 20%). They seek the lowest path more aggressively. At level 3+, one in three barrels is wild.

### Barrel Throw Rate

DK throws a new barrel every 2.5–4.0 seconds (random interval within range). At higher levels, the interval shrinks:

| Level | Throw interval | Barrel speed multiplier |
|-------|---------------|------------------------|
| 1 | 3.0–4.0s | 1.0× |
| 2 | 2.5–3.5s | 1.15× |
| 3 | 2.0–3.0s | 1.3× |
| 4+ | 1.5–2.5s | 1.45× (cap) |

### Hammer (Power-Up)

Two hammers are placed on the level — one on a mid-level girder, one higher up. They are the only offensive tool.

- **Position:** Hammer 1 at approximately (130, G3's y at that x). Hammer 2 at approximately (130, G5's y at that x). They float slightly above the girder surface (rendered 12px above the walking line).
- **Appearance:** A mallet shape — a small brown rectangle handle (4×16px, #8B4513) with a larger grey head (14×10px, #AAAAAA) on top.
- **Collection:** Mario walks through the hammer to pick it up.
- **Duration:** 10 seconds.
- **Effect:** Mario automatically and rapidly swings the hammer (the hammer oscillates over his head — two frames: hammer up and hammer down, alternating at 10Hz). Any barrel that contacts the hammer hitbox (a 28×20px zone above/in-front of Mario) is destroyed, awarding points.
- **Restrictions while hammering:**
  - Mario CANNOT climb ladders while holding the hammer. He can walk and jump only.
  - Mario's horizontal speed is slightly reduced to 80px/s.
  - Mario CAN still be killed by barrels that touch his body hitbox (not the hammer hitbox). The hammer protects the space above/in-front, but a barrel hitting his feet from behind can still kill him.
- **Visual:** When active, the hammer is prominently displayed swinging above Mario. When the hammer is about to expire (last 2 seconds), the hammer and Mario flash at 4Hz (warning).
- **Respawn:** Hammers do NOT respawn within a level. Once collected, they're gone until the level is replayed.

### Oil Drum / Fire

At the bottom-left of the level, there is an oil drum:

- **Position:** Left end of G1, approximately (56, 610).
- **Appearance:** A cylindrical drum shape, 20×28px, #333333 with a #FF4400 flame on top (animated flickering — two flame shapes, alternating at 8Hz).
- **Function:** Barrels that roll off the left end of G1 (into the drum) catch fire and become **fireballs** (see below). The barrel is consumed and a fireball spawns.

### Fireballs

- **Size:** 16×16px
- **Appearance:** A bouncing flame — an irregular blob of #FF4400 and #FF8800, with two animation frames (shape fluctuates). The fireball bounces gently as it moves (a small sine-wave y-offset, amplitude 4px, period 400ms).
- **Movement:** 60px/s. Fireballs patrol the girders somewhat randomly — they walk along a girder, and at ladders they have a 40% chance of climbing up/down (they can climb ladders!). They tend to move toward Mario's general direction (biased random walk — 60% chance of moving toward Mario's x-position, 40% random).
- **Count:** Maximum 4 fireballs alive at once. New barrels entering the drum won't create fireballs if the cap is reached.
- **Collision:** Fireball hitbox is 12×12px. Contact with Mario → death.
- **Hammer interaction:** Mario's hammer destroys fireballs on contact (same as barrels). Points awarded.
- **Persistence:** Fireballs persist until destroyed by the hammer or the level ends. They do NOT despawn on their own.

## 6. Physics

### Gravity

Mario is subject to gravity when airborne (jumping or falling off a girder edge).

- **Gravity acceleration:** 700px/s²
- **Terminal velocity:** 400px/s (falling cap)
- **Jump initial velocity:** -280px/s (upward)

Each frame:
```
if mario.airborne:
    mario.vy += 700 × dt
    if mario.vy > 400: mario.vy = 400
    mario.y += mario.vy × dt
```

### Walking on Slopes

When Mario is on a girder, his y-position is directly determined by the girder's slope at his x-position. He does not "slide" downhill — he walks at a fixed horizontal speed regardless of slope. The slope only affects his y-coordinate (he's higher on one side, lower on the other).

### Landing

When Mario's feet-y exceeds a girder's surface-y at his x-position (he's falling through a girder), snap him to the girder, set vy = 0, clear airborne state.

### Falling off Girder Edges

If Mario walks past the left or right end of a girder (beyond its x-range) without being above another girder, he falls. If the fall distance is small (< 40px — normal step between nearby girders), he's fine. If the fall distance would exceed ~60px (a full girder height gap), he dies on landing (fatal fall). This is computed by finding the next girder below and measuring the vertical gap.

In practice: Mario can safely step off a girder edge onto the girder directly below if they're close. He cannot survive falling two girder-heights.

### Barrel Physics

Barrels follow the girder slope. Their movement is defined by:
```
barrel.x += barrel.speed × barrel.direction × dt
barrel.y = girderYAtX(barrel.x)   // follows the girder surface
```

When a barrel reaches the edge of a girder:
- It either falls (drops to next girder with gravity + slight horizontal drift) or takes a ladder down.
- Falling barrels have `vy` accumulating with gravity (same 700px/s²). When they contact the next girder, they snap to it and resume rolling.

## 7. Controls

| Input | Action |
|-------|--------|
| Arrow Left / A | Walk left |
| Arrow Right / D | Walk right |
| Arrow Up / W | Climb ladder up |
| Arrow Down / S | Climb ladder down |
| Space | Jump |
| Enter | Start / Restart |
| P or Escape | Pause / Unpause |

**Movement uses held-key state.** Walking is continuous while the key is held. Climbing is continuous while on a ladder and the up/down key is held.

**Jump is edge-triggered.** One jump per press. Cannot jump while climbing. Can jump while walking (maintains horizontal velocity through the jump arc) or from a standstill (vertical-only jump).

**Climb initiation:** Mario can only start climbing when he's within ±8px of a ladder's center-x AND he's standing on the girder that the ladder connects from. Press Up to climb up, Down to climb down.

**While climbing:** Mario moves only vertically. Horizontal input is ignored. The player must reach the top or bottom of the ladder to dismount (or they can release the climb key at any point to stop and hang on the ladder — but they can't walk sideways off a ladder mid-climb).

**Ladder dismount:** When Mario reaches the top of a ladder (his feet reach the upper girder), he automatically steps onto the upper girder. When he reaches the bottom, he steps onto the lower girder.

## 8. Scoring

| Event | Points |
|-------|--------|
| Jump over a barrel (or barrel rolls under mid-jump) | 100 |
| Jump over two barrels simultaneously | 300 |
| Smash barrel with hammer | 300 |
| Smash fireball with hammer | 500 |
| Collect bonus item | 300–800 (see below) |
| Reach Pauline (level clear) | Remaining bonus timer × 1 |

**Jump scoring:** When Mario is airborne and a barrel passes through the space beneath him (the barrel's x-position crosses Mario's x-position while Mario's feet-y is above the barrel's top-y), award 100 points. Show a brief floating "100" at the jump point (12px, #FFFFFF, drifts up 30px over 0.6s, fades). If two barrels pass under during one jump, award 300 instead (show "300"). This is the primary scoring mechanism during gameplay and the reward for the risky choice to jump barrels instead of climbing to avoid them.

**Barrel passing under — detection:** Check every frame while Mario is airborne: for each barrel within ±18px of Mario's x, if the barrel's top-y > Mario's feet-y, flag it as "jumped over." At the end of the jump (Mario lands), total up the unique barrels jumped and award points. Only count each barrel once per jump.

### Bonus Items

A bonus item occasionally appears near the center of the level (on G3 or G4):

- **Pauline's dropped items:** A purse, parasol, or hat (drawn as simple shapes: purse = small rectangle #FF69B4, parasol = triangle #FF44FF, hat = semicircle #FF0000).
- **Spawn:** Appears after 20 seconds of gameplay, stays for 10 seconds.
- **Points:** 300 (purse), 500 (parasol), 800 (hat). Which item appears depends on the level (cycle through them).
- **Collection:** Mario walks through the item.

### Bonus Timer

A countdown timer displayed at the top of the screen. Starts at **5000** and decrements by approximately 100 every 2 seconds (rate: ~50 per second). When the player completes the level (reaches Pauline), the remaining bonus is added to the score. If the timer reaches 0, Mario dies (time out).

The timer creates urgency — the player can't wait forever for a safe moment. They must push upward.

## 9. Collision Detection

### Mario ↔ Barrel

Rectangle overlap between Mario's hitbox (18×28) and the barrel's hitbox (16×14). Contact → death (unless Mario has the hammer and the barrel hits the hammer zone).

### Mario ↔ Fireball

Rectangle overlap. Mario hitbox vs fireball hitbox (12×12). Contact → death.

### Hammer ↔ Barrel/Fireball

While the hammer is active, check a 28×20px zone centered above and in front of Mario (offset toward his facing direction). Any barrel or fireball overlapping this zone is destroyed.

### Mario ↔ Ladder

A ladder is "available" when Mario is within ±8px of its center-x. Check this against each ladder on Mario's current girder (for climbing up) or the girder above (for climbing down from). Mario must be standing on the correct girder to initiate climbing.

### Mario ↔ Girder (Landing)

Each frame while airborne, check if Mario's next y-position would cross any girder's surface. If so, land on it. Check all girders, snapping to the first one Mario's feet would pass through. Prioritize the highest girder that Mario is actually falling onto (not one he's already above).

### Mario ↔ Level Clear

When Mario steps onto G7 (Pauline's platform), the level is complete. Trigger: Mario's feet y ≤ G7's y-position and Mario's x is within the G7 x-range.

## 10. Lives & Death

**Starting lives:** 3.

**On death:**
1. Mario plays a death animation: he spins/tumbles in place (rotating the sprite, or showing a distinct "fallen" pose, cycling through 4 angled frames over 1 second). Color shifts to desaturated/grey.
2. All barrels and fireballs freeze (or continue — either convention works; freezing on death is more common).
3. After 1.5 seconds: if lives remain, Mario respawns at the starting position (bottom-right of G1). Barrels on screen are cleared. Fireballs persist (or clear them for mercy — clear them on levels 1–2, persist on 3+). DK resumes throwing barrels after a 2-second delay.
4. If 0 lives → GAME_OVER.

**Extra life:** At 10,000 points (once). Max 5 lives.

## 11. Level Progression

The game has one stage layout (the ramps level described above). Each successive level repeats the same layout with increased difficulty:

| Parameter | Level 1 | Level 2 | Level 3 | Level 4+ |
|-----------|---------|---------|---------|----------|
| Barrel throw interval | 3.0–4.0s | 2.5–3.5s | 2.0–3.0s | 1.5–2.5s |
| Barrel speed | 80–120 | 92–138 | 104–156 | 116–174 |
| Fireball count cap | 2 | 3 | 4 | 4 |
| Fireball speed | 50 | 60 | 70 | 80 |
| Blue barrels | None | Occasional | 1 in 3 | 1 in 2 |
| Starting bonus timer | 5000 | 6000 | 7000 | 8000 |
| Bonus timer drain rate | 50/s | 55/s | 60/s | 65/s |
| Broken ladder retract speed | 4s on / 2s off | 3.5s / 2s | 3s / 2.5s | 2.5s / 2.5s |

**On level complete:**
1. DK looks surprised (brief animation — eyes widen, arms up, 500ms).
2. A heart icon appears between Mario and Pauline (400ms).
3. DK grabs Pauline and climbs upward, off screen (1 second animation — DK and Pauline slide upward together).
4. Remaining bonus timer × 1 added to score (shown incrementing rapidly).
5. Brief "LEVEL CLEAR" (optional) for 1 second.
6. Next level begins: same layout, reset barrels/fireballs, Mario at start, difficulty increased.

## 12. Game States

```
TITLE → INTRO → PLAYING → (DEATH → RESPAWN → PLAYING) → LEVEL_CLEAR → INTRO (next level)
                    ↕                                          or
                 PAUSED                                     GAME_OVER
```

### TITLE

- The level layout renders in the background (girders, ladders, but no barrels).
- DK sits at the top with Pauline.
- **"DONKEY KONG"** centered at y ≈ 350, 42px bold monospace, #FF4400.
- Below: Mario sprite (animating walk cycle) and DK sprite (beating chest) side by side.
- **"Press Enter to Start"** at y ≈ 500, 18px, #AAAAAA, blinking.
- **"Best: {N}"** at y ≈ 540, 14px, #555555.
- Enter → INTRO.

### INTRO (Level Start Animation)

- DK climbs to the top with Pauline draped over his shoulder (animate DK climbing from the bottom to his platform position over 2 seconds — or simplify: just show DK already at top, stomps his feet, girders break/shift into their sloped positions one by one from top to bottom over 1.5 seconds).
- The iconic moment: DK jumps up and down on the top-left, causing the girders to tilt into their sloped positions. This can be simplified to: the girders render flat initially, then one by one (top-down, 200ms apart) they visually shift to their sloped positions with a brief screen shake (±2px for 100ms).
- After the intro animation (2–3 seconds total) → PLAYING.

### PLAYING

- All game logic active: Mario movement, barrel throwing, fireball behavior, timer countdown.
- P / Escape → PAUSED.

### PAUSED

- Freeze everything.
- Overlay #000000 at 60%.
- "PAUSED" 36px, #FFFFFF.
- P / Escape → resume.

### DEATH

- Death animation (1.5s).
- Lives decrement.
- If lives > 0: clear barrels, respawn Mario, 2-second DK delay → PLAYING.
- If lives = 0 → GAME_OVER.

### LEVEL_CLEAR

- Victory sequence (3–4 seconds): DK surprise, heart, DK escapes with Pauline.
- Bonus timer awards points.
- → INTRO (next level).

### GAME_OVER

- "GAME OVER" centered at y ≈ 320, 40px, #FF0000.
- "Score: {N}" at y ≈ 370, 24px, #FFFFFF.
- If new high score: "HIGH SCORE!" at y ≈ 405, 18px, #FFD700, pulsing.
- "Level: {N}" at y ≈ 435, 16px, #AAAAAA.
- "Enter to play again" at y ≈ 480, 16px, #888888, blinking.
- Enter → TITLE.

## 13. Audio

Web Audio API. `AudioContext` on first user interaction.

| Event | Sound | Implementation |
|-------|-------|----------------|
| Walking | Rhythmic footsteps | Alternating 200Hz/250Hz triangle, 30ms each, at 8Hz while moving, gain 0.08 |
| Jumping | Boing | 300Hz→500Hz sine, 80ms, gain 0.15 |
| Landing | Thud | 120Hz square, 40ms, gain 0.12 |
| Climbing | Ratchet tick | 350Hz square, 20ms, at 6Hz while climbing, gain 0.08 |
| Barrel thrown | Deep thump | 80Hz square, 100ms, gain 0.2 |
| Barrel rolling | Low rumble | 100Hz sawtooth, continuous while barrels visible, modulated at 3Hz, gain 0.05 |
| Jump over barrel | Score ding | 660Hz sine, 60ms, gain 0.18 |
| Hammer pickup | Power chord | 440Hz→660Hz square, 80ms each, gain 0.2 |
| Hammer smash | Crack | 200Hz square, 60ms → noise burst 30ms, gain 0.2 |
| Hammer expiring | Warning beeps | 800Hz square, 30ms at 4Hz, gain 0.12 (last 2 seconds) |
| Death | Descending spiral | 400Hz→100Hz sine, 600ms, gain 0.25 |
| Level clear | Victory jingle | C5→E5→G5→C6, 80ms each, sine, gain 0.2 |
| Bonus countdown | Rapid ticking | 600Hz square, 15ms at 20Hz while bonus is counting down to score, gain 0.08 |
| Extra life | Chime | 880Hz→1100Hz, 80ms each, gain 0.18 |

All gracefully optional.

### Background Music (Optional)

A simple repeating 4-bar melody at a tempo that increases with level:
- 4 notes cycling (similar to a march): 262Hz, 330Hz, 392Hz, 330Hz (C4, E4, G4, E4)
- Each note: 200ms at level 1, 150ms at level 3+
- Square wave, gain 0.06 (very quiet — background atmosphere, not foreground)
- Pauses during death animation and level transitions.

## 14. HUD

### Top Bar (y = 0–36)

| Element | Position | Style |
|---------|----------|-------|
| "SCORE" | x = 20, y = 14 | 12px monospace, #FF0000 |
| Score value | x = 20, y = 30 | 16px monospace, #FFFFFF |
| "HIGH SCORE" | Centered, y = 14 | 12px monospace, #FF0000 |
| High score value | Centered, y = 30 | 16px monospace, #FFFFFF |
| "BONUS" | Right, x = 520, y = 14 | 12px monospace, #00CCFF |
| Bonus value | Right, x = 520, y = 30 | 16px monospace, #FFFFFF. Flashes #FF4444 when < 1000. |
| "L={N}" | Far right, x = 620, y = 30 | 14px monospace, #AAAAAA |

### Bottom Bar (y = 732–768)

| Element | Position | Style |
|---------|----------|-------|
| Lives | x = 20, y = 754 | Small Mario icons (12×16px), one per remaining life (not counting active). Max 4 icons. |
| Bonus items collected | Right side | Small icons of purse/parasol/hat if collected on previous levels (cosmetic). |

## 15. Visual Style

The original Donkey Kong had a dark, industrial construction-site aesthetic. Keep it grounded:

1. **Girders:** Red-orange metallic segments. Each girder is a row of ~16×8px blocks with alternating #CC4400 and #FF6600. They look like riveted I-beams.

2. **Background:** Pure black. No sky, no fancy backdrop. The darkness emphasizes the girders and characters.

3. **Ladders:** Pale blue (#66CCFF) vertical rails with horizontal rungs. They pop against the dark background and red girders.

4. **Characters are blocky.** This is 1981 pixel art. Don't try for smooth or detailed — chunky filled rectangles that suggest the shapes are more authentic than smooth curves.

5. **Score popups:** When points are earned (jumping barrels, smashing with hammer), show the value as floating text at the event location. The text rises ~30px over 0.6 seconds and fades. Color: #FFFFFF.

6. **Screen shake:** Brief (100ms, ±2px) on DK barrel throw. Subtle but adds impact.

## 16. Implementation Notes

1. **Girder-relative positioning.** Many game objects (Mario, barrels, fireballs) are positioned relative to girders. Write a helper: `getGirderYAtX(girder, x)` that returns the girder surface y at a given x. Use it for walking, barrel rolling, and landing detection.

2. **Barrel state machine.** Each barrel has a state: HELD (DK is about to throw), ROLLING (on a girder), FALLING (between girders), ON_LADDER (descending a ladder). Update logic depends on state. Transitions: HELD → ROLLING (after throw animation), ROLLING → FALLING or ON_LADDER (at girder edge), FALLING → ROLLING (lands on girder), ON_LADDER → ROLLING (reaches bottom of ladder).

3. **Barrel-at-edge decision.** When a barrel reaches within 8px of a girder's edge: check for a ladder within 20px of that position. If a ladder exists and the random roll succeeds (20% for normal, 100% for blue), transition to ON_LADDER. Otherwise, transition to FALLING (roll off the edge).

4. **Fireball AI.** Fireballs are simple: they walk along a girder at their speed. When they reach a ladder intersection, roll for climb chance (40%). If climbing, pick up or down randomly weighted toward Mario's y-position (60% toward Mario, 40% away). When they reach a girder edge, they reverse direction. This produces an erratic-but-directed movement pattern.

5. **Mario on ladders.** When climbing, Mario's x is locked to the ladder's center-x. His y changes at climb speed. He can stop mid-ladder (release the climb key). He can't jump while on a ladder. He transitions off the ladder when reaching the top or bottom girder.

6. **Jump physics.** On jump press: `mario.vy = -280`. Set `airborne = true`. Each frame: apply gravity, update y, check for girder landings. Mario's x-movement continues during the jump at the current walking speed if a horizontal key is held. If no horizontal key: x is unchanged (pure vertical jump).

7. **Delta-time everything.** Cap dt at 50ms. All positions updated by velocity × dt. Timer decrements by rate × dt.

8. **Barrel cleanup.** Remove barrels when they fall below y = 700 (off-screen below G1). If they reach the oil drum region (x < 80 on G1), convert them to a fireball (if under cap) and remove the barrel.

9. **High score:** `localStorage` key `"donkeykong_best"`.

10. **Hammer zone calculation.** The hammer hitbox is offset based on Mario's facing direction: if facing right, the zone is (+4, -24) to (+32, -4) relative to Mario's center. If facing left, mirror it: (-32, -24) to (-4, -4). The zone swings with the animation — only active during the "down" swing frame (alternate frames: up [no hitbox] and down [hitbox active]). This means the hammer has a rhythmic vulnerability — barrels can slip through during the "up" frames. In practice at 10Hz oscillation, this is barely noticeable but adds a subtle skill element.

## 17. Acceptance Criteria

- [ ] Loads with no console errors
- [ ] Title screen with DK and game name
- [ ] Level intro animation (girders tilting into place)
- [ ] Six sloped girders rendered with construction-site aesthetic
- [ ] Ladders connect girders (some broken/retracting)
- [ ] Mario walks left/right along sloped girders at correct y-position
- [ ] Mario climbs up and down ladders
- [ ] Mario jumps with a gravity-affected arc
- [ ] DK throws barrels at regular intervals
- [ ] Barrels roll downhill along girder slopes
- [ ] Barrels fall to lower girders at edges or take ladders down
- [ ] Oil drum converts barrels to fireballs
- [ ] Fireballs patrol girders and climb ladders toward Mario
- [ ] Barrel collision kills Mario
- [ ] Fireball collision kills Mario
- [ ] Jumping over a barrel awards 100 points (300 for two)
- [ ] Two hammers collectible; smashing barrels/fireballs gives points
- [ ] Hammer prevents ladder climbing; expires after 10 seconds with warning
- [ ] Bonus timer counts down; reaching Pauline awards remaining bonus
- [ ] Reaching the top platform (Pauline) completes the level
- [ ] Next level increases barrel speed, throw rate, fireball count
- [ ] Death animation plays; respawn at starting position
- [ ] Score, high score (persisted), bonus timer, lives display correctly
- [ ] Pause freezes everything
- [ ] Game over screen with score and restart

## 18. Build Task Checklist

| # | Task | Description | Acceptance Test |
|---|------|-------------|-----------------|
| T01 | HTML scaffold | DOCTYPE, 672×768 canvas, #000000, centered, inline CSS, `<script>` | Black canvas, no errors |
| T02 | Game loop & input | `requestAnimationFrame` + delta-time (capped 50ms). Key state: arrows/WASD continuous, Space edge-triggered, Enter, P/Escape. | Smooth loop; keys tracked |
| T03 | State machine | TITLE, INTRO, PLAYING, PAUSED, DEATH, LEVEL_CLEAR, GAME_OVER. Transitions per spec. | All states reachable; transitions correct |
| T04 | Girder rendering | 6 sloped girders + Pauline's platform. Red-orange I-beam segments. Correct positions and slopes per layout. | Girders visible; slopes apparent; construction-site look |
| T05 | Ladders | Full and broken ladders connecting girders. Cyan-blue rails + rungs. Broken ladders retract/extend on timer. | Ladders visible; broken ladders toggle on/off |
| T06 | Mario: walking | 24×32 sprite. Walks at 100px/s. Y follows girder slope. Clamps to girder x-range. Walk animation (2 frames). Facing direction. | Mario walks on sloped girders smoothly |
| T07 | Mario: climbing | When at a ladder and Up/Down pressed, Mario climbs at 80px/s. Locked to ladder x. Dismounts at top/bottom girder. Climb animation. | Mario climbs ladders; transitions to girder at top/bottom |
| T08 | Mario: jumping | Space = jump (-280px/s initial vy). Gravity 700px/s². Maintains horizontal velocity. Landing detection on girders. Fall damage from excessive height. | Mario jumps in arcs; lands correctly; high falls kill |
| T09 | DK & barrel throwing | DK rendered at top-left. Throw animation. Barrels spawned every 2.5–4s. Barrel lands on G6 and starts rolling. | DK animates; barrels appear at regular intervals |
| T10 | Barrel rolling | Barrels follow girder slopes downhill. 80–120px/s. Rolling animation. At girder edge: 80% fall, 20% take ladder. Falling barrels have gravity + drift. | Barrels roll, fall between girders, zigzag downward |
| T11 | Barrel collision & scoring | Barrel hitbox vs Mario hitbox → death. Mario airborne + barrel passes under → 100 pts (300 for two). Score popup floats. | Barrels kill; jumping over awards points |
| T12 | Oil drum & fireballs | Barrels reaching oil drum → fireball (cap 4). Fireballs patrol girders, climb ladders toward Mario at 60px/s. Fireball collision → death. | Fireballs spawn; patrol; seek Mario; lethal |
| T13 | Hammer | Two hammers on the level. Collection triggers 10s power-up. Hammer oscillates above Mario. Destroys barrels/fireballs (300/500 pts). Can't climb while active. 2s warning flash. | Hammer works; smashes enemies; disables climbing; expires with warning |
| T14 | Pauline & level clear | Pauline on top platform with "HELP!" text. Mario reaching G7 → level clear. DK surprise animation → DK escapes upward. Bonus timer awards. | Reaching top completes level; bonus awards; victory animation |
| T15 | Bonus timer | Starts at 5000, drains at ~50/s. Display in HUD. Timer at 0 → death. Timer remainder → score on level clear. | Timer counts down; urgency increases; correct scoring |
| T16 | Level progression | Levels 1–4+: increasing barrel speed/rate, fireball count, blue barrels. Same layout, more pressure. | Each level noticeably harder |
| T17 | HUD | Score, high score, bonus timer, level number (top). Lives as Mario icons (bottom). High score in localStorage. Extra life at 10k. | HUD renders; scores correct; lives track |
| T18 | Intro animation | Girders shift from flat to sloped (one by one, top-down, with screen shake). DK at top. | Intro plays; girders animate; DK visible |
| T19 | Title & game over | Title: "DONKEY KONG" + character display + start prompt. Game over: score, high score, level, restart. Pause overlay. | Screens render and transition |
| T20 | Audio | Footsteps, jump boing, climb ratchet, barrel throw thump, barrel smash, hammer pickup, hammer warning, death spiral, level clear jingle, bonus countdown tick. | Sounds trigger correctly |
| T21 | Blue barrels & bonus items | Blue barrels (always take ladders) at level 2+. Bonus items (purse/parasol/hat) spawn mid-level. | Blue barrels path aggressively; bonus items collectible |
| T22 | Polish & testing | All acceptance criteria. Edge cases: jumping at girder edge, barrel on ladder while Mario climbing same ladder, hammer timing with fast barrels, fireball near ladder decision, timer expiry during climbing, multiple barrels in same spot. | All criteria met; game feels fair and challenging |
