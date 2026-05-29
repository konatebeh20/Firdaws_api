import logging
import os
import sys
import io
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
file_handler = logging.FileHandler(f'logs/nour_firdaws_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Handler pour console
# Forcer l'encodage UTF-8 sur la sortie console pour éviter les erreurs d'encodage sous Windows
console_stream = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='backslashreplace')
console_handler = logging.StreamHandler(stream=console_stream)
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