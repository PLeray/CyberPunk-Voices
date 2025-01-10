# Variables globlaes du projet
need_to_save_Projet = False
need_to_save_Playlist = False

is_PlayList_From_Projet = False

projet_instance = None  #Objet pour les projets
path_dernier_projet = ""
ligne_manuelle_instance = None  #Objet pour les nouvelle lignes
user_config = None #Objet pour gérer la conf user

dataSound = None  # Stockage donnée
#rootAccess = None  # Définition initiale

playlist_name_label = ""  # Définition initiale
playlist_count_label = None  # Définition initiale
principal_count = None  # Définition initiale

playlist_file_open = None  # Définition initiale
playlist_Block_open = None  # Définition initiale

playlist_tree = None # la playlist
# Variable globale pour la fenêtre de projet

vSexe  = None  # Définition initiale

nombre_Ligne = "number of lines"

setToAll = "ALL"
pas_Info = "NOTHING" # Définition initiale

filter_with = "Filter with "

vHomme = "V as man"
vFemme = "V as woman"

titleCol_ID = "ID"
titleCol_F_SubTitle = "(F) Subtitles"
titleCol_M_SubTitle = "(M) Subtitles"
titleCol_F_Voice = "(F) Voice"
titleCol_M_Voice = "(M) Voice"
titleCol_Quest = "Quest"

columns = (titleCol_ID, titleCol_F_SubTitle, titleCol_M_SubTitle, titleCol_F_Voice, titleCol_M_Voice, titleCol_Quest)
columns_homme = [titleCol_ID, titleCol_M_SubTitle, titleCol_M_Voice, titleCol_Quest]
columns_femme = [titleCol_ID, titleCol_F_SubTitle, titleCol_F_Voice, titleCol_Quest]

#utilisé dans la sauvegarde et BDD .json Attention !
data_ID = "stringId"
data_F_SubTitle = "femaleVariant"
data_M_SubTitle = "maleVariant"
data_F_Voice = "female_vo_path"
data_M_Voice = "male_vo_path"
data_Quest = "quest_path"

bdd_Localisation_Json="data/BDDjson/Base_fr-fr.json"

bdd_Zhincore = "data/BDDjson/subtitles.DIVQuO_-.json"

ww2ogg_path = ""
revorb_path = ""
codebooks_path = ""

project_WOLVENKIT_path = ""

# Variables globales
#CheminRacine = "D:\_CyberPunk-Creation\DialogueFR/source/raw/" # A suprimer
CheminLocalization = "localization/"
CheminLangue = "fr-fr"

# Couleurs
Couleur_BgSelectLigne = "#D3D3D3"  # Couleur pour les lignes sélectionnées
Couleur_TxtSelectLigne = "#000000"   # Couleur du texte pour les lignes sélectionnées

Couleur_Bloc = "white"  # Couleur par défaut pour les blocs

Couleur_EntetePlaylist = "#ddffd9"  #vert
Couleur_Etape = "#d9d9d9" # gris plus clair
Couleur_BlocSelect = "#33acff" # Bleu
Couleur_BlocSource = "#1dff03"  #vert
Couleur_BlocTarget = "red"
Couleur_BlocDefaut = "grey"
Couleur_Liaison = "#ff9333" # Orange
Couleur_SelectEtape = "#b884ff" # Violet

ETAPE_HEIGHT = 90  # Hauteur d'une étape
ETAPE_SPACING = 10  # Espacement vertical entre les étapes
BLOC_WIDTH = 300  # Largeur d'un bloc
BLOC_HEIGHT = 70  # Hauteur d'un bloc




