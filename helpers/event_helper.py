from model.firdaws_db import Event
from datetime import datetime
from config.db import db
from logger.logger_config import get_logger

logger = get_logger()


class EventHelper:
    @staticmethod
    def format_and_validate(data, created_by_id=None):
        """Formate, prépare et valide les données d'un événement"""
        errors = {}
        
        # Préparation & Nettoyage
        formatted = {
            'title': data.get('title', '').strip(),
            'date_str': data.get('date'),
            'time': data.get('time', '00:00').strip(),
            'location': data.get('location', 'Mosquée').strip(),
            'description': data.get('description', '').strip(),
            'imam': data.get('imam', '').strip(),
            'type': data.get('type', 'Événement').strip(),
            'image_url': data.get('image_url', '').strip(),
            'max_participants': data.get('max_participants'),
            'current_participants': data.get('current_participants', 0)
        }
        
        # Validations
        if not formatted['title']:
            errors['title'] = 'Le titre est requis'
        if not formatted['date_str']:
            errors['date'] = 'La date est requise'
        else:
            try:
                formatted['date'] = datetime.strptime(formatted['date_str'], '%Y-%m-%d').date()
            except ValueError:
                errors['date'] = 'Format de date invalide (attendu: YYYY-MM-DD)'
        
        # Ajouter l'ID du créateur si fourni
        if created_by_id:
            formatted['created_by_admin'] = created_by_id
            
        # Supprimer la clé temporaire
        formatted.pop('date_str', None)
        
        # Nettoyer les valeurs None
        formatted = {k: v for k, v in formatted.items() if v is not None}
        
        return formatted, errors


# class EventHelper:
#     """Helpers unifiés pour la gestion des événements"""
    
#     @staticmethod
#     def format_and_validate(data, admin_id=None, user_id=None):
#         """Formate, prépare et valide les données d'un événement"""
#         errors = {}
        
#         # Préparation & Nettoyage
#         formatted = {
#             'title': data.get('title', '').strip(),
#             'date_str': data.get('date'),
#             'time': data.get('time', '00:00').strip(),
#             'location': data.get('location', 'Mosquée').strip(),
#             'description': data.get('description', '').strip(),
#             'imam': data.get('imam', '').strip(),
#             'type': data.get('type', 'Événement').strip(),
#             'image_url': data.get('image_url', '').strip(),
#             'max_participants': data.get('max_participants'),
#             'current_participants': data.get('current_participants', 0)
#         }
        
#         # Validations strictes
#         if not formatted['title']:
#             errors['title'] = 'Le titre est requis'
#         if not formatted['date_str']:
#             errors['date'] = 'La date est requise'
#         else:
#             try:
#                 formatted['date'] = datetime.strptime(formatted['date_str'], '%Y-%m-%d').date()
#             except ValueError:
#                 errors['date'] = 'Format de date invalide (attendu: YYYY-MM-DD)'
        
#         # Gestion du created_by - priorité à admin_id
#         if admin_id:
#             formatted['created_by'] = admin_id
#         elif user_id:
#             formatted['created_by'] = user_id
#         else:
#             errors['created_by'] = 'ID du créateur requis'
            
#         # Supprimer la clé temporaire brute
#         formatted.pop('date_str', None)
        
#         # Supprimer les champs None
#         formatted = {k: v for k, v in formatted.items() if v is not None}
        
#         return formatted, errors


# class EventHelper:
#     """Helpers unifiés pour la gestion des événements"""
    
#     @staticmethod
#     def format_and_validate(data, admin_id=None):
#         """Formate, prépare et valide les données d'un événement"""
#         errors = {}
        
#         # Préparation & Nettoyage
#         formatted = {
#             'title': data.get('title', '').strip(),
#             'date_str': data.get('date'),
#             'time': data.get('time', '00:00').strip(),
#             'location': data.get('location', 'Mosquée').strip(),
#             'description': data.get('description', '').strip(),
#             'imam': data.get('imam', '').strip(),
#             'type': data.get('type', 'Événement').strip(),
#             'image_url': data.get('image_url', '').strip()
#         }
        
#         # Validations strictes
#         if not formatted['title']:
#             errors['title'] = 'Le titre est requis'
#         if not formatted['date_str']:
#             errors['date'] = 'La date est requise'
#         else:
#             try:
#                 # Convertit la chaîne 'YYYY-MM-DD' en objet date Python
#                 formatted['date'] = datetime.strptime(formatted['date_str'], '%Y-%m-%d').date()
#             except ValueError:
#                 errors['date'] = 'Format de date invalide (attendu: YYYY-MM-DD)'
        
#         if admin_id:
#             formatted['created_by'] = admin_id
            
#         # Supprimer la clé temporaire brute pour ne pas polluer l'instanciation de l'objet
#         formatted.pop('date_str', None)
        
#         return formatted, errors

#     @staticmethod
#     def get_upcoming(limit=5):
#         """Récupère les prochains événements non archivés à partir d'aujourd'hui"""
#         today = datetime.now().date()
#         return Event.query.filter(
#             Event.date >= today, 
#             Event.archived == False
#         ).order_by(Event.date.asc(), Event.time.asc()).limit(limit).all()

#     @staticmethod
#     def search(query):
#         """Recherche multicritère insensible à la casse"""
#         search_pattern = f"%{query}%"
#         return Event.query.filter(
#             Event.archived == False,
#             (Event.title.ilike(search_pattern) | 
#              Event.description.ilike(search_pattern) | 
#              Event.imam.ilike(search_pattern))
#         ).order_by(Event.date.desc()).all()

#     @staticmethod
#     def get_stats():
#         """Centralise les statistiques globales des événements"""
#         today = datetime.now().date()
#         return {
#             'total': Event.query.count(),
#             'active': Event.query.filter_by(archived=False).count(),
#             'archived': Event.query.filter_by(archived=True).count(),
#             'upcoming': Event.query.filter(Event.date >= today, Event.archived == False).count()
#         }

#     @staticmethod
#     def toggle_archive(event_id, archive_status=True):
#         """Archive ou désarchive un événement"""
#         event = Event.query.get(event_id)
#         if event:
#             event.archived = archive_status
#             db.session.commit()
#             return True
#         return False