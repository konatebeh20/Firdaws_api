from flask_restful import Resource
from flask import request, jsonify
from model.firdaws_db import Event
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import token_required, admin_required
from helpers.event_helper import EventHelper
from helpers.pagination_helper import PaginationHelper
from helpers.error_helper import log_error

logger = get_logger()

class EventApi(Resource):
    """Resource unique pour TOUS les endpoints événements"""
    
    # ========== DÉCORATEUR CONDITIONNEL ==========
    def get_current_admin(self):
        """Récupère l'admin si token présent"""
        from flask import request
        from helpers.auth_helper import verify_token
        
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if payload:
                from model.firdaws_db import Admin
                return Admin.query.get(payload['admin_id'])
        return None
    
    # ========== GET ==========
    def get(self, route=None, item_id=None):
        """Route GET dynamique unique"""
        try:
            current_admin = self.get_current_admin()
            
            # --- 1. GET /api/events/<int:item_id> ---
            if item_id and not route:
                event = Event.query.get(item_id)
                if not event:
                    return {'message': 'Événement non trouvé'}, 404
                return {'data': event.to_dict()}, 200
            
            # --- 2. GET /api/events/upcoming ---
            if route == 'upcoming':
                limit = request.args.get('limit', 5, type=int)
                events = EventHelper.get_upcoming(limit)
                return {
                    'events': [e.to_dict() for e in events],
                    'count': len(events)
                }, 200
            
            # --- 3. GET /api/events/search ---
            if route == 'search':
                query = request.args.get('q', '')
                if len(query) < 2:
                    return {'events': []}, 200
                events = EventHelper.search(query)
                return {
                    'events': [e.to_dict() for e in events],
                    'count': len(events)
                }, 200
            
            # --- 4. GET /api/events/admin ---
            if route == 'admin':
                if not current_admin:
                    return {'message': 'Authentification requise'}, 401
                events = Event.query.order_by(Event.event_date.desc()).all()
                return {
                    'data': [e.to_dict() for e in events],
                    'total': len(events),
                    'active': len([e for e in events if e.status == 'published']),
                    'draft': len([e for e in events if e.status == 'draft'])
                }, 200
            
            # --- 5. GET /api/events/stats ---
            if route == 'stats':
                return EventHelper.get_stats(), 200
            
            # --- 6. GET /api/events (par défaut) ---
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 100, type=int)
            include_archived = request.args.get('include_archived', 'false').lower() == 'true'
            
            if include_archived:
                query = Event.query.order_by(Event.event_date.desc())
            else:
                query = Event.query.filter_by(status='published').order_by(Event.event_date.desc())
            result = PaginationHelper.paginate(query, page, per_page)
            
            return {
                'data': [e.to_dict() for e in result['items']],
                'pagination': {k: v for k, v in result.items() if k != 'items'}
            }, 200
            
        except Exception as e:
            log_error(e, request, 'EventApi.get')
            return {'message': 'Erreur lors de la récupération'}, 500
    
    # ========== POST ==========
    @admin_required
    def post(self, current_admin, route=None, item_id=None):
        """Route POST dynamique unique"""
        try:
            data = request.get_json()
            
            # --- 1. POST /api/events/duplicate/<int:item_id> ---
            if route == 'duplicate' and item_id:
                event = Event.query.get(item_id)
                if not event:
                    return {'message': 'Événement non trouvé'}, 404
                
                new_event = Event(
                    title=f"{event.title} (copie)",
                    event_date=event.event_date,
                    description=event.description,
                    category=event.category,
                    location=event.location,
                    created_by=current_admin.id
                )
                db.session.add(new_event)
                db.session.commit()
                
                logger.info(f"✅ Événement dupliqué: {new_event.title}")
                return new_event.to_dict(), 201
            
            # --- 2. POST /api/events (création) ---
            errors = EventHelper.validate_data(data)
            if errors:
                return {'message': 'Erreur de validation', 'errors': errors}, 400
            
            event_data = EventHelper.prepare_data(data, current_admin.id)
            if 'event_date' in event_data:
                event_data['event_date'] = EventHelper.format_date(event_data['event_date'])
            
            event = Event(**event_data)
            db.session.add(event)
            db.session.commit()
            
            logger.info(f"✅ Événement créé: {event.title}")
            return {'data': event.to_dict()}, 201
            
        except Exception as e:
            log_error(e, request, 'EventApi.post')
            db.session.rollback()
            return {'message': 'Erreur lors de la création'}, 500
    
    # ========== PUT ==========
    @admin_required
    def put(self, current_admin, route=None, item_id=None):
        """Route PUT dynamique unique"""
        try:
            if not item_id:
                return {'message': 'ID requis'}, 400
            
            event = Event.query.get(item_id)
            if not event:
                return {'message': 'Événement non trouvé'}, 404
            
            data = request.get_json()

            # --- 1. PUT /api/events/archive/<int:item_id> ---
            if route == 'archive':
                event.status = data.get('status', 'archived')
                db.session.commit()
                action = "archivé" if event.status == 'archived' else "désarchivé"
                logger.info(f"✅ Événement {action}: {event.title}")
                return {'data': event.to_dict()}, 200
            
            # --- 2. Mise à jour des champs ---
            updatable_fields = ['title', 'event_date', 'description', 'category', 'location', 'status']
            for field in updatable_fields:
                if field in data:
                    if field == 'event_date':
                        event.event_date = EventHelper.format_date(data.get('event_date'))
                    else:
                        setattr(event, field, data[field])
            
            db.session.commit()
            logger.info(f"✅ Événement modifié: {event.title}")
            
            return {'data': event.to_dict()}, 200
            
        except Exception as e:
            log_error(e, request, 'EventApi.put')
            db.session.rollback()
            return {'message': 'Erreur lors de la modification'}, 500
    
    # ========== DELETE ==========
    @admin_required
    def delete(self, current_admin, route=None, item_id=None):
        """Route DELETE dynamique unique"""
        try:
            # --- DELETE /api/events/<int:item_id> ---
            if not item_id:
                return {'message': 'ID requis'}, 400
            
            event = Event.query.get(item_id)
            if not event:
                return {'message': 'Événement non trouvé'}, 404
            
            db.session.delete(event)
            db.session.commit()
            
            logger.info(f"✅ Événement supprimé: {event.title}")
            return {'data': {'message': 'Événement supprimé', 'id': item_id}}, 200
            
        except Exception as e:
            log_error(e, request, 'EventApi.delete')
            db.session.rollback()
            return {'message': 'Erreur lors de la suppression'}, 500





