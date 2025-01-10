# fichier: data_loader.py
import json
from typing import Dict
from custom_types import Dialogue  # Changez l'import si "types" cause un conflit

# Fonction pour charger et interpréter les données JSON
def load_json(file_path: str) -> Dict[str, Dialogue]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_path}' est introuvable.")
    except json.JSONDecodeError:
        print(f"Erreur : Le fichier '{file_path}' contient une erreur JSON.")
    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")
    return {}
