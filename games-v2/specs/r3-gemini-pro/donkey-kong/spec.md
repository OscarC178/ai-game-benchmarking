# Game Specification: Donkey Kong

## 1. Core Concept & Gameplay Overview
Donkey Kong is a classic single-screen platform arcade game. The player controls a small carpenter ("Mario" or "Jumpman") starting at the bottom of the screen. The objective is to navigate upward through a structure of slanted metal girders and ladders to reach the top where Donkey Kong is holding the captive Pauline.

Donkey Kong continuously throws rolling barrels down the girders. The player must jump over these barrels, climb ladders, and avoid falling. Touching a barrel results in the loss of a life. The player can temporarily grab a hammer to smash barrels for points. Reaching Pauline clears the level.

## 2. Technical Constraints
- **Format:** A single, self-contained `index.html` file.
- **Assets:** Strict zero-dependency. Render the characters and geometry using the HTML5 Canvas API (`fillRect`, `lineTo`, etc.) to create retro pixel-art approximations. No external images or CSS.
- **Game Loop:** A continuous `requestAnimationFrame` loop using delta time (`dt`) for physics calculations (gravity, velocity).

## 3. Visual Layout & Dimensions
- **Canvas Size:** ~600px width by ~750px height.
- **Background:** Black (`#000000`).
- **Typography:** Arcade-style, bright red or white monospace font.
- **Layout (The 25m Stage):**
  - **Level 6 (Top):** Only spans the middle third of the screen. Donkey Kong stands here on the left, Pauline stands on a slightly higher raised block in the center.
  - **Levels 1 to 5 (Girders):** Five long horizontal beams. They are sloped. 
    - L1 (bottom) starts on the left and slopes slightly upward to the right. 
    - L2 slopes upward to the left. 
    - L3 slopes upward to the right, etc.
  - **Ladders:** Vertical cyan lines connecting the girders. Some ladders are broken (missing middle rungs)—these cannot be climbed but barrels can still sometimes fall through them.
  - **Oil Drum:** A blue flaming barrel placed at the bottom left (start of L1).

## 4. Game Entities

### The Player (Mario)
- **Shape:** Simple pixel representation. Red overalls, blue shirt (or vice versa), skin-colored face. Size roughly 24x30 pixels.
- **Movement:** 
  - Standard side-to-side running.
  - **Jumping:** Parabolic physics. Cannot change X-velocity mid-air (commitment mechanic).
  - **Climbing:** Can only attach to an unbroken ladder when aligned with it. Cannot jump while climbing.
- **Hitbox:** Slightly smaller than the visual sprite (e.g., 20x24) to be forgiving.
- **Death:** Triggers a specific animation (spin/fall) and brief pause.

### Donkey Kong
- **Shape:** Large blocky brown/orange ape shape. Size roughly 60x60 pixels.
- **Behavior:** Stand static, periodically animate arms to "toss" a barrel. The speed of tossing increases as the level runs longer.

### The Barrels (The Primary Threat)
- **Shape:** Brown circles or octagons with a lighter center. Size roughly 18x18 pixels.
- **Spawning:** Spawns at Donkey Kong's position.
- **Movement Physics:** 
  1. Barrels are affected by gravity and roll *down* the sloped girders. 
  2. **Ladder Drop:** When a rolling barrel rolls directly over the top of a ladder (broken or unbroken), it has a random chance (e.g., ~20%) to stop rolling and fall straight down the ladder until it hits the next girder.
  3. **Edge Drop:** When a barrel reaches the end of a sloped girder, it falls straight down off the edge, landing on the girder below and reversing its rolling direction.
  4. **The Oil Drum:** The first barrel (or periodically other barrels) that reaches the bottom-left edge drops into the Oil Drum and is removed.
- **Despawn:** Barrels rolling off the screen are removed from memory.

### The Hammer
- **Placement:** Two hammers sit floating above the girders (e.g., one on L3 left, one on L4 right).
- **Behavior:** If Mario jumps into a hammer, he grabs it. 
  - The hammer automatically swings up and down rapidly via an internal timer for roughly 8-10 seconds. 
  - While holding a hammer, Mario CANNOT jump and CANNOT climb ladders. He can only run left and right.
  - If a barrel collides with Mario's front hitbox while the hammer is on a downward swing, the barrel is destroyed. If the hammer is on the upswing, Mario dies. (Alternatively, for simplicity, provide a small invulnerability hitbox in front of Mario while the hammer is active).

## 5. Controls
- **ArrowLeft / A:** Run Left.
- **ArrowRight / D:** Run Right.
- **ArrowUp / W:** Climb Up (if intersecting a ladder).
- **ArrowDown / S:** Climb Down (if intersecting a ladder).
- **Spacebar:** Jump.

## 6. Collisions & Interactions
- **Mario vs. Barrel:** If AABB overlap occurs (and hammer is not actively destroying it), Mario dies.
- **Mario vs. Pauline:** If Mario's bounding box touches the goal region near Pauline at the top, the level is cleared.
- **Gravity & Platforms:** Mario must continuously check if his bottom edge intersects a girder's top edge. Because girders are slanted, the Y-coordinate of ground under Mario must be calculated mathematically based on Mario's current X-coordinate and the slope of the nearest girder.
- **Score (Jump):** If Mario jumps completely over a barrel without touching it, award points (100 pts) as the barrel passes beneath him.

## 7. Scoring & Progression
- **Points:** 
  - Barrel Jump: 100 points.
  - Barrel Smash (Hammer): 300 points.
  - Level Clear: Base 1000 points + value of the Bonus Timer.
- **Bonus Timer:** A numeric value starting at e.g. 5000, ticking down slowly. If it reaches 0, Mario naturally dies. 
- **Escalation:** When the level is cleared, immediately restart the same level layout but decrease the Bonus Timer starting value, increase barrel rolling speed, and increase barrel spawn frequency.

## 8. Game Flow & States
- **Lives:** Start with 3.
- **STATE: START/HOW HIGH:** Brief screen showing "HOW HIGH CAN YOU GET?" and the current level number (e.g., L=01).
- **STATE: PLAYING:** Main physics loop, handling input, gravity, barrel spawning.
- **STATE: DEATH:** Freeze game, play death animation, decrement life. If lives remain, reset Mario to start and delete all current barrels.
- **STATE: GAME OVER:** Lives = 0. Display "GAME OVER". Allow restart.

## 9. Audio (Web Audio API)
Generate synthesized sound inline using `AudioContext` (triggered after first input).
- **Mario Walking:** Rhythmic, alternating high/low squeak per step.
- **Mario Jump:** Fast rising slide "boing" tone.
- **Hammer Music/Siren:** A frantic, looping 2 or 3 note sequence while the hammer is active.
- **Barrel Smash:** Sharp burst of white noise.
- **Death:** Classic descending set of 3 long tones.
- **Level Clear Jingle:** A short, triumphant major-key arpeggio.
