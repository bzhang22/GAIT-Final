import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 600  # Window size (600x600 pixels)
GRID_SIZE = 32     # Grid is 32x32
CELL_SIZE = WINDOW_SIZE // GRID_SIZE  # Size of each cell
FPS = 60           # Frames per second

# Colors (Corrected Definitions)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)          # Correct RGB for brown
YELLOW = (255, 255, 0)
GREY = (211, 211, 211)          # Correct RGB for light grey

# Enemy data
ENEMY_TYPES = {
    "common": {"health": 10, "attack": 2, "xp": 5},
    "tough": {"health": 20, "attack": 4, "xp": 10},
    "elite": {"health": 30, "attack": 6, "xp": 20},
    "boss": {"health": 50, "attack": 10, "xp": 100}
}

# Animation variables for player (Overworld and Battle)
player_overworld_scale = 1.0      # Scale factor for overworld animation
player_battle_scale = 1.0         # Scale factor for battle animation
player_animation_direction = 1    # 1 for expanding, -1 for contracting
player_animation_speed = 0.005     # Slower animation speed
player_scale_min = 0.95           # Minimum scale factor
player_scale_max = 1.05           # Maximum scale factor

# Enemy Animation Variables
enemy_animation_scales = {}       # Scale factors for each enemy type
enemy_animation_directions = {}   # Directions for each enemy type's animation
enemy_shake_flags = {}            # Flags to indicate if an enemy is shaking
enemy_shake_counters = {}         # Counters to manage shake duration

# Initialize enemy animation variables
for etype in ENEMY_TYPES.keys():
    enemy_animation_scales[etype] = 1.0
    enemy_animation_directions[etype] = 1
    enemy_shake_flags[etype] = False
    enemy_shake_counters[etype] = 0

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Chase Game with Battle Transition")

# Music setup
pygame.mixer.init()
overworld_music = r"./sound/Main game.mp3"
battle_music = r"./sound/Main battle.mp3"
final_boss_music = r"./sound/Battle music.mp3"
current_music = None

def play_music(track):
    """
    Plays the specified music track if it's not already playing.
    """
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

# Player Direction
facing_right = True  # Initially facing right

# Walls
walls = set()

def spawn_box_at(x, y):
    """
    Adds a wall at the specified grid coordinates.
    """
    walls.add((x, y))

# Add grouped walls manually
wall_groups = [
    (range(10, 13), range(4, 7)),
    (range(23, 27), range(11, 15)),
    (range(20, 24), range(16, 20)),
    (range(16, 19), range(18, 21)),
    (range(10, 14), range(21, 24)),
    (range(9, 12), range(29, 32)),
    (range(20, 23), range(28, 32)),
    (range(18, 20), range(0, 8)),
    (range(20, 27), range(7, 9)),
    (range(29, 33), range(7, 9)),
    (range(1, 5), range(21, 24))
]

for wx_range, wy_range in wall_groups:
    for wx in wx_range:
        for wy in wy_range:
            spawn_box_at(wx, wy)

# Load and resize images
def load_and_resize_image(path, width, height):
    """
    Loads an image from the specified path and resizes it to (width, height).
    """
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (width, height))
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")
        sys.exit()

background_image = load_and_resize_image(r"./images/Overworldmap.png", WINDOW_SIZE, WINDOW_SIZE)
fight_background_image = load_and_resize_image(r"./images/Forest background.png", WINDOW_SIZE, WINDOW_SIZE)
final_boss_background_image = load_and_resize_image(r"./images/Mountain background.png", WINDOW_SIZE, WINDOW_SIZE)
player_image_original = load_and_resize_image(r"./images/mainguy.png", CELL_SIZE * 2, CELL_SIZE * 2)
enemy_images_original = {
    "common": load_and_resize_image(r"./images/Gobby-4.png", CELL_SIZE * 2, CELL_SIZE * 2),
    "tough": load_and_resize_image(r"./images/Skelly-2.png", CELL_SIZE * 2, CELL_SIZE * 2),
    "elite": load_and_resize_image(r"./images/KING CROC-2.png", CELL_SIZE * 2, CELL_SIZE * 2),
    "boss": load_and_resize_image(r"./images/Dragon #2-2.png", CELL_SIZE * 4, CELL_SIZE * 4)
}

# Pre-scale enemy images for performance
enemy_images = {}
for etype, img in enemy_images_original.items():
    enemy_images[etype] = img

player_image = player_image_original  # Keep original for scaling

# Initialize enemies list
enemies = []

