# Pac-Man — Complete Game Specification

## Overview

Pac-Man is a maze chase game. The player controls a yellow circle that navigates a maze eating dots while avoiding four ghosts. The goal is to eat all 240 dots to complete a level. Large power pellets temporarily allow you to eat the ghosts. Clearing a level advances to the next with increased difficulty. The game ends when all lives are lost.

---

## Canvas and Grid

**Canvas dimensions:** 448 × 496 pixels

**Grid system:**
- 28 columns × 31 rows of tiles
- Each tile = 16 × 16 pixels
- All game elements align to tile centers

**Background color:** Black (#000000)

**Wall color:** Blue (#2121DE)

---

## The Maze Layout

The complete maze pattern (each character = one 16×16 tile):

```
############################
#............##............#
#.####.#####.##.#####.####.#
#O####.#####.##.#####.####O#
#..........................#
#.####.##.########.##.####.#
#......##....##....##......#
######.##### ## #####.######
     #.##         ##.#
     #.## ###--### ##.#
     #.## #      # ##.#
######.## #      # ##.######
      .   #      #   .
######.## #      # ##.######
     #.## ######## ##.#
     #.##          ##.#
     #.## ######## ##.#
######.## ######## ##.######
#............##............#
#.####.#####.##.#####.####.#
#O..##.......##.......##..O#
###.##.##.########.##.##.###
#......##....##....##......#
#.##########.##.##########.#
#..........................#
############################
```

**Key:**
- `#` = Wall
- `.` = Dot
- `O` = Power pellet
- `-` = Ghost house door
- Space = Empty corridor

---

## Key Locations

**Pac-Man spawn:** Bottom center (row 23, column 14)

**Power pellets:** Four corners of the maze (rows 3 and 20, columns 1 and 26)

**Tunnels:** Row 12, left and right edges — wrap around to opposite side

**Ghost house:** Center of maze (rows 12-15, centered horizontally)

**Ghost spawn positions:**
- Blinky (red): Outside house, row 9, column 14
- Pinky (pink): Inside house, row 13, column 12
- Inky (cyan): Inside house, row 13, column 14
- Clyde (orange): Inside house, row 13, column 15

---

## Pac-Man

**Visual:** Yellow circle (#FFFF00), 14 pixels diameter, with a wedge-shaped mouth that animates while moving.

**Movement:**
- Speed: 2.5 pixels per frame
- Continuous motion through corridors
- Can only turn at intersections
- Direction inputs queue until a valid turn is possible

**Mouth animation:** 3 frames cycling: closed → half-open → fully open → repeat

**Starting position:** Bottom center of maze

---

## Dots

**Small dots:**
- Count: 240
- Size: 4 pixels diameter
- Points: 10 each

**Power pellets:**
- Count: 4
- Size: 12 pixels diameter
- Points: 50 each
- Effect: Makes ghosts vulnerable (frightened mode)
- Appearance: Flashing/pulsing

**Win condition:** Eat all 240 dots

---

## The Four Ghosts

| Ghost | Color | Behavior |
|-------|-------|----------|
| Blinky | Red (#FF0000) | Directly chases Pac-Man |
| Pinky | Pink (#FFB8FF) | Targets 4 tiles ahead of Pac-Man |
| Inky | Cyan (#00FFFF) | Complex targeting using Blinky's position |
| Clyde | Orange (#FFB852) | Chases when far, flees to corner when close |

**Ghost appearance:**
- Normal: Round body with wavy bottom, white eyes with blue pupils
- Frightened: Dark blue body (#2121DE), wavy mouth expression
- Eaten: Only eyes, no body

---

## Ghost AI

### Modes

**Scatter mode:** Ghosts go to their home corners
- Blinky → top-right
- Pinky → top-left  
- Inky → bottom-right
- Clyde → bottom-left

**Chase mode:** Ghosts actively pursue Pac-Man using targeting logic

**Frightened mode:** Ghosts move randomly, can be eaten

**Eaten mode:** Ghost eyes return to ghost house

### Mode Timing

| Phase | Mode | Duration |
|-------|------|----------|
| 1 | Scatter | 7 seconds |
| 2 | Chase | 20 seconds |
| 3 | Scatter | 7 seconds |
| 4 | Chase | 20 seconds |
| 5 | Scatter | 5 seconds |
| 6 | Chase | 20 seconds |
| 7 | Scatter | 5 seconds |
| 8+ | Chase | Indefinite |

After level 4, Chase mode is permanent.

### Targeting Logic

**Blinky:** Target = Pac-Man's current position

**Pinky:** Target = 4 tiles ahead of Pac-Man's direction

**Inky:** Target = Double the vector from Blinky to 2 tiles ahead of Pac-Man

**Clyde:** Target = Pac-Man if distance > 8 tiles, else bottom-left corner

### Ghost Speeds

| State | Speed |
|-------|-------|
| Normal | 75-80% of Pac-Man |
| In tunnel | 40-50% |
| Frightened | 50% |
| Eaten (eyes) | 150-200% |

---

## Power Pellet Effects

When Pac-Man eats a power pellet:
1. All ghosts in maze enter frightened mode
2. Ghosts turn dark blue and move randomly
3. Eating ghosts awards points: 200 → 400 → 800 → 1600
4. Eaten ghosts return to house as eyes
5. Timer: 6 seconds (level 1), decreasing per level, 0 at level 6+
6. Flash warning in final 2 seconds

---

## Lives and Death

**Starting lives:** 3

**Extra life:** At 10,000 points

**Death condition:** Collision with ghost (not frightened)

**On death:**
- Death animation plays
- Ghosts return to spawn positions
- Dots remain eaten
- Pac-Man respawns at start

**Game over:** When lives = 0

---

## Level Progression

**Level complete:** All 240 dots eaten

**Changes per level:**
- Ghosts faster
- Frightened duration shorter
- Blinky gets "Cruise Elroy" speed boost when few dots remain

---

## Controls

| Key | Action |
|-----|--------|
| ↑ W | Move up |
| ↓ S | Move down |
| ← A | Move left |
| → D | Move right |
| P Escape | Pause |
| R | Restart |

---

## Bonus Fruit

Spawns below ghost house, ~10 seconds duration:

| Level | Fruit | Points |
|-------|-------|--------|
| 1 | Cherry | 100 |
| 2 | Strawberry | 300 |
| 3 | Orange | 500 |
| 4 | Apple | 700 |
| 5 | Melon | 1000 |

---

## Game States

1. **Title screen** — Press SPACE to start
2. **Ready screen** — "READY!" text, 2-3 second pause
3. **Playing** — Normal gameplay
4. **Paused** — Press P to resume
5. **Death animation** — Pac-Man shrinking
6. **Level complete** — Maze flashes
7. **Game over** — Final score, press R

---

## Technical Notes

**Maze storage:** 2D array [31][28], values: 0=empty, 1=wall, 2=dot, 3=power

**Collision:** Check if movement would overlap wall tiles

**Direction queuing:** Store next direction, apply when valid

**Tunnel:** If x < 0 then x = canvas.width, if x > canvas.width then x = 0

**Ghost direction choice:** At intersections, pick direction closest to target (can't reverse)

---

## Feature Checklist

- [ ] 448×496 canvas with 16×16 tile grid
- [ ] Complete maze with walls and corridors
- [ ] 240 dots + 4 power pellets
- [ ] Pac-Man with mouth animation
- [ ] Movement with direction queuing
- [ ] Wall collision detection
- [ ] Tunnel wraparound
- [ ] 4 ghosts with distinct colors
- [ ] Scatter/Chase/Frightened/Eaten modes
- [ ] Ghost targeting per personality
- [ ] Power pellet frightened trigger
- [ ] Ghost eating with score multiplier
- [ ] Lives system (3 lives)
- [ ] Score display
- [ ] Level progression
- [ ] Title/Ready/Playing/Paused/Game Over states
- [ ] Single HTML file, no dependencies

---

## Quick Reference

| Item | Value |
|------|-------|
| Canvas | 448×496 px |
| Tile size | 16×16 px |
| Pac-Man | 14 px diameter, 2.5 px/frame |
| Ghost | 14 px diameter, 2.0 px/frame |
| Dots | 240 (10 pts each) |
| Power pellets | 4 (50 pts each) |
| Ghost points | 200, 400, 800, 1600 |
| Lives | 3 |
| Frightened time | 6 sec (L1) to 0 sec (L6+) |

End of specification.