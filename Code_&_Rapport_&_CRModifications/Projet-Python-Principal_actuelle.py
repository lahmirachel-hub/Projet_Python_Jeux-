import pygame
import sys
import random
from classes import Joueur, Room as ImportedRoom, TreasureRoom, TrapRoom
from effet_random import niveau_verrou
import os
pygame.init()
pygame.mixer.init()



# Dimensions
TAILLE_CASE = 45
NB_LIGNES, NB_COLONNES = 9, 5
LARGEUR_GRILLE = NB_COLONNES * TAILLE_CASE
HAUTEUR_GRILLE = NB_LIGNES * TAILLE_CASE

HAUTEUR_INVENTAIRE = 150
HAUTEUR_MENU = 200
LARGEUR_FENETRE = LARGEUR_GRILLE + 300
HAUTEUR_FENETRE = HAUTEUR_GRILLE + HAUTEUR_MENU

# Crée la fenêtre AVANT de charger les images
fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
pygame.display.set_caption("Blue Prince")


# Couleurs du manoir 
BLANC = (255, 255, 255)
GRIS = (200, 200, 200)
NOIR = (0, 0, 0)
BLEU = (100, 149, 237)
VIOLET = (186, 85, 211)
MARRON = (160, 82, 45)
OR = (218, 165, 32)
GRIS_FONCE = (105, 105, 105)
# Autres
selection_piece = False
index_selection = 0
choix_pieces = []
# Police d'écriture du jeu
police = pygame.font.SysFont(None, 24)
police_titre = pygame.font.SysFont(None, 32)

# Initialisations des sons de start, game over et victory
son_depart = pygame.mixer.Sound("sounds/start.wav")
son_victoire = pygame.mixer.Sound("sounds/victory.wav")
son_defaite = pygame.mixer.Sound("sounds/defeat.wav")
# Associer au chambre les différentes images :
# Chemins relatifs vers les images (basé sur les fichiers que tu as)
chemins_images = {
    "Bibliothèque": os.path.join("image", "Study.png"),
    "Couloir": os.path.join("image", "Corridor_Icon.png"),
    "Chambre": os.path.join("image", "Bedroom.png"),
    "Coffre": os.path.join("image", "vault.png"),
    "Armurerie": os.path.join("image", "The_Armory_Icon.png"),
    "Cuisine": os.path.join("image", "kitchen.png"),
    "Antichambre": os.path.join("image", "Antechamber_Icon.png"),
    "Salle de sport": os.path.join("image", "weight Room.png"),
    "Hall d'entrée": os.path.join("image", "Entrance Hall.png"),
    "Salle obscure": os.path.join("image", "Darkroom.png"),
    "Garage": os.path.join("image", "Garage.png"),
    "Salle de repos": os.path.join("image", "SpareRoom.png"),
    "Salle des trophées": os.path.join("image", "TrophyRoom.png")
}

# Chargement des images
images_pieces = {nom: pygame.image.load(chemin).convert_alpha() for nom, chemin in chemins_images.items()}

# Catalogue complet des pièces (uniquement celles dont l’image existe)
catalogue_pieces = [
    {"nom": "Bibliothèque", "image": images_pieces["Bibliothèque"], "description": "Utiliser une gemme pour redessiner", "cout": 1, "effet": None, "niveau_verrou": niveau_verrou()},
    {"nom": "Couloir", "image": images_pieces["Couloir"], "description": "", "cout": 0, "effet": None, "niveau_verrou": niveau_verrou()},
    {"nom": "Chambre", "image": images_pieces["Chambre"], "description": "Gagnez 2 pas en entrant", "cout": 0, "effet": "gain_steps", "niveau_verrou": niveau_verrou()},
    {"nom": "Coffre", "image": images_pieces["Coffre"], "description": "Nécessite une clé pour entrer", "cout": 0, "effet": None, "niveau_verrou": niveau_verrou()},
    {"nom": "Armurerie", "image": images_pieces["Armurerie"], "description": "Gagnez 1 clé en entrant", "cout": 0, "effet": "gain_key", "niveau_verrou": niveau_verrou()},
    {"nom": "Cuisine", "image": images_pieces["Cuisine"], "description": "Acheter des fruits", "cout": 0, "effet": "gain_die", "niveau_verrou": niveau_verrou()},
    {"nom": "Salle de sport", "image": images_pieces["Salle de sport"], "description": "Mystère", "cout": 1, "effet": None, "niveau_verrou": niveau_verrou()},
    {"nom": "Salle obscure", "image": images_pieces["Salle obscure"], "description": "Salle obscure", "cout": 1, "effet": None, "niveau_verrou": niveau_verrou()},
    {"nom": "Garage", "image": images_pieces["Garage"], "description": "Salle mécanique", "cout": 1, "effet": None, "niveau_verrou": niveau_verrou()},
    {"nom": "Salle de repos", "image": images_pieces["Salle de repos"], "description": "Salle de repos", "cout": 0, "effet": None, "niveau_verrou": niveau_verrou()},
    {"nom": "Salle des trophées", "image": images_pieces["Salle des trophées"], "description": "Gagnez une gemme", "cout": 2, "effet": "gain_gem", "niveau_verrou": niveau_verrou()}
]

