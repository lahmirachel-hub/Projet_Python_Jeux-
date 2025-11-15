import pygame
import sys
import random

pygame.init()

# Dimensions
CELL_SIZE = 45
ROWS, COLS = 9, 5
GRID_WIDTH = COLS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE
INVENTORY_HEIGHT = 150
MENU_HEIGHT = 200
WINDOW_WIDTH = GRID_WIDTH + 300
WINDOW_HEIGHT = GRID_HEIGHT + MENU_HEIGHT

# Couleurs
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
PURPLE = (186, 85, 211)
BROWN = (160, 82, 45)
GOLD = (218, 165, 32)
DARK_GRAY = (105, 105, 105)

# Autres
selecting_room = False
selected_index = 0
room_choices = []

# Fenêtre
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Blue Prince")

# Fonts
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 32)

# Inventaire
inventory = {
    "Pas": 70,
    "Or": 0,
    "Gemmes": 2,
    "Clés": 1,
    "Dés": 0
}

# Catalogue complet des pièces
all_rooms_catalog = [
    {"name": "Study", "color": BLUE, "desc": "Use gems to redraw", "cost": 1, "effect": None, "locked_level": 0},
    {"name": "Corridor", "color": BROWN, "desc": "", "cost": 0, "effect": None, "locked_level": 0},
    {"name": "Bedroom", "color": PURPLE, "desc": "Gain 2 steps when visited", "cost": 0, "effect": "gain_steps", "locked_level": 0},
    {"name": "Vault", "color": GOLD, "desc": "Requires key to enter", "cost": 0, "effect": None, "locked_level": 1},
    {"name": "Armory", "color": DARK_GRAY, "desc": "Gain 1 key when visited", "cost": 0, "effect": "gain_key", "locked_level": 0},
    {"name": "Dice Room", "color": (60, 179, 113), "desc": "Gain 1 die when visited", "cost": 0, "effect": "gain_die", "locked_level": 0}

]

# Classe Room
class Room:
    def __init__(self, name="Unknown", color=(0, 0, 0), discovered=False, effect=None, locked_level=0):
        self.name = name
        self.color = color
        self.discovered = discovered
        self.effect = effect
        self.effect_triggered = False
        self.locked_level = locked_level

# Grille du manoir
grid = [[Room() for _ in range(COLS)] for _ in range(ROWS)]
grid[8][2] = Room(name="Entrance Hall", color=(173, 216, 230), discovered=True)

# Position initiale du joueur
player_pos = [8, 2]

