# fichier: recherche_functions.py
import tkinter as tk
import os, json

from tkinter import ttk
#from typing import Dict
#from custom_types import Dialogue
from data_loader import load_json

from LectureOgg import JouerAudio
from general_functions import get_SousTitres_by_id, extraire_WOLVENKIT_localise_path, get_file_path

import global_variables  # Importer les variables globales

#definition du Tableau Principal
def setup_TableauPrincipal(root, columns):
    # Frame principale pour contenir le tableau principal et le panneau d'informations
    main_frame = tk.Frame(root)
    main_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=1)  # Remplacez fill=tk.BOTH par fill=tk.X

    # Configuration du tableau principal (tree)
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=12, selectmode="extended")
    
    
    # Configurer les en-têtes de colonnes avec la possibilité de trier les données
    for column in columns:
        tree.heading(column, text=column, command=lambda c=column: sort_tree(tree, c, False))

    # Ajouter une barre de défilement verticale uniquement
    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)

    # Configurer le tableau pour utiliser la barre de défilement verticale uniquement
    tree.configure(yscroll=scrollbar.set)

    # Positionner la barre de défilement verticale et le tableau principal dans la frame principale
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)

    return tree

#Fonction pour la selection d'une ligne du tableau principal
def SelectionLigne(event, tree):
    selected_item = tree.selection()[0]
    selected_values = tree.item(selected_item, 'values')

    selected_gender = global_variables.vSexe.get()
    if selected_gender == global_variables.vHomme:
        audio_value = selected_values[4]
    else:
        audio_value = selected_values[3]

    JouerAudio(audio_value)

# Fonction pour trier le tableau principal
def sort_tree(tree, col, reverse):
    # Récupérer toutes les lignes et les trier en fonction de la colonne spécifiée
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    l.sort(reverse=reverse)

    # Réorganiser les lignes dans l'ordre trié
    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)

    # Mettre à jour le titre de la colonne pour indiquer le sens du tri
    tree.heading(col, command=lambda: sort_tree(tree, col, not reverse))    


    
# Fonction pour afficher les données dans le tableau
def generate_and_save_json(output_path):
    # Charger les données JSON
    data = load_json(get_file_path(global_variables.bdd_Zhincore))
    if not data:
        print(f"Aucune donnée trouvée dans {get_file_path(global_variables.bdd_Zhincore)}")
        return

    processed_data = []
    # Traiter les données
    for key, entry in data.items():
        # ID
        id = key

        #TRADUCTION !
        # Récupérer la quête
        quete = entry.get("_path", global_variables.pas_Info)
        quete_path = extraire_WOLVENKIT_localise_path(quete)

        fichierQuete = ""        
        if isinstance(quete_path, str):  # Vérifie si c'est une chaîne
            fichierQuete = quete_path + ".json.json"

        result = get_SousTitres_by_id(fichierQuete, id)
        if result:
            #print(f"Female Variant: {result['femaleVariant']}")
            #print(f"Male Variant: {result['maleVariant']}")
            female_text = result['femaleVariant']
            male_text = result['maleVariant']
        else:
            #print("String ID non trouvé.")
            female_text = ""
            male_text = ""

        # Récupérer les informations pour 'female'
        female_vo = entry.get("female", {}).get("vo", {}).get("main", global_variables.pas_Info)

        # Récupérer les informations pour 'male'
        male_vo = entry.get("male", {}).get("vo", {}).get("main", global_variables.pas_Info)

        # Vérifier si 'male_vo' ou 'female_vo' contient "v_"
        isV = "v_" in (male_vo or "") or "v_" in (female_vo or "")         
        
        if not male_text or male_text == global_variables.pas_Info:
            male_text = female_text        
        if not female_text or female_text == global_variables.pas_Info:
            female_text = male_text # a Confirmer si ca existe !?
       
        if not male_vo or male_vo == global_variables.pas_Info:       
            if isV :
                essai = female_vo.replace("_f_", "_m_")
                if os.path.isfile(extraire_WOLVENKIT_localise_path(essai)):
                    male_vo = essai  
                # peut etre que le son n'existe pas -->  verifier si fichier existe avec extraire_WOLVENKIT_localise_path(male_vo)
            else :
                essai = female_vo.replace("_f_", "_m_")
                if os.path.isfile(extraire_WOLVENKIT_localise_path(essai)):
                    male_vo = essai  
                else:
                    male_vo = female_vo

        if not female_vo or female_vo == global_variables.pas_Info:       
            if isV :
                essai = male_vo.replace("_m_", "_f_")
                if os.path.isfile(extraire_WOLVENKIT_localise_path(essai)):
                    female_vo = essai  
                # peut etre que le son n'existe pas -->  verifier si fichier existe avec extraire_WOLVENKIT_localise_path(male_vo)
            else :
                essai = male_vo.replace("_m_", "_f_")
                if os.path.isfile(extraire_WOLVENKIT_localise_path(essai)):
                    female_vo = essai  
                else:                
                    female_vo = male_vo                
      
        # Sauvegarder dans une structure
        processed_data.append({
            global_variables.data_ID: id,
            global_variables.data_F_SubTitle: female_text,
            global_variables.data_M_SubTitle: male_text,
            global_variables.data_F_Voice: female_vo,
            global_variables.data_M_Voice: male_vo,
            global_variables.data_Quest: quete
        })        

    # Sauvegarder les données dans le fichier JSON
    save_data_to_json(output_path, processed_data)
        

def save_data_to_json(file_path, data):
    """
    Sauvegarde les informations dans un fichier JSON.
    :param file_path: Chemin où sauvegarder le fichier JSON.
    :param data: Les données à sauvegarder (dictionnaire).
    """
    try:
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"Données sauvegardées dans : {file_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données : {e}")


def load_data_into_tree(tree):
    try:
        if global_variables.dataSound == None:
            with open(global_variables.bdd_Localisation_Json, "r", encoding="utf-8") as json_file:
                global_variables.dataSound = json.load(json_file)
                print(f"Données chargées depuis : {global_variables.bdd_Localisation_Json}")            
        else :
            print(f"Données chargées depuis : global_variables.dataSound")
        
        # Supprimer les anciennes données dans le Treeview
        tree.delete(*tree.get_children())

        # Ajouter les nouvelles données
        for entry in global_variables.dataSound:
            tree.insert("", tk.END, values=(
                entry[global_variables.data_ID],
                entry[global_variables.data_F_SubTitle],
                entry[global_variables.data_M_SubTitle],
                entry[global_variables.data_F_Voice],
                entry[global_variables.data_M_Voice],
                entry[global_variables.data_Quest]
            ))
        
    except Exception as e:
        print(f"Erreur lors de la lecture des données : {e}")

# Fonction pour afficher les données dans le tableau
def open_and_display_json(tree, file_path):
    if not os.path.exists(global_variables.bdd_Localisation_Json):
        print(f"Fichier {global_variables.bdd_Localisation_Json} introuvable. Génération du fichier...")
        generate_and_save_json(global_variables.bdd_Localisation_Json)
    
    load_data_into_tree(tree)