# Classe Salle
class Salle:
    def __init__(self, nom="Inconnue", image=None, decouverte=False, effet=None, niveau_verrou=0, necessite_cle=False):
        self.nom = nom
        self.image = image
        self.decouverte = decouverte
        self.effet = effet
        self.effet_declenche = False
        self.niveau_verrou = niveau_verrou
        self.necessite_cle = necessite_cle
    
    def declencher_effet(self, joueur):
        pass
    

# Grille du manoir
grille = [[Salle() for _ in range(NB_COLONNES)] for _ in range(NB_LIGNES)]
grille[8][2] = Salle(nom="Hall d'entrée", image=images_pieces["Hall d'entrée"], decouverte=True)
grille[0][2] = Salle(nom="Antichambre", image=images_pieces["Antichambre"], decouverte=True)

# Position initiale du joueur
# Créer une instance de votre joueur
NB_LIGNES, NB_COLONNES = 9, 5 # Récupérer les dimensions de la grille
joueur = Joueur("Blue Prince", NB_LIGNES, NB_COLONNES) 

# La position du joueur est maintenant joueur.position
# L'inventaire est joueur.inventaire
# Vous pouvez aussi initialiser le Hall d'entrée ici pour la cohérence
grille[joueur.position[0]][joueur.position[1]] = Salle(nom="Hall d'entrée", image=images_pieces["Hall d'entrée"], decouverte=True) 

# Note: Pour que le jeu fonctionne tout de suite, il faut une clé. 
# Si vous avez mis 0 dans votre classe Joueur, ajoutez temporairement 
# joueur.inventaire["Clés"] = 1 
# Ou suivez l'énoncé original (0 clé) et modifiez plus tard.


# Affichage de la grille
def afficher_grille():
    for ligne in range(NB_LIGNES):
        for colonne in range(NB_COLONNES):
            salle = grille[ligne][colonne]
            x = colonne * TAILLE_CASE
            y = ligne * TAILLE_CASE
            if salle.decouverte and salle.image is not None:
                img = pygame.transform.scale(salle.image, (TAILLE_CASE, TAILLE_CASE))
                fenetre.blit(img, (x, y))
            else:
                pygame.draw.rect(fenetre, NOIR, (x, y, TAILLE_CASE, TAILLE_CASE))
            pygame.draw.rect(fenetre, GRIS, (x, y, TAILLE_CASE, TAILLE_CASE), 1)
            # Utilisation de joueur.position
            if [ligne, colonne] == joueur.position: 
                pygame.draw.rect(fenetre, (0, 191, 255), (x + 10, y + 10, TAILLE_CASE - 20, TAILLE_CASE - 20))


# Affichage de l'inventaire
def afficher_inventaire():
    x_offset = LARGEUR_GRILLE + 20
    y_offset = 20
    fenetre.blit(police_titre.render("Inventaire", True, NOIR), (x_offset, y_offset))
    # Utilisation de joueur.inventaire
        # Utilisation de joueur.inventaire
    for i, (cle, valeur) in enumerate(joueur.inventaire.items()): 
        texte = f"{cle}: {valeur}"
        fenetre.blit(police.render(texte, True, NOIR), (x_offset, y_offset + 30 + i * 25))


