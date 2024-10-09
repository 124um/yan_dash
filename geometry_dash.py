import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen settings
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("yan dash")

# Clock for controlling the frame rate
clock = pygame.time.Clock()
fps = 60

# Colors
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
black = (0, 0, 0)
blue = (0, 0, 255)

# Player settings
player_width, player_height = 50, 50
player_x = screen_width // 3  # Fixed horizontal position for the player
player_y = screen_height - player_height - 50  # Initial vertical position
jump_force = 20
gravity = 1
player_velocity_y = 0
is_jumping = False
is_alive = True

# Camera settings
camera_offset = 0
scroll_speed = 5  # Speed at which the camera moves to the right

# Level settings
tile_size = 50
level_data = []
current_level = 1

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
state = MENU

# Load the background image for the game
background = pygame.image.load('./resources/bg.webp').convert()
background = pygame.transform.scale(background, (screen_width, screen_height))

# Load the menu background image
menu_background = pygame.image.load('./resources/bg_m.png').convert()
menu_background = pygame.transform.scale(menu_background, (screen_width, screen_height))

# Load the player image
player_image = pygame.image.load('./resources/player.webp').convert_alpha()
player_image = pygame.transform.scale(player_image, (player_width, player_height))

def load_level(level_number):
    """Load the level data based on the level number."""
    global player_y, level_data
    level_data.clear()
    file_name = f'./levels/level-{level_number}.txt'
    try:
        with open(file_name, 'r') as file:
            for y, line in enumerate(file):
                row = []
                for x, char in enumerate(line.strip()):
                    if char == '#':
                        row.append('ground')
                    elif char == 'D':
                        row.append('danger')
                    elif char == 'p':
                        player_y = y * tile_size
                        row.append('empty')
                    else:
                        row.append('empty')
                level_data.append(row)
    except FileNotFoundError:
        print(f"Level {level_number} not found. Returning to menu.")
        global state
        state = MENU

def reset_game():
    """Reset the game to its initial state."""
    global player_y, player_velocity_y, is_jumping, is_alive, camera_offset, state
    player_y = screen_height - player_height - 50
    player_velocity_y = 0
    is_jumping = False
    is_alive = True
    camera_offset = 0
    state = PLAYING
    load_level(current_level)

# Main menu function
def main_menu():
    # Draw the menu background
    screen.blit(menu_background, (0, 0))
    font = pygame.font.Font(None, 74)
    new_game_text = font.render("New Game (1)", True, white)
    restart_text = font.render("Restart (2)", True, white)
    next_level_text = font.render("Next Level (3)", True, white)

    screen.blit(new_game_text, (screen_width // 4, screen_height // 4))
    screen.blit(restart_text, (screen_width // 4, screen_height // 2))
    screen.blit(next_level_text, (screen_width // 4, 3 * screen_height // 4))

    pygame.display.flip()

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == MENU:
                if event.key == pygame.K_1:  # New Game
                    current_level = 1
                    reset_game()
                elif event.key == pygame.K_2:  # Restart
                    reset_game()
                elif event.key == pygame.K_3:  # Next Level
                    current_level += 1
                    reset_game()
            elif state == GAME_OVER:
                if event.key == pygame.K_r:  # Restart from the current level
                    reset_game()

    # Game logic based on the current state
    if state == MENU:
        main_menu()
    elif state == PLAYING:
        # Player input and game mechanics
        if is_alive:
            # Get keys pressed
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not is_jumping:  # Jump only if not already jumping
                player_velocity_y = -jump_force
                is_jumping = True

            # Apply gravity
            player_velocity_y += gravity
            player_y += player_velocity_y

            # Check for collisions
            player_on_ground = False
            for y, row in enumerate(level_data):
                for x, tile in enumerate(row):
                    tile_rect = pygame.Rect(x * tile_size - camera_offset, y * tile_size, tile_size, tile_size)
                    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

                    if tile == 'ground' and player_rect.colliderect(tile_rect):
                        # Collision with the ground, place the player on top
                        if player_velocity_y > 0:  # Falling down
                            player_y = tile_rect.top - player_height
                            player_velocity_y = 0
                            is_jumping = False
                            player_on_ground = True

                    elif tile == 'danger' and player_rect.colliderect(tile_rect):
                        # Collision with a dangerous tile, player dies
                        is_alive = False
                        state = GAME_OVER

            # If player is not on any ground, make them fall
            if not player_on_ground:
                is_jumping = True

            # Update the camera offset to move continuously to the right
            camera_offset += scroll_speed

        # Update the screen
        screen.blit(background, (0, 0))  # Draw the background

        # Draw the level
        for y, row in enumerate(level_data):
            for x, tile in enumerate(row):
                if tile == 'ground':
                    # Draw ground at the specified positions
                    pygame.draw.rect(screen, green, (x * tile_size - camera_offset, y * tile_size, tile_size, tile_size))
                elif tile == 'danger':
                    # Draw dangerous tiles as black
                    pygame.draw.rect(screen, black, (x * tile_size - camera_offset, y * tile_size, tile_size, tile_size))

        # Draw the player (if alive)
        if is_alive:
            # Draw the player image instead of a rectangle
            screen.blit(player_image, (player_x, player_y))

        pygame.display.flip()  # Update the display

    elif state == GAME_OVER:
        # Display "Game Over" message
        screen.fill(black)
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over - Press R to Restart", True, red)
        screen.blit(text, (screen_width // 8, screen_height // 3))
        pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()
