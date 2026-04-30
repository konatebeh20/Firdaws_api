import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from logger.logger_config import get_logger

logger = get_logger()

class FileUploadHelper:
    """Helper pour l'upload de fichiers"""
    
    @staticmethod
    def save_file(file, subfolder='documents'):
        """Sauvegarde un fichier et retourne son URL"""
        try:
            # Créer le dossier s'il n'existe pas
            upload_folder = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                subfolder
            )
            os.makedirs(upload_folder, exist_ok=True)
            
            # Sécuriser le nom du fichier
            filename = secure_filename(file.filename)
            # Ajouter un UUID pour éviter les doublons
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            filepath = os.path.join(upload_folder, unique_filename)
            file.save(filepath)
            
            # Retourner l'URL relative
            return f"/uploads/{subfolder}/{unique_filename}"
            
        except Exception as e:
            logger.error(f"Erreur upload fichier: {str(e)}")
            return None
    
    @staticmethod
    def delete_file(file_url):
        """Supprime un fichier"""
        try:
            if file_url and file_url.startswith('/uploads/'):
                filepath = os.path.join(
                    current_app.root_path,
                    file_url.lstrip('/')
                )
                if os.path.exists(filepath):
                    os.remove(filepath)
                    return True
        except Exception as e:
            logger.error(f"Erreur suppression fichier: {str(e)}")
        return False
    
    @staticmethod
    def get_file_size(file):
        """Retourne la taille du fichier en format lisible"""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        return FileUploadHelper.format_size(size)
    
    @staticmethod
    def format_size(bytes):
        """Formate la taille en Ko/Mo/Go"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"