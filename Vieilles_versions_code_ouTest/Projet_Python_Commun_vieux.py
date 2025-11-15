import pygame
import sys
import random
from classes import Joueur, Room as ImportedRoom, TreasureRoom, TrapRoom
import os
pygame.init()
pygame.mixer.init()
# Initialisations des sons de start, game over et victory
start_sound = pygame.mixer.Sound("sounds/start.wav")
victory_sound = pygame.mixer.Sound("sounds/victory.wav")
defeat_sound = pygame.mixer.Sound("sounds/defeat.wav")


# Dimensions
CELL_SIZE = 45
ROWS, COLS = 9, 5
GRID_WIDTH = COLS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE

INVENTORY_HEIGHT = 150
MENU_HEIGHT = 200
WINDOW_WIDTH = GRID_WIDTH + 300
WINDOW_HEIGHT = GRID_HEIGHT + MENU_HEIGHT

# Crée la fenêtre AVANT de charger les images
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Blue Prince")


# Couleurs du manoir 
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
# Police d'écriture du jeu
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 32)


# Associer au chambre les différentes images :
# Chemins relatifs vers les images (basé sur les fichiers que tu as)
image_paths = {
    "Study": os.path.join("image", "Study.png"),
    "Corridor": os.path.join("image", "Corridor_Icon.png"),
    "Bedroom": os.path.join("image", "Bedroom.png"),
    "Vault": os.path.join("image", "vault.png"),
    "Armory": os.path.join("image", "The_Armory_Icon.png"),
    "Kitchen": os.path.join("image", "kitchen.png"),
    "Antichamber": os.path.join("image", "Antechamber_Icon.png"),
    "Weight Room": os.path.join("image", "weight Room.png"),
    "Entrance Hall": os.path.join("image", "Entrance Hall.png"),
    "Darkroom": os.path.join("image", "Darkroom.png"),
    "Garage": os.path.join("image", "Garage.png"),
    "Spare Room": os.path.join("image", "SpareRoom.png"),
    "Trophy Room": os.path.join("image", "TrophyRoom.png")
}

# Chargement des images
room_images = {name: pygame.image.load(path).convert_alpha() for name, path in image_paths.items()}

# Catalogue complet des pièces (uniquement celles dont l’image existe)
all_rooms_catalog = [
    {"name": "Study", "image": room_images["Study"], "desc": "Use gems to redraw", "cost": 1, "effect": None, "locked_level": 0},
    {"name": "Corridor", "image": room_images["Corridor"], "desc": "", "cost": 0, "effect": None, "locked_level": 0},
    {"name": "Bedroom", "image": room_images["Bedroom"], "desc": "Gain 2 steps when visited", "cost": 0, "effect": "gain_steps", "locked_level": 0},
    {"name": "Vault", "image": room_images["Vault"], "desc": "Requires key to enter", "cost": 0, "effect": None, "locked_level": 1},
    {"name": "Armory", "image": room_images["Armory"], "desc": "Gain 1 key when visited", "cost": 0, "effect": "gain_key", "locked_level": 0},
    {"name": "Kitchen", "image": room_images["Kitchen"], "desc": "Buy fruits", "cost": 0, "effect": "gain_die", "locked_level": 0},
    {"name": "Weight Room", "image": room_images["Weight Room"], "desc": "Mystère", "cost": 1, "effect": None, "locked_level": 1},
    {"name": "Darkroom", "image": room_images["Darkroom"], "desc": "Salle obscure", "cost": 1, "effect": None, "locked_level": 1},
    {"name": "Garage", "image": room_images["Garage"], "desc": "Salle mécanique", "cost": 1, "effect": None, "locked_level": 1},
    {"name": "Spare Room", "image": room_images["Spare Room"], "desc": "Salle de repos", "cost": 0, "effect": None, "locked_level": 0},
    {"name": "Trophy Room", "image": room_images["Trophy Room"], "desc": "Salle des trophées", "cost": 2, "effect": "gain_gem", "locked_level": 1}
]




# Classe Room
class Room:
    def __init__(self, name="Unknown", image = None, discovered=False, effect=None, locked_level=0, requires_key=False):
        self.name = name
        self.image = image
        self.discovered = discovered
        self.effect = effect
        self.effect_triggered = False
        self.locked_level = locked_level
        self.requires_key = requires_key
    
    def trigger_effect(self, player):
        pass
    

