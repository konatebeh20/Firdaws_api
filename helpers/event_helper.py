from model.firdaws_db import Event
from datetime import datetime
from logger.logger_config import get_logger
from config.db import db

logger = get_logger()

class EventHelper:
    """Helpers pour la gestion des événements"""
    
    @staticmethod
    def validate_data(data):
        errors = {}
        if not data.get('title'):
            errors['title'] = 'Le titre est requis'
        if not data.get('date'):
            errors['date'] = 'La date est requise'
        return errors

    @staticmethod
    def prepare_data(data, admin_id):
        return {
            'title': data.get('title', '').strip(),
            'start_date': data.get('date'),
            'time': data.get('time', '00:00'),
            'location': data.get('location', 'Mosquée').strip(),
            'description': data.get('description', '').strip(),
            'imam': data.get('imam', '').strip(),
            'type': data.get('type', 'Événement').strip(),
            'created_by': admin_id
        }

    @staticmethod
    def format_date(date_str):
        if not date_str:
            return datetime.now()
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return datetime.now()

    @staticmethod
    def get_stats():
        return {
            'total': Event.query.count(),
            'active': Event.query.filter_by(archived=False).count(),
            'archived': Event.query.filter_by(archived=True).count()
        }

    @staticmethod
    def get_upcoming(limit=5):
        return Event.query.filter(Event.start_date >= datetime.now(), Event.archived == False)\
                         .order_by(Event.start_date.asc())\
                         .limit(limit).all()

    @staticmethod
    def search(query):
        search = f"%{query}%"
        return Event.query.filter(
            Event.archived == False,
            (Event.title.ilike(search) | Event.description.ilike(search))
        ).order_by(Event.start_date.desc()).all()

    @staticmethod
    def archive_event(event_id):
        event = Event.query.get(event_id)
        if event:
            event.archived = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def unarchive_event(event_id):
        event = Event.query.get(event_id)
        if event:
            event.archived = False
            db.session.commit()
            return True
        return False
