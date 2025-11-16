import pygame
import sys
import random
from classes import Joueur
from classes import Salle 
from collections import deque
from classes import COLLECTABLES_CATALOGUE, ObjetCollectable, PLACEMENT_OBJET
import os
pygame.init()
pygame.mixer.init()

''' 
          INTERFACE GRAPHIQUE_ Résumé de l'implémentation
Ce fichier Projet-Python-Principale contient:
initialisation: elle contient la creation de la fenetre avec pygame.display, titre'Blue Prince'
et definition de la taille de la grille.
Chargement des images de pièces: en utilisant un dictionnaire chemins_images et pygame pour load
Catalogue de pièces: permet de decrire les pièces (cout , effect et état de vérouillage)
Fonctions: 
afficher_inventaire(): qui affiche les ressources de gamer (nombre de pas, clés, gemmes...)
afficher_choix_pièces: affiche les 3 pièces tirés aléatoirement (si on dispose d'un dé, possibilité de relancer le tirage)
afficher_defaite et afficher_victoire: écran bleu + message+ son
principal(): la boucle principale gere les mouvements ZQSD, les tirage, inventaire, contions de victory ou game over

  '''


# Dimensions de la grille du jeux 
TAILLE_CASE = 60
NB_LIGNES, NB_COLONNES = 9, 5
LARGEUR_GRILLE = NB_COLONNES * TAILLE_CASE
HAUTEUR_GRILLE = NB_LIGNES * TAILLE_CASE

HAUTEUR_INVENTAIRE = 150
HAUTEUR_MENU = 200
LARGEUR_FENETRE = LARGEUR_GRILLE + 300
HAUTEUR_FENETRE = HAUTEUR_GRILLE + HAUTEUR_MENU

# Generer une fenetre (avant de charger les images)
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
# Lignes nécessaire au choix des pièces après tirage aléatoire 
selection_piece = False
index_selection = 0
choix_pieces = []
# Police d'écriture du jeu
police = pygame.font.SysFont(None, 24)
police_titre = pygame.font.SysFont(None, 32)

# Initialisations des sons de start, game over et victory
# Le dossier Sounds est dans le document Projet_Python_Jeux- : attention
# il faut bien se trouver dans ce dossier avant de run le code, sinon python va afficher qu'il ne trouve 
# pas les sons dans le chemin donné. 
 
son_depart = pygame.mixer.Sound("sounds/start.wav")
son_victoire = pygame.mixer.Sound("sounds/victory.wav")
son_defaite = pygame.mixer.Sound("sounds/defeat.wav")



# Associer aux chambres les différentes images :
# Chemins relatifs vers les images (basé sur les fichiers que tu as)
# Le dossier image est dans le document Projet_Python_Jeux- : attention
# il faut bien se trouver dans ce dossier avant de run le code, sinon python va afficher qu'il ne trouve 
# pas les images dans le chemin donné.  
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

def niveau_verrou(ligne_actuelle=None):
    """
    Génère un niveau de verrou aléatoire (0, 1 ou 2) selon la position dans le manoir.
    Plus on monte vers l'antichambre (ligne 0), plus les portes sont verrouillées.
    Ligne 8 (départ) : que des portes niveau 0
    Ligne 0 (arrivée) : que des portes niveau 2
    """
    if ligne_actuelle is None:
        return random.randint(0, 2)
    
    # Première rangée (départ) : que des portes déverrouillées
    if ligne_actuelle >= 7:
        return 0
    # Dernière rangée (arrivée) : que des portes niveau 2
    elif ligne_actuelle <= 1:
        return 2
    # Milieu : mélange progressif
    else:
        # Plus on monte, plus de chances d'avoir des portes verrouillées
        rand = random.random()
        if ligne_actuelle >= 5:
            # Rangées 5-6 : 70% niveau 0, 30% niveau 1
            return 0 if rand < 0.7 else 1
        elif ligne_actuelle >= 3:
            # Rangées 3-4 : 40% niveau 0, 40% niveau 1, 20% niveau 2
            if rand < 0.4:
                return 0
            elif rand < 0.8:
                return 1
            else:
                return 2
        else:
            # Rangées 2 : 20% niveau 0, 40% niveau 1, 40% niveau 2
            if rand < 0.2:
                return 0
            elif rand < 0.6:
                return 1
            else:
                return 2