# Common enemies: 1-14 tiles to the right, 16-18 tiles down
for _ in range(4):
    ex, ey = random.randint(1, 14), random.randint(16, 18)
    if (ex, ey) not in walls:
        enemies.append({"type": "common", "x": ex, "y": ey, "health": ENEMY_TYPES["common"]["health"]})

# Tough enemies: 6-17 tiles from the left, 24-27 tiles down (since GRID_SIZE - 8 = 24)
for _ in range(3):
    ex, ey = random.randint(6, 16), random.randint(GRID_SIZE - 8, GRID_SIZE - 5)
    if (ex, ey) not in walls:
        enemies.append({"type": "tough", "x": ex, "y": ey, "health": ENEMY_TYPES["tough"]["health"]})

# Elite enemies: 28-31 tiles from the left (assuming GRID_SIZE=32, so positions 28-31), 10-21 tiles up from bottom
for _ in range(2):
    ex = random.randint(GRID_SIZE - 4, GRID_SIZE - 1)
    ey = random.randint(GRID_SIZE - 22, GRID_SIZE - 11)
    if (ex, ey) not in walls:
        enemies.append({"type": "elite", "x": ex, "y": ey, "health": ENEMY_TYPES["elite"]["health"]})

# Boss enemy: 26 tiles to the right, 3 tiles down
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
    """
    Draws the XP bar on the overworld screen.
    """
    bar_width = 200
    bar_height = 20
    x = 100
    y = 10
    pygame.draw.rect(screen, YELLOW, (x, y, bar_width, bar_height), 2)  # Yellow outline
    filled_width = int(bar_width * (player_xp / xp_needed))
    pygame.draw.rect(screen, YELLOW, (x, y, filled_width, bar_height))

def draw_battle_screen():
    """
    Draws the battle screen with player and enemy stats, including animations.
    """
    global mana_warning

    # Play appropriate music and set background
    if current_enemy["type"] == "boss":
        play_music(final_boss_music)
        screen.blit(final_boss_background_image, (0, 0))
    else:
        play_music(battle_music)
        screen.blit(fight_background_image, (0, 0))

    # Animate Player in Battle
    global player_battle_scale, player_animation_direction
    # Update player animation scale factors
    player_battle_scale += player_animation_direction * player_animation_speed

    # Reverse direction if limits are reached
    if player_battle_scale <= player_scale_min or player_battle_scale >= player_scale_max:
        player_animation_direction *= -1

    # Apply scaling to player image
    scaled_player_size = int(120 * player_battle_scale)
    scaled_player_image = pygame.transform.scale(player_image_original, (scaled_player_size, scaled_player_size))

    # Ensure player always faces right in battle mode
    final_player_image = scaled_player_image  # Always face right

    # Calculate offset to keep the player centered
    player_offset = (120 - scaled_player_size) // 2

    # Create player rect with adjusted position
    player_rect = pygame.Rect(100 + player_offset, 200 + player_offset, scaled_player_size, scaled_player_size)
    screen.blit(final_player_image, player_rect)

    # Animate Enemy in Battle
    enemy_type = current_enemy["type"]
    enemy_scale = enemy_animation_scales[enemy_type]
    enemy_dir = enemy_animation_directions[enemy_type]

    # Update enemy animation scale
    enemy_scale += enemy_dir * player_animation_speed  # Reuse player animation speed for consistency
    if enemy_scale <= player_scale_min or enemy_scale >= player_scale_max:
        enemy_animation_directions[enemy_type] *= -1
    enemy_animation_scales[enemy_type] = enemy_scale

    # Apply scaling to enemy image
    enemy_size = 150 if enemy_type != "boss" else 300
    scaled_enemy_size = int(enemy_size * enemy_scale)
    scaled_enemy_image = pygame.transform.scale(enemy_images[enemy_type], (scaled_enemy_size, scaled_enemy_size))

    # Handle Enemy Shake Animation
    if enemy_shake_flags[enemy_type]:
        # Apply a small random offset to simulate shaking
        shake_offset_x = random.randint(-5, 5)
        shake_offset_y = random.randint(-5, 5)
        enemy_shake_counters[enemy_type] -= 1
        if enemy_shake_counters[enemy_type] <= 0:
            enemy_shake_flags[enemy_type] = False
    else:
        shake_offset_x = 0
        shake_offset_y = 0

    # Calculate offset to keep the enemy centered
    enemy_offset = (enemy_size - scaled_enemy_size) // 2
    enemy_rect = pygame.Rect(350 + enemy_offset + shake_offset_x, 200 + enemy_offset + shake_offset_y, scaled_enemy_size, scaled_enemy_size)
    screen.blit(scaled_enemy_image, enemy_rect)

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
        "S: Special Attack          R: Run Away"
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
    """
    Handles the logic for player's actions during battle.
    """
    global player_health, player_mana, player_xp, battle_mode, current_enemy, mana_warning
    global player_max_health, player_max_mana, player_damage, player_level, xp_needed
    global facing_right  # Ensure we can modify facing_right

    if player_action == "basic_attack":
        # Basic attack
        current_enemy["health"] -= player_damage
        trigger_enemy_shake(current_enemy["type"])
    elif player_action == "special_attack":
        if player_mana >= 3:
            # Special attack
            current_enemy["health"] -= player_damage + 2
            player_mana -= 3
            trigger_enemy_shake(current_enemy["type"])
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
        game_over_screen(victory=False)

    if current_enemy["health"] <= 0:
        player_xp += ENEMY_TYPES[current_enemy["type"]]["xp"]
        if current_enemy["type"] == "boss":
            print("You win!")
            game_over_screen(victory=True)

        enemies.remove(current_enemy)
        play_music(overworld_music)
        battle_mode = False

        # Level up check
        if player_xp >= xp_needed:
            player_level_up()

