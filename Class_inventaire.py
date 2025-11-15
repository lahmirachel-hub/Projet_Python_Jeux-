class CONSOMMABLE:
    
    """
    Cette classe modifie la quantité des objets consommés par le joueur.
    
    """
    
    
    def __init__(self, nom, quantite):
        self.nom = nom
        self.quantite = quantite
    
    def utiliser(self, joueur):
        if self.quantite > 0:
            self.quantite -= 1
    
class PERMANENT:
    
    """
    Cette classe permet d'activer les objets permanents que le joueur trouvent dans le manoir,
    l'état actif veut dire que le joueur a collecté l'unique objet permanent caché dans le manoir
    
    """
    
    def __init__(self, nom):
        self.nom = nom
        self.actif = False
    
    def activer(self):
        self.actif = True
            
        
class INVENTAIRE:
    def __init__(self):
        self.consommable = {
            "Pas": 70,
            "Gemmes": 2,
            "Clés": 1,
            "Dés": 0
            }
        self.permanent = {
            "Détecteur de métaux": 0,
            "Patte de lapin": 0,
            "Kit de crochetage": 0
            }
        
    def modifier_consommable(self, objet, quantite):
        if objet.nom in self.consommable:
            self.consommable[objet.nom].quantite += quantite
        else:
            self.consommable[objet.nom] = objet
    
    def ajouter_permanent(self, objet):
        self.permanent[objet.nom] = objet
    
    def utiliser_consommable(self, nom, joueur):
         if nom in self.consommables:
            self.consommables[nom].utiliser(joueur)
            
            