# Affichage du menu de tirage
def afficher_choix_pieces():
    base_y = HAUTEUR_GRILLE + 20
    largeur_carte = 160
    espacement_cartes = 20
    largeur_totale = len(choix_pieces) * largeur_carte + (len(choix_pieces) - 1) * espacement_cartes
    start_x = (LARGEUR_FENETRE - largeur_totale) // 2

    for i, piece in enumerate(choix_pieces):
        x = start_x + i * (largeur_carte + espacement_cartes)
        # Affiche un rectangle de fond :
        pygame.draw.rect(fenetre, GRIS_FONCE, (x, base_y, largeur_carte, 120))
        pygame.draw.rect(fenetre, NOIR, (x, base_y, largeur_carte, 120), 2)
        # Redimensionner l'image pour rentrer dans la "carte"
        img = pygame.transform.scale(piece["image"], (largeur_carte, 85))
        fenetre.blit(img, (x, base_y))
        
        fenetre.blit(police_titre.render(piece["nom"], True, BLANC), (x + 10, base_y + 90))
        fenetre.blit(police.render(piece["description"], True, BLANC), (x + 10, base_y + 110))

        if selection_piece and i == index_selection:
            pygame.draw.rect(fenetre, (255, 0, 0), (x - 5, base_y - 5, largeur_carte + 10, 130), 3)

    # Bouton "Relancer avec un dé"
    if selection_piece:
        bouton_rect = pygame.Rect(LARGEUR_FENETRE - 180, HAUTEUR_GRILLE + 150, 160, 30)
        pygame.draw.rect(fenetre, (70, 130, 180), bouton_rect)
        pygame.draw.rect(fenetre, NOIR, bouton_rect, 2)
        texte = police.render("Relancer avec un dé", True, BLANC)
        texte_rect = texte.get_rect(center=bouton_rect.center)
        fenetre.blit(texte, texte_rect)


