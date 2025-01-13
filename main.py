# fichier: main.py
import tkinter as tk
from tkinter import ttk
import time

import log_config  # Charge automatiquement la configuration de loggin

import global_variables  # Importer les variables globales
from general_functions import initConfigGlobale, find_localization_subfolders

from recherche_functions import open_and_display_json, SelectionLigne, setup_TableauPrincipal
from playlist_functions import select_and_add_to_playlist, setup_playlist, check_unsaved_playlist_changes
from filtrage import toggle_columns, filter_NA, reset_filters, filter_tree_with_filters, initialize_personnage_droplist, initialize_quete_droplist, update_quete_based_on_personnage, update_personnage_based_on_quete

from CuserConfig import UserConfig
from CprojetSequence import ProjetSequence

from Ctooltip import Tooltip

def ouvrir_projet_instance(root):
    # Vérifier si la fenêtre est déjà ouverte
    if global_variables.projet_instance is not None:
        global_variables.projet_instance.root.lift()
        global_variables.projet_instance.root.focus_force()
        print("An instance is already open, it has been brought back to the foreground.")
        return
    # Créer une nouvelle fenêtre
    global_variables.projet_instance =  ProjetSequence(tk.Toplevel(root))

def fermer_projet_instance():
    if global_variables.projet_instance is not None:
        #global_variables.projet_instance.destroy()
        global_variables.projet_instance.on_close()
        global_variables.projet_instance = None
        print("MAIN Project window closed.")

def fermer_application_principale(root):
    """Gestion de la fermeture de l'application principale."""
    # Vérifiez les modifications dans la playlist
    if not check_unsaved_playlist_changes(global_variables.playlist_tree):
        return  # Annulez la fermeture si l'utilisateur choisit d'annuler

    # Fermer la fenêtre de projet si elle est ouverte
    if global_variables.projet_instance is not None:
        fermer_projet_instance()
    # Fermer la fenêtre principale
    root.destroy()
    print("Main application closed.")

def long_function():
    # Changer le curseur en icône d'attente
    root.config(cursor="wait")
    root.update_idletasks()  # Actualiser l'interface graphique
    
    # Simuler une opération longue
    time.sleep(5)
    
    # Rétablir le curseur par défaut
    root.config(cursor="")
    root.update_idletasks()

def maj_Langue(str_langue):
    global_variables.CheminLangue = str_langue
    global_variables.bdd_Localisation_Json = "data/BDDjson/Base_" + str_langue + ".json"


# Créer la fenêtre principale
root = tk.Tk()
root.title(f"CyberPunk Dialog {global_variables.version_Logiciel} > Tool to assemble original in-game voices and test dialogue sequences for modding CyberPunk 2077")
root.geometry("1500x800")
root.minsize(1100, 800)

#global_variables.rootAccess = root #initialisation de la variable globale root pour y acceder dans les fonctions
global_variables.user_config = UserConfig("userconfig.ini")
global_variables.user_config.read_or_initialize()

initConfigGlobale()

#userconf_data = read_or_initialize_userconf()
#print(f"userconf_data : {userconf_data}")

# Récupérer le chemin du projet

global_variables.project_WOLVENKIT_path = global_variables.user_config.get("SETTINGS", "PROJECT_WOLVENKIT_PATH") + "/source/raw/"

localization_languages = find_localization_subfolders(global_variables.project_WOLVENKIT_path)

# Créer une frame pour le bouton au-dessus du tableau principal
button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

# Ajouter un bouton "Projet" à gauche de la liste déroulante
project_button = tk.Button(
    button_frame,
    text="Project",
    command=lambda: ouvrir_projet_instance(root)
)
project_button.pack(side=tk.LEFT, padx=5, pady=5)
txt_aide = (
    "The project window allows you to assemble different playlists to create a scenario with different possible choices for V."
)
Tooltip(project_button, txt_aide)

# Ajouter une liste déroulante (ComboBox)
language_var = tk.StringVar()
language_dropdown = ttk.Combobox(
    button_frame,
    textvariable=language_var,
    values=localization_languages,  # Langues récupérées par la fonction
    state="readonly",  # Lecture seule pour éviter la modification manuelle
    width=20
)

# Définir une valeur par défaut pour la liste déroulante
maj_Langue(global_variables.user_config.get("SETTINGS", "LANGUAGE"))

global_variables.CheminLangue = global_variables.user_config.get("SETTINGS", "LANGUAGE")

global_variables.bdd_Localisation_Json = "data/BDDjson/Base_" + global_variables.CheminLangue + ".json"
if global_variables.CheminLangue in localization_languages:
    language_dropdown.set(global_variables.CheminLangue)  # Définit la valeur par défaut
else:
    language_dropdown.set("Select a language")  # Définit une valeur par défaut générique

language_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

