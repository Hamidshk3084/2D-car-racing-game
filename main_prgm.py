import random
import pygame
import time
import os
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

width = 840
height = 650

# Set up the display
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height))

# Setting the caption for the window
pygame.display.set_caption("Basic Pygame Setup")

# Load background images
bg = pygame.image.load('assets/bg-1.png').convert_alpha()  # Game background
menu_bg = pygame.image.load('assets/menu_bg.png').convert_alpha()  # Main menu background




# Load and play background music
pygame.mixer.music.load("assets/bg_sound.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=-1)

#load collision effect
collision_sound = pygame.mixer.Sound('assets/crash_sound.mp3')




# Background positions
Bg_y1 = 0
Bg_y2 = -height

# Background speed
bg_speed = 6

# Score
score = 0
# Initialize high score
high_score = 0


# File to store the high score
high_score_file = "high_score.txt"

# Function to load high score from file
def load_high_score():
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as file:
            try:
                return int(file.read().strip())
            except ValueError:
                return 0  # If the file is empty or corrupt, return 0
    return 0  # If the file doesn't exist, return 0

# Function to save high score to file
def save_high_score(high_score):
    with open(high_score_file, "w") as file:
        file.write(str(high_score))

# Initialize high score by loading from file
high_score = load_high_score()

# Update high score if the current score is higher
def update_high_score(score):
    global high_score
    if score > high_score:
        high_score = score
        save_high_score(high_score)

# Movement variables
car_speed = 4.5

# Initialize font
font = pygame.font.SysFont(None, 48)
large_font = pygame.font.SysFont(None, 100)

# Load images for the player, enemies, coin, etc.
player = pygame.image.load('assets/nww.png').convert_alpha()
player_x = 430
player_y = 500
player_rect = player.get_rect(midtop=(player_x, player_y))
player_mask = pygame.mask.from_surface(player)

coin = pygame.image.load('assets/coin2.png').convert_alpha()
coin_rect = coin.get_rect(topleft=(520, 40))
coin_mask = pygame.mask.from_surface(coin)

cop = pygame.image.load('assets/van.png').convert_alpha()
cop_rect = cop.get_rect(topleft=(600, 0))
cop_mask = pygame.mask.from_surface(cop)

enemy = pygame.image.load('assets/npcc.png').convert_alpha()
enemy_rect = enemy.get_rect(topleft=(250, 50))
enemy_mask = pygame.mask.from_surface(enemy)

# Load the pause button image
pause_button = pygame.image.load('assets/pause.png').convert_alpha()
pause_button_rect = pause_button.get_rect(topleft=(10, 10))

# Game state variable
paused = False

# Button Class Definition
class Button:
    def __init__(self, x, y, width, height, text, font, bg_color, text_color, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color if hover_color else bg_color
        self.hovered = False

    def draw(self, screen):
        # Change color on hover
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.hovered = True
            color = self.hover_color
        else:
            self.hovered = False
            color = self.bg_color

        pygame.draw.rect(screen, color, self.rect)

        # Render the text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            return True
        return False

# Function to reset position to avoid collisions
def reset_position(obj_rect, other_rects):
    obj_rect.x = random.randint(120, 650)
    obj_rect.y = 0
    while any(obj_rect.colliderect(other) for other in other_rects):
        obj_rect.x = random.randint(120, 650)

# Coin and player collision
def check_pixel_collision(player_rect, player_mask, coin_rect, coin_mask):
    global score
    offset = (coin_rect.x - player_rect.x, coin_rect.y - player_rect.y)
    collision_point = player_mask.overlap(coin_mask, offset)
    if collision_point:
        score += 2
        reset_position(coin_rect, [player_rect, enemy_rect])
        print(f"Score: {score}")

# Player collision with barrier or enemy
def check_player_collision(player_rect, player_mask, obstacle_rect, obstacle_mask):
    offset = (obstacle_rect.x - player_rect.x, obstacle_rect.y - player_rect.y)
    collision_point = player_mask.overlap(obstacle_mask, offset)
    return collision_point

# Function to display the pause button
def render_pause_button(screen):
    screen.blit(pause_button, pause_button_rect)

# Function to handle pause functionality
def toggle_pause():
    global paused
    paused = not paused
    if paused:
        # Render "Paused" text when the game is paused
        paused_text = large_font.render("PAUSED", True, (255, 255, 255))
        screen.blit(paused_text, (width // 2 - paused_text.get_width() // 2, height // 2 - paused_text.get_height() // 2))
        pygame.display.update()
        # Wait until unpaused
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and pause_button_rect.collidepoint(event.pos):
                    toggle_pause()
            clock.tick(30)  # Limit the loop speed during pause

# Function to display score
def render_score(screen, score):
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
    screen.blit(score_text, (width - score_text.get_width() - 10, 10))
    screen.blit(high_score_text, (width - high_score_text.get_width() - 10, 10 + score_text.get_height() + 5))

# Render "GAME OVER" screen with buttons
def render_wasted(screen):
    # Display "GAME OVER" text
    wasted_text = large_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(wasted_text, (width // 2 - wasted_text.get_width() // 2, height // 2 - wasted_text.get_height() // 2 - 100))

    # Define button dimensions and positions
    button_width = 200
    button_height = 70

    # Play Again button
    play_again_button = Button(
        x=width // 2 - button_width // 2,
        y=height // 2,
        width=button_width,
        height=button_height,
        text="Play Again",
        font=font,
        bg_color=(0, 255, 0),
        text_color=(255, 255, 255),
        hover_color=(0, 200, 0)  # Darker green on hover
    )

    # Quit button
    quit_button = Button(
        x=width // 2 - button_width // 2,
        y=height // 2 + button_height + 20,
        width=button_width,
        height=button_height,
        text="Quit",
        font=font,
        bg_color=(255, 0, 0),
        text_color=(255, 255, 255),
        hover_color=(200, 0, 0)  # Darker red on hover
    )

    # Game over loop for handling button clicks
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.is_clicked(event):
                    game_loop()  # Restart the game
                    return  # Exit the game over screen
                elif quit_button.is_clicked(event):
                    pygame.quit()
                    sys.exit()

        # Draw the buttons on the screen
        play_again_button.draw(screen)
        quit_button.draw(screen)

        
        # Render high score below the quit button
        high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
        high_score_rect = high_score_text.get_rect(center=(width // 2, quit_button.rect.bottom + 50))
        screen.blit(high_score_text, high_score_rect)

        pygame.display.update()
        clock.tick(30)


# Main Menu Function
def main_menu():
    menu_running = True

    # Define button dimensions and positions
    button_width = 200
    button_height = 70
    play_button = Button(
        x=width // 2 - button_width // 2,
        y=height // 2 - 50,
        width=button_width,
        height=button_height,
        text="PLAY",
        font=font,
        bg_color=(0, 255, 0),
        text_color=(255, 255, 255),
        hover_color=(0, 200, 0)  # Darker green on hover
    )

    quit_button = Button(
        x=width // 2 - button_width // 2,
        y=height // 2 + 50,
        width=button_width,
        height=button_height,
        text="QUIT",
        font=font,
        bg_color=(255, 0, 0),
        text_color=(255, 255, 255),
        hover_color=(200, 0, 0)  # Darker red on hover
    )

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.is_clicked(event):
                    menu_running = False  # Start the game
                elif quit_button.is_clicked(event):
                    pygame.quit()
                    sys.exit()

        # Draw the menu background
        screen.blit(menu_bg, (0, 0))

        # Draw buttons
        play_button.draw(screen)
        quit_button.draw(screen)

        # Render high score below the quit button
        high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
        high_score_rect = high_score_text.get_rect(center=(width // 2, quit_button.rect.bottom + 50))
        screen.blit(high_score_text, high_score_rect)

        pygame.display.update()
        clock.tick(30)

# Main Game Loop
def game_loop():
    global score, Bg_y1, Bg_y2, player_rect, enemy_rect, coin_rect, cop_rect
    score = 0
    Bg_y1 = 0
    Bg_y2 = -height
    player_rect.x = 430
    player_rect.y = 500
    enemy_rect.x = 250
    enemy_rect.y = 0
    coin_rect.x = 520
    coin_rect.y = 0
    cop_rect.x = 600
    cop_rect.y = 0

    running = True
    while running:
        # rest of your game loop code
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and pause_button_rect.collidepoint(event.pos):
                toggle_pause()

        # Movement and game logic here
        # Movement of the player and adding border to the movement of the player's car
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 105:
            player_rect.x -= car_speed
        if keys[pygame.K_RIGHT] and player_rect.right < 728:
            player_rect.x += car_speed
        if keys[pygame.K_UP] and player_rect.top > 200:
            player_rect.y -= car_speed
        if keys[pygame.K_DOWN] and player_rect.bottom < height:
            player_rect.y += car_speed

        # Move the background down
        Bg_y1 += bg_speed
        Bg_y2 += bg_speed

        # Reset the background positions to create a seamless loop
        if Bg_y1 >= height:
            Bg_y1 = -height
        if Bg_y2 >= height:
            Bg_y2 = -height

        # Fill the screen with the scrolling background
        screen.blit(bg, (0, Bg_y1))
        screen.blit(bg, (0, Bg_y2))

        # Player
        screen.blit(player, player_rect)

        # Enemy Movement
        enemy_rect.y += 3
        if enemy_rect.y > height:
            enemy_rect.y = 0
            reset_position(enemy_rect, [coin_rect, cop_rect])
        screen.blit(enemy, enemy_rect)

        # Coin Movement
        coin_rect.y += 3
        if coin_rect.y > height:
            coin_rect.y = 0
            reset_position(coin_rect, [enemy_rect, cop_rect])
        screen.blit(coin, coin_rect)

        # Cop Movement
        cop_rect.y += 3
        if cop_rect.y > height:
            cop_rect.y = 0
            reset_position(cop_rect, [coin_rect, enemy_rect])
        screen.blit(cop, cop_rect)

        # Check collisions
        check_pixel_collision(player_rect, player_mask, coin_rect, coin_mask)

        # Check for collision between player and enemy or cop
        if (check_player_collision(player_rect, player_mask, enemy_rect, enemy_mask) or
                check_player_collision(player_rect, player_mask, cop_rect, cop_mask)):
            # Play the collision sound
            collision_sound.play()
            render_wasted(screen)

        # Update high score based on current score
        update_high_score(score)
        # Render score
        render_score(screen, score)
        # Render pause button
        render_pause_button(screen)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

# Run the main menu first
main_menu()

# Then start the game loop
game_loop()
