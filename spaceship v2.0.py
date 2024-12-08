import pygame
import random
from pathlib import Path

ROOT_DIR = str(Path(__file__).parent)
WIDTH, HEIGHT = 800, 800  # Adjusted window size to fit the entire game
FPS = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Enhanced")
clock = pygame.time.Clock()

# Load spaceship, enemy, and power-up images
SPACESHIP_IMG = pygame.image.load(ROOT_DIR+"\\spaceship.png")
ENEMY_IMG = pygame.image.load(ROOT_DIR+"\\enemy.png")
POWER_UP_IMG = pygame.image.load(ROOT_DIR+"\\powerup.png")

# Resize the images to smaller sizes
SPACESHIP_IMG = pygame.transform.scale(SPACESHIP_IMG, (50, 50))  # Space ship 50x50
ENEMY_IMG = pygame.transform.scale(ENEMY_IMG, (40, 40))  # Enemy 40x40
POWER_UP_IMG = pygame.transform.scale(POWER_UP_IMG, (30, 30))  # Power-up 30x30

# Spaceship class
class Spaceship:
    def __init__(self):
        self.image = SPACESHIP_IMG
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.speed = 5
        self.health = 3
        self.bullets = []
        self.double_bullet = False  # Power-up flag
        self.shield = False  # Shield power-up flag
        self.shield_timer = 0  # Timer for shield effect
        self.double_bullet_timer = 0  # Timer for double bullet effect

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def shoot(self):
        if self.double_bullet:
            self.bullets.append(Bullet(self.rect.centerx - 10, self.rect.top))
            self.bullets.append(Bullet(self.rect.centerx + 10, self.rect.top))
        else:
            self.bullets.append(Bullet(self.rect.centerx, self.rect.top))

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.shield:
            # Draw a blue circle around the spaceship if shield is active
            pygame.draw.circle(surface, BLUE, self.rect.center, self.rect.width // 2 + 5, 2)
        for bullet in self.bullets:
            bullet.draw(surface)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)

    def take_damage(self):
        if self.shield:
            # Shield prevents damage
            return True
        self.health -= 1
        if self.health <= 0:
            return False
        return True

    def update_power_up_timers(self):
        if self.shield_timer > 0:
            self.shield_timer -= 1
        else:
            self.shield = False
        
        if self.double_bullet_timer > 0:
            self.double_bullet_timer -= 1
        else:
            self.double_bullet = False

# Bullet class
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 5, y, 10, 20)
        self.speed = -10

    def move(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)

# Enemy class
class Enemy:
    def __init__(self):
        self.image = ENEMY_IMG
        self.rect = self.image.get_rect(
            center=(random.randint(0, WIDTH), random.randint(-100, -40))
        )
        self.speed = random.randint(3, 6)

    def move(self):
        self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Power-up class
class PowerUp:
    def __init__(self):
        self.image = POWER_UP_IMG
        self.rect = self.image.get_rect(
            center=(random.randint(0, WIDTH), random.randint(-100, -40))
        )
        self.type = random.choice(["double_bullet", "shield"])

    def move(self):
        self.rect.y += 3

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Main function
def main():
    running = True
    spaceship = Spaceship()
    enemies = [Enemy() for _ in range(5)]
    power_ups = []
    score = 0

    font = pygame.font.SysFont(None, 30)  # Reduced font size to fit the game window

    while running:
        screen.fill(WHITE)
        keys = pygame.key.get_pressed()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                spaceship.shoot()

        # Spawn power-ups randomly
        if random.random() < 0.01:
            power_ups.append(PowerUp())

        # Update spaceship and bullets
        spaceship.move(keys)
        spaceship.update_bullets()

        # Update enemies
        for enemy in enemies[:]:
            enemy.move()
            if enemy.rect.top > HEIGHT:
                enemies.remove(enemy)
                enemies.append(Enemy())
            if enemy.rect.colliderect(spaceship.rect):
                if not spaceship.take_damage():
                    print("Game Over!")
                    running = False
            for bullet in spaceship.bullets:
                if enemy.rect.colliderect(bullet.rect):
                    spaceship.bullets.remove(bullet)
                    enemies.remove(enemy)
                    enemies.append(Enemy())
                    score += 1

        # Update power-ups
        for power_up in power_ups[:]:
            power_up.move()
            if power_up.rect.colliderect(spaceship.rect):
                if power_up.type == "double_bullet":
                    spaceship.double_bullet = True
                    spaceship.double_bullet_timer = 300  # lasts for 300 frames
                elif power_up.type == "shield":
                    spaceship.shield = True
                    spaceship.shield_timer = 300  # lasts for 300 frames
                power_ups.remove(power_up)

        # Update power-up timers
        spaceship.update_power_up_timers()

        # Draw everything
        spaceship.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for power_up in power_ups:
            power_up.draw(screen)

        # Display score and health
        score_text = font.render(f"Score: {score}", True, BLACK)
        health_text = font.render(f"Health: {spaceship.health}", True, RED)
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 40))

        # Display power-up timers
        if spaceship.shield:
            shield_time_text = font.render(f"Shield: {spaceship.shield_timer // FPS} sec", True, GREEN)
            screen.blit(shield_time_text, (WIDTH - 150, 10))
        
        if spaceship.double_bullet:
            double_bullet_time_text = font.render(f"Double Bullet: {spaceship.double_bullet_timer // FPS} sec", True, YELLOW)
            screen.blit(double_bullet_time_text, (WIDTH - 200, 40))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
