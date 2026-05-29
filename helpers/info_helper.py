from datetime import datetime
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
        is_published = data.get('is_published', True)
        publish_date = data.get('publish_date') or data.get('published_at')
        if isinstance(publish_date, str) and publish_date:
            try:
                publish_date = datetime.fromisoformat(publish_date)
            except ValueError:
                publish_date = None
        return {
            'title':        data.get('title', '').strip(),
            'content':      data.get('content', '').strip(),
            'priority':     data.get('priority') or data.get('category', 'normal'),  # ← les deux
            'status':       data.get('status') or ('published' if is_published else 'draft'),
            'publish_date': publish_date,
            'created_by':   admin_id
        }
    
    @staticmethod
    def get_recent_infos(limit=5):
        """Récupère les informations les plus récentes"""
        return Info.query.filter(
            Info.status.in_(['published', 'draft'])
        ).order_by(Info.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def search_infos(query):
        """Recherche dans les informations"""
        search = f"%{query}%"
        return Info.query.filter(
            Info.status != 'archived',
            (Info.title.ilike(search) | Info.content.ilike(search))
        ).order_by(Info.created_at.desc()).all()
