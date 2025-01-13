import configparser
import os
from tkinter import filedialog, Tk

class UserConfig:
    def __init__(self, file_path="userconfig.ini"):
        #    Initialise l'objet UserConfig avec le chemin du fichier de configuration.    Si le fichier n'existe pas, il sera créé lors de la sauvegarde.
        self.file_path = file_path
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # Respecter la casse des clés
        #self._load_config()
        self.read_or_initialize

    def _load_config(self):
        #        Charge la configuration depuis le fichier ini. Si le fichier n'existe pas, initialise une structure vide.
        if os.path.exists(self.file_path):
            self.config.read(self.file_path)
        else:
            print(f"File {self.file_path} not found. Created while saving.")

    def save(self):
        #     Sauvegarde les données actuelles de la configuration dans le fichier ini.
        with open(self.file_path, "w") as configfile:
            self.config.write(configfile)
        print(f"Configuration saved in {self.file_path}.")

    def get(self, section, key, default=None):
        #    Récupère la valeur d'une clé dans une section donnée. Retourne une valeur par défaut si la clé n'existe pas.
        return self.config.get(section, key, fallback=default)

    def set(self, section, key, value):
        #     Met à jour ou ajoute une clé dans une section donnée.
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        print(f"Parameter updated : [{section}] {key} = {value}")
        self.save()

    def read_or_initialize2(self):
        #Charge ou initialise la configuration si le fichier n'existe pas. Demande à l'utilisateur un chemin de projet Wolvenkit si nécessaire.
        if not os.path.exists(self.file_path):
            root = Tk()
            root.withdraw()  # Masquer la fenêtre principale de tkinter
            project_path = filedialog.askdirectory(
                title="Select the Wolvenkit project path (The location where you extracted the game localization files)"
            )
            root.destroy()

            if not project_path:
                raise ValueError("No path selected. Cannot continue without setting PROJECT_WOLVENKIT_PATH.")

            # Initialiser les données par défaut
            self.set("SETTINGS", "PROJECT_WOLVENKIT_PATH", project_path)
            self.set("SETTINGS", "LANGUAGE", "en-us")
        else:
            self._load_config()

    def read_or_initialize(self):
        # Charge ou initialise la configuration si le fichier n'existe pas.  Vérifie que PROJECT_WOLVENKIT_PATH est défini et que le chemin existe.
        # Si le chemin est manquant ou invalide, redemande à l'utilisateur de sélectionner un dossier.
        if not os.path.exists(self.file_path):
            # Fichier de configuration inexistant, demander le chemin du projet
            print(f"File {self.file_path} not found. Initializing.")
            self._prompt_and_set_project_path()
        else:
            # Charger la configuration existante
            self._load_config()

            # Vérifier si PROJECT_WOLVENKIT_PATH est défini
            project_path = self.get("SETTINGS", "PROJECT_WOLVENKIT_PATH", default=None)
            if not project_path or not os.path.exists(project_path):
                if not project_path:
                    print("PROJECT_WOLVENKIT_PATH not found or empty.")
                else:
                    print(f"Path specified for PROJECT_WOLVENKIT_PATH not found: {project_path}")
                self._prompt_and_set_project_path()

    def _prompt_and_set_project_path(self):
        # Demande à l'utilisateur de sélectionner un dossier pour PROJECT_WOLVENKIT_PATH et met à jour la configuration en conséquence.
        root = Tk()
        root.withdraw()  # Masquer la fenêtre principale de tkinter
        project_path = filedialog.askdirectory(
            title="Select the Wolvenkit project path (The location where you extracted the game localization files)"
        )
        root.destroy()

        if not project_path:
            raise ValueError("No path selected. Cannot continue without defining PROJECT_WOLVENKIT_PATH.")

        # Enregistrer le chemin du projet et initialiser les paramètres par défaut
        self.set("SETTINGS", "PROJECT_WOLVENKIT_PATH", project_path)
        if not self.get("SETTINGS", "LANGUAGE", default=None):
            self.set("SETTINGS", "LANGUAGE", "en-us")