# from flask_restful import Resource
# from flask import request, jsonify
# from model.firdaws_db import Event
# from config.db import db
# from logger.logger_config import get_logger
# from helpers.auth_helper import token_required, admin_required
# from helpers.event_helper import EventHelper
# from helpers.pagination_helper import PaginationHelper
# from helpers.error_helper import log_error
# import traceback

# logger = get_logger()

# class EventApi(Resource):
#     """Resource unique pour tous les endpoints événements"""
    
#     # ========== GET ==========
#     @token_required
#     def get(self, current_admin=None, route=None, item_id=None):
#         """Gère tous les GET : /events, /events/upcoming, /events/search, /events/admin, /events/<id>"""
#         try:
#             # GET /api/events/<int:id>
#             if item_id:
#                 event = Event.query.get(item_id)
#                 if not event:
#                     return {'message': 'Événement non trouvé'}, 404
#                 return event.to_dict(), 200
            
#             # GET /api/events/upcoming
#             if route == 'upcoming':
#                 limit = request.args.get('limit', 5, type=int)
#                 events = EventHelper.get_upcoming(limit)
#                 return {
#                     'events': [e.to_dict() for e in events],
#                     'count': len(events)
#                 }, 200
            
#             # GET /api/events/search
#             if route == 'search':
#                 query = request.args.get('q', '')
#                 if len(query) < 2:
#                     return {'events': []}, 200
#                 events = EventHelper.search(query)
#                 return {
#                     'events': [e.to_dict() for e in events],
#                     'count': len(events)
#                 }, 200
            
