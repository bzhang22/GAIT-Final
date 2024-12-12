import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 600  # New size of the window (600x600 pixels)
GRID_SIZE = 32     # Grid is 32x32
CELL_SIZE = WINDOW_SIZE // GRID_SIZE  # Size of each cell
FPS = 60           # Frames per second

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)  # Brown for walls
YELLOW = (255, 255, 0)
GREY = (211, 211, 211)  # Light grey for text backgrounds

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Chase Game with Battle Transition")

# Music
pygame.mixer.init()
overworld_music = r"./sound/Main game.mp3"
battle_music = r"./sound/Main battle.mp3"
final_boss_music = r"./sound/Battle music.mp3"
current_music = None

# Play music function
def play_music(track):
    global current_music
    if current_music != track:
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            current_music = track
        except pygame.error as e:
            print(f"Error loading music file {track}: {e}")

play_music(overworld_music)  # Start with overworld music

# Sprite position (grid coordinates)
sprite_x, sprite_y = 0, 0

# Walls
walls = set()

# Add grouped walls manually
for wx in range(10, 13):
    for wy in range(4, 7):
        walls.add((wx, wy))

for wx in range(23, 27):
    for wy in range(11, 15):
        walls.add((wx, wy))

for wx in range(20, 24):
    for wy in range(16, 20):
        walls.add((wx, wy))

for wx in range(16, 19):
    for wy in range(18, 21):
        walls.add((wx, wy))

for wx in range(10, 14):
    for wy in range(21, 24):
        walls.add((wx, wy))

for wx in range(9, 12):
    for wy in range(29, 32):
        walls.add((wx, wy))

for wx in range(20, 23):
    for wy in range(28, 32):
        walls.add((wx, wy))

for wx in range(18, 20):
    for wy in range(0, 8):
        walls.add((wx, wy))

for wx in range(20, 27):
    for wy in range(7, 9):
        walls.add((wx, wy))

for wx in range(29, 33):
    for wy in range(7, 9):
        walls.add((wx, wy))

# Load and resize images
def load_and_resize_image(path, width, height):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, (width, height))

background_image = load_and_resize_image(r"./images/Overworldmap.png", WINDOW_SIZE, WINDOW_SIZE)
fight_background_image = load_and_resize_image(r"./images/Forest background.png", WINDOW_SIZE, WINDOW_SIZE)
final_boss_background_image = load_and_resize_image(r"./images/Mountain background.png", WINDOW_SIZE, WINDOW_SIZE)
player_image = load_and_resize_image(r"./images/mainguy.png", CELL_SIZE * 2, CELL_SIZE * 2)
enemy_images = {
    "common": load_and_resize_image(r"./images/Gobby-4.png", CELL_SIZE * 2, CELL_SIZE * 2),
    "tough": load_and_resize_image(r"./images/Skelly-2.png", CELL_SIZE * 2, CELL_SIZE * 2),
    "elite": load_and_resize_image(r"./images/KING CROC-2.png", CELL_SIZE * 2, CELL_SIZE * 2),
    "boss": load_and_resize_image(r"./images/Dragon #2-2.png", CELL_SIZE * 4, CELL_SIZE * 4)
}

# HD versions of images for battle screen
player_image_hd = load_and_resize_image(r"./images/mainguy_hd.png", 200, 200)
enemy_images_hd = {
    "common": load_and_resize_image(r"./images/Gobby-4_hd.png", 200, 200),
    "tough": load_and_resize_image(r"./images/Skelly-2_hd.png", 200, 200),
    "elite": load_and_resize_image(r"./images/KING CROC-2_hd.png", 225, 225),
    "boss": load_and_resize_image(r"./images/Dragon #2-2.png", 250, 250)
}

# Enemy data
ENEMY_TYPES = {
    "common": {"health": 10, "attack": 2, "xp": 5},
    "tough": {"health": 20, "attack": 4, "xp": 10},
    "elite": {"health": 30, "attack": 6, "xp": 20},
    "boss": {"health": 50, "attack": 10, "xp": 100}
}

def spawn_box_at(x, y):
    walls.add((x, y))

# Add grouped walls manually
for wx in range(1, 5):
    for wy in range(21, 24):
        spawn_box_at(wx, wy)

