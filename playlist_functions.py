# fichier: playlist.py
import json, threading, pygame, os

# Extraire uniquement le nom du fichier sans le chemin
from os.path import basename

from tkinter import ttk, filedialog, Menu, messagebox
import tkinter as tk
from LectureOgg import JouerAudio, fusionnerPlaylist
from general_functions import get_SousTitres_from_csv, get_SousTitres_by_id, extraire_WOLVENKIT_localise_path, extraire_PROJET_localise_path, get_Perso_from_Wem, phrase_to_filename

import global_variables  # Accéder au Label global
from CligneManuelle import LigneManuelle

def select_and_add_to_playlist(event, tree, playlist_tree):
    # Identifier la ligne sous le curseur
    item = tree.identify_row(event.y)
    if item:  # Si une ligne est détectée
        tree.selection_set(item)  # Sélectionner cette ligne
        # Appeler la fonction pour ajouter à la playlist
        add_to_playlist(tree, playlist_tree)

        # Mettre à jour le compteur
        majInfoPlaylist(playlist_tree, True)
        colorize_playlist_rows(playlist_tree)

 # Fonction pour ajouter une/des ligne sélectionnée(s) au tableau playlist
def add_to_playlist(tree, playlist_tree):
    # Ajouter toutes les lignes sélectionnées
    selected_items = tree.selection()  # Obtenir toutes les lignes sélectionnées
    for item in selected_items:
        selected_values = tree.item(item, 'values')  # Obtenir les valeurs de la ligne
        playlist_tree.insert("", tk.END, values=selected_values)  # Ajouter à la playlist

    # Mettre à jour le compteur
    majInfoPlaylist(playlist_tree, True)
    colorize_playlist_rows(playlist_tree)        