#             # GET /api/events/admin (admin seulement)
#             if route == 'admin':
#                 if not current_admin:
#                     return {'message': 'Authentification requise'}, 401
#                 events = Event.query.order_by(Event.archived, Event.start_date.desc()).all()
#                 return {
#                     'events': [e.to_dict() for e in events],
#                     'total': len(events),
#                     'active': len([e for e in events if not e.archived]),
#                     'archived': len([e for e in events if e.archived])
#                 }, 200
            
#             # GET /api/events (public)
#             page = request.args.get('page', 1, type=int)
#             per_page = request.args.get('per_page', 10, type=int)
            
#             query = Event.query.filter_by(archived=False).order_by(Event.start_date)
#             result = PaginationHelper.paginate(query, page, per_page)
            
#             return {
#                 'events': [e.to_dict() for e in result['items']],
#                 'pagination': {k: v for k, v in result.items() if k != 'items'},
#                 'stats': EventHelper.get_stats()
#             }, 200
            
#         except Exception as e:
#             log_error(e, request, 'EventApi.get')
#             return {'message': 'Erreur lors de la récupération'}, 500
    
#     # ========== POST ==========
#     @admin_required
#     def post(self, current_admin, route=None, item_id=None):
#         """Gère tous les POST : /events, /events/archive/<id>"""
#         try:
#             data = request.get_json()
            
#             # POST /api/events/archive/<id>
#             if route == 'archive' and item_id:
#                 event = Event.query.get(item_id)
#                 if not event:
#                     return {'message': 'Événement non trouvé'}, 404
                
#                 event.archived = data.get('archived', True)
#                 db.session.commit()
                
#                 action = "archivé" if event.archived else "désarchivé"
#                 logger.info(f"✅ Événement {action}: {event.title}")
#                 return event.to_dict(), 200
            
#             # POST /api/events (création)
#             errors = EventHelper.validate_data(data)
#             if errors:
#                 return {'message': 'Erreur de validation', 'errors': errors}, 400
            
#             event_data = EventHelper.prepare_data(data, current_admin.id)
#             event_data['date'] = EventHelper.format_date(event_data['date'])
            
#             event = Event(**event_data)
#             db.session.add(event)
#             db.session.commit()
            
#             logger.info(f"✅ Événement créé: {event.title}")
#             return event.to_dict(), 201
            
#         except Exception as e:
#             log_error(e, request, 'EventApi.post')
#             db.session.rollback()
#             return {'message': 'Erreur lors de la création'}, 500
    
#     # ========== PUT ==========
#     @admin_required
#     def put(self, current_admin, route=None, item_id=None):
#         """Gère tous les PUT : /events/<id>"""
#         try:
#             if not item_id:
#                 return {'message': 'ID requis'}, 400
            
#             event = Event.query.get(item_id)
#             if not event:
#                 return {'message': 'Événement non trouvé'}, 404
            
#             data = request.get_json()
            
#             # Mise à jour
#             if 'title' in data:
#                 event.title = data['title']
#             if 'date' in data:
#                 event.date = EventHelper.format_date(data['date'])
#             if 'time' in data:
#                 event.time = data['time']
#             if 'imam' in data:
#                 event.imam = data['imam']
#             if 'description' in data:
#                 event.description = data['description']
#             if 'type' in data:
#                 event.type = data['type']
            
#             db.session.commit()
#             logger.info(f"✅ Événement modifié: {event.title}")
            
#             return event.to_dict(), 200
            
