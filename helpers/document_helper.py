from model.firdaws_db import Document
import os
from werkzeug.utils import secure_filename
from logger.logger_config import get_logger

logger = get_logger()

class DocumentHelper:
    """Helpers pour la gestion des documents"""
    
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'}
    ALLOWED_MIMETYPES = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    }
    
    @staticmethod
    def format_document_data(data, admin_id=None):
        """Formate et valide les données d'un document"""
        formatted = {
            'title': data.get('title', '').strip(),
            'description': data.get('description', '').strip(),
            'author': data.get('author', '').strip(),
            'type': data.get('type', 'PDF').strip(),
            'icon': data.get('icon', '📄'),
            'file_size': data.get('file_size', ''),
            'file_url': data.get('file_url', '#'),
        }
        
        errors = {}
        if not formatted['title']:
            errors['title'] = 'Le titre est requis'
        
        if admin_id:
            formatted['created_by'] = admin_id
        
        return formatted, errors
    
    @staticmethod
    def allowed_file(filename):
        """Vérifie si l'extension du fichier est autorisée"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in DocumentHelper.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_file_icon(filename):
        """Retourne l'icône correspondant au type de fichier"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        icons = {
            'pdf': '📄',
            'doc': '📝',
            'docx': '📝',
            'ppt': '📊',
            'pptx': '📊',
            'xls': '📈',
            'xlsx': '📈',
            'txt': '📃'
        }
        return icons.get(ext, '📁')
    
    @staticmethod
    def format_file_size(size_bytes):
        """Formate la taille du fichier en format lisible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