# Affichage du message de fin
def afficher_fin():
    texte = police_titre.render("Fin de la partie", True, (200, 0, 0))
    rect = texte.get_rect(center=(LARGEUR_GRILLE // 2, HAUTEUR_GRILLE // 2))
    fenetre.blit(texte, rect)

# fonction d'affichage d'un message défaite + écran  
def afficher_defaite():
    fenetre.fill((0, 0, 139))  # définition d'un écran bleu
    #police = pygame.font.SysFont("Arial", 80)  # taille plus grande
    police = pygame.font.Font("style/Signtelly.ttf", 50)
    texte = police.render("GAME OVER!", True, (220, 20, 60))
    rect = texte.get_rect(center=(LARGEUR_FENETRE // 2, HAUTEUR_FENETRE // 2))
    fenetre.blit(texte, rect)
    pygame.display.update()
# fonction d'affichage d'un message victoire
def afficher_victoire():
    fenetre.fill((0, 0, 139))  # fond bleu clair (SteelBlue)
    #police = pygame.font.SysFont("Arial", 80)  # taille grande comme pour GAME OVER
    police = pygame.font.Font("style/Signtelly.ttf", 50)
    texte = police.render("VICTOIRE !", True, (255, 215, 0)) # couleur dorée
    rect = texte.get_rect(center=(LARGEUR_FENETRE // 2, HAUTEUR_FENETRE // 2))
    fenetre.blit(texte, rect)
    pygame.display.update()


# Boucle principale
def principal():
    global selection_piece, index_selection, choix_pieces
    horloge = pygame.time.Clock()
    son_depart.play() # initialisation avec un son de départ

    while True:
        fenetre.fill(BLANC)

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Menu de sélection de pièce
            if selection_piece:
                if evenement.type == pygame.KEYDOWN:
                    if evenement.key == pygame.K_LEFT:
                        index_selection = (index_selection - 1) % len(choix_pieces)
                    elif evenement.key == pygame.K_RIGHT:
                        index_selection = (index_selection + 1) % len(choix_pieces)
                    elif evenement.key == pygame.K_RETURN:
                        ligne, colonne = joueur.position
                        choix = choix_pieces[index_selection]
                        cout = choix.get("cout", 0)
                        verrou = choix.get("niveau_verrou", 0)

                        if joueur.inventaire["Gemmes"] >= cout:
                            if verrou > 0 and joueur.inventaire["Clés"] < verrou:
                                print(f"Pas assez de clés pour placer {choix['nom']} (niveau {verrou})")
                            else:
                                joueur.inventaire["Gemmes"] -= cout
                                if verrou > 0:
                                    joueur.inventaire["Clés"] -= verrou
                                    print(f"Clé utilisée pour placer {choix['nom']}")

                                # Déterminer la classe à utiliser
                                classe_salle = choix.get("class", Salle) 
                                
                                # Création de la nouvelle salle
                                nouvelle_salle = classe_salle(
                                    nom=choix["nom"],
                                    image=choix["image"],
                                    effet=choix.get("effet"), 
                                    niveau_verrou=choix.get("niveau_verrou", 0),
                                    decouverte=True # La nouvelle salle est découverte dès sa construction
                                )

                                # Déclenchement de l'effet immédiat
                                nouvelle_salle.declencher_effet(joueur) 
                                
                                grille[ligne][colonne] = nouvelle_salle
                                selection_piece = False

                                # Effets immédiats
                                if nouvelle_salle.effet == "gain_steps":
                                    joueur.inventaire["Pas"] += 2
                                    nouvelle_salle.effet_declenche = True
                                    print("Effet immédiat : +2 pas")
                                elif nouvelle_salle.effet == "gain_key":
                                    joueur.inventaire["Clés"] += 1
                                    nouvelle_salle.effet_declenche = True
                                    print("Effet immédiat : +1 clé")
                                elif nouvelle_salle.effet == "gain_die":
                                    joueur.inventaire["Dés"] += 1
                                    nouvelle_salle.effet_declenche = True
                                    print("Effet immédiat : +1 dé")

                                grille[ligne][colonne] = nouvelle_salle
                                selection_piece = False
                        else:
                            print("Pas assez de gemmes pour cette pièce !")

                elif evenement.type == pygame.MOUSEBUTTONDOWN:
                    souris_x, souris_y = evenement.pos
                    bouton_rect = pygame.Rect(LARGEUR_FENETRE - 180, HAUTEUR_GRILLE + 150, 160, 30)
                    if bouton_rect.collidepoint(souris_x, souris_y):
                        if joueur.inventaire["Dés"] > 0:
                            joueur.inventaire["Dés"] -= 1
                            choix_pieces = random.sample(catalogue_pieces, 3)
                            print("Tirage relancé avec un dé")
                        else:
                            print("Pas de dés disponibles pour relancer")

            # Déplacement du joueur
            elif evenement.type == pygame.KEYDOWN and joueur.inventaire["Pas"] > 0:
                ligne, colonne = joueur.position
                nouvelle_ligne, nouvelle_colonne = ligne, colonne
                if evenement.key == pygame.K_z and ligne > 0:
                    nouvelle_ligne -= 1
                elif evenement.key == pygame.K_s and ligne < NB_LIGNES - 1:
                    nouvelle_ligne += 1
                elif evenement.key == pygame.K_q and colonne > 0:
                    nouvelle_colonne -= 1
                elif evenement.key == pygame.K_d and colonne < NB_COLONNES - 1:
                    nouvelle_colonne += 1

                if [nouvelle_ligne, nouvelle_colonne] != [ligne, colonne]:
                    salle_cible = grille[nouvelle_ligne][nouvelle_colonne]
                    if salle_cible.niveau_verrou > 0 and not salle_cible.decouverte:
                        if joueur.inventaire["Clés"] >= salle_cible.niveau_verrou:
                            joueur.inventaire["Clés"] -= salle_cible.niveau_verrou
                            print(f"Porte niveau {salle_cible.niveau_verrou} ouverte avec une clé")
                        else:
                            print("Porte verrouillée, clé requise")
                            continue

                    joueur.position[0], joueur.position[1] = nouvelle_ligne, nouvelle_colonne
                    joueur.inventaire["Pas"] -= 1

                    if not salle_cible.decouverte:
                        choix_pieces = random.sample(catalogue_pieces, 3)
                        selection_piece = True
                        index_selection = 0
                    elif salle_cible.effet == "gain_steps" and not salle_cible.effet_declenche:
                        joueur.inventaire["Pas"] += 2
                        salle_cible.effet_declenche = True
                        print("Effet activé : +2 pas")
                    elif salle_cible.effet == "gain_key" and not salle_cible.effet_declenche:
                        joueur.inventaire["Clés"] += 1
                        salle_cible.effet_declenche = True
                        print("Effet activé : +1 clé")
                    elif salle_cible.effet == "gain_die" and not salle_cible.effet_declenche:
                        joueur.inventaire["Dés"] += 1
                        salle_cible.effet_declenche = True
                        print("Effet activé : +1 dé")

        afficher_grille()
        afficher_inventaire()
        afficher_choix_pieces()
        if joueur.inventaire["Pas"] <= 0:
             print("Défaite 😢😢 Plus de pas disponibles")
             son_defaite.play()   # joue le son de défaite
             afficher_defaite()   # écran bleu avec texte Défaite
             pygame.time.wait(3000)
             pygame.quit()
             sys.exit()
        salle_actuelle = grille[joueur.position[0]][joueur.position[1]]
        if salle_actuelle.necessite_cle and joueur.inventaire["Clés"] <= 0:
            print("Défaite ! Vous n'avez plus de clés pour entrer dans cette salle")
            son_defaite.play()
            afficher_defaite()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit() 

        if joueur.position == [0, 2]:  # condition de victoire
            print("Victoire ! Vous avez atteint l'Antichambre !")
            son_victoire.play()
            afficher_victoire()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()
        
        pygame.display.update()
        horloge.tick(60)

principal()