#definition de la playlist
def setup_playlist(root, tree, columns):
    # Définir un style personnalisé pour le Treeview
    style = ttk.Style(root)
    style.configure(
        "Custom.Treeview.Heading",
        background=global_variables.Couleur_EntetePlaylist,  # Fond bleu pour les fichiers
        foreground="black",
        font=("Arial", 10)
    )            

    main_frame = tk.Frame(root)
    main_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)  # Ajoutez expand=True ici

    button_frame = tk.Frame(main_frame)
    button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

    playlist_frame = tk.Frame(main_frame, height=450, bg='lightgray')
    playlist_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)  # Ajoutez expand=True ici

    # Frame pour les labels au-dessus des boutons
    label_frame = tk.Frame(button_frame)
    label_frame.pack(side=tk.TOP, fill=tk.X, padx=200, pady=(0, 0))  # Ajoutez un espacement entre les labels et les boutons

    # Ajouter les labels dans label_frame
    global_variables.playlist_name_label = tk.Label(label_frame, text="Playlist : " + global_variables.pas_Info)
    global_variables.playlist_name_label.pack(side=tk.LEFT, padx=(10, 0))  # Alignement à gauche

    global_variables.playlist_count_label = tk.Label(label_frame, text=global_variables.nombre_Ligne + " : 0")
    global_variables.playlist_count_label.pack(side=tk.LEFT, padx=(10, 0))  # Alignement à gauche


    playlist_columns = columns
    playlist_tree = ttk.Treeview(playlist_frame, columns=playlist_columns, show="headings", height=10, style="Custom.Treeview")

    # Configurer les colonnes (largeur, alignement, etc.)
    for column in playlist_columns:
        playlist_tree.heading(column, text=column)

    playlist_scrollbar = ttk.Scrollbar(playlist_frame, orient=tk.VERTICAL, command=playlist_tree.yview)
    playlist_tree.configure(yscroll=playlist_scrollbar.set)
    playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    playlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Ajouter le clic droit pour supprimer une ligne dans la playlist
    playlist_tree.bind("<Button-3>", lambda event: show_context_menu_Playlist(event, playlist_tree, root))
    # lecture ligne
    playlist_tree.bind("<<TreeviewSelect>>", lambda event: SelectionLignePlayliste(event, playlist_tree))  # Sélectionner une ligne pour afficher les détails


    add_button = tk.Button(button_frame, text="Add selection to playlist ⤵️", command=lambda: add_to_playlist(tree, playlist_tree))
    add_button.pack(side=tk.LEFT, padx=5)

    add_manual_button = tk.Button(button_frame, text="Add Personal line ✏️", command=lambda: open_manual_entry_window(button_frame, playlist_tree))
    add_manual_button.pack(side=tk.LEFT, padx=5)

    move_up_button = tk.Button(button_frame, text="Up ⬆️", command=lambda: move_up_playlist(playlist_tree))
    move_up_button.pack(side=tk.LEFT, padx=5)

    move_down_button = tk.Button(button_frame, text="Down ⬇️", command=lambda: move_down_playlist(playlist_tree))
    move_down_button.pack(side=tk.LEFT, padx=5)

    play_button = tk.Button(button_frame, text="Play to the playlist ▶️", command=lambda: ecouterPlaylist(playlist_tree))
    play_button.pack(side=tk.LEFT, padx=(20, 5))
    
    stop_button = tk.Button(button_frame, text="Stop ⏹️", command=lambda: stopperPlaylist())
    stop_button.pack(side=tk.LEFT, padx=(5, 20))

    load_button = tk.Button(button_frame, text="Load playlist ↩️", command=lambda: load_playlist_from_file(playlist_tree))
    load_button.pack(side=tk.LEFT, padx=5)

    save_button = tk.Button(button_frame, text="Save playlist 🖫", command=lambda: save_playlist_to_file(playlist_tree))
    save_button.pack(side=tk.LEFT, padx=5)

    clear_button = tk.Button(button_frame, text="Clean playlist ❌", command=lambda: clear_playlist(playlist_tree))
    #clear_button = tk.Button(button_frame, text="Fusio FICHIER", command=lambda: fusionner_audio_json(chemin_json="", chemin_ogg="chemin_ogg"))
    clear_button.pack(side=tk.LEFT, padx=5)

    record_button = tk.Button(button_frame, text="Record playlist ⭕", command=lambda: record_playlist(playlist_tree))
    record_button.pack(side=tk.LEFT, padx=5)

    txtDialog_button = tk.Button(button_frame, text="Dialog playlist ☷", command=lambda: save_playlist_to_txt(playlist_tree))
    txtDialog_button.pack(side=tk.LEFT, padx=5)

    return playlist_tree

def SelectionLignePlayliste(event, playlist_tree):
    try:
        # Vérifiez si une ligne est sélectionnée
        selected_items = playlist_tree.selection()
        if not selected_items:
            print("Aucune ligne sélectionnée dans le Treeview.")
            return

        # Obtenir le premier élément sélectionné
        selected_item = selected_items[0]
        selected_values = playlist_tree.item(selected_item, 'values')

        # Vérifiez si les valeurs sélectionnées contiennent les indices nécessaires
        if len(selected_values) < 5:
            print("Données insuffisantes dans la ligne sélectionnée.")
            return

        # Déterminer le genre sélectionné et choisir la valeur audio
        selected_gender = global_variables.vSexe.get()
        if selected_gender == global_variables.vHomme:
            audio_value = selected_values[4]
        else:
            audio_value = selected_values[3]

        # Jouer l'audio correspondant
        JouerAudio(audio_value)

    except IndexError:
        print("Erreur : Aucun élément sélectionné ou sélection invalide.")
    except Exception as e:
        print(f"Erreur dans SelectionLignePlayliste : {e}")


#Fonction pour la selection d'une ligne de la playlist
def SelectionLignePlayliste222(event, playlist_tree):
    selected_item = playlist_tree.selection()[0]
    selected_values = playlist_tree.item(selected_item, 'values')

    selected_gender = global_variables.vSexe.get()
    if selected_gender == global_variables.vHomme:
        audio_value = selected_values[4]
    else:
        audio_value = selected_values[3]

    JouerAudio(audio_value)

