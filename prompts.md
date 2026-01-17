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

## Game Features Summary

### Core Mechanics
- Flappy Bird style gameplay with gravity and jump controls (SPACE)
- Projectile shooting system (X key)
- Heat management system preventing spam-firing

### Visual Effects
- Particle explosions on all collisions
- Color-matched enemy destruction particles
- Fading and gravity-affected particles

### Enemy System
- Three enemy types with unique visual designs
- Random size, speed, and movement patterns
- Bobbing/floating motion with sine waves
- Rotating animations and effects

### UI Elements
- Score display (center top)
- Heat gauge (top-left corner)
- Start/restart instructions
- Game over screen

### Scoring
- 1 point for passing an enemy
- 1 point for destroying an enemy with projectile

### Controls
- SPACE: Jump / Start game / Restart
- X: Fire projectile
- ESC: Quit game
