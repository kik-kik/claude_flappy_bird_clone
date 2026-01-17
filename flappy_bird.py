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

# Bird settings
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
BIRD_X = 50
GRAVITY = 0.5
JUMP_STRENGTH = -10

# Pipe settings
PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_VELOCITY = 3

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

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.passed = False
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - self.height - PIPE_GAP)

    def update(self):
        self.x -= PIPE_VELOCITY
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, GREEN, self.bottom_rect)
        # Pipe caps
        pygame.draw.rect(screen, (0, 150, 0), (self.x - 5, self.height - 20, PIPE_WIDTH + 10, 20))
        pygame.draw.rect(screen, (0, 150, 0), (self.x - 5, self.height + PIPE_GAP, PIPE_WIDTH + 10, 20))

    def is_off_screen(self):
        return self.x < -PIPE_WIDTH

    def collides_with(self, bird):
        return bird.rect.colliderect(self.top_rect) or bird.rect.colliderect(self.bottom_rect)

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
        self.pipes = [Pipe(SCREEN_WIDTH + 200)]
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
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

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

        # Update pipes
        for pipe in self.pipes:
            pipe.update()

            # Check collision
            if pipe.collides_with(self.bird):
                if not self.game_over:
                    self.create_collision_particles(self.bird.x + BIRD_WIDTH // 2, self.bird.y + BIRD_HEIGHT // 2)
                self.game_over = True

            # Check if bird passed the pipe
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1

        # Remove off-screen pipes
        self.pipes = [pipe for pipe in self.pipes if not pipe.is_off_screen()]

        # Add new pipes
        if len(self.pipes) == 0 or self.pipes[-1].x < SCREEN_WIDTH - 300:
            self.pipes.append(Pipe(SCREEN_WIDTH))

    def create_collision_particles(self, x, y):
        """Create an explosion of particles at collision point"""
        # Create 30-50 particles for a nice explosion effect
        num_particles = random.randint(30, 50)
        for _ in range(num_particles):
            # Mix of yellow (bird color), red, and orange for explosion effect
            color = random.choice([YELLOW, RED, ORANGE, (255, 200, 0)])
            self.particles.append(Particle(x, y, color))

    def draw(self):
        # Background
        self.screen.fill(BLUE)

        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)

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