def show_context_menu_Playlist(event, playlist_tree, root):
    # Sélectionner la ligne sous le curseur
    item = playlist_tree.identify_row(event.y)  # Identifie la ligne sous le clic
    if item:  # Si une ligne est détectée
        playlist_tree.selection_set(item)  # Sélectionne cette ligne

        # Créer et afficher le menu contextuel
        menu = Menu(root, tearoff=0)
        menu.add_command(label="Remove from playlist", command=lambda: remove_selected_from_playlist(playlist_tree))
        #menu.add_command(label="Open in Personal line", command=lambda: open_manual_entry_window(button_frame, playlist_tree))
        menu.post(event.x_root, event.y_root)  # Affiche le menu à l'emplacement du clic
    else:
        # Si aucune ligne n'est détectée, ne rien faire ou désélectionner
        playlist_tree.selection_remove(playlist_tree.selection())

# Fonction pour supprimer une ligne de la playlist via un clic droit
def remove_selected_from_playlist(playlist_tree):
    try:
        selected_item = playlist_tree.selection()[0]
        playlist_tree.delete(selected_item)
        majInfoPlaylist(playlist_tree, True)
    except IndexError:
        pass
    
# Fonction pour déplacer une ligne vers le haut dans le tableau de playlist
def move_up_playlist(playlist_tree):
    try:
        selected_item = playlist_tree.selection()[0]
        index = playlist_tree.index(selected_item)
        if index > 0:
            playlist_tree.move(selected_item, playlist_tree.parent(selected_item), index - 1)
            majInfoPlaylist(playlist_tree, True)
    except IndexError:
        pass

# Fonction pour déplacer une ligne vers le bas dans le tableau de playlist
def move_down_playlist(playlist_tree):
    try:
        selected_item = playlist_tree.selection()[0]
        index = playlist_tree.index(selected_item)
        if index < len(playlist_tree.get_children()) - 1:
            playlist_tree.move(selected_item, playlist_tree.parent(selected_item), index + 1)
            majInfoPlaylist(playlist_tree, True)
    except IndexError:
        pass

# Fonction pour effacer le tableau de playlist
def clear_playlist(playlist_tree):
    # Vérifiez les modifications avant de charger
    if not check_unsaved_playlist_changes(playlist_tree):
        return
        
    for item in playlist_tree.get_children():
        playlist_tree.delete(item)  
    majInfoPlaylist(playlist_tree, True)

# Fonction pour fusionner et enregistrer la Playlist du tableau playlist
def record_playlist(playlist_tree):
    fusionnerPlaylist(playlist_tree, nom_playlist() )


def nom_playlist():    # Récupérer le texte du Label et le nom de la playlist sans extension
    texte_playlist = global_variables.playlist_name_label.cget("text")
    #print(f"texte playlist : {texte_playlist}.")
    if global_variables.is_PlayList_From_Projet :
        nom_sans_extension = global_variables.pas_Info
    else : 
        file_name_playlist = texte_playlist.split(" : ")[1]  # Extraire le nom de la playlist
        nom_sans_extension = os.path.splitext(file_name_playlist)[0] 
        #print(f"nom_sans_extension : {nom_sans_extension}")

    if nom_sans_extension[-4:] == " (*)":
        nom_sans_extension = nom_sans_extension[:-4]  # Supprimer les 4 derniers caractères
    if nom_sans_extension == global_variables.pas_Info:
        nom_sans_extension = Suggestion_Playlist_Name(global_variables.playlist_tree)
    return nom_sans_extension

def Suggestion_Playlist_Name(playlist_tree):
    second_column_value = ""
    if playlist_tree.get_children():
        first_row_id = playlist_tree.get_children()[0]
        first_row_values = playlist_tree.item(first_row_id, "values")
        second_column_value = first_row_values[1]  # Deuxième colonne valeur de femaleVariant
    return phrase_to_filename(second_column_value)
    