# Ajouter un texte à droite de la liste déroulante
text_label = tk.Label(button_frame, text="Use left click to listen to a line, right click to add a line to the playlist. Multiple selection is possible and addition to the playlist with the Add selection to playlist button.", font=("Arial", 10))
text_label.pack(side=tk.LEFT, padx=5, pady=5)

# Ajouter un bouton pour traiter toutes les langues
process_button = tk.Button(
    button_frame,
    text="Process All Languages",
    command=lambda: process_all_languages(root)  # Appeler la fonction avec root
)
process_button.pack(side=tk.LEFT, padx=5, pady=5)
txt_aide = (
    "This button allows you to generate HTML and OGG files for all accessible languages."
)
Tooltip(process_button, txt_aide)

def process_all_languages(root):
    """Parcours toutes les langues et effectue les opérations requises."""
    # Sauvegarder la langue actuelle
    langue_initiale = global_variables.user_config.get("SETTINGS", "LANGUAGE")
    print(f"Initial language : {langue_initiale}")

    for langue in localization_languages:
        print(f"Language processing : {langue}")

        # Changer la langue
        maj_Langue(langue)
        global_variables.user_config.set("SETTINGS", "LANGUAGE", langue)
        print(f"Language update : {langue}")

        # Fermer la fenêtre projet si elle est ouverte
        if global_variables.projet_instance is not None:
            fermer_projet_instance()

        # Ouvrir une nouvelle instance de la fenêtre projet
        ouvrir_projet_instance(root)

        # Générer les fichiers .ogg
        try:
            if hasattr(global_variables.projet_instance, "generate_Ogg"):
                global_variables.projet_instance.generate_Ogg()
                print(f"Generated .ogg files for language : {langue}")
        except Exception as e:
            print(f"Error generating .ogg files : {e}")

        # Générer la page HTML
        try:
            if hasattr(global_variables.projet_instance, "generate_project_html"):
                global_variables.projet_instance.generate_project_html()
                print(f"HTML page generated for language : {langue}")
        except Exception as e:
            print(f"Error generating HTML page : {e}")

        # Pause entre les langues pour éviter les conflits de ressources (optionnel)
        time.sleep(2)

    # Restauration de la langue initiale
    print(f"Restoration of the original language : {langue_initiale}")
    maj_Langue(langue_initiale)
    global_variables.user_config.set("SETTINGS", "LANGUAGE", langue_initiale)
    if global_variables.projet_instance is not None:
        fermer_projet_instance()
    ouvrir_projet_instance(root)


# Ajouter une commande lors de la sélection
def on_language_selected(event):
    global_variables.dataSound = None
    maj_Langue(language_var.get())
    global_variables.user_config.set("SETTINGS", "LANGUAGE", global_variables.CheminLangue)
    # mettre ca si on veut les langues des tableau synchro filter_tree_with_filters(tree, filters, global_variables.bdd_Localisation_Json)
    print(f"Selected language : {global_variables.CheminLangue}")

language_dropdown.bind("<<ComboboxSelected>>", on_language_selected)

# Créer la frame pour les filtres et l'ajouter au-dessus du tableau principal
filter_frame = tk.Frame(root)  # <-- Correction : définition correcte
filter_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

# Exemple d'initialisation du Treeview avec un thème compatible
style = ttk.Style()
style.theme_use("default")  # Changez le thème
style.configure("Treeview", rowheight=25)  # Augmentez la hauteur des lignes si nécessaire
style.map(
    "Treeview", 
    background=[("selected", global_variables.Couleur_BgSelectLigne)],  # Couleur pour les lignes sélectionnées
    foreground=[("selected", global_variables.Couleur_TxtSelectLigne)]   # Couleur du texte pour les lignes sélectionnées
)

# Créer une variable pour gérer l'état des boutons radio
global_variables.vSexe = tk.StringVar(value=global_variables.vHomme)  # Par défaut sur "homme"

#definition du Tableau Principal
tree = setup_TableauPrincipal(root, global_variables.columns)

# Fonction pour configurer le tableau de playlist
global_variables.playlist_tree = setup_playlist(root, tree, global_variables.columns)

# Ajouter le Label pour les lignes correspondantes
global_variables.principal_count = tk.Label(filter_frame, text="Number of lines: 0")
global_variables.principal_count.grid(row=1, column=9, padx=5)

# Bouton pour appliquer tous les filtres
apply_all_filters_button = tk.Button(
    filter_frame,
    text="Apply all filters ✔️",
    command=lambda: filter_tree_with_filters(tree, filters, global_variables.bdd_Localisation_Json)
    #command=lambda: apply_all_filters(tree, filters)
)
apply_all_filters_button.grid(row=1, column=7, padx=5)
Tooltip(apply_all_filters_button, "Apply filters")


root.bind('<Return>', lambda event: filter_tree_with_filters(tree, filters, global_variables.bdd_Localisation_Json))

