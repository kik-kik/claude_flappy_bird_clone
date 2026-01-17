import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (147, 51, 234)
CYAN = (0, 255, 255)

# Bird settings
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
BIRD_X = 50
GRAVITY = 0.5
JUMP_STRENGTH = -10

# Projectile settings
PROJECTILE_SIZE = 6
PROJECTILE_SPEED = 8
PROJECTILE_COLOR = (255, 255, 100)
HEAT_PER_SHOT = 25  # Heat added per shot
HEAT_COOLDOWN_DELAY = 60  # Frames before cooldown starts (1 second at 60 FPS)
HEAT_COOLDOWN_RATE = 1.5  # Heat reduced per frame during cooldown
MAX_HEAT = 100  # Maximum heat before overheat

# Enemy settings
ENEMY_SIZE_MIN = 20  # Minimum enemy size
ENEMY_SIZE_MAX = 40  # Maximum enemy size
ENEMY_VELOCITY_MIN = 2  # Minimum speed
ENEMY_VELOCITY_MAX = 5  # Maximum speed
ENEMY_SPAWN_MIN = 100  # Minimum Y position
ENEMY_SPAWN_MAX = SCREEN_HEIGHT - 100  # Maximum Y position

# Drop settings
DROP_SIZE = 12  # Size of collectible drops
DROP_FALL_SPEED = 2  # Speed drops fall
DROP_VALUE = 20  # How much each drop fills the power-up bar (always 20 per drop)
INITIAL_DROPS_NEEDED = 2  # Initial number of drops needed for first power-up
DROP_PICKUP_RANGE = 25  # Pickup radius (larger than visual size for easier collection)

# Power-up settings
SHIELD_DURATION = 300  # Frames shield lasts (5 seconds)
DOUBLE_SHOT_DURATION = 600  # Frames double shot lasts (10 seconds)
FAST_FIRE_DURATION = 600  # Frames fast fire lasts (10 seconds)
FAST_FIRE_HEAT_MULTIPLIER = 0.5  # Heat per shot when fast fire is active

class Drop:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, DROP_SIZE, DROP_SIZE)
        # Random velocity in both x and y directions (reduced speed)
        self.vx = random.uniform(-2, -0.5)  # Slower leftward velocity
        self.vy = random.uniform(-2, 2)  # Slower vertical velocity
        self.frame = 0

    def update(self):
        # Update position with velocity
        self.x += self.vx
        self.y += self.vy

        # Bounce off top edge
        if self.y < DROP_SIZE:
            self.y = DROP_SIZE
            self.vy = abs(self.vy)  # Reverse to downward

        # Bounce off bottom edge
        if self.y > SCREEN_HEIGHT - DROP_SIZE:
            self.y = SCREEN_HEIGHT - DROP_SIZE
            self.vy = -abs(self.vy)  # Reverse to upward

        # Bounce off right edge
        if self.x > SCREEN_WIDTH - DROP_SIZE:
            self.x = SCREEN_WIDTH - DROP_SIZE
            self.vx = -abs(self.vx)  # Reverse to leftward

        # Update rect position
        self.rect.x = self.x
        self.rect.y = self.y
        self.frame += 1

    def draw(self, screen):
        # Draw a glowing collectible gem with pulsing effect
        pulse = math.sin(self.frame * 0.15) * 2
        size = DROP_SIZE + int(pulse)

        # Outer glow
        pygame.draw.circle(screen, (100, 255, 100), (int(self.x), int(self.y)), size)
        # Inner core
        pygame.draw.circle(screen, (200, 255, 200), (int(self.x), int(self.y)), size - 3)
        # Bright center
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), size - 6)

    def is_off_screen(self):
        # Only destroy when passing through left edge
        return self.x < -DROP_SIZE

    def collides_with(self, bird):
        # Use distance-based collision for larger pickup range
        bird_center_x = bird.x + BIRD_WIDTH // 2
        bird_center_y = bird.y + BIRD_HEIGHT // 2
        drop_center_x = self.x
        drop_center_y = self.y

        # Calculate distance between centers
        distance = math.sqrt((bird_center_x - drop_center_x)**2 + (bird_center_y - drop_center_y)**2)

        # Return true if within pickup range
        return distance < DROP_PICKUP_RANGE

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # Random velocity in all directions
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 60  # Frames until particle disappears
        self.size = random.randint(3, 8)
        self.gravity = 0.2

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Apply gravity to particles
        self.life -= 1
        # Slow down particles over time
        self.vx *= 0.98
        self.vy *= 0.98

    def draw(self, screen):
        # Fade out as life decreases
        alpha = int(255 * (self.life / 60))
        # Create a copy of the color with alpha
        color = (
            min(255, self.color[0]),
            min(255, self.color[1]),
            min(255, self.color[2])
        )
        # Draw particle with fading effect (using size reduction as proxy for fade)
        current_size = max(1, int(self.size * (self.life / 60)))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), current_size)

    def is_dead(self):
        return self.life <= 0

class Projectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, PROJECTILE_SIZE, PROJECTILE_SIZE)
        self.speed = PROJECTILE_SPEED

    def update(self):
        self.x += self.speed
        self.rect.x = self.x

    def draw(self, screen):
        # Draw projectile as a glowing yellow circle with trail effect
        pygame.draw.circle(screen, PROJECTILE_COLOR, (int(self.x), int(self.y)), PROJECTILE_SIZE)
        # Add a glow effect
        pygame.draw.circle(screen, (255, 255, 200), (int(self.x), int(self.y)), PROJECTILE_SIZE - 2)

    def is_off_screen(self):
        return self.x > SCREEN_WIDTH

class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, BIRD_WIDTH, BIRD_HEIGHT)

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x + BIRD_WIDTH // 2), int(self.y + BIRD_HEIGHT // 2)), BIRD_HEIGHT // 2)
        # Simple wing
        pygame.draw.circle(screen, (255, 200, 0), (int(self.x + 5), int(self.y + BIRD_HEIGHT // 2)), 8)

class Enemy:
    def __init__(self, x, enemy_type=None):
        self.x = x
        # Randomly choose enemy type if not specified
        if enemy_type is None:
            self.enemy_type = random.choice(['spiky', 'square', 'wavy'])
        else:
            self.enemy_type = enemy_type

        # Random size for each enemy
        self.size = random.randint(ENEMY_SIZE_MIN, ENEMY_SIZE_MAX)
        # Random speed for each enemy
        self.velocity = random.uniform(ENEMY_VELOCITY_MIN, ENEMY_VELOCITY_MAX)
        self.y = random.randint(ENEMY_SPAWN_MIN, ENEMY_SPAWN_MAX)
        self.passed = False
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        # Add some variation to enemy movement with wider range
        self.bob_offset = random.uniform(0, 2 * math.pi)
        self.bob_speed = random.uniform(0.03, 0.15)  # More speed variation
        self.bob_amplitude = random.randint(10, 60)  # Wider range of motion
        self.initial_y = self.y
        self.frame = 0
        # Random rotation speed for spikes
        self.spike_rotation_speed = random.uniform(0.02, 0.08)
        # Wave pattern for wavy enemy
        self.wave_offset = random.uniform(0, 2 * math.pi)

    def update(self):
        self.x -= self.velocity  # Use individual velocity
        # Add bobbing motion
        self.frame += 1
        self.y = self.initial_y + math.sin(self.frame * self.bob_speed + self.bob_offset) * self.bob_amplitude
        self.rect.x = self.x
        self.rect.y = self.y
        self.rect.width = self.size
        self.rect.height = self.size

    def draw(self, screen):
        center_x = int(self.x + self.size // 2)
        center_y = int(self.y + self.size // 2)

        if self.enemy_type == 'spiky':
            self.draw_spiky(screen, center_x, center_y)
        elif self.enemy_type == 'square':
            self.draw_square(screen, center_x, center_y)
        elif self.enemy_type == 'wavy':
            self.draw_wavy(screen, center_x, center_y)

    def draw_spiky(self, screen, center_x, center_y):
        # Original spiky enemy (red with rotating spikes)
        # Draw spikes around the enemy
        num_spikes = 8
        for i in range(num_spikes):
            angle = (2 * math.pi * i / num_spikes) + (self.frame * self.spike_rotation_speed)
            spike_length = self.size // 2 + int(self.size * 0.2)
            end_x = center_x + math.cos(angle) * spike_length
            end_y = center_y + math.sin(angle) * spike_length
            spike_thickness = max(2, int(self.size * 0.1))
            pygame.draw.line(screen, (150, 0, 0), (center_x, center_y), (int(end_x), int(end_y)), spike_thickness)

        # Main body
        pygame.draw.circle(screen, RED, (center_x, center_y), self.size // 2)

        # Eyes
        eye_offset = max(4, int(self.size * 0.2))
        eye_size = max(3, int(self.size * 0.13))
        pupil_size = max(2, int(self.size * 0.07))
        pygame.draw.circle(screen, WHITE, (center_x - eye_offset, center_y - 3), eye_size)
        pygame.draw.circle(screen, WHITE, (center_x + eye_offset, center_y - 3), eye_size)
        pygame.draw.circle(screen, BLACK, (center_x - eye_offset, center_y - 3), pupil_size)
        pygame.draw.circle(screen, BLACK, (center_x + eye_offset, center_y - 3), pupil_size)

    def draw_square(self, screen, center_x, center_y):
        # Square enemy (purple with pulsing outline)
        half_size = self.size // 2

        # Pulsing effect
        pulse = math.sin(self.frame * 0.1) * 3
        outline_size = int(4 + pulse)

        # Draw outline (darker purple)
        outline_rect = pygame.Rect(center_x - half_size - outline_size,
                                   center_y - half_size - outline_size,
                                   self.size + outline_size * 2,
                                   self.size + outline_size * 2)
        pygame.draw.rect(screen, (80, 20, 120), outline_rect)

        # Main body (rotating square)
        rotation = self.frame * self.spike_rotation_speed
        corners = []
        for i in range(4):
            angle = rotation + (i * math.pi / 2) + math.pi / 4
            corner_x = center_x + math.cos(angle) * half_size * 1.4
            corner_y = center_y + math.sin(angle) * half_size * 1.4
            corners.append((int(corner_x), int(corner_y)))
        pygame.draw.polygon(screen, PURPLE, corners)

        # Inner square (lighter)
        inner_corners = []
        for i in range(4):
            angle = rotation + (i * math.pi / 2) + math.pi / 4
            corner_x = center_x + math.cos(angle) * half_size * 0.7
            corner_y = center_y + math.sin(angle) * half_size * 0.7
            inner_corners.append((int(corner_x), int(corner_y)))
        pygame.draw.polygon(screen, (200, 100, 255), inner_corners)

        # Eyes
        eye_offset = max(4, int(self.size * 0.15))
        eye_size = max(2, int(self.size * 0.1))
        pygame.draw.circle(screen, WHITE, (center_x - eye_offset, center_y), eye_size)
        pygame.draw.circle(screen, WHITE, (center_x + eye_offset, center_y), eye_size)

    def draw_wavy(self, screen, center_x, center_y):
        # Wavy enemy (cyan with trailing wave effect)
        # Draw trailing wave segments
        num_segments = 5
        for i in range(num_segments):
            segment_x = center_x + i * (self.size // 3)
            wave_y = center_y + math.sin((self.frame + i * 10) * 0.15 + self.wave_offset) * (self.size * 0.3)
            segment_size = max(3, int(self.size // 2 - i * 2))
            # Fade out trail
            brightness = 255 - (i * 40)
            color = (0, max(0, brightness), max(0, brightness))
            pygame.draw.circle(screen, color, (int(segment_x), int(wave_y)), segment_size)

        # Main body (brighter cyan)
        pygame.draw.circle(screen, CYAN, (center_x, center_y), self.size // 2)

        # Add some tentacle-like appendages
        num_tentacles = 4
        for i in range(num_tentacles):
            angle = (2 * math.pi * i / num_tentacles) + (self.frame * 0.05)
            tentacle_length = self.size // 2 + int(self.size * 0.3)
            # Wavy tentacle
            for j in range(3):
                progress = j / 3
                tent_x = center_x + math.cos(angle) * tentacle_length * progress
                tent_y = center_y + math.sin(angle) * tentacle_length * progress
                tent_y += math.sin((self.frame + j * 5) * 0.2) * 3
                tent_size = max(1, int((self.size * 0.1) * (1 - progress)))
                pygame.draw.circle(screen, (0, 200, 200), (int(tent_x), int(tent_y)), tent_size)

        # Eyes
        eye_offset = max(4, int(self.size * 0.2))
        eye_size = max(3, int(self.size * 0.12))
        pupil_size = max(2, int(self.size * 0.06))
        pygame.draw.circle(screen, WHITE, (center_x - eye_offset, center_y - 2), eye_size)
        pygame.draw.circle(screen, WHITE, (center_x + eye_offset, center_y - 2), eye_size)
        pygame.draw.circle(screen, BLACK, (center_x - eye_offset, center_y - 2), pupil_size)
        pygame.draw.circle(screen, BLACK, (center_x + eye_offset, center_y - 2), pupil_size)

    def is_off_screen(self):
        return self.x < -self.size

    def collides_with(self, bird):
        return bird.rect.colliderect(self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)
        self.reset()

    def reset(self):
        self.bird = Bird()
        self.enemies = [Enemy(SCREEN_WIDTH + 200)]
        self.projectiles = []
        self.drops = []  # Collectible drops
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.particles = []
        self.heat = 0  # Current heat level
        self.heat_cooldown_timer = 0  # Timer for when cooldown starts
        self.powerup_charge = 0  # Current charge toward power-up
        self.powerup_menu_active = False  # Whether power-up selection menu is shown
        self.active_powerups = {}  # Dictionary to track active power-ups and their durations
        self.drops_needed = INITIAL_DROPS_NEEDED  # Number of drops needed for next power-up (increases each time)
        # Possible power-ups: 'shield', 'double_shot', 'fast_fire'

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_started:
                        self.game_started = True
                    if not self.game_over:
                        if not self.powerup_menu_active:
                            self.bird.jump()
                    else:
                        self.reset()
                if event.key == pygame.K_x:
                    # Fire projectile
                    if self.game_started and not self.game_over and not self.powerup_menu_active and self.heat < MAX_HEAT:
                        self.shoot_projectile()
                        # Adjust heat based on active power-ups
                        heat_to_add = HEAT_PER_SHOT
                        if 'fast_fire' in self.active_powerups:
                            heat_to_add *= FAST_FIRE_HEAT_MULTIPLIER
                        self.heat = min(MAX_HEAT, self.heat + heat_to_add)
                        self.heat_cooldown_timer = HEAT_COOLDOWN_DELAY  # Reset cooldown timer
                # Power-up selection keys (1, 2, 3)
                if self.powerup_menu_active:
                    if event.key == pygame.K_1:
                        self.activate_powerup('shield')
                    elif event.key == pygame.K_2:
                        self.activate_powerup('double_shot')
                    elif event.key == pygame.K_3:
                        self.activate_powerup('fast_fire')
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def shoot_projectile(self):
        """Create a new projectile from the bird's position"""
        projectile_x = self.bird.x + BIRD_WIDTH
        projectile_y = self.bird.y + BIRD_HEIGHT // 2
        self.projectiles.append(Projectile(projectile_x, projectile_y))

        # If double shot is active, fire a second projectile above/below
        if 'double_shot' in self.active_powerups:
            offset = 15
            self.projectiles.append(Projectile(projectile_x, projectile_y - offset))
            self.projectiles.append(Projectile(projectile_x, projectile_y + offset))

    def activate_powerup(self, powerup_type):
        """Activate a power-up"""
        if powerup_type == 'shield':
            self.active_powerups['shield'] = SHIELD_DURATION
        elif powerup_type == 'double_shot':
            self.active_powerups['double_shot'] = DOUBLE_SHOT_DURATION
        elif powerup_type == 'fast_fire':
            self.active_powerups['fast_fire'] = FAST_FIRE_DURATION

        # Reset power-up charge and close menu
        self.powerup_charge = 0
        self.powerup_menu_active = False

        # Increase drops needed for next power-up
        self.drops_needed += 1

    def update(self):
        # Always update particles, even during game over
        for particle in self.particles:
            particle.update()

        # Remove dead particles
        self.particles = [p for p in self.particles if not p.is_dead()]

        # Always update drops (even when menu is open)
        for drop in self.drops:
            drop.update()

        # Remove off-screen drops
        self.drops = [d for d in self.drops if not d.is_off_screen()]

        if not self.game_started or self.game_over:
            return

        # If power-up menu is active, pause game but allow menu interaction
        if self.powerup_menu_active:
            return

        # Update active power-ups
        powerups_to_remove = []
        for powerup, duration in self.active_powerups.items():
            self.active_powerups[powerup] = duration - 1
            if self.active_powerups[powerup] <= 0:
                powerups_to_remove.append(powerup)
        for powerup in powerups_to_remove:
            del self.active_powerups[powerup]

        # Update heat cooldown system
        if self.heat > 0:
            if self.heat_cooldown_timer > 0:
                # Still waiting before cooldown starts
                self.heat_cooldown_timer -= 1
            else:
                # Cooldown active - reduce heat
                self.heat = max(0, self.heat - HEAT_COOLDOWN_RATE)

        # Update bird
        self.bird.update()

        # Check drop collection
        for drop in self.drops[:]:
            if drop.collides_with(self.bird):
                self.powerup_charge += DROP_VALUE
                self.drops.remove(drop)
                # Calculate max charge based on drops needed
                max_charge = self.drops_needed * DROP_VALUE
                # Open power-up menu when charge is full
                if self.powerup_charge >= max_charge:
                    self.powerup_menu_active = True

        # Check if bird hits ground or ceiling
        if self.bird.y > SCREEN_HEIGHT - BIRD_HEIGHT or self.bird.y < 0:
            # Shield protects from ground/ceiling
            if 'shield' not in self.active_powerups:
                if not self.game_over:
                    self.create_collision_particles(self.bird.x + BIRD_WIDTH // 2, self.bird.y + BIRD_HEIGHT // 2)
                self.game_over = True

        # Update projectiles
        for projectile in self.projectiles:
            projectile.update()

        # Remove off-screen projectiles
        self.projectiles = [p for p in self.projectiles if not p.is_off_screen()]

        # Check projectile-enemy collisions
        enemies_to_remove = []
        projectiles_to_remove = []

        for projectile in self.projectiles:
            for enemy in self.enemies:
                if projectile.rect.colliderect(enemy.rect):
                    # Create explosion particles at enemy location
                    self.create_enemy_explosion(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2, enemy.enemy_type)
                    if enemy not in enemies_to_remove:
                        enemies_to_remove.append(enemy)
                        # Spawn a drop at enemy location
                        self.drops.append(Drop(enemy.x + enemy.size // 2, enemy.y + enemy.size // 2))
                    if projectile not in projectiles_to_remove:
                        projectiles_to_remove.append(projectile)
                    # Award points for destroying enemy
                    self.score += 1

        # Remove destroyed enemies and projectiles
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
        for projectile in projectiles_to_remove:
            if projectile in self.projectiles:
                self.projectiles.remove(projectile)

        # Update enemies
        for enemy in self.enemies:
            enemy.update()

            # Check collision
            if enemy.collides_with(self.bird):
                # Shield protects from enemies
                if 'shield' not in self.active_powerups:
                    if not self.game_over:
                        self.create_collision_particles(self.bird.x + BIRD_WIDTH // 2, self.bird.y + BIRD_HEIGHT // 2)
                    self.game_over = True

            # Check if bird passed the enemy
            if not enemy.passed and enemy.x + enemy.size < self.bird.x:
                enemy.passed = True
                self.score += 1

        # Remove off-screen enemies
        self.enemies = [enemy for enemy in self.enemies if not enemy.is_off_screen()]

        # Add new enemies at random intervals
        if len(self.enemies) == 0 or self.enemies[-1].x < SCREEN_WIDTH - random.randint(200, 400):
            self.enemies.append(Enemy(SCREEN_WIDTH))

    def create_collision_particles(self, x, y):
        """Create an explosion of particles at collision point"""
        # Create 30-50 particles for a nice explosion effect
        num_particles = random.randint(30, 50)
        for _ in range(num_particles):
            # Mix of yellow (bird color), red, and orange for explosion effect
            color = random.choice([YELLOW, RED, ORANGE, (255, 200, 0)])
            self.particles.append(Particle(x, y, color))

    def create_enemy_explosion(self, x, y, enemy_type):
        """Create an explosion of particles when enemy is destroyed"""
        # Create more particles for a bigger explosion
        num_particles = random.randint(40, 60)
        for _ in range(num_particles):
            # Use colors matching the enemy type
            if enemy_type == 'spiky':
                color = random.choice([RED, ORANGE, (255, 100, 100)])
            elif enemy_type == 'square':
                color = random.choice([PURPLE, (200, 100, 255), (147, 51, 234)])
            elif enemy_type == 'wavy':
                color = random.choice([CYAN, (0, 200, 200), (100, 255, 255)])
            else:
                color = random.choice([WHITE, (200, 200, 200)])
            self.particles.append(Particle(x, y, color))

    def draw_cooldown_gauge(self):
        """Draw the heat gauge"""
        # Gauge position and size
        gauge_x = 10
        gauge_y = 10
        gauge_width = 100
        gauge_height = 15

        # Background (empty gauge)
        pygame.draw.rect(self.screen, (50, 50, 50), (gauge_x, gauge_y, gauge_width, gauge_height))
        pygame.draw.rect(self.screen, WHITE, (gauge_x, gauge_y, gauge_width, gauge_height), 2)

        # Fill (heat level)
        heat_percentage = self.heat / MAX_HEAT
        fill_width = int(gauge_width * heat_percentage)

        # Color changes from green (cool) to red (overheated)
        if heat_percentage < 0.5:
            # Green to yellow
            color = (int(255 * heat_percentage * 2), 255, 0)
        else:
            # Yellow to red
            color = (255, int(255 * (1 - heat_percentage) * 2), 0)

        if fill_width > 0:
            pygame.draw.rect(self.screen, color, (gauge_x, gauge_y, fill_width, gauge_height))

        # Label changes based on heat state
        if self.heat >= MAX_HEAT:
            label_text = self.small_font.render("OVERHEAT!", True, RED)
        elif self.heat > MAX_HEAT * 0.7:
            label_text = self.small_font.render("HEAT", True, ORANGE)
        else:
            label_text = self.small_font.render("HEAT", True, WHITE)
        self.screen.blit(label_text, (gauge_x + gauge_width + 10, gauge_y - 5))

    def draw_powerup_bar(self):
        """Draw the power-up charge bar"""
        # Bar position and size (below heat gauge)
        bar_x = 10
        bar_y = 35
        bar_width = 100
        bar_height = 15

        # Background (empty bar)
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

        # Calculate max charge based on drops needed
        max_charge = self.drops_needed * DROP_VALUE

        # Fill (power-up charge level)
        charge_percentage = min(1.0, self.powerup_charge / max_charge)
        fill_width = int(bar_width * charge_percentage)

        # Color: green with pulsing effect when full
        if charge_percentage >= 1.0:
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 100)
            color = (100 + pulse, 255, 100 + pulse)
        else:
            color = (100, 255, 100)

        if fill_width > 0:
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))

        # Label shows drops collected / drops needed
        drops_collected = int(self.powerup_charge / DROP_VALUE)
        if charge_percentage >= 1.0:
            label_text = self.small_font.render("READY!", True, GREEN)
        else:
            label_text = self.small_font.render(f"{drops_collected}/{self.drops_needed}", True, WHITE)
        self.screen.blit(label_text, (bar_x + bar_width + 10, bar_y - 5))

    def draw_active_powerups(self):
        """Draw icons for active power-ups"""
        icon_x = SCREEN_WIDTH - 120
        icon_y = 10
        icon_size = 30
        spacing = 5

        y_offset = 0
        for powerup, duration in self.active_powerups.items():
            # Draw background
            pygame.draw.rect(self.screen, (50, 50, 50), (icon_x, icon_y + y_offset, icon_size, icon_size))
            pygame.draw.rect(self.screen, WHITE, (icon_x, icon_y + y_offset, icon_size, icon_size), 2)

            # Draw icon based on type
            center_x = icon_x + icon_size // 2
            center_y = icon_y + y_offset + icon_size // 2

            if powerup == 'shield':
                # Shield icon (hexagon)
                points = []
                for i in range(6):
                    angle = math.pi / 3 * i
                    px = center_x + math.cos(angle) * 10
                    py = center_y + math.sin(angle) * 10
                    points.append((int(px), int(py)))
                pygame.draw.polygon(self.screen, CYAN, points)
            elif powerup == 'double_shot':
                # Double shot icon (two circles)
                pygame.draw.circle(self.screen, YELLOW, (center_x - 5, center_y), 5)
                pygame.draw.circle(self.screen, YELLOW, (center_x + 5, center_y), 5)
            elif powerup == 'fast_fire':
                # Fast fire icon (three arrows)
                for i in range(3):
                    offset = (i - 1) * 6
                    pygame.draw.polygon(self.screen, ORANGE, [
                        (center_x - 5, center_y + offset),
                        (center_x + 5, center_y + offset),
                        (center_x + 8, center_y + offset + 3),
                        (center_x + 5, center_y + offset),
                        (center_x + 8, center_y + offset - 3)
                    ])

            # Draw duration bar
            duration_percentage = duration / (SHIELD_DURATION if powerup == 'shield' else DOUBLE_SHOT_DURATION)
            bar_width = int(icon_size * duration_percentage)
            pygame.draw.rect(self.screen, GREEN, (icon_x, icon_y + y_offset + icon_size - 3, bar_width, 3))

            y_offset += icon_size + spacing

    def draw_powerup_menu(self):
        """Draw the power-up selection menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Menu background
        menu_width = 350
        menu_height = 300
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2

        pygame.draw.rect(self.screen, (30, 30, 30), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 3)

        # Title
        title_text = self.font.render("POWER-UP", True, GREEN)
        self.screen.blit(title_text, (menu_x + menu_width // 2 - 80, menu_y + 20))

        # Power-up options
        option_y = menu_y + 80
        option_height = 50
        option_spacing = 10

        options = [
            ("1. SHIELD", "Temporary invincibility", CYAN),
            ("2. DOUBLE SHOT", "Fire 3 projectiles", YELLOW),
            ("3. FAST FIRE", "Reduced heat buildup", ORANGE)
        ]

        for i, (title, description, color) in enumerate(options):
            y = option_y + i * (option_height + option_spacing)

            # Option background
            pygame.draw.rect(self.screen, (50, 50, 50), (menu_x + 20, y, menu_width - 40, option_height))
            pygame.draw.rect(self.screen, color, (menu_x + 20, y, menu_width - 40, option_height), 2)

            # Title
            title_text = self.small_font.render(title, True, color)
            self.screen.blit(title_text, (menu_x + 30, y + 5))

            # Description
            desc_font = pygame.font.Font(None, 20)
            desc_text = desc_font.render(description, True, WHITE)
            self.screen.blit(desc_text, (menu_x + 30, y + 30))

    def draw(self):
        # Background
        self.screen.fill(BLUE)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

        # Draw drops
        for drop in self.drops:
            drop.draw(self.screen)

        # Draw particles (before bird so they appear behind)
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw bird
        self.bird.draw(self.screen)

        # Draw shield effect around bird if active
        if 'shield' in self.active_powerups:
            shield_pulse = math.sin(pygame.time.get_ticks() * 0.01) * 3
            shield_radius = BIRD_HEIGHT // 2 + 8 + int(shield_pulse)
            pygame.draw.circle(self.screen, CYAN,
                             (int(self.bird.x + BIRD_WIDTH // 2), int(self.bird.y + BIRD_HEIGHT // 2)),
                             shield_radius, 3)

        # Draw score
        score_text = self.font.render(str(self.score), True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 20, 50))

        # Draw cooldown gauge
        if self.game_started and not self.game_over:
            self.draw_cooldown_gauge()
            self.draw_powerup_bar()
            self.draw_active_powerups()

        # Draw power-up menu if active
        if self.powerup_menu_active:
            self.draw_powerup_menu()

        # Draw instructions or game over
        if not self.game_started:
            start_text = self.small_font.render("Press SPACE to start", True, WHITE)
            self.screen.blit(start_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
            shoot_text = self.small_font.render("Press X to shoot", True, WHITE)
            self.screen.blit(shoot_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 30))

        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 50))
            restart_text = self.small_font.render("Press SPACE to restart", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
