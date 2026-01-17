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

# Enemy settings
ENEMY_SIZE_MIN = 20  # Minimum enemy size
ENEMY_SIZE_MAX = 40  # Maximum enemy size
ENEMY_VELOCITY_MIN = 2  # Minimum speed
ENEMY_VELOCITY_MAX = 5  # Maximum speed
ENEMY_SPAWN_MIN = 100  # Minimum Y position
ENEMY_SPAWN_MAX = SCREEN_HEIGHT - 100  # Maximum Y position

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
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.particles = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_started:
                        self.game_started = True
                    if not self.game_over:
                        self.bird.jump()
                    else:
                        self.reset()
                if event.key == pygame.K_x:
                    # Fire projectile
                    if self.game_started and not self.game_over:
                        self.shoot_projectile()
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def shoot_projectile(self):
        """Create a new projectile from the bird's position"""
        projectile_x = self.bird.x + BIRD_WIDTH
        projectile_y = self.bird.y + BIRD_HEIGHT // 2
        self.projectiles.append(Projectile(projectile_x, projectile_y))

    def update(self):
        # Always update particles, even during game over
        for particle in self.particles:
            particle.update()

        # Remove dead particles
        self.particles = [p for p in self.particles if not p.is_dead()]

        if not self.game_started or self.game_over:
            return

        # Update bird
        self.bird.update()

        # Check if bird hits ground or ceiling
        if self.bird.y > SCREEN_HEIGHT - BIRD_HEIGHT or self.bird.y < 0:
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

    def draw(self):
        # Background
        self.screen.fill(BLUE)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

        # Draw particles (before bird so they appear behind)
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw bird
        self.bird.draw(self.screen)

        # Draw score
        score_text = self.font.render(str(self.score), True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 20, 50))

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