# Ajouter un bouton pour réinitialiser les filtres
reset_filter_button = tk.Button(
    filter_frame,
    text="Reset filters ✖️",
    command=lambda: [
        reset_filters(tree, filters, global_variables.bdd_Localisation_Json)
    ]
    
)
reset_filter_button.grid(row=1, column=8, padx=5)
Tooltip(reset_filter_button, "Reset filters")

# Ajouter une case à cocher pour "Afficher N/A"
na_var = tk.BooleanVar(value=True)  # Initialiser à "coché" (True)

checkbox_na = tk.Checkbutton(
    filter_frame,
    text="keep lines with " + global_variables.pas_Info,
    variable=na_var,
    command=lambda: filter_NA(tree, na_var)  # Appeler le filtre quand l'état change
)
checkbox_na.grid(row=1, column=12, padx=5)

# Charger les données dans le tableau
open_and_display_json(tree, global_variables.bdd_Localisation_Json)

def on_personnage_selected(event):
    personnage_value = event.widget.get()
    update_quete_based_on_personnage(tree, filters, 5, 3, personnage_value)  # 5 = colonne Quête, 3 = colonne Personnage F
    update_quete_based_on_personnage(tree, filters, 5, 4, personnage_value)  # 5 = colonne Quête, 4 = colonne Personnage M

def on_quete_selected(event):
    quete_value = event.widget.get()
    update_personnage_based_on_quete(
        tree,
        filters,
        quete_column_index=5,
        personnage_column_indexes=(3, 4),  # Les indices des colonnes Voix"
        quete_value=quete_value
    )


def resize_columns(event):
    toggle_columns(tree, global_variables.playlist_tree,  filters)   

# Créer les champs de filtre uniquement pour les colonnes sélectionnées
filters = []  # Initialisation de la liste des filtres

width_mapping = {
    global_variables.titleCol_F_Voice: 15,
    global_variables.titleCol_M_Voice: 15,
    global_variables.titleCol_Quest: 40,
}
# Création des filtres avec labels explicites
for i, column in enumerate(global_variables.columns):
    label = tk.Label(filter_frame, text=f"{global_variables.filter_with}{column}")  #Filter with
    label.grid(row=0, column=i, padx=5)

    if column in width_mapping:  # Combobox avec largeur spécifique
        entry = ttk.Combobox(filter_frame, state="readonly", width=width_mapping[column])        
        if column == global_variables.titleCol_F_Voice:
            entry["values"] = initialize_personnage_droplist(tree, 3)
            entry.set(global_variables.setToAll)
            entry.bind("<<ComboboxSelected>>", on_personnage_selected)
        elif column == global_variables.titleCol_M_Voice:
            entry["values"] = initialize_personnage_droplist(tree, 4)
            entry.set(global_variables.setToAll)
            entry.bind("<<ComboboxSelected>>", on_personnage_selected)
        elif column == global_variables.titleCol_Quest:
            entry["values"] = initialize_quete_droplist(tree, 5)
            entry.set(global_variables.setToAll)
            entry.bind("<<ComboboxSelected>>", on_quete_selected)
    else:  # TextBox
        entry = tk.Entry(filter_frame)

    # Placer les widgets
    entry.grid(row=1, column=i, padx=5)
    filters.append((column, label, entry))  # Ajouter le label et le widget à la liste des filtres


# Bouton radio pour "Homme"
radio_homme = tk.Radiobutton(
    filter_frame,
    text=global_variables.vHomme,
    variable=global_variables.vSexe,
    value=global_variables.vHomme,
    command=lambda: toggle_columns(tree, global_variables.playlist_tree, filters)  # Appeler la fonction de mise à jour des colonnes
)
radio_homme.grid(row=1, column=10, padx=5)

# Bouton radio pour "Femme"
radio_femme = tk.Radiobutton(
    filter_frame,
    text=global_variables.vFemme,
    variable=global_variables.vSexe,
    value=global_variables.vFemme,
    command=lambda: toggle_columns(tree, global_variables.playlist_tree,  filters)  # Appeler la fonction de mise à jour des colonnes
)
radio_femme.grid(row=1, column=11, padx=5)

#filter_tree_with_filters(tree, filters, global_variables.bdd_Localisation_Json)




# Lier les événements du tableau principal
tree.bind("<Button-3>", lambda event: select_and_add_to_playlist(event, tree, global_variables.playlist_tree))
tree.bind("<<TreeviewSelect>>", lambda event: SelectionLigne(event, tree))  # Sélectionner une ligne pour afficher les détails

# Lier l'événement de redimensionnement
root.bind("<Configure>", resize_columns)
#root.protocol("WM_DELETE_WINDOW", on_main_close)
# Associer la fermeture de la fenêtre principale
root.protocol("WM_DELETE_WINDOW", lambda: fermer_application_principale(root))

# Lancer la boucle principale de l'application
root.mainloop()

