from datetime import datetime, timezone
from sqlalchemy import or_
from model.firdaws_db import Info
from config.db import db
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
    def _parse_datetime(value):
        """Parse une chaîne ISO en datetime, retourne None si invalide"""
        if not value or not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _now():
        return datetime.now(timezone.utc)

    @staticmethod
    def is_expired(info):
        expire_date = info.event_date or info.expire_date
        if not expire_date:
            return False
        return expire_date < InfoHelper._now()

    @staticmethod
    def archive_expired_infos():
        now = InfoHelper._now()
        expired_infos = Info.query.filter(
            Info.status != 'archived',
            or_(Info.event_date != None, Info.expire_date != None),
            or_(Info.event_date < now, Info.expire_date < now)
        ).all()
        if not expired_infos:
            return 0

        for info in expired_infos:
            info.status = 'archived'

        db.session.commit()
        return len(expired_infos)

    @staticmethod
    def prepare_data(data, admin_id):
        is_published = data.get('is_published', True)

        publish_date = InfoHelper._parse_datetime(
            data.get('publish_date') or data.get('published_at')
        )
        
        event_date = InfoHelper._parse_datetime(data.get('event_date'))
        expire_date = InfoHelper._parse_datetime(data.get('expire_date'))
        
        return {
            'title':        data.get('title', '').strip(),
            'content':      data.get('content', '').strip(),
            'priority':     data.get('priority') or data.get('category', 'normal'),  # ← les deux
            'status':       data.get('status') or ('published' if is_published else 'draft'),
            'publish_date': publish_date,
            'event_date':   event_date,
            'expire_date':  expire_date,
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