# Fonction pour sauvegarder la playlist dans un fichier JSON
def save_playlist_to_file(playlist_tree, file_path = None):
    if not file_path :
        nom_sans_extension = nom_playlist()  
        if nom_sans_extension == global_variables.pas_Info:
            nom_sans_extension = Suggestion_Playlist_Name(playlist_tree)
        file_path = filedialog.asksaveasfilename(
            title="Save the playlist in JSON format",
            initialfile=f"{nom_sans_extension}.json",  # Nom par défaut basé sur la playlist
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
            )
    
    if file_path:
        playlist_data = get_playlist_data(playlist_tree)

        # Sauvegarder les données dans un fichier JSON
        #print(f"Sauvegarde de la playlist dans {file_path}.")  # Debugging
        with open(file_path, "w") as file:
            json.dump(playlist_data, file, indent=4)
        
        #global_variables.playlist_name_label.config(text=f"Playlist : {basename(file_path)}")
        majInfoPlaylist(playlist_tree, False)
        charger_playlist_from_file(playlist_tree, file_path)

def get_playlist_data(playlist_tree):        
    playlist_data = []
    # Récupérer les données de chaque ligne de la playlist
    for child in playlist_tree.get_children():
        values = playlist_tree.item(child, "values")
        if len(values) < 6:
            print(f"Ligne invalide ignorée : {values}")
            continue        
        # Sauvegarder dans une structure
        playlist_data.append({
            global_variables.data_ID: values[0],
            global_variables.data_F_SubTitle: values[1],
            global_variables.data_M_SubTitle: values[2],
            global_variables.data_F_Voice: values[3],
            global_variables.data_M_Voice: values[4],
            global_variables.data_Quest: values[5]
        })      
    return playlist_data

# Fonction pour charger la playlist à partir d'un fichier JSON
def load_playlist_from_file(playlist_tree):
    # Vérifiez les modifications avant de charger
    if not check_unsaved_playlist_changes(playlist_tree):
        return
        
    file_path = filedialog.askopenfilename(
        title="Load a playlist in JSON format", 
        filetypes=[("JSON files", "*.json")]
        )
    #print(f"Fichier playlist : {file_path}")
    if file_path:
        charger_playlist_from_file(playlist_tree, file_path)

# Fonction pour charger la playlist à partir d'un fichier JSON
def charger_playlist_from_file(playlist_tree, file_path):
    global_variables.playlist_file_open = file_path
    global_variables.playlist_Block_open = None
    global_variables.is_PlayList_From_Projet = False
    if file_path:
        #print(f"Fichier playlist : {file_path}")
        with open(file_path, "r") as file:
            playlist_data = json.load(file)
        set_playlist_data(playlist_tree, playlist_data)       
        majInfoPlaylist(playlist_tree, False)
    else:
        print(f"pas de fichier playlist")

# Fonction pour charger la playlist à partir d'un fichier JSON
def set_playlist_data(playlist_tree, playlist_data):                
    # Effacer l'ancienne playlist avant de charger la nouvelle
    clear_playlist(playlist_tree)

    # Ajouter les nouvelles données
    for entry in playlist_data:
        recup_Quete = entry[global_variables.data_Quest]
        fichierQuete = "" 
        if recup_Quete.lower().endswith(".csv"):
            #print(f"Le fichier {recup_Quete} est un fichier CSV.")
            recup_Quete = extraire_PROJET_localise_path(recup_Quete)
            #print(f"new chemein  {extraire_PROJET_localise_path(recup_Quete)} ")
            fichierQuete = "data/projet/"  + recup_Quete 
            fichierQuete = recup_Quete 
            # Action spécifique pour les fichiers CSV
            result = get_SousTitres_from_csv(fichierQuete, entry[global_variables.data_ID])
        else:
            #TRADUCTION DEPUIS LE JEU ! >>> Récupérer la quête
            quete_path = extraire_WOLVENKIT_localise_path(recup_Quete)
            #print(f"Fichier Quete : {quete_path}")    
            if isinstance(quete_path, str):  # Vérifie si c'est une chaîne
                fichierQuete = quete_path + ".json.json"
            #print(f"Fichier Quete : {quete_path}")
            result = get_SousTitres_by_id(fichierQuete, entry[global_variables.data_ID])
        
        if result:
            female_text = result[global_variables.data_F_SubTitle]
            male_text = result[global_variables.data_M_SubTitle]
        else:
            #print("String ID non trouvé.")
            female_text = "(NO TRADUCTION)"
            male_text = "(NO TRADUCTION)"  

        if not male_text or male_text == global_variables.pas_Info:
            male_text = female_text        
        if not female_text or female_text == global_variables.pas_Info:
            female_text = male_text # a Confirmer si ca existe !?                     

        playlist_tree.insert("", tk.END, values=(
            entry[global_variables.data_ID],
            female_text,
            male_text,
            entry[global_variables.data_F_Voice],
            entry[global_variables.data_M_Voice],
            entry[global_variables.data_Quest]
        ))
    # Mettre à jour le compteur
    update_treeview_header_style(playlist_tree)
    majInfoPlaylist(playlist_tree, False)
    colorize_playlist_rows(playlist_tree)

