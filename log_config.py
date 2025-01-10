# log_config.py
import logging
import sys

# Définir le fichier log
log_file = "application.log"

# Configurer le logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Affiche les logs dans le terminal
        logging.FileHandler(log_file, mode='a', encoding='utf-8')  # Enregistre les logs dans le fichier
    ]
)

# Classe pour rediriger les messages print() vers le logger
class LoggerWriter:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip():  # Ignore les lignes vides
            self.logger.log(self.level, message.strip())

    def flush(self):
        pass  # Nécessaire pour éviter les erreurs avec sys.stdout et sys.stderr

# Rediriger sys.stdout et sys.stderr vers le logger
sys.stdout = LoggerWriter(logging.getLogger(), logging.INFO)
sys.stderr = LoggerWriter(logging.getLogger(), logging.ERROR)