#         except Exception as e:
#             log_error(e, request, 'EventApi.put')
#             db.session.rollback()
#             return {'message': 'Erreur lors de la modification'}, 500
    
#     # ========== DELETE ==========
#     @admin_required
#     def delete(self, current_admin, route=None, item_id=None):
#         """Gère tous les DELETE : /events/<id>"""
#         try:
#             if not item_id:
#                 return {'message': 'ID requis'}, 400
            
#             event = Event.query.get(item_id)
#             if not event:
#                 return {'message': 'Événement non trouvé'}, 404
            
#             db.session.delete(event)
#             db.session.commit()
            
#             logger.info(f"✅ Événement supprimé: {event.title}")
#             return {'message': 'Événement supprimé'}, 200
            
#         except Exception as e:
#             log_error(e, request, 'EventApi.delete')
#             db.session.rollback()
#             return {'message': 'Erreur lors de la suppression'}, 500

# from flask_restful import Resource
# from flask import request
# from model.firdaws_db import Event
# from config.db import db
# from logger.logger_config import get_logger
# from helpers.auth_helper import admin_required, token_required
# from helpers.event_helper import EventHelper
# from helpers.pagination_helper import PaginationHelper
# from helpers.validation_helper import ValidationHelper

# logger = get_logger()

# class EventListResource(Resource):
#     def get(self):
#         """Récupère tous les événements non archivés (public)"""
#         try:
#             page = request.args.get('page', 1, type=int)
#             per_page = request.args.get('per_page', 10, type=int)
            
#             query = Event.query.filter_by(archived=False).order_by(Event.start_date)
#             result = PaginationHelper.paginate(query, page, per_page)
            
#             return {
#                 'events': [e.to_dict() for e in result['items']],
#                 'pagination': {k: v for k, v in result.items() if k != 'items'},
#                 'stats': EventHelper.get_stats()
#             }, 200
#         except Exception as e:
#             logger.error(f"Erreur récupération événements: {str(e)}")
#             return {'message': 'Erreur lors de la récupération'}, 500
    
#     @admin_required
#     def post(self, current_admin):
#         """Crée un nouvel événement"""
#         try:
#             data = request.get_json()
            
#             # Validation
#             errors = EventHelper.validate_data(data)
#             if errors:
#                 return {'message': 'Erreur de validation', 'errors': errors}, 400
            
#             # Préparer les données
#             event_data = EventHelper.prepare_data(data, current_admin.id)
#             event_data['date'] = EventHelper.format_date(event_data['date'])
            
#             event = Event(**event_data)
#             db.session.add(event)
#             db.session.commit()
            
#             logger.info(f"✅ Événement créé: {event.title}")
#             return event.to_dict(), 201
            
#         except Exception as e:
#             logger.error(f"Erreur création événement: {str(e)}")
#             db.session.rollback()
#             return {'message': 'Erreur lors de la création'}, 500

# class EventResource(Resource):
#     def get(self, event_id):
#         """Récupère un événement spécifique"""
#         event = Event.query.get(event_id)
#         if not event:
#             return {'message': 'Événement non trouvé'}, 404
#         return event.to_dict(), 200
    
#     @admin_required
#     def put(self, current_admin, event_id):
#         """Modifie un événement"""
#         try:
#             event = Event.query.get(event_id)
#             if not event:
#                 return {'message': 'Événement non trouvé'}, 404
            
#             data = request.get_json()
            
#             # Mise à jour
#             if 'title' in data:
#                 event.title = data['title']
#             if 'date' in data:
#                 event.date = EventHelper.format_date(data['date'])
#             if 'time' in data:
#                 event.time = data['time']
#             if 'imam' in data:
#                 event.imam = data['imam']
#             if 'description' in data:
#                 event.description = data['description']
#             if 'type' in data:
#                 event.type = data['type']
            
#             db.session.commit()
#             logger.info(f"✅ Événement modifié: {event.title}")
            
#             return event.to_dict(), 200
            
