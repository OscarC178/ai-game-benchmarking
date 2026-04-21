# Game Specification: Space Invaders

## 1. Core Concept & Gameplay Overview
Space Invaders is a fixed-shooter arcade game. The player controls a laser cannon (a small ship) that moves horizontally across the bottom of the screen. Above the player is a grid of alien enemies that move collectively side-to-side, dropping lower each time they touch a screen edge. 

The objective is to destroy all the aliens in the wave before they reach the bottom of the screen. The aliens shoot projectiles down at the player. The player can take cover behind destructible shields (bunkers) placed slightly above the ship. Occasionally, a special "mystery ship" flies across the top of the screen for bonus points. If the aliens reach the bottom of the screen, or if the player loses all their lives, the game is over.

## 2. Technical Constraints
- **Format:** A single, self-contained `index.html` file.
- **Assets:** Strict zero-dependency rule. All graphics must be drawn using Canvas API primitives (lines, rectangles, paths). Do NOT use external images, Base64 images, CSS files, or audio files.
- **Rendering:** HTML5 `<canvas>` using the 2D context.
- **Timing & Physics:** Use `requestAnimationFrame` for a smooth render loop. Use delta time (`dt`) for player/projectile movement to ensure frame-rate independence. 
- **Alien Movement:** Unlike the player, the alien grid moves in discrete "steps" or "ticks" (mimicking the hardware limitations of the original arcade machine), rather than continuous smooth movement.

## 3. Visual Design & Layout
- **Canvas Size:** 800px width by 600px height. Centered on the page with a `#000000` (black) background.
- **Typography:** Monospace font (e.g., `"Courier New", monospace`), colored white (`#FFFFFF`) or green (`#00FF00`).
- **HUD:** 
  - **Score:** Displayed in the top left.
  - **High Score:** Displayed in the top center (stored via `localStorage`).
  - **Lives:** Displayed in the top right (either numerically or as small ship icons).

## 4. Game Entities

### The Player (Laser Cannon)
- **Shape:** A geometric representation of a cannon (e.g., a wide base rectangle with a narrower rectangle on top acting as the gun barrel).
- **Dimensions:** Approx 40px width by 20px height.
- **Color:** Bright Green (`#00FF00`).
- **Position:** Fixed vertically near the bottom (e.g., `y = 550`). Horizontally bounds-checked so it cannot leave the canvas.
- **Movement Speed:** 300 pixels per second, strictly horizontal.

### The Aliens (The Invader Grid)
- **Grid Setup:** 5 rows and 11 columns of aliens.
- **Spacing:** Approx 40px horizontal and 40px vertical spacing between alien centers. The entire grid should be centered horizontally at the start.
- **Alien Types & Colors:** (Different point values assigned based on row height).
  - Top 1 Row: Type C (Small/Squid-like) | 30 points | Pink (`#FF00FF`) or White.
  - Middle 2 Rows: Type B (Medium/Crab-like) | 20 points | Cyan (`#00FFFF`) or Light Blue.
  - Bottom 2 Rows: Type A (Large/Octopus-like) | 10 points | Yellow (`#FFFF00`) or Orange.
- **Shapes:** Draw these using simple pixel-art style `fillRect` arrays or path representations. They should have a simple 2-frame animation state (arms up / arms down) that toggles every time the grid steps.
- **Movement Logic:** 
  - The entire grid acts as a single bounding box. 
  - The grid moves horizontally by a fixed amount (e.g., 10px) every `tick`.
  - If the grid's bounding box hits the right or left canvas edge: On the next tick, the movement direction reverses, AND the entire grid moves *down* by a fixed amount (e.g., 20px).
  - **Speed Scaling:** The time between movement ticks decreases (the game speeds up) inversely proportional to the number of remaining aliens. (e.g., 1000ms delay with 55 aliens; 50ms delay with 1 alien).

### Alien Projectiles
- **Shape:** A vertical line or small jagged zig-zag line.
- **Color:** White (`#FFFFFF`).
- **Behavior:** Randomly, an alien in the *bottom-most* occupied position of a column will drop a projectile. 
- **Limits:** Only a set number of alien projectiles (e.g., maximum 3) are permitted on screen at once.
- **Speed:** Moves downwards at approx 200 pixels per second.