# Fonction pour lire la Playlist
def majInfoPlaylist(playlist_tree, modified = False):   
    txtModif = ""
    nomPlaylist = ""
    if global_variables.is_PlayList_From_Projet :
        #print(f"is_PlayList_From_Projet : {global_variables.is_PlayList_From_Projet}")
        if global_variables.projet_instance :
            #global_variables.need_to_save_Projet = modified
            global_variables.need_to_save_Playlist = modified
            nomPlaylist = f"{basename(global_variables.projet_instance.file_Projet)} > BLOCK: {global_variables.projet_instance.selected_block.identifiant}"
            global_variables.projet_instance.mise_a_jour_info_projet(global_variables.need_to_save_Projet)
    else:
        global_variables.need_to_save_Playlist = modified
        if global_variables.playlist_file_open:
            nomPlaylist = basename(global_variables.playlist_file_open)
        else:
            nomPlaylist = global_variables.pas_Info    
    
    if modified:
        txtModif = " (*)"

    global_variables.playlist_name_label.config(text=f"Playlist : {nomPlaylist}{txtModif}")         
    count_playlist_rows(playlist_tree)

# Fonction pour lire la Playlist
def ecouterPlaylist(playlist_tree):
    #    Lance la lecture de la playlist dans un thread séparé.
    global is_playlist_playing  # Utiliser la variable globale
    is_playlist_playing = True  # Activer l'état de lecture

    def lecture_playlist():
        global is_playlist_playing
        selected_items = playlist_tree.selection()
        items = playlist_tree.get_children()

        if not items:
            print("La playlist est vide.")
            is_playlist_playing = False
            return

        start_index = 0
        if selected_items:
            start_index = items.index(selected_items[0])

        for item in items[start_index:]:
            if not is_playlist_playing:  # Vérification pour stopper la lecture
                #print("Lecture de la playlist interrompue.")
                break

            # Mettre à jour la sélection de l'élément en cours de lecture
            playlist_tree.selection_set(item)  # Sélectionner l'élément
            playlist_tree.see(item)  # Faire défiler pour afficher l'élément
            playlist_tree.update_idletasks()  # Rafraîchir l'affichage du Treeview
            
            selected_values = playlist_tree.item(item, "values")

            selected_gender = global_variables.vSexe.get()
            if selected_gender == global_variables.vHomme:
                audio_value = selected_values[4]
            else:
                audio_value = selected_values[3]

            if audio_value:
                #print(f"Lecture de : {audio_value}")
                try:
                    JouerAudio(audio_value)
                except Exception as e:
                    print(f"Erreur lors de la lecture de {audio_value} : {e}")
            else:
                print(f"Aucun fichier audio pour la ligne {item}.")

            while is_playlist_playing and pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

        is_playlist_playing = False  # Réinitialiser l'état de lecture après la fin

    # Démarrage du thread
    thread = threading.Thread(target=lecture_playlist, daemon=True)
    thread.start()