# Catalogue complet des pièces (uniquement celles dont l'image existe)
# AJOUT: attribut "rarete" pour chaque pièce (0 = commun, 1 = peu commun, 2 = rare, 3 = très rare)
catalogue_pieces = [
    {"nom": "Bibliothèque", "image": images_pieces["Bibliothèque"], "description": "Utiliser une gemme pour redessiner", "cout": 1, "effet": None, "niveau_verrou": niveau_verrou(), "rarete": 1},
    {"nom": "Couloir", "image": images_pieces["Couloir"], "description": "", "cout": 0, "effet": None, "niveau_verrou": niveau_verrou(), "rarete": 0},
    {"nom": "Chambre", "image": images_pieces["Chambre"], "description": "Gagnez 2 pas en entrant", "cout": 0, "effet": "gain_steps", "niveau_verrou": niveau_verrou(), "rarete": 0},
    {"nom": "Coffre", "image": images_pieces["Coffre"], "description": "Nécessite une clé pour entrer", "cout": 0, "effet": None, "niveau_verrou": niveau_verrou(), "rarete": 2},
    {"nom": "Armurerie", "image": images_pieces["Armurerie"], "description": "Gagnez 1 clé en entrant", "cout": 0, "effet": "gain_key", "niveau_verrou": niveau_verrou(), "rarete": 1},
    {"nom": "Cuisine", "image": images_pieces["Cuisine"], "description": "Gagnez un aliment", "cout": 0, "effet": "gain_nourriture", "niveau_verrou": niveau_verrou(), "rarete": 0},
    {"nom": "Salle de sport", "image": images_pieces["Salle de sport"], "description": "Mystère", "cout": 1, "effet": None, "niveau_verrou": niveau_verrou(), "rarete": 1},
    {"nom": "Salle obscure", "image": images_pieces["Salle obscure"], "description": "Salle obscure", "cout": 1, "effet": None, "niveau_verrou": niveau_verrou(), "rarete": 2},
    {"nom": "Garage", "image": images_pieces["Garage"], "description": "Salle mécanique", "cout": 1, "effet": None, "niveau_verrou": niveau_verrou(), "rarete": 1},
    {"nom": "Salle de repos", "image": images_pieces["Salle de repos"], "description": "Salle de repos", "cout": 0, "effet": None, "niveau_verrou": niveau_verrou(), "rarete": 0},
    {"nom": "Salle des trophées", "image": images_pieces["Salle des trophées"], "description": "Gagnez une gemme", "cout": 2, "effet": "gain_gem", "niveau_verrou": niveau_verrou(), "rarete": 2}
]


# NOUVELLE FONCTION: Tirer des pièces en tenant compte de la rareté
def tirer_pieces_avec_rarete(catalogue, nombre=3):
    """
    Tire des pièces aléatoirement en tenant compte de leur rareté.
    Rareté 0 = probabilité 1
    Rareté 1 = probabilité 1/3
    Rareté 2 = probabilité 1/9
    Rareté 3 = probabilité 1/27
    S'assure qu'au moins une pièce coûte 0 gemmes.
    """
    if len(catalogue) < nombre:
        return catalogue
    
    # Calculer les poids en fonction de la rareté
    poids = []
    for piece in catalogue:
        rarete = piece.get("rarete", 0)
        poids.append(1 / (3 ** rarete))
    
    # Tirer les pièces avec les poids
    choix = random.choices(catalogue, weights=poids, k=nombre)
    
    # S'assurer qu'au moins une pièce coûte 0 gemmes
    if not any(p["cout"] == 0 for p in choix):
        pieces_gratuites = [p for p in catalogue if p["cout"] == 0]
        if pieces_gratuites:
            choix[0] = random.choice(pieces_gratuites)
    
    return choix

    

# Définition de la grille qui représente le manoir du jeu 
grille = [[Salle() for _ in range(NB_COLONNES)] for _ in range(NB_LIGNES)]
grille[8][2] = Salle(nom="Hall d'entrée", image=images_pieces["Hall d'entrée"], decouverte=True)
grille[0][2] = Salle(nom="Antichambre", image=images_pieces["Antichambre"], decouverte=True)

# Position intiale du joueur 
NB_LIGNES, NB_COLONNES = 9, 5 # Récupère les dimensions de la grille pour indiquer le domaine de déplacement au joueur
joueur = Joueur("Blue Prince", NB_LIGNES, NB_COLONNES)  # Le joueur peut se déplacer sur l'interface du jeux (sur toute la grille)

"""
Ici on va gérer l'aléatoire de la position des collectables dans le manoir
"""
# ici, on va faire un random pour les positions des differents objets collectables dans le manoir
position_possible = []
for i in range(NB_LIGNES):
    for j in range(NB_COLONNES):
        position = (i, j) 
        # Ne pas placer d'objets sur la position de départ et d'arrivée
        if position != (8, 2) and position != (0, 2):
            position_possible.append(position)