# Grille du manoir
grid = [[Room() for _ in range(COLS)] for _ in range(ROWS)]
grid[8][2] = Room(name="Entrance Hall", image=room_images["Entrance Hall"], discovered=True)
grid[0][2] = Room(name="Antichamber", image=room_images["Antichamber"], discovered=True)

# Position initiale du joueur
# Créer une instance de votre joueur
ROWS, COLS = 9, 5 # Récupérer les dimensions de la grille
player = Joueur("Blue Prince", ROWS, COLS) 

# La position du joueur est maintenant player.position
# L'inventaire est player.inventaire
# Vous pouvez aussi initialiser l'Entrance Hall ici pour la cohérence
grid[player.position[0]][player.position[1]] = Room(name="Entrance Hall", image=room_images["Entrance Hall"], discovered=True) 

# Note: Pour que le jeu fonctionne tout de suite, il faut une clé. 
# Si vous avez mis 0 dans votre classe Joueur, ajoutez temporairement 
# player.inventaire["Clés"] = 1 
# Ou suivez l'énoncé original (0 clé) et modifiez plus tard.


# Affichage de la grille
def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            room = grid[row][col]
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            if room.discovered and room.image is not None:
                img = pygame.transform.scale(room.image, (CELL_SIZE, CELL_SIZE))
                window.blit(img, (x, y))
            else:
                pygame.draw.rect(window, BLACK, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(window, GRAY, (x, y, CELL_SIZE, CELL_SIZE), 1)
            # Utilisation de player.position
            if [row, col] == player.position: 
                pygame.draw.rect(window, (0, 191, 255), (x + 10, y + 10, CELL_SIZE - 20, CELL_SIZE - 20))


# Affichage de l'inventaire
def draw_inventory():
    x_offset = GRID_WIDTH + 20
    y_offset = 20
    window.blit(title_font.render("Inventaire", True, BLACK), (x_offset, y_offset))
    # Utilisation de player.inventaire
    for i, (key, value) in enumerate(player.inventaire.items()): 
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
        # Affiche un rectangle de fond :
        pygame.draw.rect(window, DARK_GRAY, (x, base_y, card_width, 120))
        pygame.draw.rect(window, BLACK, (x, base_y, card_width, 120), 2)
        # Redimensionner l'image pour rentrer dans la "carte"
        img = pygame.transform.scale(room["image"], (card_width, 85))
        window.blit(img, (x, base_y))
        
        window.blit(title_font.render(room["name"], True, WHITE), (x + 10, base_y + 90))
        window.blit(font.render(room["desc"], True, WHITE), (x + 10, base_y + 110))

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
# fonction d'affichage d'un message défaite+ écran  
def draw_defeat():
    window.fill((0, 0, 139))  # définition d'un écran bleu
    #font = pygame.font.SysFont("Arial", 80)  # taille plus grande
    font = pygame.font.Font("style/Signtelly.ttf", 50)
    text = font.render("GAME OVER!", True, (220, 20, 60))
    rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    window.blit(text, rect)
    pygame.display.update()
# fonction d'affichage d'un message victoire
def draw_victory():
    window.fill((0, 0, 139))  # fond bleu clair (SteelBlue)
    #font = pygame.font.SysFont("Arial", 80)  # taille grande comme pour GAME OVER
    font = pygame.font.Font("style/Signtelly.ttf", 50)
    text = font.render("VICTOIRE!", True, (255, 215, 0))# ((255, 215, 0))pour une couleur doré 
    rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    window.blit(text, rect)
    pygame.display.update()


# Boucle principale
def main():
    global selecting_room, selected_index, room_choices
    clock = pygame.time.Clock()
    start_sound.play() # initialisation avec un son pour start 

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
                        row, col = player.position
                        chosen = room_choices[selected_index]
                        cost = chosen.get("cost", 0)
                        lock = chosen.get("locked_level", 0)

                        if player.inventaire["Gemmes"] >= cost:
                            if lock > 0 and player.inventaire["Clés"] < lock:
                                print(f"Pas assez de clés pour placer {chosen['name']} (niveau {lock})")
                            else:
                                player.inventaire["Gemmes"] -= cost
                                if lock > 0:
                                    player.inventaire["Clés"] -= lock
                                    print(f"Clé utilisée pour placer {chosen['name']}")

                                # On détermine la classe à utiliser
                                # 1. Tente de récupérer la valeur associée à la clé 'class' dans le dictionnaire 'chosen'.
                                #    (Ex: 'class': TreasureRoom).
                                # 2. Si la clé 'class' n'existe pas, elle utilise la classe Room par défaut.
                                room_class = chosen.get("class", Room) 
                                
                                # Création de la nouvelle pièce en utilisant la classe déterminée (room_class)
                                new_room = room_class(
                                    name=chosen["name"],
                                    image=chosen["image"],
                                    # L'effet est passé, même si les classes héritées (Treasure/Trap) 
                                    # l'ignorent dans leur propre logique d'effet.
                                    effect=chosen.get("effect"), 
                                    locked_level=chosen.get("locked_level", 0),
                                    discovered=True # La nouvelle pièce est découverte dès sa construction
                                )

                                # Déclenchement de l'effet immédiat
                                # L'avantage de la POO est que Python sait quelle méthode appeler :
                                # - Si c'est une 'TreasureRoom', il appelle la méthode TreasureRoom.trigger_effect.
                                # - Si c'est une 'Room', il appelle la méthode Room.trigger_effect.
                                new_room.trigger_effect(player) 
                                
                                grid[row][col] = new_room
                                selecting_room = False

                                # Effets immédiats
                                if new_room.effect == "gain_steps":
                                    player.inventaire["Pas"] += 2
                                    new_room.effect_triggered = True
                                    print("Effet immédiat : +2 pas")
                                elif new_room.effect == "gain_key":
                                    player.inventaire["Clés"] += 1
                                    new_room.effect_triggered = True
                                    print("Effet immédiat : +1 clé")
                                elif new_room.effect == "gain_die":
                                    player.inventaire["Dés"] += 1
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
                        if player.inventaire["Dés"] > 0:
                            player.inventaire["Dés"] -= 1
                            room_choices = random.sample(all_rooms_catalog, 3)
                            print("Tirage relancé avec un dé")
                        else:
                            print("Pas de dés disponibles pour relancer")

            # Déplacement du joueur
            elif event.type == pygame.KEYDOWN and player.inventaire["Pas"] > 0:
                row, col = player.position
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
                        if player.inventaire["Clés"] >= target_room.locked_level:
                            player.inventaire["Clés"] -= target_room.locked_level
                            print(f"Porte niveau {target_room.locked_level} ouverte avec une clé")
                        else:
                            print("Porte verrouillée, clé requise")
                            continue

                    player.position[0], player.position[1] = new_row, new_col
                    player.inventaire["Pas"] -= 1

                    if not target_room.discovered:
                        room_choices = random.sample(all_rooms_catalog, 3)
                        selecting_room = True
                        selected_index = 0
                    elif target_room.effect == "gain_steps" and not target_room.effect_triggered:
                        player.inventaire["Pas"] += 2
                        target_room.effect_triggered = True
                        print("Effet activé : +2 pas")
                    elif target_room.effect == "gain_key" and not target_room.effect_triggered:
                        player.inventaire["Clés"] += 1
                        target_room.effect_triggered = True
                        print("Effet activé : +1 clé")
                    elif target_room.effect == "gain_die" and not target_room.effect_triggered:
                        player.inventaire["Dés"] += 1
                        target_room.effect_triggered = True
                        print("Effet activé : +1 dé")

        draw_grid()
        draw_inventory()
        draw_room_choices()
        if player.inventaire["Pas"] <= 0:
             print("Défaite 😢😢 Plus de pas disponibles")
             defeat_sound.play()   # joue le son de défaite
             draw_defeat()         # écran rouge avec texte Défaite
             pygame.time.wait(3000)
             pygame.quit()
             sys.exit()
        current_room = grid[player.position[0]][player.position[1]]
        if current_room.requires_key and player.inventaire["Clé"] <= 0:
            print("Défaite! Vous n'avez plus de clé pour entrer dans cette salle")
            defeat_sound.play()
            draw_defeat()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit() 

        if player.position == [0, 2]:  # condition de victoire
            print("Victoire! Vous avez atteint l'Antichamber !")
            victory_sound.play()
            draw_victory()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()
        
        pygame.display.update()
        clock.tick(60)

main()

