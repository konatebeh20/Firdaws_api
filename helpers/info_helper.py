from model.firdaws_db import Info
from logger.logger_config import get_logger

logger = get_logger()

class InfoHelper:
    """Helpers pour la gestion des informations"""
    
    @staticmethod
    def validate_data(data):
        errors = {}
        if not data.get('title'):
            errors['title'] = 'Le titre est requis'
        if not data.get('content'):
            errors['content'] = 'Le contenu est requis'
        return errors

    @staticmethod
    def prepare_data(data, admin_id):
        return {
            'title': data.get('title', '').strip(),
            'content': data.get('content', '').strip(),
            'category': data.get('category', 'Général').strip(),
            'is_published': data.get('is_published', True),
            'created_by': admin_id
        }
    
    @staticmethod
    def get_recent_infos(limit=5):
        """Récupère les informations les plus récentes"""
        infos = Info.query.filter_by(archived=False)\
                         .order_by(Info.created_at.desc())\
                         .limit(limit).all()
        return infos
    
    @staticmethod
    def search_infos(query):
        """Recherche dans les informations"""
        search = f"%{query}%"
        infos = Info.query.filter(
            Info.archived == False,
            (Info.title.ilike(search) | Info.content.ilike(search))
        ).order_by(Info.created_at.desc()).all()
        return infos
