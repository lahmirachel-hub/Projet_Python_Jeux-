 #Les filles le commentaire est à ajouté dans le doc du cours rapport expliquant le code - Menouha Rachel


# Le fichier ci-contre, classes.py contient la création des classes d'objets du jeu.
# Attention ce fichier doit absolument être dans le même répertoire que celui du code contenant
# la pipeline global du jeu. (On va importer les classes créées d'ici, dans le code principal).
# On procède ainsi pour que le code principal ne soit pas trop long et complexe. 

import random

# Création classe joueur = représente le joueur et ses actions dans le manoir.
class Joueur:
    """Cette classe représente le joueur et son état complet(nom, prénom, nombre pas restants...)
      dans le jeu Blue Prince."""
    # Le constructeur nous est utile pour créer et initialiser un objet de la classe 
    # (ici :  on initialise tous les attributs du joueur = son nom, sa position, son nombre de pas... )
    def __init__(self, nom, lignes, colonnes):
        # Correction de l'erreur: le premier paramètre doit être 'self'
        # et les attributs doivent être assignés à 'self'.
        
        self.nom = nom
        # Position initiale du joueur : (ligne, colonne). 8, 2 correspond à 'Entrance Hall'
        self.position = [8, 2] 
        self.lignes = lignes
        self.colonnes = colonnes
        
        # Inventaire du joueur (conforme à la section 2.1 de l'énoncé et au code Pygame)
        self.inventaire = {
            "Pas": 70,       # Initialement à 70 [cite: 246]
            "Or": 0,         # Initialement à 0 [cite: 247]
            "Gemmes": 2,     # Initialement à 2 [cite: 248]
            "Clés": 0,       # Initialement à 0 (le code Pygame utilise 1, nous suivons l'énoncé) [cite: 249]
            "Dés": 0         # Initialement à 0 [cite: 250]
        }
        
        # Objets permanents (non implémentés dans le Pygame de Bousadia, mais prêts)
        self.objets_permanents = {
            "Pelle": False,
            "Marteau": False,
            "Kit de crochetage": False, # Permet d'ouvrir les portes niveau 1 sans clé [cite: 254, 324]
            "Détecteur de métaux": False,
            "Patte de lapin": False
        }
        
    def perdre_pas(self):
        """Décrémente le compte de pas de 1."""
        if self.inventaire["Pas"] > 0:
            self.inventaire["Pas"] -= 1
            return True
        return False
        
    def gagner_ressource(self, ressource, quantite):
        """Augmente la quantité d'une ressource de l'inventaire."""
        if ressource in self.inventaire:
            self.inventaire[ressource] += quantite
            print(f"{self.nom} a gagné {quantite} de {ressource}")
            return True
        return False

    def deplacer(self, direction):
        """Calcule la nouvelle position après un déplacement (Z, Q, S, D)."""
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
        
        return None, None # Déplacement impossible
    

# === FICHIER: classes.py (Classe Room) ===

class Room:
    def trigger_effect(self, player):
        """
        Déclenche l'effet de la pièce si elle n'a pas été découverte et que l'effet n'a pas été activé.
        :param player: L'objet Joueur qui entre dans la pièce.
        """
        if self.effect is not None and not self.effect_triggered:
            if self.effect == "gain_steps":
                player.gagner_ressource("Pas", 2)
                print("Effet activé : +2 pas")
            elif self.effect == "gain_key":
                player.gagner_ressource("Clés", 1)
                print("Effet activé : +1 clé")
            elif self.effect == "gain_die":
                player.gagner_ressource("Dés", 1)
                print("Effet activé : +1 dé")
            # NOTE : Le code ci-dessus est pour les effets simples.
            # Les sous-classes vont surcharger cette méthode pour les cas Trap et Treasure.
            
            # Si l'effet est un effet simple géré ici, on le marque comme déclenché.
            if self.effect in ["gain_steps", "gain_key", "gain_die"]:
                self.effect_triggered = True
                return True
            
            return False # Retourne False si l'effet est géré par une sous-classe ou inconnu
        return False


class TreasureRoom(Room):
    """
    Représente une pièce Trésor. 
    Hérite de Room.
    L'effet déclenche un gain d'Or aléatoire et coûte un pas pour en sortir.
    """
    def __init__(self, name, image, discovered=False, locked_level=0, effect="treasure", effect_triggered=False):
        # Appel du constructeur de la classe mère (Room)
        super().__init__(name, image, discovered, locked_level, effect, effect_triggered)
        
    def trigger_effect(self, player):
        if not self.effect_triggered:
            # 1. Gain d'Or aléatoire (ex: entre 5 et 15 Or)
            gain_or = random.randint(5, 15)
            player.gagner_ressource("Or", gain_or)
            print(f"Trésor découvert! Vous gagnez {gain_or} Or. Coût: 1 Pas de plus pour quitter la pièce.")
            
            # 2. Coût additionnel d'un Pas
            if player.inventaire["Pas"] > 0:
                player.inventaire["Pas"] -= 1 # Perte d'un pas directement dans l'inventaire
                
            self.effect_triggered = True
            return True
        return False
    

    # === FICHIER: classes.py (Suite) ===

class TrapRoom(Room):
    """
    Représente une pièce Piège. 
    Hérite de Room.
    L'effet fait perdre des Pas au joueur.
    """
    def __init__(self, name, image, discovered=False, locked_level=0, effect="trap", effect_triggered=False):
        # Appel du constructeur de la classe mère (Room)
        super().__init__(name, image, discovered, locked_level, effect, effect_triggered)
        
    def trigger_effect(self, player):
        if not self.effect_triggered:
            # Perte de Pas aléatoire (ex: entre 3 et 7 Pas)
            perte_pas = random.randint(3, 7)
            
            # S'assurer que le joueur ne passe pas en Pas négatifs
            if player.inventaire["Pas"] >= perte_pas:
                player.inventaire["Pas"] -= perte_pas
                print(f"Piège activé! Vous perdez {perte_pas} Pas...")
            elif player.inventaire["Pas"] > 0:
                # Perdre le reste des Pas si c'est moins que la pénalité
                perte_reelle = player.inventaire["Pas"]
                player.inventaire["Pas"] = 0
                print(f"Piège activé! Vous perdez tous vos {perte_reelle} Pas restants.")
            else:
                print("Piège activé, mais vous n'aviez plus de Pas à perdre.")
                
            self.effect_triggered = True
            return True
        return False