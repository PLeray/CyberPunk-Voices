import tkinter as tk
from tkinter import Menu, filedialog, simpledialog
import json, os, webbrowser

import global_variables  # Importer les variables globales
from general_functions import get_Perso_from_Wem, phrase_to_filename
from playlist_functions import set_playlist_data, get_playlist_data, check_unsaved_playlist_changes
from Csequence import Sequence
from Cetape import Etape
from Cblock import Block  # Import de la classe Block
from CpageHTML import PageHTML
from Ctooltip import Tooltip

class ProjetSequence:
    def __init__(self, root):
        self.root = root
        self.root.title("Project window dialog sequence")
        self.root.geometry("800x1000")
        # Variables
        self.sequence = Sequence("Nouvelle Séquence")
        self.selected_etape = None
        self.selected_to_connect_blocks = {"green": [], "red": []}
        self.selected_block = None  # Initialisation ajoutée
        self.file_Projet = "(New Projet)"

        # Frame principale
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Barre de boutons
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, side=tk.TOP)

        self.create_buttons()  # Créez les boutons dans la barre
        self.update_button_state()

        # Canvas pour afficher les séquences
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas avec Scrollbar
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", scrollregion=(0, 0, 1000, 1000))
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(yscrollcommand=self.v_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Créer une fenêtre interne dans le Canvas pour y placer le contenu
        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.window_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # Mise à jour automatique de la région défilable
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")))

        # Événements de défilement avec la molette
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_scroll)  # Windows et macOS
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux (haut)
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))   # Linux (bas)

        # Événements
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<KeyPress>", self.on_key_press)
        self.canvas.bind("<Shift-Button-1>", self.on_shift_click)
        self.canvas.bind("<Control-Button-1>", self.on_ctrl_click)
        self.canvas.focus_set()

        # Ajouter une première étape
        self.add_etape()
        self.mise_a_jour_info_projet()
        self.load_from_file(global_variables.path_dernier_projet)
        # Redimensionnement
        self.root.bind("<Configure>", self.on_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_adjusted_coordinates(self, event):
        #Retourne les coordonnées ajustées pour tenir compte du scroll.
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        return x, y

    def on_mouse_scroll(self, event):
        #Déplacer la scrollbar avec la molette de la souris.
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")  

    def mise_a_jour_info_projet(self, modified = False):
        global_variables.need_to_save_Projet = modified
        #print("mise_a_jour_info_projet")
        #leTitre = "Scenario : " + os.path.splitext(os.path.basename(self.file_Projet))[0]
        leTitre = "Scenario : " + self.sequence.name
        self.root.title(leTitre)
        if modified:
            self.root.title(f"{leTitre} (*)")

    def on_left_click(self, event):
        #Gérer les clics gauche pour sélectionner un bloc ou une étape.
        x, y = self.get_adjusted_coordinates(event)  # Coordonnées corrigées
        clicked = self.canvas.find_closest(x, y)
        tags = self.canvas.gettags(clicked)

        if "block" in tags:
            # Get the block by indices from tags
            etape_idx, block_idx = int(tags[1]), int(tags[2])
            block = self.sequence.etapes[etape_idx].blocs[block_idx]

            # Select the block (Blue outline)
            self.selected_to_connect_blocks = {"green": [], "red": []}  # Reset source/target selections
            self.selected_block = block  # Track selected block

            for etape in self.sequence.etapes:
                for unBlocs in etape.blocs:
                    unBlocs.isSelected = False  
            block.isSelected = True
            self.selected_etape = None  # Clear étape selection
            print(f"Bloc sélectionné : {block.title} Rang {block.etape_position} (Étape {etape_idx}).")

        elif "etape" in tags:
            # Select the étape
            etape_idx = int(tags[1])
            self.selected_etape = self.sequence.etapes[etape_idx]
            self.selected_block = None  # Clear block selection
            self.selected_to_connect_blocks = {"green": [], "red": []}  # Reset source/target selections
            print(f"Étape sélectionnée : {etape_idx}.")

            for etape in self.sequence.etapes:
                for unBlocs in etape.blocs:
                    unBlocs.isSelected = False  
        else:
            # No valid selection
            print("Aucun élément valide sélectionné.")
            self.selected_block = None
            self.selected_etape = None

        self.update_button_state()
        # Redraw to reflect the selection changes
        self.Open_Bloc()
        self.draw_sequence()

    def on_shift_click(self, event):
        #Gérer les clics gauche pour sélectionner un bloc ou une étape.
        x, y = self.get_adjusted_coordinates(event)  # Coordonnées corrigées
        clicked = self.canvas.find_closest(x, y)
        tags = self.canvas.gettags(clicked)

        if "block" in tags:
            etape_idx, block_idx = int(tags[1]), int(tags[2])
            block = self.sequence.etapes[etape_idx].blocs[block_idx]

            # Ajouter le bloc à la liste rouge (cibles) s'il n'y est pas déjà
            if block not in self.selected_to_connect_blocks["red"]:
                self.selected_to_connect_blocks["red"].append(block)
                print(f"Bloc cible ajouté : {block.title} (Étape {etape_idx}).")
            else:
                print(f"Bloc déjà dans les cibles : {block.title}")
        else:
            print("Aucun bloc valide pour la sélection de cibles.")

        self.update_button_state()
        # Redessiner après la sélection
        self.draw_sequence()

    def on_ctrl_click(self, event):
        #Gérer les clics gauche pour sélectionner un bloc ou une étape.
        x, y = self.get_adjusted_coordinates(event)  # Coordonnées corrigées
        clicked = self.canvas.find_closest(x, y)
        tags = self.canvas.gettags(clicked)

        if "block" in tags:
            etape_idx, block_idx = int(tags[1]), int(tags[2])
            block = self.sequence.etapes[etape_idx].blocs[block_idx]

            # Ajouter le bloc à la liste verte (sources) s'il n'y est pas déjà
            if block not in self.selected_to_connect_blocks["green"]:
                self.selected_to_connect_blocks["green"].append(block)
                print(f"Bloc source ajouté : {block.title} (Étape {etape_idx}).")
            else:
                print(f"Bloc déjà dans les sources : {block.title}")
        else:
            print("Aucun bloc valide pour la sélection des sources.")

        self.update_button_state()
        # Redessiner après la sélection
        self.draw_sequence()

    def on_right_click(self, event):
        self.on_left_click(event)
        #Gérer les clics gauche pour sélectionner un bloc ou une étape.
        x, y = self.get_adjusted_coordinates(event)  # Coordonnées corrigées
        clicked = self.canvas.find_closest(x, y)
        tags = self.canvas.gettags(clicked)

        if "block" in tags:
            etape_idx, block_idx = int(tags[1]), int(tags[2])
            self.selected_block = self.sequence.etapes[etape_idx].blocs[block_idx]
            # Configurer le menu contextuel pour les blocs
            self.menu = Menu(self.root, tearoff=0)
            self.menu.add_command(label="Show Block in Playlist", command=self.Open_Bloc)
            self.menu.add_command(label="Import Playlist into Block", command=self.import_playlist_file_to_block)            
            self.menu.add_command(label="Delete Block", command=self.delete_block)
            self.menu.add_command(label="Remove Connections", command=self.delete_connections)
            self.menu.post(event.x_root, event.y_root)
            print(f"Menu for the block {self.selected_block.title} is open.")

        elif "etape" in tags:
            etape_idx = int(tags[1])
            self.selected_etape = self.sequence.etapes[etape_idx]
            # Configurer le menu contextuel pour les étapes
            self.menu = Menu(self.root, tearoff=0)
            self.menu.add_command(label="Add a Block", command=self.add_block)
            self.menu.add_command(label="Delete Step", command=self.delete_etape)
            self.menu.post(event.x_root, event.y_root)
            print(f"Menu for the Step {self.selected_etape.numero} is open.")

    def on_key_press(self, event):
        #Gérer les pressions de touches pour déplacer les blocs dans une étape.
        if self.selected_block:
            block_to_move = self.selected_block
            etape_idx = block_to_move.etape_number
            etape = self.sequence.etapes[etape_idx]

            # Déterminer la direction du déplacement
            direction = None
            if event.keysym == "Left":
                direction = "left"
            elif event.keysym == "Right":
                direction = "right"

            if direction and etape.move_block_laterally(block_to_move, direction):
                # Réorganiser les positions des blocs après le déplacement
                etape.reorganize_blocks()
                # Mettre à jour les connexions
                self.sequence.update_connections()
                # Redessiner la séquence
                self.draw_sequence()

    def update_width_and_reorganize(self):
        #Mettre à jour la largeur des étapes et réorganiser leurs blocs.
        canvas_width = self.canvas.winfo_width()
        for etape in self.sequence.etapes:
            etape.width = canvas_width
            etape.reorganize_blocks()

    def on_resize(self, event):
        #print(f"on_resize")
        self.update_width_and_reorganize()
        self.draw_sequence()

    def draw_sequence(self):
        #Dessiner toute la séquence sur le canvas.
        # Mettre à jour la largeur des étapes et réorganiser
        self.update_width_and_reorganize()
        self.sequence.reorganize_etapes()  # S'assurer que tout est bien aligné
        # Effacer et redessiner
        self.canvas.delete("all")
        # Utiliser la méthode `draw` de la séquence
        self.sequence.draw(
            canvas=self.canvas,
            selected_to_connect_blocks=self.selected_to_connect_blocks,
            selected_etape=self.selected_etape
        )
        # Mettre à jour la région défilable pour la scrollbar
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))  

    def create_buttons(self):
        #Créer les boutons Load, Save, Ajouter Étape, Ajouter Bloc et Connect.
        btn_new_project = tk.Button(self.button_frame, text="New project", command=self.new_project)
        btn_new_project.pack(side=tk.LEFT, padx=5, pady=5)
        Tooltip(btn_new_project, "Créez un nouveau projet.")

        btn_load_from_file = tk.Button(self.button_frame, text="Load project", command=self.load_from_file)
        btn_load_from_file.pack(side=tk.LEFT, padx=5, pady=5)
        Tooltip(btn_load_from_file, "Load a project.")
        
        btn_save_to_file = tk.Button(self.button_frame, text="Save project", command=self.save_to_file)
        btn_save_to_file.pack(side=tk.LEFT, padx=5, pady=5)
        Tooltip(btn_save_to_file, "Save the project.")

        btn_add_etape = tk.Button(self.button_frame, text="Add Step", command=self.add_etape)
        btn_add_etape.pack(side=tk.LEFT, padx=5, pady=5)
        Tooltip(btn_add_etape, "Add a Step to the project.")

        self.btn_connect = tk.Button(self.button_frame, text="Connect Blocks", command=self.create_connections)     
        self.btn_connect.pack(side=tk.LEFT, padx=5, pady=5)
        #btn_connect.config(state="disabled")  # Désactiver le bouton au départ
        # Ajouter l'infobulle au bouton
        txt_aide_connect = (
            "To connect blocks:\n"
            "1) ctrl + click to select one or more Source blocks.\n"
            "2) shift + click to select one or more Destination blocks.\n"
            "3) Now the Connect Blocs button is enabled and you can connect the blocks.\n"
            "Note that you can connect several source blocks to a destination block and vice versa, "
            "but not several source blocks to several destination blocks."
        )
        Tooltip(self.btn_connect, txt_aide_connect)     

        btn_generate_project_html = tk.Button(self.button_frame, text="Create HTML Page", command=self.generate_project_html)
        btn_generate_project_html.pack(side=tk.LEFT, padx=5, pady=5)
        Tooltip(btn_generate_project_html, "Create a HTML Page that show the project.")

        btn_generate_Ogg = tk.Button(self.button_frame, text="Generate ogg sound files", command=self.generate_Ogg)
        btn_generate_Ogg.pack(side=tk.LEFT, padx=5, pady=5)
        Tooltip(btn_generate_Ogg, "Generate ogg audio files that can be played from the HTML page.")

        btn_open_project_web_page = tk.Button(self.button_frame, text="See Html", command=self.open_project_web_page)
        btn_open_project_web_page.pack(side=tk.LEFT, padx=5, pady=5)
        Tooltip(btn_open_project_web_page, "Open th HTML page.")

    def update_button_state(self):
        if self.selected_to_connect_blocks["green"] and self.selected_to_connect_blocks["red"]:
            self.btn_connect.config(state="normal")  # Activer le bouton
        else:
            self.btn_connect.config(state="disabled")  # Désactiver le bouton        

    def open_project_web_page(self):
        project_name = os.path.splitext(os.path.basename(self.file_Projet))[0]
        output_dir = os.path.join(os.path.dirname(self.file_Projet), f"{project_name}_files")
        html_filename = os.path.join(output_dir, f"{global_variables.CheminLocalization + global_variables.CheminLangue}/{project_name}.html")
        #print(f"html_filename lien: {html_filename}.") 
        url = html_filename
        webbrowser.open(url)        

    def Open_Bloc(self):
        if self.selected_block:
            #if self.check_unsaved_Projet_changes():  # Vérifie s'il faut sauvegarder   
            if check_unsaved_playlist_changes(global_variables.playlist_tree):  # Vérifie s'il faut sauvegarder  la playliste          
                global_variables.is_PlayList_From_Projet = True
                set_playlist_data(global_variables.playlist_tree, self.selected_block.playlist)
                global_variables.need_to_save_Playlist = False
                global_variables.playlist_Block_open = self.selected_block

    def import_playlist_file_to_block(self):
        if self.selected_block:
            # Ouvrir une boîte de dialogue pour sélectionner le fichier
            file_path = filedialog.askopenfilename(
                title="Select a JSON playlist",
                filetypes=[("JSON Files", "*.json")]
            )
            if not file_path:
                print("No files selected.")
                return
            else :
                self.import_playlist_to_block(file_path)

    def import_playlist_to_block(self, file_path):
        if self.selected_block:
            leBloc = self.selected_block        
            try:
                # Charger les données de la playlist
                with open(file_path, "r", encoding="utf-8") as file:
                    playlist_data = json.load(file)
                
                # Vérifier si la playlist contient des données
                if not playlist_data or not isinstance(playlist_data, list):
                    print(f"The file {file_path} does not contain a valid playlist.")
                    return
                
                # Assigner les données de la playlist directement au bloc
                leBloc.playlist = playlist_data
                leBloc.playlist_lien = file_path  # Garder une trace du fichier si nécessaire
                leBloc.title = os.path.splitext(os.path.basename(file_path))[0]
                
                # Construire le commentaire à partir de la première ligne
                first_entry = playlist_data[0]
                selected_gender = global_variables.vSexe.get()
                if selected_gender == global_variables.vHomme:
                    perso = get_Perso_from_Wem(first_entry[global_variables.data_M_Voice])  # Valeur pour homme
                    sous_titre = first_entry[global_variables.data_M_SubTitle]
                else:
                    perso = get_Perso_from_Wem(first_entry[global_variables.data_F_Voice])  # Valeur pour femme
                    sous_titre = first_entry[global_variables.data_F_SubTitle]
                
                # Construire le commentaire avec le format requis
                leBloc.comment = f"{perso}:  {sous_titre}"
                
                # A SUPR : Mettre à jour les autres attributs du bloc
                leBloc.playlist_lien = ""
                leBloc.title = os.path.splitext(os.path.basename(file_path))[0]  # Nom du fichier sans extension
                # A SUPR : 
                self.mise_a_jour_info_projet(True)
                self.draw_sequence()

                print(f"Playlist successfully imported: {file_path}")

            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error importing playlist: {e}")

    def add_etape(self):
        #Ajouter une nouvelle étape après l'étape sélectionnée.
        if self.selected_etape is not None:
            # Ajouter avant l'étape sélectionnée
            new_index = self.sequence.etapes.index(self.selected_etape) 
        else:
            # Ajouter à la fin si aucune étape n'est sélectionnée
            new_index = len(self.sequence.etapes)

        y = new_index * (global_variables.ETAPE_HEIGHT + global_variables.ETAPE_SPACING) + global_variables.ETAPE_HEIGHT // 2
        new_etape = Etape(numero=new_index, y=y, width=self.canvas.winfo_width())
        self.sequence.etapes.insert(new_index, new_etape)

        # Réajuster les positions et numéros des étapes suivantes
        for idx, etape in enumerate(self.sequence.etapes):
            etape.numero = idx
            # Réajuster les numéros des étapes pour les blocs
            for block in etape.blocs:
                block.etape_number = idx
            etape.y = idx * (global_variables.ETAPE_HEIGHT + global_variables.ETAPE_SPACING) + global_variables.ETAPE_HEIGHT // 2
        
        self.mise_a_jour_info_projet(True)
        # Redessiner la séquence
        self.draw_sequence()

    def delete_etape(self):
        #Supprimer l'étape sélectionnée.
        if self.selected_etape:
            self.sequence.remove_etape(self.selected_etape)  # Appel à Sequence.remove_etape
            self.selected_etape = None
            self.draw_sequence()
            print("Étape supprimée.")
            self.mise_a_jour_info_projet(True)

    def add_block(self):
        #Ajouter un bloc dans l'étape sélectionnée.
        if not self.selected_etape:
            print("Aucune étape sélectionnée pour ajouter un bloc.")
            return
        self.selected_etape.add_block()
        self.draw_sequence()
        print(f"Bloc ajouté à l'étape {self.selected_etape.numero}.")
        self.mise_a_jour_info_projet(True)

    def delete_block(self):
        #Supprimer le bloc sélectionné.
        if self.selected_block:
            etape = self.selected_block.parent_etape  # Utiliser parent_etape
            etape.remove_block(self.selected_block)  # Supprimer le bloc de l'étape
            self.selected_block = None
            self.draw_sequence()
            print("Bloc supprimé.")
            self.mise_a_jour_info_projet(True)

    def create_connections(self):
        #Créer des connexions entre les blocs sélectionnés.
        if not self.selected_to_connect_blocks["green"] or not self.selected_to_connect_blocks["red"]:
            print("Sélectionnez des blocs sources et cibles pour créer une connexion.")
            return
        for source in self.selected_to_connect_blocks["green"]:
            for target in self.selected_to_connect_blocks["red"]:
                self.sequence.add_connection(source, target)
        # Réinitialiser les sélections
        self.selected_to_connect_blocks = {"green": [], "red": []}
        self.update_button_state()
        self.mise_a_jour_info_projet(True)
        # Redessiner après validation
        self.draw_sequence()

    def delete_connections(self):
        #Supprimer toutes les connexions du bloc sélectionné.
        if self.selected_block:
            self.sequence.delete_connection(self.selected_block)
            self.draw_sequence()
            print(f"Connexions du bloc {self.selected_block.identifiant} supprimées.")
            self.mise_a_jour_info_projet(True)

    def save_to_file(self, filename = None):
        if not filename :
            #Sauvegarder les étapes et blocs dans un fichier JSON.
            filename = filedialog.asksaveasfilename(
                filetypes=[("JSON Files", "*.json")],
                initialfile=self.file_Projet
                )
            if not filename:
                return
        # Construire la structure de données pour la sauvegarde
        data = {
            "name": self.sequence.name,
            "etapes": [
                {
                    "numero": etape.numero,
                    "y": etape.y,
                    "width": etape.width,
                    "blocs": [block.to_dict() for block in etape.blocs]
                }
                for etape in self.sequence.etapes
            ]
        }
        # Écrire dans le fichier JSON
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Sauvegardé dans {filename}")
        global_variables.need_to_save_Projet = False
        global_variables.need_to_save_Playlist = False    
        return filename

    def validate_json(data):
        #Valider que le JSON ne contient pas de doublons dans les connexions.
        for etape in data.get("etapes", []):
            for block in etape.get("blocs", []):
                block["blocs_precedents"] = list(set(block["blocs_precedents"]))
                block["blocs_suivants"] = list(set(block["blocs_suivants"]))
        return data
        
    def load_from_file(self, LefichierProjet = None):
        if self.check_unsaved_Projet_changes():     
            #Charger les étapes, blocs et connexions depuis un fichier JSON. 
            if not LefichierProjet:
                filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
                if not filename:
                    return
                global_variables.user_config.set("SETTINGS", "PROJECT", filename)
            else:
                filename = LefichierProjet

            with open(filename, "r") as f:
                data = json.load(f)

            self.file_Projet = filename
            # Charger la séquence depuis les données du fichier
            self.sequence = Sequence.from_dict(data)

            # Collecter tous les identifiants des blocs
            existing_ids = [
                block["identifiant"]
                for etape in data["etapes"]
                for block in etape["blocs"]
            ]

            # Initialiser le compteur global pour les blocs
            Block.initialize_counter(existing_ids)
            # Mettre à jour le champ playlist des blocs avec uneFonction
            for etape in self.sequence.etapes:
                for block in etape.blocs:
                    # Si `block.playlist_lien` est présent
                    if block.playlist_lien:
                        # Définir le bloc comme sélectionné et importer la playlist
                        self.selected_block = block
                        try:
                            self.import_playlist_to_block(block.playlist_lien)
                            print(f"Playlist importée pour le bloc {block.identifiant}.")
                        except Exception as e:
                            print(f"Erreur lors de l'importation de la playlist pour le bloc {block.identifiant}: {e}")
                    # Cas où block.playlist_lien est vide mais block.playlist contient des données
                
            # Vider les connexions actuelles
            self.sequence.connections = []

            # Reconstruire les connexions entre les blocs
            for etape in self.sequence.etapes:
                for block in etape.blocs:
                    #print(f"Reconstruire les connexions pour le bloc {block.identifiant}:")
                    blocs_precedents = []
                    blocs_suivants = []
                    block.parent_etape = etape  # Associer le bloc à son étape

                    # Ajouter uniquement des blocs uniques
                    for prev_id in block.blocs_precedents:
                        bloc = self.sequence.find_block({"identifiant": prev_id})
                        if bloc and bloc not in blocs_precedents:
                            blocs_precedents.append(bloc)
                            # Ajouter la connexion à la séquence
                            self.sequence.connections.append({"start": bloc, "end": block})

                    for next_id in block.blocs_suivants:
                        bloc = self.sequence.find_block({"identifiant": next_id})
                        if bloc and bloc not in blocs_suivants:
                            blocs_suivants.append(bloc)
                            # Ajouter la connexion à la séquence
                            self.sequence.connections.append({"start": block, "end": bloc})

                    block.blocs_precedents = blocs_precedents
                    block.blocs_suivants = blocs_suivants
                    #print(f"  Précédents: {[b.identifiant for b in block.blocs_precedents]}")
                    #print(f"  Suivants: {[b.identifiant for b in block.blocs_suivants]}")

            # Redessiner la séquence
            self.draw_sequence()
            print(f"Chargé depuis {filename}")
            self.mise_a_jour_info_projet()
  
    def generate_project_html(self):
        # Créer une instance de PageHTML et générer le fichier HTML
        page = PageHTML(self.sequence, self.file_Projet)
        page.generate_project_html()
        
    def generate_Ogg(self):
        # Créer une instance de PageHTML et générer le fichier HTML
        page = PageHTML(self.sequence, self.file_Projet)
        page.generate_Ogg()        

    def new_project(self):
        self.check_unsaved_Projet_changes()

        # Demander le nom du nouveau projet
        project_name = simpledialog.askstring(
            "New Project", 
            "Enter the name of the new project:", 
            parent=self.root
        )
        # Si l'utilisateur annule ou laisse vide, ne pas continuer
        if not project_name:
            print("Création du projet annulée.")
            return

        # Réinitialiser les variables
        self.sequence = Sequence(project_name)
        self.selected_etape = None
        self.selected_to_connect_blocks = {"green": [], "red": []}
        self.update_button_state()
        # Vider le canvas
        self.canvas.delete("all")
        # Ajouter une étape initiale
        self.add_etape()

        # Mise à jour de l'interface
        self.mise_a_jour_info_projet()
        self.file_Projet = phrase_to_filename(project_name) + ".json"
        self.file_Projet = self.save_to_file()
        global_variables.user_config.set("SETTINGS", "PROJECT", self.file_Projet)    
        print(f"Nouveau projet créé : {project_name}")

    def check_unsaved_Projet_changes(self):
        if global_variables.need_to_save_Projet:
            response = tk.messagebox.askyesno(
                "Unsaved changes in your PROJECT",
                "You have unsaved changes. Would you like to save your project before continuing?"
            )
            print(f"Projet reponse {response}") 
            if response:  # yes : Sauvegarder
                global_variables.playlist_Block_open.playlist = get_playlist_data(global_variables.playlist_tree)
                self.save_to_file(self.file_Projet)
                #print(f"save to {self.file_Projet}")
            #else:  # no
            global_variables.need_to_save_Projet = False
            global_variables.need_to_save_Playlist = False              
        return True  # Continuer l'action      

    def on_close(self):
        if self.check_unsaved_Projet_changes():  # Vérifie s'il faut sauvegarder
            self.root.destroy()  # Ferme l'application  
            global_variables.projet_instance = None
            print("Project window closed.")            