import os, json
import subprocess

import tempfile
import shutil
import pygame

import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment

import global_variables  # Importer les variables globales

from general_functions import extraire_WOLVENKIT_localise_path, get_file_path

def stop_sound():
    #"""Arrête le son en cours de lecture."""
    pygame.mixer.music.stop()


def play_ogg_file(file_path):
    # """Joue un fichier .ogg, en arrêtant le son précédent."""
    try:
        # Initialiser pygame
        pygame.mixer.init()
        
        # Arrêter tout son en cours de lecture
        stop_sound()

        # Charger le fichier .ogg
        pygame.mixer.music.load(file_path)
        #print(f"Lecture de : {file_path}")

        # Jouer le fichier audio
        pygame.mixer.music.play()

    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")


def JouerAudio(audio_value):
    #test_path = r"D:\_CyberPunk-Creation\Dialogues-Multi\source\raw\ep1\localization\fr-fr\vo\judy_q307_f_2e6b76cd023bc000.ogg"
    # Arrêter tout son en cours de lecture
    print(f"chemin du wem audio_value : {audio_value}")
    if audio_value.endswith(".wem"):    
        sound_Path = extraire_WOLVENKIT_localise_path(audio_value)
        sound_Path = convert_wem_to_ogg_if_needed(sound_Path)
        if sound_Path:
            play_ogg_file(sound_Path)
        else:
            pygame.mixer.init()
            # Arrêter tout son en cours de lecture
            stop_sound()

# Définir la fonction de conversion
def convert_wem_to_ogg_if_needed(ogg_path):
    # Vérifier si le fichier .ogg existe déjà
    try:
        if os.path.exists(ogg_path):
            return ogg_path
        else :
            # Construire le chemin du fichier .wem correspondant
            #print(f"chemin du ogg_path : {ogg_path}")
            wem_path = ogg_path.replace("/raw/", "/archive/").replace(".ogg", ".wem")
            #print(f"chemin du wem_path : {wem_path}")
            # Vérifier si le fichier .wem existe
            if not os.path.exists(wem_path):
                raise FileNotFoundError(f"Le xxx fichier .wem correspondant n'existe pas : {wem_path}")

            # Créer les dossiers nécessaires pour le fichier .ogg s'ils n'existent pas
            ogg_dir = os.path.dirname(ogg_path)
            if not os.path.exists(ogg_dir):
                os.makedirs(ogg_dir)

            # Créer un répertoire temporaire spécifique à côté du script
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            try:
                # Convertir le fichier .wem en .ogg
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg", dir=temp_dir) as temp_ogg_file:
                    temp_ogg_path = temp_ogg_file.name

                conversion_command = [
                    get_file_path(global_variables.ww2ogg_path),
                    wem_path,
                    "--pcb",
                    get_file_path(global_variables.codebooks_path),
                    "-o",
                    temp_ogg_path
                ]
                print(f"conversion_command : {conversion_command}")
                try:
                    subprocess.run(conversion_command, check=True)
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(f"Erreur lors de la conversion du fichier .wem en .ogg : {e}")

                # Fermer le fichier temporaire avant d'utiliser revorb
                temp_ogg_file.close()

                # Appliquer revorb directement au fichier temporaire .ogg généré
                revorb_command = [
                    get_file_path(global_variables.revorb_path),
                    temp_ogg_path,
                    ogg_path
                ]
                print(f"revorb_command : {revorb_command}")
                try:
                    subprocess.run(revorb_command, check=True)
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(f"Erreur lors de l'application de revorb : {e}")

                # Déplacer le fichier revorb .ogg à l'emplacement souhaité
                #shutil.move(temp_ogg_path, ogg_path)
            
            finally:
                # Supprimer le dossier temporaire à la fin
                if os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                        print(f"Dossier temporaire supprimé : {temp_dir}")
                    except Exception as e:
                        print(f"Erreur lors de la suppression du dossier temporaire : {e}")
                        
            return ogg_path    
        
    except FileNotFoundError as e:
        print(f"Erreur : {e}")
        return None  # Retournez une valeur par défaut ou gérez autrement        

