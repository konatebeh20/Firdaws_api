from model.firdaws_db import Event
from datetime import datetime
from logger.logger_config import get_logger

logger = get_logger()

class EventHelper:
    """Helpers pour la gestion des événements"""
    
    @staticmethod
    def format_event_data(data, admin_id=None):
        """Formate et valide les données d'un événement"""
        formatted = {
            'title': data.get('title', '').strip(),
            'date': data.get('date'),
            'time': data.get('time'),
            'imam': data.get('imam', '').strip(),
            'description': data.get('description', '').strip(),
            'type': data.get('type', 'Événement'),
        }
        
        # Validation
        errors = {}
        if not formatted['title']:
            errors['title'] = 'Le titre est requis'
        if not formatted['date']:
            errors['date'] = 'La date est requise'
        if not formatted['time']:
            errors['time'] = 'L\'heure est requise'
        
        if admin_id:
            formatted['created_by'] = admin_id
        
        return formatted, errors
    
    @staticmethod
    def get_upcoming_events(limit=5):
        """Récupère les prochains événements"""
        today = datetime.now().date()
        events = Event.query.filter(
            Event.date >= today,
            Event.archived == False
        ).order_by(Event.date).limit(limit).all()
        return events
    
    @staticmethod
    def get_event_stats():
        """Statistiques des événements"""
        total = Event.query.count()
        active = Event.query.filter_by(archived=False).count()
        archived = Event.query.filter_by(archived=True).count()
        upcoming = Event.query.filter(
            Event.date >= datetime.now().date(),
            Event.archived == False
        ).count()
        
        return {
            'total': total,
            'active': active,
            'archived': archived,
            'upcoming': upcoming
        }
    
    @staticmethod
    def search_events(query):
        """Recherche d'événements"""
        search = f"%{query}%"
        events = Event.query.filter(
            Event.archived == False,
            (Event.title.ilike(search) | 
             Event.description.ilike(search) |
             Event.imam.ilike(search))
        ).order_by(Event.date).all()
        return events