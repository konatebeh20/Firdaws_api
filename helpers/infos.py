from model.firdaws_db import Info
from logger.logger_config import get_logger

logger = get_logger()

class InfoHelper:
    """Helpers pour la gestion des informations"""
    
    @staticmethod
    def format_info_data(data, admin_id=None):
        """Formate et valide les données d'une information"""
        formatted = {
            'title': data.get('title', '').strip(),
            'content': data.get('content', '').strip(),
        }
        
        errors = {}
        if not formatted['title']:
            errors['title'] = 'Le titre est requis'
        if not formatted['content']:
            errors['content'] = 'Le contenu est requis'
        
        if admin_id:
            formatted['created_by'] = admin_id
        
        return formatted, errors
    
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