#         except Exception as e:
#             logger.error(f"Erreur modification événement: {str(e)}")
#             db.session.rollback()
#             return {'message': 'Erreur lors de la modification'}, 500
    
#     @admin_required
#     def delete(self, current_admin, event_id):
#         """Supprime un événement"""
#         try:
#             event = Event.query.get(event_id)
#             if not event:
#                 return {'message': 'Événement non trouvé'}, 404
            
#             db.session.delete(event)
#             db.session.commit()
            
#             logger.info(f"✅ Événement supprimé: {event.title}")
#             return {'message': 'Événement supprimé'}, 200
            
#         except Exception as e:
#             logger.error(f"Erreur suppression événement: {str(e)}")
#             db.session.rollback()
#             return {'message': 'Erreur lors de la suppression'}, 500

# class EventArchiveResource(Resource):
#     @admin_required
#     def put(self, current_admin, event_id):
#         """Archive ou désarchive un événement"""
#         try:
#             event = Event.query.get(event_id)
#             if not event:
#                 return {'message': 'Événement non trouvé'}, 404
            
#             data = request.get_json()
#             event.archived = data.get('archived', True)
#             db.session.commit()
            
#             action = "archivé" if event.archived else "désarchivé"
#             logger.info(f"✅ Événement {action}: {event.title}")
            
#             return event.to_dict(), 200
            
#         except Exception as e:
#             logger.error(f"Erreur archivage événement: {str(e)}")
#             db.session.rollback()
#             return {'message': 'Erreur lors de l\'archivage'}, 500

# class EventAdminListResource(Resource):
#     @admin_required
#     def get(self, current_admin):
#         """Récupère TOUS les événements (admin)"""
#         try:
#             events = Event.query.order_by(Event.archived, Event.date.desc()).all()
#             return {
#                 'events': [e.to_dict() for e in events],
#                 'total': len(events),
#                 'active': len([e for e in events if not e.archived]),
#                 'archived': len([e for e in events if e.archived])
#             }, 200
#         except Exception as e:
#             logger.error(f"Erreur récupération admin événements: {str(e)}")
#             return {'message': 'Erreur lors de la récupération'}, 500

# class EventSearchResource(Resource):
#     def get(self):
#         """Recherche d'événements"""
#         try:
#             query = request.args.get('q', '')
#             if len(query) < 2:
#                 return {'events': []}, 200
            
#             events = EventHelper.search(query)
#             return {
#                 'events': [e.to_dict() for e in events],
#                 'count': len(events)
#             }, 200
#         except Exception as e:
#             logger.error(f"Erreur recherche événements: {str(e)}")
#             return {'message': 'Erreur lors de la recherche'}, 500

# class EventUpcomingResource(Resource):
#     def get(self):
#         """Récupère les prochains événements"""
#         try:
#             limit = request.args.get('limit', 5, type=int)
#             events = EventHelper.get_upcoming(limit)
#             return {
#                 'events': [e.to_dict() for e in events],
#                 'count': len(events)
#             }, 200
#         except Exception as e:
#             logger.error(f"Erreur récupération prochains événements: {str(e)}")
#             return {'message': 'Erreur lors de la récupération'}, 500

# from flask_restful import Resource
# from flask import request
# from model.firdaws_db import Event
# from config.db import db
# from logger.logger_config import get_logger
# from header.auth import token_required, admin_required
# from datetime import datetime

# logger = get_logger()

# class EventListResource(Resource):
#     def get(self):
#         """Récupère tous les événements non archivés (public)"""
#         events = Event.query.filter_by(archived=False).order_by(Event.date).all()
#         return {
#             'events': [e.to_dict() for e in events],
#             'total': len(events)
#         }, 200
    
#     @admin_required
#     def post(self, current_admin):
#         """Crée un nouvel événement (admin)"""
#         try:
#             data = request.get_json()
            