def player_level_up():
    """
    Handles player leveling up.
    """
    global player_level, player_xp, xp_needed
    global player_max_health, player_max_mana, player_damage
    global player_health, player_mana

    player_level += 1
    player_xp = 0
    xp_needed += 5
    player_max_health += 10
    player_max_mana += 5
    player_damage += 2
    player_health = player_max_health
    player_mana = player_max_mana
    print(f"Level Up! You are now level {player_level}.")

def game_over_screen(victory=False):
    """
    Displays the game over or victory screen.
    """
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    if victory:
        text = font.render("You Win!", True, WHITE)
    else:
        text = font.render("Game Over", True, WHITE)
    screen.blit(text, (WINDOW_SIZE//2 - text.get_width()//2, WINDOW_SIZE//2 - text.get_height()//2))
    pygame.display.flip()

    # Wait for a few seconds before quitting
    pygame.time.delay(3000)
    pygame.quit()
    sys.exit()

def trigger_enemy_shake(enemy_type):
    """
    Triggers the shake animation for the specified enemy type.
    """
    if enemy_type in enemy_shake_flags:
        enemy_shake_flags[enemy_type] = True
        enemy_shake_counters[enemy_type] = 30  # Shake for 30 frames

# Create a semi-transparent wall surface
wall_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
wall_alpha = 0  # 0 (fully transparent) to 255 (fully opaque)
wall_color = BROWN + (wall_alpha,)  # Adding alpha to the color
wall_surface.fill(wall_color)

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
                moved = False  # Flag to check if movement occurred
                if event.key == pygame.K_UP and sprite_y > 0:
                    # Check collision for all cells the sprite will occupy after movement
                    collision = False
                    for dx in range(2):
                        for dy in range(2):
                            if (sprite_x + dx, sprite_y - 1 + dy) in walls:
                                collision = True
                                break
                        if collision:
                            break
                    if not collision:
                        sprite_y -= 1
                        moved = True
                elif event.key == pygame.K_DOWN and sprite_y < GRID_SIZE - 2:
                    collision = False
                    for dx in range(2):
                        for dy in range(2):
                            if (sprite_x + dx, sprite_y + 2 + dy) in walls:
                                collision = True
                                break
                        if collision:
                            break
                    if not collision:
                        sprite_y += 1
                        moved = True
                elif event.key == pygame.K_LEFT and sprite_x > 0:
                    collision = False
                    for dx in range(2):
                        for dy in range(2):
                            if (sprite_x - 1 + dx, sprite_y + dy) in walls:
                                collision = True
                                break
                        if collision:
                            break
                    if not collision:
                        sprite_x -= 1
                        moved = True
                        facing_right = False  # Change direction to left
                elif event.key == pygame.K_RIGHT and sprite_x < GRID_SIZE - 2:
                    collision = False
                    for dx in range(2):
                        for dy in range(2):
                            if (sprite_x + 2 + dx, sprite_y + dy) in walls:
                                collision = True
                                break
                        if collision:
                            break
                    if not collision:
                        sprite_x += 1
                        moved = True
                        facing_right = True  # Change direction to right

                # If movement occurred, you can trigger movement-based animations here
                if moved:
                    pass  # Currently, animation is continuous. Modify if you want animation tied to movement.

                # Check for collisions with enemies
                for enemy in enemies:
                    enemy_size = 2 if enemy["type"] != "boss" else 4
                    if (sprite_x < enemy["x"] + enemy_size and
                        sprite_x + 2 > enemy["x"] and
                        sprite_y < enemy["y"] + enemy_size and
                        sprite_y + 2 > enemy["y"]):
                        battle_mode = True
                        current_enemy = enemy
                        facing_right = True  # Ensure player faces right in battle mode
                        break  # Initiate battle with the first collided enemy

    # Clear the screen
    if battle_mode:
        draw_battle_screen()
    else:
        screen.blit(background_image, (0, 0))

        # Draw the walls first to ensure they are at the bottom layer
        for (wx, wy) in walls:
            wall_rect = pygame.Rect(wx * CELL_SIZE, wy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            screen.blit(wall_surface, wall_rect)  # Blit the semi-transparent wall

        # Draw the animated sprite
        player_pos_x = sprite_x * CELL_SIZE
        player_pos_y = sprite_y * CELL_SIZE

        # Apply scaling based on overworld animation
        scaled_player_size = int(CELL_SIZE * 2 * player_overworld_scale)
        scaled_player_image = pygame.transform.scale(player_image_original, (scaled_player_size, scaled_player_size))

        # Flip the player image based on direction
        if facing_right:
            final_player_image = scaled_player_image
        else:
            final_player_image = pygame.transform.flip(scaled_player_image, True, False)

        # Calculate offset to keep the player centered
        player_offset = (CELL_SIZE * 2 - scaled_player_size) // 2

        # Create a rect with adjusted position
        player_rect = pygame.Rect(player_pos_x + player_offset, player_pos_y + player_offset, scaled_player_size, scaled_player_size)
        screen.blit(final_player_image, player_rect)

        # Update player animation scale factors (Overworld)
        player_overworld_scale += player_animation_direction * player_animation_speed
        player_overworld_scale = max(min(player_overworld_scale, player_scale_max), player_scale_min)

        # Reverse direction if limits are reached
        if player_overworld_scale <= player_scale_min or player_overworld_scale >= player_scale_max:
            player_animation_direction *= -1

        # Draw the enemies
        for enemy in enemies:
            size = CELL_SIZE * 2 if enemy["type"] != "boss" else CELL_SIZE * 4
            enemy_rect = pygame.Rect(enemy["x"] * CELL_SIZE, enemy["y"] * CELL_SIZE, size, size)

            # Get enemy type
            enemy_type = enemy["type"]

            # Get current animation scale for the enemy
            enemy_scale = enemy_animation_scales[enemy_type]

            # Apply scaling
            scaled_enemy_size = int(size * enemy_scale)
            scaled_enemy_image = pygame.transform.scale(enemy_images[enemy_type], (scaled_enemy_size, scaled_enemy_size))

            # Handle Enemy Shake Animation
            if enemy_shake_flags[enemy_type]:
                # Apply a small random offset to simulate shaking
                shake_offset_x = random.randint(-5, 5)
                shake_offset_y = random.randint(-5, 5)
                enemy_shake_counters[enemy_type] -= 1
                if enemy_shake_counters[enemy_type] <= 0:
                    enemy_shake_flags[enemy_type] = False
            else:
                shake_offset_x = 0
                shake_offset_y = 0

            # Calculate offset to keep the enemy centered
            enemy_offset = (size - scaled_enemy_size) // 2
            enemy_rect_scaled = pygame.Rect(
                enemy["x"] * CELL_SIZE + enemy_offset + shake_offset_x,
                enemy["y"] * CELL_SIZE + enemy_offset + shake_offset_y,
                scaled_enemy_size,
                scaled_enemy_size
            )

            # Blit the scaled (and possibly shaken) enemy image
            screen.blit(scaled_enemy_image, enemy_rect_scaled)

            # Update enemy animation scale factors
            enemy_animation_scales[enemy_type] += enemy_animation_directions[enemy_type] * player_animation_speed
            enemy_animation_scales[enemy_type] = max(min(enemy_animation_scales[enemy_type], player_scale_max), player_scale_min)

            # Reverse direction if limits are reached
            if enemy_animation_scales[enemy_type] <= player_scale_min or enemy_animation_scales[enemy_type] >= player_scale_max:
                enemy_animation_directions[enemy_type] *= -1

        # Draw the XP bar
        draw_xp_bar()

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()