### Player Projectile
- **Shape:** A simple vertical rectangle (e.g., 2px wide, 10px high).
- **Color:** Bright Green (`#00FF00`).
- **Behavior:** Fired straight up from the player's cannon. 
- **Limitation:** The player can ONLY have exactly 1 projectile on the screen at a time. The player cannot fire again until their current projectile hits a target or leaves the top of the canvas.
- **Speed:** Moves upwards at approx 600 pixels per second.

### The Shields (Bunkers)
- **Count:** 4 shields spaced evenly across the screen above the player (e.g., `y = 450`).
- **Shape/Size:** Roughly shaped like a blocky igloo or arch. Approx 80px width, 60px height.
- **Color:** Bright Green (`#00FF00`).
- **Destructibility:** Shields are not single entities. They must degrade realistically. 
  - *Implementation approach:* Represent each shield as a grid of small (e.g., 4x4 or 5x5 pixel) "chunks". When a projectile (player or alien) intersects a chunk, destroy that chunk and remove the projectile. This creates a "nibbling" effect.

### The Mystery Ship (UFO)
- **Shape:** An elliptical/saucer shape drawn at the very top of the playing area (below the HUD).
- **Color:** Red (`#FF0000`).
- **Behavior:** Spawns randomly (or on a timer) and travels linearly from one side of the screen to the other without changing height. Does not drop projectiles.
- **Points:** Awards a random high point value when hit (e.g., 50, 100, 150, or 300).

## 5. Controls
- **ArrowLeft / A:** Move player left.
- **ArrowRight / D:** Move player right.
- **Spacebar:** Fire player projectile.
- **Enter:** Start / Restart game.

## 6. Physics & Collisions
Use AABB overlap detection for collision logic.

- **Player Projectile vs Alien:** Destroy alien. Add points. Remove player projectile. Check if alien was the last in its column to update the grid bounding box. Play explosion sound.
- **Player Projectile vs Mystery Ship:** Destroy mystery ship. Display random score briefly. Play UFO hit sound.
- **Alien Projectile vs Player:** Player loses 1 life. Pause briefly, clear all projectiles, reset player to center, resume. If lives = 0, Game Over.
- **Any Projectile vs Shield Chunk:** Destroy the intersected chunk(s) and remove the projectile.
- **Player Projectile vs Alien Projectile:** (Optional but authentic) Projectiles cancel each other out if they collide mid-air.
- **Alien Grid vs Player (or Bottom of Screen):** If the lowest alien touches the player's Y-coordinate, immediate Game Over (regardless of remaining lives).
- **Alien Grid vs Shields:** If the aliens descend into the shields, they destroy the shield chunks they overlap.

## 7. Game Flow & States
- **Lives:** Start with 3 lives.
- **STATE: STARTUP:** Display title "SPACE INVADERS", a point value legend for the alien types, and "Press Enter to Start".
- **STATE: PLAYING:** Main game loop. Update continuous entities (projectiles, player) via `dt`, update discrete entities (aliens) over fixed interval timers.
- **STATE: WAVE CLEAR:** If all aliens are destroyed, pause briefly, recreate the 5x11 grid, reset the player, and start a new wave. The new wave should start slightly lower on the screen than the previous wave to increase base difficulty.
- **STATE: GAME OVER:** Stop movement. Display "GAME OVER". Allow restart.

## 8. Audio (Web Audio API)
Browser security policies require audio to start only *after* user interaction. Implement a simple `AudioContext` synthesizer.
- **Player Fire:** Short, high-pitched "pew" (e.g., rapid descending sweep from 1000Hz to 200Hz over 0.1s, square wave).
- **Alien Destroyed:** Harsh noise/static burst (e.g., use a low-frequency oscillator or noise buffer for a short crunch).
- **Player Hit / Death:** Deeper, longer explosion sound.
- **Alien March (The Heartbeat):** A set of 4 descending low-frequency tones (e.g., 120Hz, 110Hz, 100Hz, 90Hz) that trigger one by one every time the alien grid steps. The tempo of this physical sound effect naturally accelerates as the aliens speed up, creating the iconic tension.
- **Mystery Ship Flyover:** A continuous high-frequency wobble (e.g., alternating between 600Hz and 800Hz) playing only while the UFO is on screen.