enemies = []
# Common enemies: 16-21 tiles down, 1-14 tiles to the right
for _ in range(4):
    ex, ey = random.randint(1, 14), random.randint(16, 18)
    if (ex, ey) not in walls:
        enemies.append({"type": "common", "x": ex, "y": ey, "health": ENEMY_TYPES["common"]["health"]})

# Tough enemies: 5-8 tiles up from the bottom, 6-17 tiles from the left
for _ in range(3):
    ex, ey = random.randint(6, 16), random.randint(GRID_SIZE - 8, GRID_SIZE - 5)
    if (ex, ey) not in walls:
        enemies.append({"type": "tough", "x": ex, "y": ey, "health": ENEMY_TYPES["tough"]["health"]})

# Elite enemies: 11-22 tiles up from the bottom, 28-31 tiles from the right
for _ in range(2):
    ex, ey = random.randint(GRID_SIZE - 3, GRID_SIZE - 1), random.randint(GRID_SIZE - 22, GRID_SIZE - 11)
    if (ex, ey) not in walls:
        enemies.append({"type": "elite", "x": ex, "y": ey, "health": ENEMY_TYPES["elite"]["health"]})

# Boss enemy: 3 tiles down, 26 tiles to the right
enemies.append({"type": "boss", "x": 26, "y": 3, "health": ENEMY_TYPES["boss"]["health"]})

# Battle variables
player_health = 20
player_max_health = 20
player_damage = 3
player_mana = 10
player_max_mana = 10
player_xp = 0
xp_needed = 5
player_level = 1
battle_mode = False
player_action = None
current_enemy = None
mana_warning = False


def draw_xp_bar():
    """Draw the XP bar."""
    bar_width = 200
    bar_height = 20
    x = 100
    y = 10
    pygame.draw.rect(screen, YELLOW, (x, y, bar_width, bar_height), 2)  # Yellow outline
    filled_width = int(bar_width * (player_xp / xp_needed))
    pygame.draw.rect(screen, YELLOW, (x, y, filled_width, bar_height))

