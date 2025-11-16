# Le fichier ci-contre, classes.py contient la création des classes d'objets du jeu.
# Attention ce fichier doit absolument être dans le même répertoire que celui du code contenant
# la pipeline global du jeu. (On va importer les classes créées d'ici, dans le code principal).
# On procède ainsi pour que le code principal ne soit pas trop long et complexe. 

import random

# Création classe joueur = représente le joueur (nom, prénom, nombre pas restants...) et ses actions (nombre de gemmes gagnées, perdues...)
#  dans le manoir  dans le jeu Blue Prince.
class Joueur:
    # Le constructeur est utile pour créer et initialiser un objet d'une classe 
    # (On l'utilise ici pour initialiser tous les attributs du joueur = son nom, sa position, son nombre de pas... )
    def __init__(self, nom, lignes, colonnes):
        # Erreur- On la corrige. Le premier paramètre doit être 'self'
        # et les attributs doivent être assignés à 'self', sinon ça ne fonctionne pas. 

        self.nom = nom
        # Initialisation de la position du joueur (ligne, colonne). 8, 2 correspond à la position de la pièce 'Entrance Hall'
        self.position = [8, 2] 
        self.lignes = lignes
        self.colonnes = colonnes
        
        # Initialisation de l'inventaire du joueur (conforme à la section 2.1 de l'énoncé pour les étudiants en IPS)
        self.inventaire = {
            "Pas": 70,      
            "Gemmes": 2,     
            "Clés": 0,       # Initialement à 0 selon l'énoncé
            "Dés": 0,        # Initialement à 0 selon l'énoncé
            "KitCrochetage": 0,
            "DetecteurMetaux": 0,
            "PatteDeLapin": 0      
        }
        
        # Initialisation des objets permanents .  
        # Le joueur ne les obtient que s'il les trouve dans les pièces, on les initialise tous à False 
        self.objets_permanents = {
            "Pelle": False,
            "Marteau": False,
            "Kit de crochetage": False, # Ce kit permet au joueur d'ouvrir les portes niveau 1 sans perdre de clé 
            "Détecteur de métaux": False,
            "Patte de lapin": False
        }
        
    def perdre_pas(self):
        """Cette fonction calcule et décrémente le compte de pas de 1 pour chaque déplacement du joueur."""
        if self.inventaire["Pas"] > 0:
            self.inventaire["Pas"] -= 1
            return True
        return False
        
    def gagner_ressource(self, ressource, quantite):
        """Cette fonction augmente la quantité d'une ressource de l'inventaire lorsque le joueur en trouve."""
        if ressource in self.inventaire:
            self.inventaire[ressource] += quantite
            print(f"{self.nom} a gagné {quantite} de {ressource}")
            return True
        return False

    def deplacer(self, direction):
        """Cette fonction calcule la nouvelle position après un déplacement 
        (Les déplacements se faisant avec les touches Z, Q, S, D du clavier, on les utilise 
        pour créer la fonction qui implémente le déplacement du joueur)."""
        row, col = self.position
        new_row, new_col = row, col
        
        if direction == 'z' and row > 0:
            new_row -= 1
        elif direction == 's' and row < self.lignes - 1:
            new_row += 1
        elif direction == 'q' and col > 0:
            new_col -= 1
        elif direction == 'd' and col < self.colonnes - 1:
            new_col += 1
            
        if [new_row, new_col] != [row, col]:
            return new_row, new_col
        
        return None, None # Si le déplacement est impossible
    
# Création de la classe Salle pour créer et caractériser chaque salle du jeu 
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
        """Déclenche l'effet de la salle sur le joueur si l'effet n'a pas encore été déclenché"""
        if self.effet_declenche:
            return
            
        if self.effet == "gain_steps":
            joueur.inventaire["Pas"] += 2
            self.effet_declenche = True
            print("Youpi! +2 pas")
        elif self.effet == "gain_key":
            joueur.inventaire["Clés"] += 1
            self.effet_declenche = True
            print("Youpi! +1 clé")
        elif self.effet == "gain_die":
            joueur.inventaire["Dés"] += 1
            self.effet_declenche = True
            print("Youpi! +1 dé")
        elif self.effet == "gain_gem":
            joueur.inventaire["Gemmes"] += 1
            self.effet_declenche = True
            print("Youpi! +1 gemme")