# On mélange et on prend autant de positions qu'il y a d'objets
position_aleatoire = random.sample(position_possible, min(len(COLLECTABLES_CATALOGUE), len(position_possible)))

pos_objet = []
for objet, pos in zip(COLLECTABLES_CATALOGUE, position_aleatoire):
    pos_objet.append(PLACEMENT_OBJET(objet, pos))

# CORRECTION: On ne collecte PAS les objets ici, on le fait dans la boucle principale
# Supprimé le code qui collectait les objets avant même de commencer le jeu

ARRIVEE = (0, 2)   # case correspondante à l'antichambre 

# La position du joueur est maintenant joueur.position. (on a nommé self = joueur)
# L'inventaire est maintenant joueur.inventaire .
# On initialise ici le Hall d'entrée (position initiale du joueur).
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
            
            # AJOUT: Afficher un petit indicateur si un objet est présent et non collecté
            for objet_present in pos_objet:
                if not objet_present.collecte and objet_present.position == (ligne, colonne):
                    pygame.draw.circle(fenetre, OR, (x + TAILLE_CASE - 10, y + 10), 5)
            
            # Utilisation de joueur.position
            if [ligne, colonne] == joueur.position: 
                pygame.draw.rect(fenetre, (0, 191, 255), (x + 10, y + 10, TAILLE_CASE - 20, TAILLE_CASE - 20))


# Affichage de l'inventaire
def afficher_inventaire():
    x_offset = LARGEUR_GRILLE + 20
    y_offset = 20
    fenetre.blit(police_titre.render("Inventaire", True, NOIR), (x_offset, y_offset))
    # Utilisation de joueur.inventaire
    for i, (cle, valeur) in enumerate(joueur.inventaire.items()): 
        texte = f"{cle}: {valeur}"
        fenetre.blit(police.render(texte, True, NOIR), (x_offset, y_offset + 30 + i * 25))
    
    # AJOUT: Afficher les objets permanents activés
    y_permanent = y_offset + 30 + len(joueur.inventaire) * 25 + 20
    fenetre.blit(police_titre.render("Objets permanents:", True, NOIR), (x_offset, y_permanent))
    y_permanent += 30
    for nom, possede in joueur.objets_permanents.items():
        if possede:
            fenetre.blit(police.render(f"✓ {nom}", True, (0, 150, 0)), (x_offset, y_permanent))
            y_permanent += 25


# Affichage du menu de tirage:
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

