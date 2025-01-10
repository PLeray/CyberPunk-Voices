import global_variables  # Importer les variables globales

from Cetape import Etape

class Sequence:
    def __init__(self, name):
        self.name = name
        self.etapes = []
        self.connections = []  # Liste des connexions entre blocs


    def add_connection(self, source, target):
        # Ajouter une connexion entre deux blocs.
        print(f"Ajouter une connexion entre deux blocs")
        if source.etape_number == target.etape_number:
            print("Les connexions au sein d'une même étape ne sont pas autorisées.")
            return

        # Vérifiez si la connexion existe déjà
        for conn in self.connections:
            if conn["start"] == source and conn["end"] == target:
                print(f"Connexion déjà existante : {source.identifiant} -> {target.identifiant}")
                return

        # Ajouter la connexion
        self.connections.append({"start": source, "end": target})

        # Mettre à jour les connexions des blocs
        source.blocs_suivants.append(target)
        target.blocs_precedents.append(source)

        print(f"Connexion ajoutée : {source.identifiant} -> {target.identifiant}")

    def update_connections(self):
        """Mettre à jour les connexions entre blocs après des modifications dans les étapes."""
        updated_connections = []

        for conn in self.connections:
            start_block = conn["start"]
            end_block = conn["end"]

            # Vérifiez que les étapes des blocs existent toujours
            if start_block.etape_number >= len(self.etapes) or end_block.etape_number >= len(self.etapes):
                print(f"Connexion supprimée : {start_block.identifiant} -> {end_block.identifiant}")
                continue

            # Ajouter la connexion valide à la liste mise à jour
            updated_connections.append(conn)

        # Remplacez les connexions par celles mises à jour
        self.connections = updated_connections

    def delete_connection(self, block):
        """
        Supprime toutes les références au bloc donné dans les autres blocs.
        Args:
            block (Block): Le bloc dont on supprime les connexions.
        """
        for conn in self.connections[:]:  # Itérer sur une copie pour pouvoir modifier la liste
            if conn["start"] == block:
                # Vérifier que le bloc à supprimer existe dans blocs_precedents
                if block in conn["end"].blocs_precedents:
                    conn["end"].blocs_precedents.remove(block)
                self.connections.remove(conn)
            elif conn["end"] == block:
                # Vérifier que le bloc à supprimer existe dans blocs_suivants
                if block in conn["start"].blocs_suivants:
                    conn["start"].blocs_suivants.remove(block)
                self.connections.remove(conn)

        # Nettoyer les connexions du bloc donné
        block.clear_connections()

    def add_etape(self, selected_etape=None):
        """Ajouter une étape juste après l'étape sélectionnée, ou à la fin."""
        if selected_etape is not None:
            new_index = selected_etape.numero + 1
        else:
            new_index = len(self.etapes)

        # Créer une nouvelle étape
        #y = self.HAUTEUR * new_index + self.SEPARATION
        y = new_index * (global_variables.ETAPE_HEIGHT + global_variables.ETAPE_SPACING) + global_variables.ETAPE_HEIGHT // 2
        new_etape = Etape(new_index, y, self.etapes[0].width if self.etapes else 800)

        # Insérer la nouvelle étape et décaler les suivantes
        self.etapes.insert(new_index, new_etape)
        self.reorganize_etapes()
        

    def remove_etape(self, etape):
        """Supprimer une étape de la séquence."""
        if etape in self.etapes:
            # Supprimer les blocs et leurs connexions
            for block in etape.blocs:
                block.clear_connections()

            # Retirer l'étape de la liste
            self.etapes.remove(etape)

            # Réorganiser les numéros et positions des étapes restantes
            for idx, remaining_etape in enumerate(self.etapes):
                remaining_etape.numero = idx
                #remaining_etape.y = self.SEPARATION + idx * self.HAUTEUR
                remaining_etape.y = idx * (global_variables.ETAPE_HEIGHT + global_variables.ETAPE_SPACING) + global_variables.ETAPE_HEIGHT // 2
                
                # Réajuster les numéros des étapes pour les blocs
                for block in remaining_etape.blocs:
                    block.etape_number = idx

    def reorganize_etapes(self):
        """Réorganiser les étapes en ajustant leurs positions Y."""
        """
        for idx, etape in enumerate(self.etapes):
            etape.numero = idx
            etape.y = self.HAUTEUR * idx + self.SEPARATION        
        """
        for idx, etape in enumerate(self.etapes):
            etape.numero = idx
            etape.y = idx * (global_variables.ETAPE_HEIGHT + global_variables.ETAPE_SPACING) + global_variables.ETAPE_HEIGHT // 2
            #print(f"Étape {etape.numero}: y={etape.y}, height={global_variables.ETAPE_HEIGHT}, spacing={global_variables.ETAPE_SPACING}")


    def draw(self, canvas, selected_to_connect_blocks, selected_etape=None):
        """Dessiner toutes les étapes et connexions."""
        for etape in self.etapes:
            etape.draw(
                canvas,
                selected_to_connect_blocks,
                selected_etape=(etape == selected_etape)  # Passe correctement l'étape sélectionnée
            )
    
        # Dessiner les connexions
        for conn in self.connections:
            start = conn["start"]
            end = conn["end"]

            # Validation des coordonnées
            if not hasattr(start, 'x') or not hasattr(start, 'y') or not hasattr(end, 'x') or not hasattr(end, 'y'):
                print(f"Connexion invalide : {conn}")
                continue
            
            # Calcul des points de connexion
            start_x = start.x
            start_y = start.y + global_variables.BLOC_HEIGHT // 2  # Bas du bloc source
            end_x = end.x
            end_y = end.y - global_variables.BLOC_HEIGHT // 2  # Haut du bloc cible

            canvas.create_line(start_x, start_y, end_x, end_y, fill=global_variables.Couleur_Liaison, width=2)


    def find_block(self, block_data):
        identifiant = block_data.get("identifiant")
        if not identifiant:
            #print("Identifiant introuvable dans les données de connexion :", block_data)
            return None

        for etape in self.etapes:
            for block in etape.blocs:
                if block.identifiant == identifiant:
                    #print(f"Bloc trouvé : {identifiant}")
                    return block

        #print(f"Bloc introuvable : {identifiant}")
        return None

    @staticmethod
    def from_dict(data):
        """Créer une séquence à partir d'un dictionnaire."""
        sequence = Sequence(name=data["name"])
        sequence.connections = data.get("connections", [])
        
        # Charger les étapes sans doubler les blocs
        sequence.etapes = [Etape.from_dict(etape_data) for etape_data in data["etapes"]]
        
        return sequence