# Fonction pour stopper Playlist
def stopperPlaylist():
    """
    Stoppe complètement la lecture de la playlist.
    """
    global is_playlist_playing
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()  # Arrête l'audio en cours
        is_playlist_playing = False  # Stoppe la progression dans la playlist
        #print("Lecture de la playlist complètement arrêtée.")
    except Exception as e:
        print(f"Erreur lors de l'arrêt de la lecture : {e}")

def count_playlist_rows(playlist_tree):
    """
    Compte et affiche le nombre de lignes dans le Treeview de la playlist.
    """
    row_count = len(playlist_tree.get_children())
    if global_variables.playlist_count_label:  # Mettre à jour le Label global
        global_variables.playlist_count_label.config(text=f"{global_variables.nombre_Ligne}: {row_count}")
    else:
        print(f"{global_variables.nombre_Ligne} : {row_count}")


def colorize_playlist_rows(playlist_tree):
    """
    Colore les lignes de playlist_tree en fonction de la valeur extraite de la 4ème colonne.
    Les lignes ayant une valeur commune dans la 4ème colonne auront la même couleur.

    :param playlist_tree: Le Treeview contenant les données.
    """
    # Dictionnaire pour stocker les couleurs attribuées
    color_mapping = {}
    # Liste de couleurs disponibles
    colors = ["#FFCCCC", "#CCFFCC", "#CCCCFF", "#FFFFCC", "#FFCCFF", "#CCFFFF"]

    # Fonction pour extraire la valeur significative de la 4ème colonne
    def extract_value(column_value):
        personnage = ""
        if not column_value or "/" not in column_value or "_" not in column_value:
            personnage = "unknown"
        try:
            last_part = column_value.rsplit("/", 1)[-1]  # Récupérer la partie après le dernier '/'
            personnage = last_part.split("_", 1)[0]  # Récupérer la partie avant le premier '_'
        except IndexError:
            personnage = "unknown"
        #print(f"Nb lines in playlist : {personnage}")
        return personnage

    # Parcourir toutes les lignes de playlist_tree
    rows = playlist_tree.get_children()
    for row in rows:
        values = playlist_tree.item(row, "values")  # Récupérer les valeurs de la ligne
        if len(values) >= 4:
            key = extract_value(values[3])  # Extraire la clé depuis la 4ème colonne
        else:
            key = "unknown"

        # Assigner une couleur à cette clé si elle n'a pas encore de couleur
        if key not in color_mapping:
            color_mapping[key] = colors[len(color_mapping) % len(colors)]  # Cycle dans la liste des couleurs

        # Appliquer la couleur au fond de la ligne
        playlist_tree.tag_configure(key, background=color_mapping[key])
        playlist_tree.item(row, tags=(key,))

