from model.firdaws_db import Khutba
from datetime import datetime
from logger.logger_config import get_logger

logger = get_logger()

class KhutbaHelper:
    """Helpers pour la gestion des khutba"""
    
    @staticmethod
    def format_khutba_data(data, admin_id=None):
        """Formate et valide les données d'une khutba"""
        formatted = {
            'title': data.get('title', '').strip(),
            'date': data.get('date', datetime.now().strftime('%d/%m/%Y')),
            'imam': data.get('imam', '').strip(),
            'content': data.get('content', '').strip(),
        }
        
        errors = {}
        if not formatted['title']:
            errors['title'] = 'Le titre est requis'
        if not formatted['imam']:
            errors['imam'] = "Le nom de l'imam est requis"
        
        if admin_id:
            formatted['created_by'] = admin_id
        
        return formatted, errors
    
    @staticmethod
    def get_latest_khutba(limit=5):
        """Récupère les dernières khutba"""
        khutba = Khutba.query.filter_by(archived=False)\
                              .order_by(Khutba.created_at.desc())\
                              .limit(limit).all()
        return khutba
    
    @staticmethod
    def get_khutba_by_imam(imam_name):
        """Récupère les khutba d'un imam spécifique"""
        khutba = Khutba.query.filter(
            Khutba.imam.ilike(f"%{imam_name}%"),
            Khutba.archived == False
        ).order_by(Khutba.created_at.desc()).all()
        return khutba