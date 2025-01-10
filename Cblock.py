import global_variables  # Importer les variables globales
from general_functions import charger_sous_titres_from_Projet_playlist

class Block:
    id_counter = 0  # Compteur global pour générer les identifiants

    """Représente un bloc dans une étape."""
    def __init__(self, etape_number, etape_position, identifiant, title="Bloc", comment="", playlist_lien="", playlist=None, parent_etape=None):
        self.etape_number = etape_number
        self.etape_position = etape_position
        self.identifiant = identifiant
        self.title = title
        self.comment = comment
        self.playlist_lien = playlist_lien
        self.playlist = playlist or []  # Liste vide par défaut
        self.blocs_precedents = []
        self.blocs_suivants = []
        self.x = 0
        self.y = 0
        self.parent_etape = parent_etape  # Référence à l'étape parente
        self.isSelected = False

    @classmethod
    def initialize_counter(cls, existing_ids):
        """
        Initialiser le compteur basé sur les identifiants existants.
        Args:            existing_ids (list): Liste des identifiants existants sous forme de chaînes.
        """
        if existing_ids:
            max_id = max(int(identifiant) for identifiant in existing_ids if identifiant.isdigit())
            cls.id_counter = max_id + 1
        else:
            cls.id_counter = 1  # Commence à 1 si aucune donnée
    
    @classmethod
    def create(cls, etape_number, etape_position, parent_etape=None):
        """Créer un nouveau bloc avec un identifiant unique basé sur le compteur."""
        identifiant = f"{cls.id_counter:04}"  # Formaté sur 4 chiffres
        cls.id_counter += 1
        return cls(etape_number, etape_position, identifiant, parent_etape=parent_etape)


    #def draw(self, canvas, x, y, is_source=False, is_target=False, selected=False, tags=None):
    def draw(self, canvas, x, y, is_source=False, is_target=False, tags=None):
        outline_color = ""
        #print(f"valeur de self.isSelected dans class Block :  {self.isSelected} ")
        # Déterminer la couleur de l'entourage
        #if selected:
        if self.isSelected:
            outline_color = global_variables.Couleur_BlocSelect
        else:
            outline_color = global_variables.Couleur_BlocDefaut            
        if is_source:
            #print(f"valeur is_source :  {is_source} ")
            outline_color = global_variables.Couleur_BlocSource
        elif is_target:
            #print(f"valeur is_target :  {is_target} ")
            outline_color = global_variables.Couleur_BlocTarget

        # Dessiner le rectangle du bloc
        canvas.create_rectangle(
            x - global_variables.BLOC_WIDTH // 2, y - global_variables.BLOC_HEIGHT // 2, 
            x + global_variables.BLOC_WIDTH // 2, y + global_variables.BLOC_HEIGHT // 2,
            fill=global_variables.Couleur_Bloc,
            outline=outline_color,
            width=3 if outline_color else 1,
            tags=tags
        )
        # Calculer la position de départ pour l'alignement à gauche
        left_x = x - (global_variables.BLOC_WIDTH // 2) + 10  # Marge gauche de 10 pixels 

        # Ajouter les textes (titre, commentaire, lien)
        text_y_offset = -25  # Décalage initial pour le premier texte
        canvas.create_text(
            left_x, y + text_y_offset, text= "BLOCK: " + self.identifiant, font=("Arial", 8), fill=global_variables.Couleur_Liaison, anchor="w", tags=tags
        )           
        if len(self.playlist):
            subtitle = charger_sous_titres_from_Projet_playlist(self.playlist)
            text_y_offset = -10  # Décalage initial pour le premier texte
            canvas.create_text(
                left_x, y + text_y_offset, text="In > " + self.get_SousTitre(subtitle, 0) , font=("Arial", 9), anchor="w", tags=tags
            )        
            text_y_offset += 12  # Décalage pour le commentaire
            canvas.create_text(
                left_x + 2, y + text_y_offset, text="↓", font=("Arial", 12, "bold"), fill=global_variables.Couleur_Liaison, anchor="w", tags=tags
            )
            text_y_offset += 15  # Décalage pour le commentaire
            canvas.create_text(
                left_x, y + text_y_offset, text="Out > " + self.get_SousTitre(subtitle, -1), font=("Arial", 9), anchor="w", tags=tags
            )   

    def get_SousTitre(self, subtitle, index):    
        #subtitle = charger_sous_titres_from_Projet_playlist(self.playlist)
        perso = subtitle[index].get("perso", "Inconnu").capitalize()
        sous_titre = subtitle[index].get("sous_titre", "")                            
        if perso.strip():  # Vérifie si le texte est vide ou contient uniquement des espaces
            perso = perso + " : "
        sous_titre = perso + sous_titre   
        chaine_limitee_tronquee = sous_titre[:40] + " (...)" if len(sous_titre) > 20 else sous_titre
        return chaine_limitee_tronquee

    def clear_connections(self):
        """Supprimer toutes les connexions (précédents et suivants)."""
        self.blocs_precedents.clear()
        self.blocs_suivants.clear()

    def to_dict(self):
        """Convertir le bloc en dictionnaire pour sauvegarde."""
        return {
            "etape_number": self.etape_number,
            "etape_position": self.etape_position,
            "identifiant": self.identifiant,
            "title": self.title,
            "comment": self.comment,
            "playlist_lien": self.playlist_lien,
            "playlist": self.playlist,  # Inclure la playlist dans le dictionnaire
            "blocs_precedents": [bloc.identifiant for bloc in self.blocs_precedents],
            "blocs_suivants": [bloc.identifiant for bloc in self.blocs_suivants],
        }

    @staticmethod
    def from_dict(data):
        """Créer un bloc depuis un dictionnaire."""
        block = Block(
            etape_number=data["etape_number"],
            etape_position=data["etape_position"],
            identifiant=data["identifiant"],
            title=data.get("title", ""),
            comment=data.get("comment", ""),
            playlist_lien=data.get("playlist_lien", ""),
            playlist=data.get("playlist", []),  # Charger la playlist si elle existe
        )
        # Initialement vide, les listes seront remplies après reconstruction
        block.blocs_precedents = data.get("blocs_precedents", [])
        block.blocs_suivants = data.get("blocs_suivants", [])
        return block
