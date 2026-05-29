import os
from model.firdaws_db import Document
from logger.logger_config import get_logger

# from werkzeug.utils import secure_filename

logger = get_logger()

class DocumentHelper:
    """Helpers pour la gestion des documents"""
    
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt' , 'zip', 'jpg', 'jpeg', 'png', 'gif'}
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in DocumentHelper.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_file_icon(filename: str) -> str:
        """Détermine dynamiquement l'émoji icône d'après l'extension réelle du fichier"""
        if '.' not in filename:
            return '📁'
        
        ext = filename.rsplit('.', 1)[1].lower()
        icons = {
            'pdf': '📄',
            'doc': '📝', 'docx': '📝', 'txt': '📃',
            'xls': '📊', 'xlsx': '📊', 
            'ppt': '📽️', 'pptx': '📽️',
            'zip': '🗜️',
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️'
        }
        return icons.get(ext, '📁')
    
    
        # for unit in ['B', 'KB', 'MB', 'GB']:
        #     if size_bytes < 1024.0:
        #         return f"{size_bytes:.1f} {unit}"
        #     size_bytes /= 1024.0
        # return f"{size_bytes:.1f} TB"
    
    
    @staticmethod
    def validate_data(data: dict) -> dict:
        """Valide les données — retourne un dict d'erreurs (vide si OK)"""
        errors = {}
        if not data:
            return {'general': 'Données manquantes'}
        
        title = data.get('title', '').strip()
        
        if not title:
            errors['title'] = 'Le titre du document est requis'
            
        return errors

        

    @staticmethod
    def prepare_data(data: dict, admin_id: int) -> dict:
        """
        Prépare structurellement le dictionnaire final prêt à être injecté 
        dans l'instanciation de ton modèle Document SQLALchemy.
        """
        
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'PDF'
        
        return {
            'title': data.get('title', '').strip(),
            'description': data.get('description', '').strip(),
            'author': data.get('author', 'Anonyme').strip(),
            'type': ext.upper(),
            'icon': DocumentHelper.get_file_icon(filename),
            'file_size': DocumentHelper.format_file_size(size_bytes),
            'file_url': file_url,
            'created_by': admin_id,
        }
        

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Convertit intelligemment une taille en octets (int) en chaîne lisible (KB, MB, etc.)"""
        try:
            size_float = float(size_bytes)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_float < 1024.0:
                    return f"{size_float:.1f} {unit}"
                size_float /= 1024.0
            return f"{size_float:.1f} TB"
        except (ValueError, TypeError):
            return "0.0 B"
        
