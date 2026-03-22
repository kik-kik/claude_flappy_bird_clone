# Flappy Bird Development Prompts

This document contains all the prompts used during the development of this enhanced Flappy Bird game, along with summaries of the completed tasks.

## Prompt 1: Initial Feature Request
**Prompt:** "can you take the flappy bird clone and add additional features to it. Specifically I would like some sort of particle effect to take place when the player collides with an obstacle."

**Summary:** Added a particle system with explosion effects on collision. Created a `Particle` class that generates 30-50 particles with random velocities, colors (yellow, red, orange), gravity effects, and fade-out animations when the player collides with obstacles, ground, or ceiling.

---

## Prompt 2: Replace Pipes with Enemies
**Prompt:** "could we replace the static pipes with enemies that are similar size to the player themeselves that get randomly spawned"

**Summary:** Replaced static pipe obstacles with enemy entities similar in size to the player (30x30 pixels). Enemies spawn at random heights and intervals, feature bobbing/floating motion with sine wave movement, have rotating spikes, and include animated eyes. Each enemy has unique bobbing speed, amplitude, and movement patterns.

---

## Prompt 3: Add Enemy Randomness
**Prompt:** "Let's tweak the enemies a little bit, can we introduce some randomness to the enemy size, speed and range of motion?"

**Summary:** Added extensive randomization to enemies:
- Size: 20-40 pixels (randomized per enemy)
- Speed: 2-5 pixels per frame (randomized per enemy)
- Bobbing amplitude: 10-60 pixels (wider range of motion)
- Bobbing speed: 0.03-0.15 (more variation)
- Spike rotation speed: 0.02-0.08 (randomized)
- All visual elements scale proportionally with enemy size

---

## Prompt 4: Add Enemy Variety
**Prompt:** "can we add a little bit of a variaty of the enemies, perhaps we could introduce 2 new types of enemies?"

**Summary:** Created three distinct enemy types with unique appearances and animations:
1. **Spiky Enemy (Red)**: Original design with rotating spikes radiating from center
2. **Square Enemy (Purple)**: Rotating square shape with pulsing outline and nested inner square
3. **Wavy Enemy (Cyan)**: Jellyfish-like creature with trailing wave effect and 4 animated tentacles

Each type is randomly selected when spawned, creating visual diversity.

---

## Prompt 5: Add Projectile Shooting
**Prompt:** "can we give the player an ability to fire projectiles that when contact that destroy the enemies on impact (this should destroy the enemy object and result in a particle effect)"

**Summary:** Implemented a shooting mechanic:
- Press X to fire glowing yellow projectiles
- Projectiles travel horizontally at speed 8
- Collision with enemies destroys both projectile and enemy
- Enemy destruction creates color-matched particle explosions (40-60 particles)
- Awards 1 point for destroying enemies (same as passing them)
- Updated instructions to show "Press X to shoot"

---

## Prompt 6: Adjust Scoring
**Prompt:** "when enemy is killed we should only get 1 score point not 2"

**Summary:** Changed scoring from 2 points to 1 point for killing enemies, matching the reward for passing enemies.

---

## Prompt 7: Add Shooting Cooldown
**Prompt:** "Let's add some sort of cooldown to the player firing projectiles. Perhaps some sort of gauge that if the player fires too quickly then they will have to wait a little bit before they can fire again"

**Summary:** Implemented a visual cooldown gauge system:
- 30-frame cooldown between shots (0.5 seconds)
- Gauge located in top-left corner (100x15 pixels)
- Color-coded: Red (cooling) → Yellow (halfway) → Green (ready)
- Labeled "SHOOT" to indicate purpose
- Prevents spam-firing projectiles

---

## Prompt 8: Replace with Heat System
**Prompt:** "Let's tweak the cooldown a little bit. Instead of having a fixed amount of time between each shot let's make it so that each shot fills the gauge. The gauge should cool down if the player has not been firing for a 2 seconds. If the gauge fills the player should not be able to fire again until the gauge cools down completely"

**Summary:** Replaced fixed cooldown with a heat gauge system:
- Each shot adds 25 heat (max 100) - can fire 4 shots before overheating
- Heat starts cooling after 2 seconds of not firing
- Cooldown rate: 1.5 heat per frame
- Visual feedback: Green (cool) → Yellow → Orange → Red (overheated)
- "OVERHEAT!" warning when maxed out
- Must cool completely from overheat before firing again

---

## Prompt 9: Reduce Cooldown Delay
**Prompt:** "Could we reduce the cooldown delay bu half?"