#             # Validation
#             required_fields = ['title', 'date', 'time']
#             for field in required_fields:
#                 if field not in data:
#                     return {'message': f'Champ {field} requis'}, 400
            
#             # Créer l'événement
#             event = Event(
#                 title=data['title'],
#                 date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
#                 time=data['time'],
#                 imam=data.get('imam', ''),
#                 description=data.get('description', ''),
#                 type=data.get('type', 'Événement'),
#                 created_by=current_admin.id
#             )
            
#             db.session.add(event)
#             db.session.commit()
            
#             logger.info(f"✅ Événement créé: {event.title} par {current_admin.email}")
            
#             return event.to_dict(), 201
            
#         except Exception as e:
#             logger.error(f"Erreur création événement: {str(e)}")
#             db.session.rollback()
#             return {'message': 'Erreur lors de la création'}, 500

# class EventResource(Resource):
#     def get(self, event_id):
#         """Récupère un événement spécifique"""
#         event = Event.query.get(event_id)
#         if not event:
#             return {'message': 'Événement non trouvé'}, 404
#         return event.to_dict(), 200
    
#     @admin_required
#     def put(self, current_admin, event_id):
#         """Modifie un événement"""
#         try:
#             event = Event.query.get(event_id)
#             if not event:
#                 return {'message': 'Événement non trouvé'}, 404
            
#             data = request.get_json()
            
#             # Mise à jour des champs
#             if 'title' in data:
#                 event.title = data['title']
#             if 'date' in data:
#                 event.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
#             if 'time' in data:
#                 event.time = data['time']
#             if 'imam' in data:
#                 event.imam = data['imam']
#             if 'description' in data:
#                 event.description = data['description']
#             if 'type' in data:
#                 event.type = data['type']
            
#             db.session.commit()
            
#             logger.info(f"✅ Événement modifié: {event.title}")
            
#             return event.to_dict(), 200
            
#         except Exception as e:
#             logger.error(f"Erreur modification événement: {str(e)}")
#             db.session.rollback()
#             return {'message': 'Erreur lors de la modification'}, 500
    
#     @admin_required
#     def delete(self, current_admin, event_id):
#         """Supprime un événement"""
#         try:
#             event = Event.query.get(event_id)
#             if not event:
#                 return {'message': 'Événement non trouvé'}, 404
            
#             db.session.delete(event)
#             db.session.commit()
            
#             logger.info(f"✅ Événement supprimé: {event.title}")
            
#             return {'message': 'Événement supprimé'}, 200
            
#         except Exception as e:
#             logger.error(f"Erreur suppression événement: {str(e)}")
#             db.session.rollback()
#             return {'message': 'Erreur lors de la suppression'}, 500

# class EventArchiveResource(Resource):
#     @admin_required
#     def put(self, current_admin, event_id):
#         """Archive ou désarchive un événement"""
#         try:
#             event = Event.query.get(event_id)
#             if not event:
#                 return {'message': 'Événement non trouvé'}, 404
            
#             data = request.get_json()
#             archive_status = data.get('archived', True)
            
#             event.archived = archive_status
#             db.session.commit()
            
#             action = "archivé" if archive_status else "désarchivé"
#             logger.info(f"✅ Événement {action}: {event.title}")
            
#             return event.to_dict(), 200
            
#         except Exception as e:
#             logger.error(f"Erreur archivage événement: {str(e)}")
#             db.session.rollback()
#             return {'message': 'Erreur lors de l\'archivage'}, 500

# class EventAdminListResource(Resource):
#     @admin_required
#     def get(self, current_admin):
#         """Récupère TOUS les événements (y compris archivés) pour l'admin"""
#         events = Event.query.order_by(Event.archived, Event.date.desc()).all()
#         return {
#             'events': [e.to_dict() for e in events],
#             'total': len(events),
#             'active': len([e for e in events if not e.archived]),
#             'archived': len([e for e in events if e.archived])
#         }, 200