def draw_battle_screen():
    """Draw the battle screen."""
    global mana_warning

    if current_enemy["type"] == "boss":
        play_music(final_boss_music)
        screen.blit(final_boss_background_image, (0, 0))
    else:
        play_music(battle_music)
        screen.blit(fight_background_image, (0, 0))

    # Draw the player
    player_rect = pygame.Rect(100, 200, 240, 240)
    screen.blit(player_image_hd, player_rect)

    # Draw the enemy
    enemy_type = current_enemy["type"]
    if enemy_type == "boss":
        enemy_rect = pygame.Rect(350, 150, 480, 480)
    else:
        enemy_rect = pygame.Rect(350, 200, 240, 240)
    screen.blit(enemy_images_hd[enemy_type], enemy_rect)

    # Draw a background for text
    text_bg_rect = pygame.Rect(50, 400, 500, 200)
    pygame.draw.rect(screen, GREY, text_bg_rect)
    pygame.draw.rect(screen, BLACK, text_bg_rect, 2)  # Border

    # Draw text to indicate a battle
    font = pygame.font.Font(None, 50)
    battle_text = font.render("Battle!", True, BLACK)
    screen.blit(battle_text, (WINDOW_SIZE // 2 - battle_text.get_width() // 2, 420))

    # Draw health bars and mana
    font_small = pygame.font.Font(None, 30)
    player_health_text = font_small.render(f"HP: {player_health}/{player_max_health}", True, BLACK)
    screen.blit(player_health_text, (70, 450))

    enemy_health_text = font_small.render(f"Enemy HP: {current_enemy['health']}", True, BLACK)
    screen.blit(enemy_health_text, (70, 480))

    player_mana_text = font_small.render(f"Mana: {player_mana}/{player_max_mana}", True, BLACK)
    screen.blit(player_mana_text, (70, 510))

    # Menu for player actions
    action_text_lines = [
        "Space: Basic Attack",
        "S: Special Attack                  R: Run Away"
    ]
    for i, line in enumerate(action_text_lines):
        action_text = font_small.render(line, True, BLACK)
        screen.blit(action_text, (70, 540 + i * 30))

    # Display mana warning
    if mana_warning:
        warning_text = font_small.render("Out of Mana!", True, BLACK)
        screen.blit(warning_text, (WINDOW_SIZE // 2 - warning_text.get_width() // 2, 600))
        mana_warning = False

def handle_battle():
    """Handle the player's actions in battle."""
    global player_health, player_mana, player_xp, battle_mode, sprite_x, sprite_y, current_enemy, mana_warning
    global player_max_health, player_max_mana, player_damage, player_level, xp_needed

    if player_action == "basic_attack":
        # Basic attack
        current_enemy["health"] -= player_damage
    elif player_action == "special_attack":
        if player_mana >= 3:
            # Special attack
            current_enemy["health"] -= player_damage + 2
            player_mana -= 3
        else:
            mana_warning = True
            return
    elif player_action == "run_away":
        # Run away
        play_music(overworld_music)
        battle_mode = False
        return

    # Enemy's turn to attack
    if current_enemy["health"] > 0:
        player_health -= ENEMY_TYPES[current_enemy["type"]]["attack"]

    # Check if battle is over
    if player_health <= 0:
        print("You lost the game!")
        pygame.quit()
        sys.exit()

    if current_enemy["health"] <= 0:
        player_xp += ENEMY_TYPES[current_enemy["type"]]["xp"]
        if current_enemy["type"] == "boss":
            print("You win!")
            pygame.quit()
            sys.exit()

        enemies.remove(current_enemy)
        play_music(overworld_music)
        battle_mode = False

        # Level up check
        if player_xp >= xp_needed:
            player_level += 1
            player_xp = 0
            xp_needed += 5
            player_max_health += 10
            player_max_mana += 5
            player_damage += 2
            player_health = player_max_health
            player_mana = player_max_mana

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if battle_mode:
                if event.key == pygame.K_SPACE:
                    player_action = "basic_attack"
                    handle_battle()
                elif event.key == pygame.K_s:
                    player_action = "special_attack"
                    handle_battle()
                elif event.key == pygame.K_r:
                    player_action = "run_away"
                    handle_battle()
            else:
                # Move the sprite with arrow keys (when not in battle)
                if event.key == pygame.K_UP and sprite_y > 0 and all((sprite_x + dx, sprite_y - 1 + dy) not in walls for dx in range(2) for dy in range(2)):
                    sprite_y -= 1
                elif event.key == pygame.K_DOWN and sprite_y < GRID_SIZE - 2 and all((sprite_x + dx, sprite_y + 2 + dy) not in walls for dx in range(2) for dy in range(2)):
                    sprite_y += 1
                elif event.key == pygame.K_LEFT and sprite_x > 0 and all((sprite_x - 1 + dx, sprite_y + dy) not in walls for dx in range(2) for dy in range(2)):
                    sprite_x -= 1
                elif event.key == pygame.K_RIGHT and sprite_x < GRID_SIZE - 2 and all((sprite_x + 2 + dx, sprite_y + dy) not in walls for dx in range(2) for dy in range(2)):
                    sprite_x += 1

                # Check for collisions with enemies
                for enemy in enemies:
                    enemy_size = 2 if enemy["type"] != "boss" else 4
                    if sprite_x < enemy["x"] + enemy_size and sprite_x + 2 > enemy["x"] and sprite_y < enemy["y"] + enemy_size and sprite_y + 2 > enemy["y"]:
                        battle_mode = True
                        current_enemy = enemy

    # Clear the screen
    if battle_mode:
        draw_battle_screen()
    else:
        screen.blit(background_image, (0, 0))

        # Draw the walls (now invisible)
        for (wx, wy) in walls:
            wall_rect = pygame.Rect(wx * CELL_SIZE, wy * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        # Draw the sprite
        sprite_rect = pygame.Rect(sprite_x * CELL_SIZE, sprite_y * CELL_SIZE, CELL_SIZE * 2, CELL_SIZE * 2)
        screen.blit(player_image, sprite_rect)

        # Draw the enemies
        for enemy in enemies:
            size = CELL_SIZE * (2 if enemy["type"] != "boss" else 4)
            enemy_rect = pygame.Rect(enemy["x"] * CELL_SIZE, enemy["y"] * CELL_SIZE, size, size)
            scaled_enemy_image = pygame.transform.scale(enemy_images[enemy["type"]], (size, size))
            screen.blit(scaled_enemy_image, enemy_rect)

        # Draw the XP bar
        draw_xp_bar()

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()