# Fonction pour fusionner les fichiers audio de la playlist
def fusionnerPlaylist(playlist_tree, NonfichierOGG):
    # Liste des fichiers audio à fusionner
    fichiers_audio = []
    items = playlist_tree.get_children()

    if not items:
        print("La playlist est vide. Impossible de fusionner.")
        return

    for item in items:
        selected_values = playlist_tree.item(item, "values")
        selected_gender = global_variables.vSexe.get()
        
        if selected_gender == global_variables.vHomme:
            audio_value = selected_values[4]
        else:
            audio_value = selected_values[3]

        if audio_value.endswith(".wem"): 
            audio_value = extraire_WOLVENKIT_localise_path(audio_value)
            #print(f"chemin audio {audio_value}.")
            if audio_value:
                fichiers_audio.append(audio_value)
            else:
                print(f"Aucun fichier audio trouvé pour l'élément {item}.")

    if not fichiers_audio:
        print("Aucun fichier audio valide trouvé pour fusionner.")
        return

    try:
        # Charger le premier fichier
        fusion_audio = AudioSegment.from_file(fichiers_audio[0], format="ogg")

        # Concaténer les fichiers restants
        for fichier in fichiers_audio[1:]:
            audio = AudioSegment.from_file(fichier, format="ogg")
            fusion_audio += audio

        # Demander où sauvegarder le fichier fusionné
        root = tk.Tk()
        root.withdraw()  # Masquer la fenêtre principale

        #nom_sans_extension = nom_playlist()
        
        default_dir = get_file_path("data/playlists/")    
        fichier_sauvegarde = filedialog.asksaveasfilename(
            title="Save the record of the playlist",
            initialfile=f"{NonfichierOGG}.ogg",  # Nom par défaut basé sur la playlist
            defaultextension=".ogg",
            filetypes=[("Fichiers OGG", "*.ogg")],
            initialdir=default_dir  # Dossier pré-sélectionné
        )
        root.destroy()  # Assurez-vous de détruire la fenêtre après utilisation
        if fichier_sauvegarde:
            # Exporter le fichier fusionné
            fusion_audio.export(fichier_sauvegarde, format="ogg")
            print(f"Fichier fusionné sauvegardé avec succès dans {fichier_sauvegarde}")
        else:
            print("Opération annulée. Aucun fichier sauvegardé.")
            return
        del fusion_audio  # Libérer les ressources AudioSegment

    except Exception as e:
        print(f"Erreur lors de la fusion des fichiers : {e}")



# Fonction pour fusionner les fichiers audio à partir d'un fichier JSON
def fusionner_audio_json(chemin_json="", chemin_ogg=""):
    # Charger les données du fichier JSON
    with open(chemin_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Vérifier que le JSON contient des données
    if not data:
        print("Le fichier JSON est vide.")
        return
    fusionner_audio_data(data, chemin_ogg)

def fusionner_audio_data(data=None, chemin_ogg=""):  
    try:        
        if not data:
            print("Le fichier JSON est vide.")
            return
                
        # Liste des fichiers audio à fusionner
        fichiers_audio = []

        selected_gender = global_variables.vSexe.get()
        
        if selected_gender == global_variables.vHomme:
            chemin_attribut = global_variables.data_M_Voice
        else:
            chemin_attribut = global_variables.data_F_Voice
       
        for entry in data:
            chemin_audio = entry.get(chemin_attribut, "")
            if chemin_audio.endswith(".wem"):  
                chemin_audio = extraire_WOLVENKIT_localise_path(chemin_audio)
                chemin_audio = convert_wem_to_ogg_if_needed(chemin_audio)

                if os.path.isfile(chemin_audio):                
                    fichiers_audio.append(chemin_audio)
                else:
                    print(f"audio EXTRAIT n'existe pas : {chemin_audio}.")       

        #print(f"tous les fichiers_audio valide : {fichiers_audio}.")   
        # Vérifier si des fichiers audio valides ont été trouvés
        fichiers_audio = [os.path.abspath(fichier) for fichier in fichiers_audio if os.path.exists(fichier)]
        if not fichiers_audio:
            print("Aucun fichier audio valide trouvé pour la fusion.")
            return

        # Charger et fusionner les fichiers audio
        fusion_audio = AudioSegment.from_file(fichiers_audio[0], format="ogg")
        for fichier in fichiers_audio[1:]:
            audio = AudioSegment.from_file(fichier, format="ogg")
            fusion_audio += audio

        # Sauvegarder le fichier fusionné
        fusion_audio.export(chemin_ogg, format="ogg")
        print(f"Fichier audio fusionné sauvegardé avec succès : {chemin_ogg}")

    except Exception as e:
        print(f"Erreur lors de la fusion des fichiers audio : {e}")
  