def save_playlist_to_txt(playlist_tree):
    nom_sans_extension = nom_playlist()
    fichier_sauvegarde = filedialog.asksaveasfilename(
        title="Save the dialog of the playlist",
        initialfile=f"{nom_sans_extension}.txt",  # Nom par défaut basé sur la playlist
        defaultextension=".txt",
        filetypes=[("Fichiers txt", "*.txt")],
        )
    if fichier_sauvegarde:
        try:
            # Ouvrir le fichier en mode écriture
            with open(fichier_sauvegarde, "w", encoding="utf-8") as file:
                # Parcourir les lignes du tableau
                for child in playlist_tree.get_children():
                    values = playlist_tree.item(child, "values")
                    selected_gender = global_variables.vSexe.get()
                    if selected_gender == global_variables.vHomme:
                        Perso = get_Perso_from_Wem(values[4])  
                        sousTitre = values[2]
                    else:
                        Perso =get_Perso_from_Wem(values[3])
                        sousTitre = values[1]  
                    # Construire la ligne au format spécifié
                    line = f"Id: {values[0]}\t{Perso}:  {sousTitre}\n"
                    # Écrire dans le fichier
                    file.write(line)
            print(f"Fichier sauvegardé avec succès dans : {fichier_sauvegarde}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

def open_manual_entry_window(button_frame, playlist_tree):
    def save_playlist():
        #Callback pour sauvegarder la playlist.
        if global_variables.is_PlayList_From_Projet :
            save_playlist_to_projet(playlist_tree)  
            set_playlist_data(global_variables.playlist_tree, global_variables.projet_instance.selected_block.playlist)
        else:
            save_playlist_to_file(playlist_tree, global_variables.playlist_file_open)
            charger_playlist_from_file(playlist_tree, global_variables.playlist_file_open)
        print("Playlist sauvegardée après la fermeture de LigneManuelle.")
    #_____________________________________________________________________
    # Récupérer l'ID de la ligne sélectionnée dans la playlist
    selected_items = playlist_tree.selection()
    selected_id = None
    if selected_items:
        # Récupérer la première ligne sélectionnée (si plusieurs sont sélectionnées)
        item = selected_items[0]
        values = playlist_tree.item(item, 'values')
        if values:
            selected_id = values[0]  # Suppose que l'ID est la première colonne    
    
    
    # Vérifier si une instance existe déjà
    if global_variables.ligne_manuelle_instance is None or not global_variables.ligne_manuelle_instance.window.winfo_exists():
        global_variables.ligne_manuelle_instance = LigneManuelle(
            button_frame, 
            playlist_tree, 
            save_callback=save_playlist,
            selected_id=selected_id,  # Passer l'ID sélectionné
            )

    else:
        # Ramener la fenêtre existante au premier plan
        global_variables.ligne_manuelle_instance.window.lift()
        global_variables.ligne_manuelle_instance.window.focus_force()
        print("Une instance est déjà ouverte, elle a été ramenée au premier plan.")

def check_unsaved_playlist_changes(playlist_tree):
    #Vérifie si des modifications non sauvegardées existent dans la playlist.
    if global_variables.need_to_save_Playlist:
        if global_variables.is_PlayList_From_Projet :
            msg = "You have unsaved changes. Would you like to save the playlist in your project before continuing?" 
        else:
            msg = "You have unsaved changes. Would you like to save the playlist before continuing?"           
        response = messagebox.askyesno("Unsaved changes in the playlist", msg)
        print(f"Playlist reponse {response}") 
        if response:  # Si "yes" # Sauvegarder
            save_playlist_Projet_or_File(playlist_tree)
        else:  # Si "No"
            if global_variables.is_PlayList_From_Projet : 
                global_variables.need_to_save_Projet = False
            global_variables.need_to_save_Playlist = False         
    return True  # Continuer

def save_playlist_Projet_or_File(playlist_tree):
    if global_variables.is_PlayList_From_Projet :
        save_playlist_to_projet(playlist_tree)  
        global_variables.need_to_save_Projet = False
    else:
        save_playlist_to_file(playlist_tree, global_variables.playlist_file_open)  
    global_variables.need_to_save_Playlist = False         

def save_playlist_to_projet(playlist_tree):
    #A REVOIR
    if global_variables.playlist_Block_open :
        if global_variables.projet_instance :
            global_variables.playlist_Block_open.playlist = get_playlist_data(playlist_tree)
            print(f"Tententive de sauver projet avec bloc : {global_variables.playlist_Block_open.identifiant}")
            global_variables.projet_instance.save_to_file(global_variables.projet_instance.file_Projet)
            majInfoPlaylist(playlist_tree, False)

def update_treeview_header_style(playlist_tree):
    root = playlist_tree.master
    style = ttk.Style(root)
    if global_variables.is_PlayList_From_Projet:         # Style pour les données provenant d'un bloc
        style.configure(
            "Custom.Treeview.Heading",
            background=global_variables.Couleur_BlocSelect,  # Fond vert pour les blocs
            foreground="black",  
            font=("Arial", 10)
        )       
    else:        # Style pour les données provenant d'un fichier
        style.configure(
            "Custom.Treeview.Heading",
            background=global_variables.Couleur_EntetePlaylist,  # Fond bleu pour les fichiers
            foreground="black",
            font=("Arial", 10)
        )
