from model.firdaws_db import Khutba
from datetime import datetime
from logger.logger_config import get_logger
from config.db import db

logger = get_logger()

class KhutbaHelper:
    """Helpers pour la gestion des khutba"""
    
    @staticmethod
    def validate_data(data):
        """Valide les données d'une khutba"""
        errors = {}
        if not data.get('title'):
            errors['title'] = 'Le titre est requis'
        if not data.get('imam'):
            errors['imam'] = "Le nom de l'imam est requis"
        return errors

    @staticmethod
    def prepare_data(data, admin_id):
        """Prépare les données pour l'insertion"""
        return {
            'title': data.get('title', '').strip(),
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'imam': data.get('imam', '').strip(),
            'content': data.get('content', '').strip(),
            'created_by': admin_id
        }
    
    @staticmethod
    def get_latest(limit=5):
        """Récupère les dernières khotbas"""
        return Khutba.query.filter_by(archived=False)\
                           .order_by(Khutba.created_at.desc())\
                           .limit(limit).all()
    
    @staticmethod
    def get_by_imam(imam_name):
        """Récupère les khotbas d'un imam spécifique"""
        return Khutba.query.filter(
            Khutba.imam.ilike(f"%{imam_name}%"),
            Khutba.archived == False
        ).order_by(Khutba.created_at.desc()).all()