**Summary:** Reduced heat cooldown delay from 120 frames (2 seconds) to 60 frames (1 second), making the combat more responsive while maintaining the heat management mechanic.

---

## Prompt 10: Add Drop and Power-Up System
**Prompt:** "can we add drops after an enemy dies, this should will up a bar and when full give the player an ability to pick a powerup such as a shield, double projective with each shot, faster firing cool down"

**Summary:** Implemented a comprehensive drop and power-up system:
- **Drops**: Killed enemies spawn glowing green collectible gems
- **Power-Up Bar**: Fills as drops are collected (located below heat gauge)
- **Power-Up Menu**: Opens when bar is full, pauses game for selection
- **Three Power-Ups**:
  1. **Shield** (5 seconds): Temporary invincibility from enemies and walls
  2. **Double Shot** (10 seconds): Fires 3 projectiles simultaneously
  3. **Fast Fire** (10 seconds): 50% reduced heat buildup
- **Visual Feedback**: Active power-up icons shown on right side with duration bars
- **Selection**: Press 1, 2, or 3 to choose power-up when menu appears

---

## Prompt 11: Add Bouncing Physics to Drops
**Prompt:** "can you make the power up energy bounce off the top, bottm, and the right side of the screen? When it passes through the left side of the screen it should be destroyed"

**Summary:** Modified drop physics for more dynamic gameplay:
- Drops now have random velocity in both X and Y directions
- Bounce off top, bottom, and right edges of screen
- Only destroyed when passing through left edge
- Creates chase-based collection mechanic where drops bounce around before escaping

---

## Prompt 12: Adjust Drop Speed and Pickup Range
**Prompt:** "can you make the power ups move a little slower and also make the pick-up range a little bit bigger so that it is a bit easier for the player to pick it up during the game"

**Summary:** Made drops easier to collect:
- **Slower Movement**: Reduced velocity from (-3 to -1, -4 to 4) to (-2 to -0.5, -2 to 2)
- **Larger Pickup Range**: Increased from 12 pixels to 25 pixels
- **Distance-Based Collision**: Changed from rectangle to distance-based detection for smoother collection experience

---

## Prompt 13: Progressive Power-Up Difficulty
**Prompt:** "can we make a tweak so that the number of power up drops required to get an upgrade goes up with each time we get a power up? Starting with only needing two at the beginning?"

**Summary:** Implemented scaling power-up requirements:
- **Starting Requirement**: Only 2 drops needed for first power-up (reduced from 5)
- **Progressive Increase**: Each power-up activation increases requirement by 1
  - 1st power-up: 2 drops
  - 2nd power-up: 3 drops
  - 3rd power-up: 4 drops
  - And so on...
- **Visual Counter**: Bar label shows "X/Y" format (e.g., "2/3" = collected 2, need 3 total)
- **Dynamic Scaling**: Bar fills proportionally based on current requirement

---

## Game Features Summary

### Core Mechanics
- Flappy Bird style gameplay with gravity and jump controls (SPACE)
- Projectile shooting system (X key)
- Heat management system preventing spam-firing
- Drop collection system with bouncing physics
- Progressive power-up system with scaling difficulty

### Visual Effects
- Particle explosions on all collisions
- Color-matched enemy destruction particles
- Fading and gravity-affected particles
- Glowing pulsing drop gems
- Shield visual effect around player

### Enemy System
- Three enemy types with unique visual designs
- Random size, speed, and movement patterns
- Bobbing/floating motion with sine waves
- Rotating animations and effects
- Drop glowing gems when destroyed by projectiles

### Power-Up System
- **Drops**: Bouncing collectibles with physics (bounce off top/bottom/right, destroyed at left edge)
- **Collection**: Large pickup range (25 pixels) for easier gameplay
- **Progressive Requirements**: Starts at 2 drops, increases by 1 each time
- **Three Power-Ups**:
  - Shield: 5 seconds invincibility
  - Double Shot: 10 seconds triple projectile firing
  - Fast Fire: 10 seconds 50% heat reduction
- **Menu System**: Pause-on-full selection interface (keys 1, 2, 3)

### UI Elements
- Score display (center top)
- Heat gauge (top-left corner)
- Power-up bar with X/Y counter (below heat gauge)
- Active power-up icons (right side with duration bars)
- Power-up selection menu (semi-transparent overlay)
- Start/restart instructions
- Game over screen

### Scoring
- 1 point for passing an enemy
- 1 point for destroying an enemy with projectile

### Controls
- SPACE: Jump / Start game / Restart
- X: Fire projectile
- 1/2/3: Select power-up (when menu is active)
- ESC: Quit game