# Affichage de la grille
def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            room = grid[row][col]
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            color = room.color if room.discovered else BLACK
            pygame.draw.rect(window, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(window, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)
            if [row, col] == player_pos:
                pygame.draw.rect(window, (0, 191, 255), (x + 10, y + 10, CELL_SIZE - 20, CELL_SIZE - 20))

# Affichage de l'inventaire
def draw_inventory():
    x_offset = GRID_WIDTH + 20
    y_offset = 20
    window.blit(title_font.render("Inventaire", True, BLACK), (x_offset, y_offset))
    for i, (key, value) in enumerate(inventory.items()):
        text = f"{key}: {value}"
        window.blit(font.render(text, True, BLACK), (x_offset, y_offset + 30 + i * 25))

# Affichage du menu de tirage
def draw_room_choices():
    base_y = GRID_HEIGHT + 20
    card_width = 160
    card_spacing = 20
    total_width = len(room_choices) * card_width + (len(room_choices) - 1) * card_spacing
    start_x = (WINDOW_WIDTH - total_width) // 2

    for i, room in enumerate(room_choices):
        x = start_x + i * (card_width + card_spacing)
        pygame.draw.rect(window, room["color"], (x, base_y, card_width, 120))
        pygame.draw.rect(window, BLACK, (x, base_y, card_width, 120), 2)
        window.blit(title_font.render(room["name"], True, WHITE), (x + 10, base_y + 10))
        window.blit(font.render(room["desc"], True, WHITE), (x + 10, base_y + 50))

        if selecting_room and i == selected_index:
            pygame.draw.rect(window, (255, 0, 0), (x - 5, base_y - 5, card_width + 10, 130), 3)

    # Bouton "Relancer avec un dé"
    if selecting_room:
        button_rect = pygame.Rect(WINDOW_WIDTH - 180, GRID_HEIGHT + 150, 160, 30)
        pygame.draw.rect(window, (70, 130, 180), button_rect)
        pygame.draw.rect(window, BLACK, button_rect, 2)
        text = font.render("Relancer avec un dé", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        window.blit(text, text_rect)


# Affichage du message de fin
def draw_game_over():
    text = title_font.render("Game is over!", True, (200, 0, 0))
    rect = text.get_rect(center=(GRID_WIDTH // 2, GRID_HEIGHT // 2))
    window.blit(text, rect)

# Boucle principale
def main():
    global selecting_room, selected_index, room_choices
    clock = pygame.time.Clock()
    while True:
        window.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Menu de sélection de pièce
            if selecting_room:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        selected_index = (selected_index - 1) % len(room_choices)
                    elif event.key == pygame.K_RIGHT:
                        selected_index = (selected_index + 1) % len(room_choices)
                    elif event.key == pygame.K_RETURN:
                        row, col = player_pos
                        chosen = room_choices[selected_index]
                        cost = chosen.get("cost", 0)
                        lock = chosen.get("locked_level", 0)

                        if inventory["Gemmes"] >= cost:
                            if lock > 0 and inventory["Clés"] < lock:
                                print(f"Pas assez de clés pour placer {chosen['name']} (niveau {lock})")
                            else:
                                inventory["Gemmes"] -= cost
                                if lock > 0:
                                    inventory["Clés"] -= lock
                                    print(f"Clé utilisée pour placer {chosen['name']}")

                                new_room = Room(
                                    name=chosen["name"],
                                    color=chosen["color"],
                                    discovered=True,
                                    effect=chosen.get("effect"),
                                    locked_level=lock
                                )

                                # Effets immédiats
                                if new_room.effect == "gain_steps":
                                    inventory["Pas"] += 2
                                    new_room.effect_triggered = True
                                    print("Effet immédiat : +2 pas")
                                elif new_room.effect == "gain_key":
                                    inventory["Clés"] += 1
                                    new_room.effect_triggered = True
                                    print("Effet immédiat : +1 clé")
                                elif new_room.effect == "gain_die":
                                    inventory["Dés"] += 1
                                    new_room.effect_triggered = True
                                    print("Effet immédiat : +1 dé")

                                grid[row][col] = new_room
                                selecting_room = False
                        else:
                            print("Pas assez de gemmes pour cette pièce !")

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    button_rect = pygame.Rect(WINDOW_WIDTH - 180, GRID_HEIGHT + 150, 160, 30)
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        if inventory["Dés"] > 0:
                            inventory["Dés"] -= 1
                            room_choices = random.sample(all_rooms_catalog, 3)
                            print("Tirage relancé avec un dé")
                        else:
                            print("Pas de dés disponibles pour relancer")

            # Déplacement du joueur
            elif event.type == pygame.KEYDOWN and inventory["Pas"] > 0:
                row, col = player_pos
                new_row, new_col = row, col
                if event.key == pygame.K_z and row > 0:
                    new_row -= 1
                elif event.key == pygame.K_s and row < ROWS - 1:
                    new_row += 1
                elif event.key == pygame.K_q and col > 0:
                    new_col -= 1
                elif event.key == pygame.K_d and col < COLS - 1:
                    new_col += 1

                if [new_row, new_col] != [row, col]:
                    target_room = grid[new_row][new_col]
                    if target_room.locked_level > 0 and not target_room.discovered:
                        if inventory["Clés"] >= target_room.locked_level:
                            inventory["Clés"] -= target_room.locked_level
                            print(f"Porte niveau {target_room.locked_level} ouverte avec une clé")
                        else:
                            print("Porte verrouillée, clé requise")
                            continue

                    player_pos[0], player_pos[1] = new_row, new_col
                    inventory["Pas"] -= 1

                    if not target_room.discovered:
                        room_choices = random.sample(all_rooms_catalog, 3)
                        selecting_room = True
                        selected_index = 0
                    elif target_room.effect == "gain_steps" and not target_room.effect_triggered:
                        inventory["Pas"] += 2
                        target_room.effect_triggered = True
                        print("Effet activé : +2 pas")
                    elif target_room.effect == "gain_key" and not target_room.effect_triggered:
                        inventory["Clés"] += 1
                        target_room.effect_triggered = True
                        print("Effet activé : +1 clé")
                    elif target_room.effect == "gain_die" and not target_room.effect_triggered:
                        inventory["Dés"] += 1
                        target_room.effect_triggered = True
                        print("Effet activé : +1 dé")

        draw_grid()
        draw_inventory()
        draw_room_choices()
        if inventory["Pas"] <= 0:
            draw_game_over()
        pygame.display.update()
        clock.tick(60)

main()

