import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_COLOR = BLUE
PLAYER_SPEED = 5
PLAYER_JUMP_HEIGHT = 15  # Increased jump height

# Gravity
GRAVITY = 1

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Italian Plumber Game")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join("stuff","italian_plumber.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT
        self.change_x = 0
        self.change_y = 0
        self.on_ground = False
        self.jumps = 0

    def update(self, obstacles):
        self.calc_grav()
        self.rect.x += self.change_x

        # Check for collisions with walls
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        # Check for collisions with obstacles (horizontal)
        collision_list = pygame.sprite.spritecollide(self, obstacles, False)
        for obstacle in collision_list:
            if self.change_x > 0:  # Moving right
                self.rect.right = obstacle.rect.left
            elif self.change_x < 0:  # Moving left
                self.rect.left = obstacle.rect.right

        self.rect.y += self.change_y

        # Check for collisions with the ground
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.change_y = 0
            self.on_ground = True
            self.jumps = 0

        # Check for collisions with obstacles (vertical)
        self.on_ground = False  # Assume the player is not on the ground
        collision_list = pygame.sprite.spritecollide(self, obstacles, False)
        for obstacle in collision_list:
            if self.change_y > 0:  # Falling down
                self.rect.bottom = obstacle.rect.top
                self.change_y = 0
                self.on_ground = True
                self.jumps = 0
            elif self.change_y < 0:  # Jumping up
                self.rect.top = obstacle.rect.bottom
                self.change_y = 0

    def calc_grav(self):
        if not self.on_ground:
            self.change_y += GRAVITY
        else:
            self.change_y = 0

    def jump(self):
        if self.on_ground or self.jumps < 2:
            self.change_y = -PLAYER_JUMP_HEIGHT
            self.on_ground = False
            self.jumps += 1

    def move_left(self):
        self.change_x = -PLAYER_SPEED

    def move_right(self):
        self.change_x = PLAYER_SPEED

    def stop(self):
        self.change_x = 0

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Star class
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.change_x = 2  # Speed of the star

    def update(self, *args):
        self.rect.x += self.change_x
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.change_x *= -1  # Reverse direction

# Monster class
class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=2):
        super().__init__()
        self.image = pygame.image.load(os.path.join("stuff","mushroom.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))  # Decreased size
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.change_x = speed  # Speed of the monster

    def update(self, *args):
        self.rect.x += self.change_x
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.change_x *= -1  # Reverse direction

# Princess class
class Princess(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join("stuff","princess.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def display_message(screen, message, color=RED):
    font = pygame.font.Font(None, 74)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

def initialize_level(level):
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    monsters = pygame.sprite.Group()
    princess = None  # Initialize princess to None

    if level == 1:
        # Create obstacles
        obstacle_positions = [(100, 500), (200, 450), (250, 200), (400, 400), (200, 350), (100, 300), (500, 250), (700, 200)]
        for pos in obstacle_positions:
            obstacle = Obstacle(pos[0], pos[1], 100, 20)
            all_sprites.add(obstacle)
            obstacles.add(obstacle)
        # Create stars above the obstacles
        for pos in obstacle_positions:
            star = Star(pos[0] + 40, pos[1] - 30)  # Adjust position to be above the obstacle
            all_sprites.add(star)
            stars.add(star)
        # Create monsters
        monster_positions = [(200, 550), (400, 450), (600, 350)]
        for pos in monster_positions:
            monster = Monster(pos[0], pos[1], speed=2)
            all_sprites.add(monster)
            monsters.add(monster)
        # Create princess
        princess = Princess(750, 150)
        all_sprites.add(princess)

    elif level == 2:
        # Create stairs that change direction
        obstacle_positions = [(100, 500), (200, 450), (250, 200), (400, 400), (200, 350), (100, 300), (500, 250), (700, 200)]
        direction = 1  # 1 for right, -1 for left
        for i, pos in enumerate(obstacle_positions):
            if i % 4 == 0:
                direction *= -1
            obstacle = Obstacle(pos[0], pos[1], 100, 20)
            all_sprites.add(obstacle)
            obstacles.add(obstacle)
        # Create stars above the obstacles
        for pos in obstacle_positions:
            star = Star(pos[0] + 40, pos[1] - 30)  # Adjust position to be above the obstacle
            all_sprites.add(star)
            stars.add(star)
        # Create faster monsters
        monster_positions = [(200, 550), (400, 450), (600, 350)]
        for pos in monster_positions:
            monster = Monster(pos[0], pos[1], speed=4)  # Faster monsters
            all_sprites.add(monster)
            monsters.add(monster)
        # Create princess
        princess = Princess(750, 250)
        all_sprites.add(princess)

    return all_sprites, obstacles, stars, monsters, princess

def main(level=1, deaths=0, points=0):
    # Initialize counters

    # Create player
    player = Player()
    all_sprites, obstacles, stars, monsters, princess = initialize_level(level)
    all_sprites.add(player)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    player.move_left()
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    player.move_right()
                elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    player.jump()
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a) and player.change_x < 0:
                    player.stop()
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and player.change_x > 0:
                    player.stop()

        # Update all sprites
        all_sprites.update(obstacles)

        # Check for collisions with stars
        stars_collected = pygame.sprite.spritecollide(player, stars, True)
        if stars_collected:
            points += len(stars_collected)
            print(f"Collected {len(stars_collected)} star(s)! Total points: {points}")

        # Check for collisions with monsters
        if pygame.sprite.spritecollideany(player, monsters):
            deaths += 1
            print(f"Player touched a monster! Game Over! Total deaths: {deaths}")
            display_message(screen, "Game Over! Press R to Restart", color=BLUE)
            waiting_for_restart = True
            while waiting_for_restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            main(level, deaths)  # Restart the game with updated deaths count
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()

        # Check for collision with princess
        if pygame.sprite.collide_rect(player, princess):
            if level < 2:
                display_message(screen, "Level Complete! Press R for Next Level", color=BLUE)
                waiting_for_next_level = True
                while waiting_for_next_level:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                main(level + 1, deaths, points)  # Start the next level
                            elif event.key == pygame.K_q:
                                pygame.quit()
                                sys.exit()
            else:
                display_message(screen, "You Win! Press R to Restart", color=BLUE)
                waiting_for_restart = True
                while waiting_for_restart:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                main(1, deaths, points)  # Restart the game from level 1
                            elif event.key == pygame.K_q:
                                pygame.quit()
                                sys.exit()

        # Draw everything
        screen.fill(WHITE)
        all_sprites.draw(screen)

        # Display points, deaths, and level
        font = pygame.font.Font(None, 36)
        points_text = font.render(f"Points: {points}", True, GREEN)
        deaths_text = font.render(f"Deaths: {deaths}", True, RED)
        level_text = font.render(f"Level: {level}" + "/2", True, BLUE)
        screen.blit(points_text, (10, 10))
        screen.blit(deaths_text, (10, 50))
        screen.blit(level_text, (10, 90))

        # Flip the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Start the game
main()