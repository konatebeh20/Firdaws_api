import logging
import os
from datetime import datetime

# Créer le dossier logs s'il n'existe pas
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configuration du logger principal
logger = logging.getLogger('nour_firdaws')
logger.setLevel(logging.DEBUG)

# Format des logs
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler pour fichier
file_handler = logging.FileHandler(f'logs/nour_firdaws_{datetime.now().strftime("%Y%m%d")}.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Handler pour console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Ajouter les handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Logger pour les erreurs critiques
error_logger = logging.getLogger('nour_firdaws_error')
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler('logs/error.log')
error_handler.setFormatter(formatter)
error_logger.addHandler(error_handler)

def get_logger():
    """Retourne le logger principal"""
    return logger

def get_error_logger():
    """Retourne le logger d'erreurs"""
    return error_logger