# Création classe des objets collectables au cours du jeu = représente les objets dissimulés dans le jeu (nourriture...).
# Ces objets sont ajoutés à l'inventaire du joueur lorsqu'il les trouve. 
class ObjetCollectable:
    
    def __init__(self, nom, resource_cle, montant, type_objet="Consommable"):
        """On crée un constructeur de la classe ObjetCollectable pour initialiser les objets collectables. 
        Le paramètre nom représente le nom de l'objet (par ex = pomme).
        Le paramètre ressource_cle représente l'élément de l'inventaire à modifier (par ex = Pas).
        Le paramètre montant représente le montant à ajouter à l'inventaire (pour l'incrémentation des pas par exemple).
        Le paramètre type_objet représente le type d'objet à modifier dans l'inventaire 
        # (Nourriture). 
        """
        self.nom = nom
        self.resource_cle = resource_cle
        self.montant = montant
        self.type_objet = type_objet 

    def appli_effets(self, player):
        """Cette fonction applique l'effet de l'objet sur l'inventaire du joueur
        (par exemple s'il trouve une pomme, il gagne 2 pas).
        Elle ajoute la ressource à l'inventaire du joueur.
        Le paramètre player représente la classe Joueur dans laquelle se trouve l'inventaire à modifier.
        """
        # On utilise un if .
        # Si la ressource (une clé par ex) existe dans l'inventaire du joueur, alors on l'implémente 
        # selon le montant supplémentaire donné par l'objet trouvé. Sinon, on affiche un bugg. 
        if self.resource_cle in player.inventaire:
            player.inventaire[self.resource_cle] += self.montant
            print(f"Objet trouvé : {self.nom} ! +{self.montant} {self.resource_cle}.")
            print(f"Bravo! Vous avez gagné {self.montant} {self.resource_cle}")
            
            # Si c'est un objet permanent, on active aussi le flag correspondant
            if self.type_objet == "Permanent":
                if self.nom == "Kit de crochetage":
                    player.objets_permanents["Kit de crochetage"] = True
                elif self.nom == "Détecteur de métaux":
                    player.objets_permanents["Détecteur de métaux"] = True
                elif self.nom == "Patte de lapin":
                    player.objets_permanents["Patte de lapin"] = True
            
            return True
        else:
            print(f"Bugg : La ressource {self.resource_cle} n'existe pas dans l'inventaire.")
            return False


# On définit un catalogue d'objets spécifiques pour placer ensuite avec un 
# tirage aléatoire ces objets dans le manoir (dans les différentes pièces)
# CORRECTION: On crée des objets individuels au lieu de listes
COLLECTABLES_CATALOGUE = [
    # Objet de type Nourriture. Effet = incrémente le nombre de pas : 
    ObjetCollectable(nom="Pomme", resource_cle="Pas", montant=2, type_objet="Nourriture"),
    ObjetCollectable(nom="Pomme", resource_cle="Pas", montant=2, type_objet="Nourriture"),
    ObjetCollectable(nom="Pomme", resource_cle="Pas", montant=2, type_objet="Nourriture"),
    ObjetCollectable(nom="Banane", resource_cle="Pas", montant=3, type_objet="Nourriture"),
    ObjetCollectable(nom="Banane", resource_cle="Pas", montant=3, type_objet="Nourriture"),
    ObjetCollectable(nom="Gâteau", resource_cle="Pas", montant=10, type_objet="Nourriture"),
    ObjetCollectable(nom="Gâteau", resource_cle="Pas", montant=10, type_objet="Nourriture"),
    ObjetCollectable(nom="Sandwich", resource_cle="Pas", montant=15, type_objet="Nourriture"),
    ObjetCollectable(nom="Sandwich", resource_cle="Pas", montant=15, type_objet="Nourriture"),
    ObjetCollectable(nom="Repas", resource_cle="Pas", montant=25, type_objet="Nourriture"),
    ObjetCollectable(nom="Kit de crochetage", resource_cle="KitCrochetage", montant=1, type_objet="Permanent"),
    ObjetCollectable(nom="Détecteur de métaux", resource_cle="DetecteurMetaux", montant=1, type_objet="Permanent"),
    ObjetCollectable(nom="Patte de lapin", resource_cle="PatteDeLapin", montant=1, type_objet="Permanent"),
    # Ajout de quelques clés et gemmes
    ObjetCollectable(nom="Clé", resource_cle="Clés", montant=1, type_objet="Consommable"),
    ObjetCollectable(nom="Clé", resource_cle="Clés", montant=1, type_objet="Consommable"),
    ObjetCollectable(nom="Gemme", resource_cle="Gemmes", montant=1, type_objet="Consommable"),
]

    
class PLACEMENT_OBJET:
    """
    Cette classe définit la position et l'état de collecte d'un objet en particulier
    """
    def __init__(self, objet, position):
        self.objet = objet
        self.position = position
        self.collecte = False
        
        
        