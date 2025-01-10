import global_variables  # Importer les variables globales

from Cblock import Block

class Etape:
    """Représente une étape, contenant des blocs."""
    def __init__(self, numero, y, width):
        self.numero = numero
        self.y = y
        self.width = width
        self.blocs = []

    def add_block(self, block=None):
        """Ajouter un bloc à l'étape."""
        if block is None:
            # Création d'un nouveau bloc
            etape_position = len(self.blocs)
            block = Block.create(self.numero, etape_position, parent_etape=self)

        # Ajouter le bloc à la liste et réorganiser
        self.blocs.append(block)
        self.reorganize_blocks()  # Recentre les blocs


    def remove_block(self, block):
        """Supprimer un bloc de cette étape."""
        if block in self.blocs:
            block.clear_connections()  # Vider les connexions
            self.blocs.remove(block)  # Retirer le bloc de la liste
            self.reorganize_blocks()  # Réorganiser les positions des blocs


    def reorganize_blocks(self):
        """Recentrer les blocs horizontalement dans l'étape."""
        block_count = len(self.blocs)
        if block_count == 0:
            return

        spacing = (self.width - block_count * global_variables.BLOC_WIDTH) // (block_count + 1)
        current_x = spacing

        for index, block in enumerate(self.blocs):
            block.x = current_x + global_variables.BLOC_WIDTH // 2
            block.y = self.y
            block.etape_position = index
            current_x += global_variables.BLOC_WIDTH + spacing
            #print(f"Bloc {block.identifiant}: x={block.x}, y={block.y}, width={global_variables.BLOC_WIDTH}")

    def draw(self, canvas, selected_to_connect_blocks, selected_etape=False):
        """
        Dessiner l'étape sur le canvas.
        """
        # Définir la couleur de l'entourage pour l'étape

        step_top = self.y - global_variables.ETAPE_HEIGHT // 2
        step_bottom = self.y + global_variables.ETAPE_HEIGHT // 2
        outline_color = global_variables.Couleur_SelectEtape if selected_etape else ""

        canvas.create_rectangle(
            10, step_top, self.width - 10, step_bottom,
            fill=global_variables.Couleur_Etape, outline=outline_color, width=4 if outline_color else 1, tags=("etape", self.numero)
        )

        # Dessiner les blocs dans l'étape
        for i, block in enumerate(self.blocs):
            is_source = block in selected_to_connect_blocks["green"]
            is_target = block in selected_to_connect_blocks["red"]

            block_tags = ("block", self.numero, i)  # Tags pour chaque bloc
            # block.draw(canvas, block.x, self.y, is_source=is_source, is_target=is_target, selected=selected, tags=block_tags)
            block.draw(canvas, block.x, self.y, is_source=is_source, is_target=is_target, tags=block_tags)


    def get_connections_for_block(self, block, connections):
        """Retourner les connexions où le bloc est impliqué."""
        block_connections = [
            conn for conn in connections
            if conn["start"] == block or conn["end"] == block
        ]
        return block_connections
    

    def move_block_laterally(self, block_to_move, direction):
        """
        Déplace un bloc vers la gauche ou la droite dans l'étape.
        
        Args:
            block_to_move (Block): Le bloc à déplacer.
            direction (str): "left" pour gauche, "right" pour droite.
        
        Returns:
            bool: True si le déplacement a été effectué, False sinon.
        """
        try:
            block_idx = self.blocs.index(block_to_move)
        except ValueError:
            print(f"Le bloc {block_to_move.title} n'est pas dans l'étape {self.numero}.")
            return False

        if direction == "left" and block_idx > 0:
            # Échanger avec le bloc à gauche
            self.blocs[block_idx], self.blocs[block_idx - 1] = self.blocs[block_idx - 1], self.blocs[block_idx]
            print(f"Bloc déplacé à gauche : {block_to_move.title}")
            return True
        elif direction == "right" and block_idx < len(self.blocs) - 1:
            # Échanger avec le bloc à droite
            self.blocs[block_idx], self.blocs[block_idx + 1] = self.blocs[block_idx + 1], self.blocs[block_idx]
            print(f"Bloc déplacé à droite : {block_to_move.title}")
            return True
        else:
            print(f"Impossible de déplacer le bloc {block_to_move.title} vers {direction}.")
            return False

    @staticmethod
    def from_dict(data):
        """Créer une étape à partir d'un dictionnaire."""
        etape = Etape(numero=data["numero"], y=data["y"], width=data["width"])
        
        # Charger directement les blocs dans la liste
        etape.blocs = [Block.from_dict(block_data) for block_data in data["blocs"]]
        
        return etape