# fonction d'affichage d'un message défaite + écran  condition de défaite
def afficher_defaite():
    fenetre.fill((0, 0, 139))  # définition d'un écran bleu
    police_defaite = pygame.font.SysFont("Arial", 80)
    texte = police_defaite.render("GAME OVER!", True, (220, 20, 60))
    rect = texte.get_rect(center=(LARGEUR_FENETRE // 2, HAUTEUR_FENETRE // 2))
    fenetre.blit(texte, rect)
    pygame.display.update()
    
# fonction d'affichage d'un message victoire
def afficher_victoire():
    fenetre.fill((0, 0, 139))  # fond bleu clair (SteelBlue)
    police_victoire = pygame.font.SysFont("Arial", 80)
    texte = police_victoire.render("VICTOIRE !", True, (255, 215, 0)) # couleur dorée
    rect = texte.get_rect(center=(LARGEUR_FENETRE // 2, HAUTEUR_FENETRE // 2))
    fenetre.blit(texte, rect)
    pygame.display.update()

# fonction pour défaite si bloqué (plus de possibilité d'évoluer vers l'antichambre)
def chemin_vers_arrivee_existe(grille, joueur, ARRIVEE):
    nb_lignes = len(grille)
    nb_colonnes = len(grille[0])

    # Convertir la position du joueur en tuple (obligatoire pour le set)
    position_depart = (joueur.position[0], joueur.position[1])

    file = deque([position_depart])
    visites = {position_depart}

    while file:
        x, y = file.popleft()

        # Si on atteint l'arrivée
        if (x, y) == ARRIVEE:
            return True

        # Déplacements haut, bas, gauche, droite
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x + dx, y + dy

            if 0 <= nx < nb_lignes and 0 <= ny < nb_colonnes:

                salle = grille[nx][ny]

                accessible = True
                # CORRECTION: Vérifier si on peut ouvrir avec le kit de crochetage
                if salle.necessite_cle:
                    if joueur.inventaire["Clés"] <= 0:
                        # Si c'est une porte niveau 1 et qu'on a le kit, c'est accessible
                        if not (salle.niveau_verrou == 1 and joueur.objets_permanents["Kit de crochetage"]):
                            accessible = False

                if accessible and (nx, ny) not in visites:
                    visites.add((nx, ny))
                    file.append((nx, ny))

    return False

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
                                # CORRECTION: Vérifier si on peut ouvrir avec le kit de crochetage
                                if not (verrou == 1 and joueur.objets_permanents["Kit de crochetage"]):
                                    print(f"Pas assez de clés pour placer {choix['nom']} (niveau {verrou})")
                                    continue
                            
                            joueur.inventaire["Gemmes"] -= cout
                            print(f"-{cout} gemme(s) dépensée(s). Gemmes restantes : {joueur.inventaire['Gemmes']}")

                            # CORRECTION: Utiliser le kit de crochetage si disponible
                            if verrou == 1 and joueur.objets_permanents["Kit de crochetage"]:
                                print("Porte ouverte avec le kit de crochetage!")
                            elif verrou > 0:
                                joueur.inventaire["Clés"] -= verrou
                                print(f"-{verrou} clé(s) utilisée(s). Clés restantes : {joueur.inventaire['Clés']}")
                        
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

                            # CORRECTION: Utiliser la méthode declencher_effet de la classe Salle
                            nouvelle_salle.declencher_effet(joueur)
                            
                            # Gestion spéciale pour gain_nourriture
                            if nouvelle_salle.effet == "gain_nourriture" and not nouvelle_salle.effet_declenche:
                                aliments = ["Pomme", "Banane", "Gâteau", "Sandwich", "Repas"]
                                aliment_choisi = random.choice(aliments)
                                
                                # Trouver l'objet correspondant
                                montants = {"Pomme": 2, "Banane": 3, "Gâteau": 10, "Sandwich": 15, "Repas": 25}
                                joueur.inventaire["Pas"] += montants.get(aliment_choisi, 2)
                                nouvelle_salle.effet_declenche = True
                                print(f"Vous avez trouvé un aliment : {aliment_choisi} ! +{montants.get(aliment_choisi, 2)} pas")

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
                            # CORRECTION: Utiliser la fonction avec rareté
                            choix_pieces = tirer_pieces_avec_rarete(catalogue_pieces, 3)
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
                    
                    # CORRECTION: Gestion améliorée avec kit de crochetage
                    if salle_cible.niveau_verrou > 0 and not salle_cible.decouverte:
                        # Si c'est niveau 1 et qu'on a le kit, pas besoin de clé
                        if salle_cible.niveau_verrou == 1 and joueur.objets_permanents["Kit de crochetage"]:
                            print("Porte niveau 1 ouverte avec le kit de crochetage!")
                        elif joueur.inventaire["Clés"] >= salle_cible.niveau_verrou:
                            joueur.inventaire["Clés"] -= salle_cible.niveau_verrou
                            print(f"Porte niveau {salle_cible.niveau_verrou} ouverte avec une clé")
                        else:
                            print("Porte verrouillée, clé requise")
                            continue

                    joueur.position[0], joueur.position[1] = nouvelle_ligne, nouvelle_colonne
                    joueur.inventaire["Pas"] -= 1

                    # AJOUT: Vérifier si un objet est présent à cette position
                    for objet_present in pos_objet:
                        if not objet_present.collecte and tuple(joueur.position) == objet_present.position:
                            objet_present.objet.appli_effets(joueur)
                            objet_present.collecte = True

                    if not salle_cible.decouverte:
                        # CORRECTION: Utiliser la fonction avec rareté
                        choix_pieces = tirer_pieces_avec_rarete(catalogue_pieces, 3)
                        selection_piece = True
                        index_selection = 0
                    else:
                        # CORRECTION: Utiliser la méthode declencher_effet
                        salle_cible.declencher_effet(joueur)

        afficher_grille()
        afficher_inventaire()
        afficher_choix_pieces()

        #salle_actuelle = grille[joueur.position[0]][joueur.position[1]]

        # Condition de défaite 1: Plus de pas
        if joueur.inventaire["Pas"] <= 0:
             print("Défaite 😢😢 Plus de pas disponibles")
             son_defaite.play()
             afficher_defaite()
             pygame.time.wait(3000)
             pygame.quit()
             sys.exit()

        # Condition de défaire 2: Bloqué (impossible d'atteindre l'arrivée)
        if not chemin_vers_arrivee_existe(grille, joueur, ARRIVEE):
            print("Défaite ! Vous êtes bloqué, impossible d'atteindre l'antichambre")
            son_defaite.play()
            afficher_defaite()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()

        # Condition de victoire
        if joueur.position == [0, 2]:
            print("Victoire ! Vous avez atteint l'Antichambre !")
            son_victoire.play()
            afficher_victoire()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()
        
        pygame.display.update()
        horloge.tick(60)

principal()


