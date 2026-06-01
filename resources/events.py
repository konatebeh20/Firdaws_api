import traceback
from flask_restful import Resource
from flask import request
from model.firdaws_db import Event
from config.db import db
from logger.logger_config import get_logger
from helpers.event_helper import EventHelper

logger = get_logger()

MSG_NOT_FOUND   = 'Événement non trouvé'
MSG_CREATE_ERROR = 'Erreur lors de la création'
MSG_UPDATE_ERROR = 'Erreur lors de la modification'
MSG_DELETE_ERROR = 'Erreur lors de la suppression'


class EventListApi(Resource):
    """/api/events  →  GET (liste) | POST (création)"""

    def get(self):
        try:
            events = Event.query.filter_by(archived=False)\
                          .order_by(Event.date.desc()).all()
            return {'events': [e.to_dict() for e in events], 'count': len(events)}, 200
        except Exception as e:
            logger.error(f"GET /events: {e}")
            return {'message': 'Erreur lors de la récupération'}, 500

    def post(self):
        try:
            data = request.get_json() or {}
            from model.firdaws_db import Admin
            admin    = Admin.query.first()
            admin_id = admin.id if admin else None

            formatted_data, errors = EventHelper.format_and_validate(data, created_by_id=admin_id)
            if errors:
                return {'message': 'Données invalides', 'errors': errors}, 400

            new_event = Event(**formatted_data)
            new_event.save()
            logger.info(f"Événement créé: {new_event.id} - {new_event.title}")
            return {'message': 'Événement créé avec succès', 'data': new_event.to_dict()}, 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"POST /events: {e}\n{traceback.format_exc()}")
            return {'message': f'{MSG_CREATE_ERROR}: {str(e)}'}, 500


class EventItemApi(Resource):
    """/api/events/<int:item_id>  →  GET | PUT | DELETE"""

    def get(self, item_id):
        try:
            event = Event.query.get(item_id)
            if not event:
                return {'message': MSG_NOT_FOUND}, 404
            return {'data': event.to_dict()}, 200
        except Exception as e:
            logger.error(f"GET /events/{item_id}: {e}")
            return {'message': 'Erreur interne'}, 500

    def put(self, item_id):
        try:
            event = Event.query.get(item_id)
            if not event:
                return {'message': MSG_NOT_FOUND}, 404

            data = request.get_json() or {}
            formatted_data, errors = EventHelper.format_and_validate(data)
            if errors:
                return {'message': 'Données invalides', 'errors': errors}, 400

            for key, value in formatted_data.items():
                setattr(event, key, value)
            db.session.commit()
            return {'message': 'Mis à jour avec succès', 'data': event.to_dict()}, 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"PUT /events/{item_id}: {e}")
            return {'message': MSG_UPDATE_ERROR}, 500

    def delete(self, item_id):
        try:
            event = Event.query.get(item_id)
            if not event:
                return {'message': MSG_NOT_FOUND}, 404
            event.delete()
            logger.info(f"Événement supprimé: {item_id}")
            return {'message': 'Supprimé avec succès'}, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"DELETE /events/{item_id}: {e}")
            return {'message': MSG_DELETE_ERROR}, 500


class EventActionApi(Resource):
    """/api/events/<string:route>[/<int:item_id>]  →  actions nommées"""

    def get(self, route, item_id=None):
        try:
            if route == 'upcoming':
                limit  = request.args.get('limit', 5, type=int)
                events = Event.query.filter_by(archived=False)\
                              .order_by(Event.date.asc()).limit(limit).all()
                return {'events': [e.to_dict() for e in events], 'count': len(events)}, 200

            if route == 'search':
                q = request.args.get('q', '', type=str)
                if not q:
                    return {'events': [], 'count': 0}, 200
                events = Event.query.filter(
                    Event.title.ilike(f'%{q}%'),
                    Event.archived == False
                ).all()
                return {'events': [e.to_dict() for e in events], 'count': len(events)}, 200

            return {'message': f"Route '{route}' introuvable"}, 404

        except Exception as e:
            logger.error(f"GET /events/{route}: {e}")
            return {'message': 'Erreur interne'}, 500

    def put(self, route, item_id=None):
        try:
            if not item_id:
                return {'message': 'ID requis'}, 400

            event = Event.query.get(item_id)
            if not event:
                return {'message': MSG_NOT_FOUND}, 404

            if route == 'archive':
                event.archived = True
            elif route == 'unarchive':
                event.archived = False
            else:
                return {'message': f"Action '{route}' non reconnue"}, 404

            db.session.commit()
            return {'message': 'Succès', 'data': event.to_dict()}, 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"PUT /events/{route}/{item_id}: {e}")
            return {'message': 'Erreur interne'}, 500



# import traceback
# from flask_restful import Resource
# from flask import request
# from model.firdaws_db import Event
# from config.db import db
# from logger.logger_config import get_logger
# from helpers.event_helper import EventHelper

# logger = get_logger()

# MSG_NOT_FOUND = 'Événement non trouvé'
# MSG_CREATE_ERROR = 'Erreur lors de la création'
# MSG_UPDATE_ERROR = 'Erreur lors de la modification'
# MSG_DELETE_ERROR = 'Erreur lors de la suppression'


# class EventListApi(Resource):
#     """
#     /api/events
#     GET  → liste tous les événements
#     POST → crée un événement
#     """

#     def get(self):
#         try:
#             events = Event.query.filter_by(archived=False)\
#                           .order_by(Event.date.desc()).all()
#             return {'events': [e.to_dict() for e in events], 'count': len(events)}, 200
#         except Exception as e:
#             logger.error(f"GET /events: {str(e)}")
#             return {'message': 'Erreur lors de la récupération'}, 500

#     def post(self):
#         try:
#             data = request.get_json() or {}

#             from model.firdaws_db import Admin
#             admin = Admin.query.first()
#             admin_id = admin.id if admin else None

#             formatted_data, errors = EventHelper.format_and_validate(data, created_by_id=admin_id)
#             if errors:
#                 return {'message': 'Données invalides', 'errors': errors}, 400

#             new_event = Event(**formatted_data)
#             new_event.save()
#             logger.info(f"Événement créé: {new_event.id} - {new_event.title}")
#             return {'message': 'Événement créé avec succès', 'data': new_event.to_dict()}, 201

#         except Exception as e:
#             db.session.rollback()
#             logger.error(f"POST /events: {str(e)}\n{traceback.format_exc()}")
#             return {'message': f'{MSG_CREATE_ERROR}: {str(e)}'}, 500


# class EventItemApi(Resource):
#     """
#     /api/events/<int:item_id>
#     GET    → détail d'un événement
#     PUT    → modification complète
#     DELETE → suppression
#     """

#     def get(self, item_id):
#         try:
#             event = Event.query.get(item_id)
#             if not event:
#                 return {'message': MSG_NOT_FOUND}, 404
#             return {'data': event.to_dict()}, 200
#         except Exception as e:
#             logger.error(f"GET /events/{item_id}: {str(e)}")
#             return {'message': 'Erreur interne'}, 500

#     def put(self, item_id):
#         try:
#             event = Event.query.get(item_id)
#             if not event:
#                 return {'message': MSG_NOT_FOUND}, 404

#             data = request.get_json() or {}
#             formatted_data, errors = EventHelper.format_and_validate(data)
#             if errors:
#                 return {'message': 'Données invalides', 'errors': errors}, 400

#             for key, value in formatted_data.items():
#                 setattr(event, key, value)
#             db.session.commit()
#             return {'message': 'Mis à jour avec succès', 'data': event.to_dict()}, 200

#         except Exception as e:
#             db.session.rollback()
#             logger.error(f"PUT /events/{item_id}: {str(e)}")
#             return {'message': MSG_UPDATE_ERROR}, 500

#     def delete(self, item_id):
#         try:
#             event = Event.query.get(item_id)
#             if not event:
#                 return {'message': MSG_NOT_FOUND}, 404
#             event.delete()
#             logger.info(f"Événement supprimé: {item_id}")
#             return {'message': 'Supprimé avec succès'}, 200
#         except Exception as e:
#             db.session.rollback()
#             logger.error(f"DELETE /events/{item_id}: {str(e)}")
#             return {'message': MSG_DELETE_ERROR}, 500


# class EventActionApi(Resource):
#     """
#     /api/events/<string:route>
#     /api/events/<string:route>/<int:item_id>

#     GET routes  : upcoming, search
#     PUT routes  : archive/<id>, unarchive/<id>
#     """

#     def get(self, route):
#         try:
#             if route == 'upcoming':
#                 limit = request.args.get('limit', 5, type=int)
#                 events = Event.query.filter_by(archived=False)\
#                               .order_by(Event.date.asc()).limit(limit).all()
#                 return {'events': [e.to_dict() for e in events], 'count': len(events)}, 200

#             if route == 'search':
#                 q = request.args.get('q', '', type=str)
#                 if not q:
#                     return {'events': [], 'count': 0}, 200
#                 events = Event.query.filter(
#                     Event.title.ilike(f'%{q}%'),
#                     Event.archived == False
#                 ).all()
#                 return {'events': [e.to_dict() for e in events], 'count': len(events)}, 200

#             return {'message': f"Route '{route}' introuvable"}, 404

#         except Exception as e:
#             logger.error(f"GET /events/{route}: {str(e)}")
#             return {'message': 'Erreur interne'}, 500

#     def put(self, route, item_id=None):
#         try:
#             if not item_id:
#                 return {'message': 'ID requis'}, 400

#             event = Event.query.get(item_id)
#             if not event:
#                 return {'message': MSG_NOT_FOUND}, 404

#             if route == 'archive':
#                 event.archived = True
#             elif route == 'unarchive':
#                 event.archived = False
#             else:
#                 return {'message': f"Action '{route}' non reconnue"}, 404

#             db.session.commit()
#             return {'message': 'Succès', 'data': event.to_dict()}, 200

#         except Exception as e:
#             db.session.rollback()
#             logger.error(f"PUT /events/{route}/{item_id}: {str(e)}")
#             return {'message': 'Erreur interne'}, 500
            

# # from flask_restful import Resource
# # from flask import request
# # from model.firdaws_db import Event
# # from config.db import db
# # from logger.logger_config import get_logger
# # from helpers.event_helper import EventHelper
# # # Décommente et adapte selon tes besoins réels de sécurité
# # # from helpers.auth_helper import admin_required, token_required 

# # logger = get_logger()

# # MSG_EVENT_NOT_FOUND = 'Événement non trouvé'
# # MSG_CREATE_ERROR = 'Erreur lors de la création'
# # MSG_UPDATE_ERROR = 'Erreur lors de la modification'



# # class EventListApi(Resource):
# #     def post(self):
# #         """POST /api/events -> Crée un événement"""
# #         try:
# #             data = request.get_json() or {}
            
# #             # Récupérer un ID valide (1 par défaut si admin existe)
# #             from model.firdaws_db import Admin
# #             admin = Admin.query.first()
# #             admin_id = admin.id if admin else 1
            
# #             formatted_data, errors = EventHelper.format_and_validate(data, created_by_id=admin_id)
            
# #             if errors:
# #                 return {'message': 'Données invalides', 'errors': errors}, 400
                
# #             new_event = Event(**formatted_data)
# #             new_event.save()
            
# #             return {
# #                 'message': 'Événement créé avec succès', 
# #                 'data': new_event.to_dict()
# #             }, 201
            
# #         except Exception as e:
# #             db.session.rollback()
# #             logger.error(f"Erreur création événement: {str(e)}")
# #             logger.error(traceback.format_exc())
# #             return {'message': f'Erreur lors de la création: {str(e)}'}, 500

# # # class EventListApi(Resource):
# # #     """Gère la collection globale des événements (/api/events)"""
    
# # #     def get(self):
# # #         """GET /api/events -> Liste tous les événements"""
# # #         try:
# # #             # Optionnel: filtrer les événements archivés
# # #             archived = request.args.get('archived', 'false').lower() == 'true'
# # #             include_archived = request.args.get('include_archived', 'false').lower() == 'true'
            
# # #             query = Event.query
            
# # #             if not include_archived:
# # #                 query = query.filter(Event.archived == archived)
                
# # #             events = query.order_by(Event.date.desc(), Event.time.desc()).all()
            
# # #             return {
# # #                 'events': [e.to_dict() for e in events],
# # #                 'count': len(events)
# # #             }, 200
# # #         except Exception as e:
# # #             logger.error(f"Erreur lors de la récupération des événements: {str(e)}")
# # #             return {'message': 'Erreur lors de la récupération des événements'}, 500

# # #     def post(self):
# # #         """POST /api/events -> Crée un événement"""
# # #         try:
# # #             data = request.get_json() or {}
            
# # #             # Récupérer l'admin depuis le token (à décommenter quand l'auth est active)
# # #             # admin_id = get_current_admin_id()  # À implémenter
            
# # #             # Temporairement, utiliser un admin existant ou créer le premier admin
# # #             from model.firdaws_db import Admin
# # #             admin = Admin.query.first()
# # #             if not admin:
# # #                 # Créer un admin par défaut si aucun n'existe
# # #                 admin = Admin(
# # #                     username='default_admin',
# # #                     email='default@firdaws.com',
# # #                     phone='00000000',
# # #                     role='admin'
# # #                 )
# # #                 admin.set_password('default123')
# # #                 admin.save()
# # #                 logger.info("Admin par défaut créé")
            
# # #             formatted_data, errors = EventHelper.format_and_validate(data, admin_id=admin.id)
            
# # #             if errors:
# # #                 logger.warning(f"Erreurs de validation: {errors}")
# # #                 return {'message': 'Données invalides', 'errors': errors}, 400
                
# # #             new_event = Event(**formatted_data)
# # #             new_event.save()  # Utiliser la méthode save() au lieu de commit direct
            
# # #             logger.info(f"Événement créé avec succès: {new_event.id} - {new_event.title}")
# # #             return {
# # #                 'message': 'Événement créé avec succès', 
# # #                 'data': new_event.to_dict()
# # #             }, 201
            
# # #         except Exception as e:
# # #             db.session.rollback()
# # #             logger.error(f"{MSG_CREATE_ERROR}: {str(e)}")
# # #             logger.error(traceback.format_exc())
# # #             return {'message': MSG_CREATE_ERROR, 'error': str(e)}, 500

# # class EventItemApi(Resource):
# #     """Gère un événement unique par son ID (/api/events/<int:item_id>)"""
    
# #     def get(self, item_id):
# #         """GET /api/events/<id> -> Détail d'un événement"""
# #         try:
# #             event = Event.query.get(item_id)
# #             if not event: 
# #                 return {'message': MSG_EVENT_NOT_FOUND}, 404
# #             return {'data': event.to_dict()}, 200
# #         except Exception as e:
# #             logger.error(f"Erreur lors du GET de l'événement {item_id}: {str(e)}")
# #             return {'message': "Une erreur interne est survenue"}, 500

# #     def put(self, item_id):
# #         """PUT /api/events/<id> -> Modification complète"""
# #         try:
# #             event = Event.query.get(item_id)
# #             if not event: 
# #                 return {'message': MSG_EVENT_NOT_FOUND}, 404
            
# #             data = request.get_json() or {}
# #             formatted_data, errors = EventHelper.format_and_validate(data)
# #             if errors: 
# #                 return {'message': 'Données invalides', 'errors': errors}, 400
            
# #             for key, value in formatted_data.items():
# #                 setattr(event, key, value)
                
# #             db.session.commit()
# #             return {'message': 'Mis à jour avec succès', 'data': event.to_dict()}, 200
# #         except Exception as e:
# #             db.session.rollback()
# #             logger.error(f"{MSG_UPDATE_ERROR} {item_id}: {str(e)}")
# #             return {'message': MSG_UPDATE_ERROR}, 500

# #     def delete(self, item_id):
# #         """DELETE /api/events/<id> -> Suppression définitive"""
# #         try:
# #             event = Event.query.get(item_id)
# #             if not event: 
# #                 return {'message': MSG_EVENT_NOT_FOUND}, 404
# #             event.delete()
# #             return {'message': 'Supprimé avec succès'}, 200
# #         except Exception as e:
# #             db.session.rollback()
# #             logger.error(f"Erreur lors de la suppression de l'événement {item_id}: {str(e)}")
# #             return {'message': 'Erreur lors de la suppression'}, 500


# # class EventActionApi(Resource):
# #     """Gère les actions spécifiques et filtres dynamiques"""
    
# #     def get(self, route):
# #         """GET /api/events/upcoming ou /api/events/stats ou /api/events/search"""
# #         try:
# #             if route == 'upcoming':
# #                 limit = request.args.get('limit', 5, type=int)
# #                 events = EventHelper.get_upcoming(limit)
# #                 return {'events': [e.to_dict() for e in events], 'count': len(events)}, 200
                
# #             if route == 'search':
# #                 query = request.args.get('q', '', type=str)
# #                 events = EventHelper.search(query)
# #                 return {'events': [e.to_dict() for e in events], 'count': len(events)}, 200
                
# #             if route == 'stats':
# #                 return {'stats': EventHelper.get_stats()}, 200
                
# #             return {'message': 'Route action introuvable'}, 404
# #         except Exception as e:
# #             logger.error(f"Erreur action GET sur la route {route}: {str(e)}")
# #             return {'message': "Une erreur interne est survenue"}, 500

# #     def put(self, route, item_id=None):
# #         """PUT /api/events/archive/<id> ou /api/events/unarchive/<id>"""
# #         try:
# #             if not item_id: 
# #                 return {'message': 'ID requis'}, 400
            
# #             if route == 'archive':
# #                 if EventHelper.toggle_archive(item_id, archive_status=True):
# #                     return {'message': 'Archivé avec succès'}, 200
# #             elif route == 'unarchive':
# #                 if EventHelper.toggle_archive(item_id, archive_status=False):
# #                     return {'message': 'Désarchivé avec succès'}, 200
                    
# #             return {'message': 'Action non reconnue ou événement introuvable'}, 404
# #         except Exception as e:
# #             db.session.rollback()
# #             logger.error(f"Erreur action PUT sur la route {route} (ID: {item_id}): {str(e)}")
# #             return {'message': "Une erreur interne est survenue"}, 500

# # # from flask_restful import Resource
# # # from flask import request
# # # from model.firdaws_db import Event
# # # from config.db import db
# # # from logger.logger_config import get_logger
# # # from helpers.event_helper import EventHelper
# # # # Supposons que verify_token provient de votre auth_helper
# # # from helpers.auth_helper import admin_required, token_required 

# # # logger = get_logger()

# # # MSG_EVENT_NOT_FOUND = 'Événement non trouvé'
# # # MSG_CREATE_ERROR = 'Erreur lors de la création'
# # # MSG_UPDATE_ERROR = 'Erreur lors de la modification'

# # # class EventApi(Resource):
# # #     """Resource unique pour gérer le cycle de vie et les listes d'événements"""
    
# # #     def get_current_admin(self):
# # #         """Décode le token optionnel pour identifier l'administrateur en cours"""
# # #         auth_header = request.headers.get('Authorization')
# # #         if auth_header and auth_header.startswith('Bearer '):
# # #             token = auth_header.split(' ')[1]
# # #             # payload = verify_token(token) # Décommentez selon votre auth_helper réel
# # #             # if payload and 'admin_id' in payload:
# # #             #     from model.firdaws_db import Admin
# # #             #     return Admin.query.get(payload['admin_id'])
# # #         return None

# # #     # ========== GET (Lecture standard & Routes dynamiques) ==========
# # #     def get(self, route=None, item_id=None):
# # #         try:
# # #             # 1. GET /api/events/<int:item_id> (Détail d'un événement)
# # #             if item_id and not route:
# # #                 event = Event.query.get(item_id)
# # #                 if not event:
# # #                     return {'message': MSG_EVENT_NOT_FOUND}, 404
# # #                 return {'data': event.to_dict()}, 200
            
# # #             # 2. GET /api/events/upcoming (Prochains événements)
# # #             if route == 'upcoming':
# # #                 limit = request.args.get('limit', 5, type=int)
# # #                 events = EventHelper.get_upcoming(limit)
# # #                 return {
# # #                     'events': [e.to_dict() for e in events],
# # #                     'count': len(events)
# # #                 }, 200
            
# # #             # 3. GET /api/events/search (Moteur de recherche)
# # #             if route == 'search':
# # #                 query = request.args.get('q', '', type=str)
# # #                 if not query:
# # #                     return {'events': [], 'count': 0}, 200
# # #                 events = EventHelper.search(query)
# # #                 return {
# # #                     'events': [e.to_dict() for e in events],
# # #                     'count': len(events)
# # #                 }, 200
                
# # #             # 4. GET /api/events/stats (Statistiques globales)
# # #             if route == 'stats':
# # #                 return {'stats': EventHelper.get_stats()}, 200

# # #             # 5. GET /api/events (Liste par défaut de tous les événements non archivés)
# # #             events = Event.query.filter_by(archived=False).order_by(Event.date.desc()).all()
# # #             return {'events': [e.to_dict() for e in events], 'count': len(events)}, 200

# # #         except Exception as e:
# # #             logger.error(f"Erreur lors du traitement GET: {str(e)}")
# # #             return {'message': "Une erreur interne est survenue"}, 500

# # #     # ========== POST (Création) ==========
# # #     def post(self):
# # #         """Créer un nouvel événement - Requiert d'être Admin"""
# # #         # admin = self.get_current_admin() # Décommentez si vous utilisez l'auth manuelle ici
# # #         try:
# # #             data = request.get_json() or {}
# # #             # Remplacer 1 par admin.id après activation de la sécurité
# # #             formatted_data, errors = EventHelper.format_and_validate(data, admin_id=1) 
            
# # #             if errors:
# # #                 return {'message': 'Données invalides', 'errors': errors}, 400
                
# # #             new_event = Event(**formatted_data)
# # #             db.session.add(new_event)
# # #             db.session.commit()
            
# # #             return {'message': 'Événement créé avec succès', 'data': new_event.to_dict()}, 201
# # #         except Exception as e:
# # #             db.session.rollback()
# # #             logger.error(f"{MSG_CREATE_ERROR}: {str(e)}")
# # #             return {'message': MSG_CREATE_ERROR}, 500

# # #     # ========== PUT (Mise à jour complète ou Archivage dynamique) ==========
# # #     def put(self, route=None, item_id=None):
# # #         try:
# # #             if not item_id:
# # #                 return {'message': 'ID requis'}, 400
                
# # #             # Gérer l'archivage/désarchivage via l'URI : /api/events/archive/<id>
# # #             if route == 'archive':
# # #                 success = EventHelper.toggle_archive(item_id, archive_status=True)
# # #                 if not success: return {'message': MSG_EVENT_NOT_FOUND}, 404
# # #                 return {'message': 'Événement archivé avec succès'}, 200
                
# # #             if route == 'unarchive':
# # #                 success = EventHelper.toggle_archive(item_id, archive_status=False)
# # #                 if not success: return {'message': MSG_EVENT_NOT_FOUND}, 404
# # #                 return {'message': 'Événement désarchivé avec succès'}, 200

# # #             # Mise à jour classique des données de l'événement
# # #             event = Event.query.get(item_id)
# # #             if not event:
# # #                 return {'message': MSG_EVENT_NOT_FOUND}, 404
                
# # #             data = request.get_json() or {}
# # #             formatted_data, errors = EventHelper.format_and_validate(data)
# # #             if errors:
# # #                 return {'message': 'Données invalides', 'errors': errors}, 400
                
# # #             # Assigner dynamiquement les valeurs modifiées
# # #             for key, value in formatted_data.items():
# # #                 setattr(event, key, value)
                
# # #             db.session.commit()
# # #             return {'message': 'Événement mis à jour avec succès', 'data': event.to_dict()}, 200
            
# # #         except Exception as e:
# # #             db.session.rollback()
# # #             logger.error(f"{MSG_UPDATE_ERROR}: {str(e)}")
# # #             return {'message': MSG_UPDATE_ERROR}, 500

# # # class EventListApi(Resource):
# # #     def get(self):
# # #         """GET /api/events -> Récupère tous les événements"""
# # #         events = Event.query.filter_by(archived=False).order_by(Event.date.desc()).all()
# # #         return {'events': [e.to_dict() for e in events], 'count': len(events)}, 200

# # #     def post(self):
# # #         """POST /api/events -> Crée un événement"""
# # #         data = request.get_json() or {}
# # #         formatted_data, errors = EventHelper.format_and_validate(data, admin_id=1)
# # #         if errors:
# # #             return {'message': 'Données invalides', 'errors': errors}, 400
            
# # #         new_event = Event(**formatted_data)
# # #         new_event.save()
# # #         return {'message': 'Événement créé', 'data': new_event.to_dict()}, 201


# # # # from flask_restful import Resource
# # # # from flask import request, jsonify
# # # # from model.firdaws_db import Event
# # # # from config.db import db
# # # # from logger.logger_config import get_logger
# # # # from helpers.auth_helper import token_required, admin_required
# # # # from helpers.event_helper import EventHelper
# # # # from helpers.pagination_helper import PaginationHelper
# # # # from helpers.error_helper import log_error

# # # # logger = get_logger()

# # # # # Constants for error messages
# # # # MSG_EVENT_NOT_FOUND = 'Événement non trouvé'
# # # # MSG_AUTH_REQUIRED = 'Authentification requise'
# # # # MSG_ID_REQUIRED = 'ID requis'
# # # # MSG_CREATE_ERROR = 'Erreur lors de la création'
# # # # MSG_UPDATE_ERROR = 'Erreur lors de la modification'
# # # # MSG_DELETE_ERROR = 'Erreur lors de la suppression'

# # # # class EventApi(Resource):
# # # #     """Resource unique pour TOUS les endpoints événements"""
    
# # # #     def get_current_admin(self):
# # # #         """Récupère l'admin si token présent"""
# # # #         auth_header = request.headers.get('Authorization')
# # # #         if auth_header and auth_header.startswith('Bearer '):
# # # #             token = auth_header.split(' ')[1]
# # # #             payload = verify_token(token)
# # # #             if payload:
# # # #                 from model.firdaws_db import Admin
# # # #                 return Admin.query.get(payload['admin_id'])
# # # #         return None
    
# # # #     # ========== GET ==========
# # # #     def get(self, route=None, item_id=None):
# # # #         """Route GET dynamique unique"""
# # # #         try:
# # # #             current_admin = self.get_current_admin()
            
# # # #             # --- 1. GET /api/events/<int:item_id> ---
# # # #             if item_id and not route:
# # # #                 event = Event.query.get(item_id)
# # # #                 if not event:
# # # #                     return {'message': MSG_EVENT_NOT_FOUND}, 404
# # # #                 return {'data': event.to_dict()}, 200
            
# # # #             # --- 2. GET /api/events/upcoming ---
# # # #             if route == 'upcoming':
# # # #                 limit = request.args.get('limit', 5, type=int)
# # # #                 events = EventHelper.get_upcoming(limit)
# # # #                 return {
# # # #                     'events': [e.to_dict() for e in events],
# # # #                     'count': len(events)
# # # #                 }, 200
            
# # # #             # --- 3. GET /api/events/search ---
# # # #             if route == 'search':
# # # #                 query = request.args.get('q', '')
# # # #                 if len(query) < 2:
# # # #                     return {'events': []}, 200
# # # #                 events = EventHelper.search(query)
# # # #                 return {
# # # #                     'events': [e.to_dict() for e in events],
# # # #                     'count': len(events)
# # # #                 }, 200
            
# # # #             # --- 4. GET /api/events/admin ---
# # # #             if route == 'admin':
# # # #                 if not current_admin:
# # # #                     return {'message': MSG_AUTH_REQUIRED}, 401
# # # #                 events = Event.query.order_by(Event.event_date.desc()).all()
# # # #                 return {
# # # #                     'data': [e.to_dict() for e in events],
# # # #                     'total': len(events),
# # # #                     'active': len([e for e in events if e.status == 'published']),
# # # #                     'draft': len([e for e in events if e.status == 'draft'])
# # # #                 }, 200
            
# # # #             # --- 5. GET /api/events/stats ---
# # # #             if route == 'stats':
# # # #                 return EventHelper.get_stats(), 200
            
# # # #             # --- 6. GET /api/events (par défaut) ---
# # # #             page = request.args.get('page', 1, type=int)
# # # #             per_page = request.args.get('per_page', 100, type=int)
# # # #             include_archived = request.args.get('include_archived', 'false').lower() == 'true'
            
# # # #             if include_archived:
# # # #                 query = Event.query.order_by(Event.event_date.desc())
# # # #             else:
# # # #                 query = Event.query.filter_by(status='published').order_by(Event.event_date.desc())
# # # #             result = PaginationHelper.paginate(query, page, per_page)
            
# # # #             return {
# # # #                 'data': [e.to_dict() for e in result['items']],
# # # #                 'pagination': {k: v for k, v in result.items() if k != 'items'}
# # # #             }, 200
            
# # # #         except Exception as e:
# # # #             log_error(e, request, 'EventApi.get')
# # # #             return {'message': 'Erreur lors de la récupération'}, 500
    
# # # #     # ========== POST ==========
# # # #     def post(self, route=None, item_id=None):
# # # #         """Route POST dynamique unique"""
# # # #         try:
# # # #             current_admin = self.get_current_admin()
            
# # # #             if not current_admin:
# # # #                 logger.warning("Tentative de création d'événement sans authentification")
# # # #                 return {'message': MSG_AUTH_REQUIRED}, 401

# # # #             data = request.get_json()
# # # #             logger.info(f"Données reçues pour création événement: {data}")
            
# # # #             # --- 1. POST /api/events/duplicate/<int:item_id> ---
# # # #             if route == 'duplicate' and item_id:
# # # #                 return self._duplicate_event(item_id, current_admin.id)
            
# # # #             # --- 2. POST /api/events (création) ---
# # # #             return self._create_event(data, current_admin.id)
            
# # # #         except Exception as e:
# # # #             logger.error(f"Erreur lors de la création d'événement: {str(e)}", exc_info=True)
# # # #             log_error(e, request, 'EventApi.post')
# # # #             db.session.rollback()
# # # #             return {'message': f'{MSG_CREATE_ERROR}: {str(e)}'}, 500

# # # #     def _duplicate_event(self, item_id, admin_id):
# # # #         """Duplicate an existing event"""
# # # #         event = Event.query.get(item_id)
# # # #         if not event:
# # # #             return {'message': MSG_EVENT_NOT_FOUND}, 404
        
# # # #         new_event = Event(
# # # #             title=f"{event.title} (copie)",
# # # #             event_date=event.event_date,
# # # #             description=event.description,
# # # #             category=event.category,
# # # #             location=event.location,
# # # #             created_by=admin_id
# # # #         )
# # # #         db.session.add(new_event)
# # # #         db.session.commit()
        
# # # #         logger.info(f"✅ Événement dupliqué: {new_event.title}")
# # # #         return new_event.to_dict(), 201

# # # #     def _create_event(self, data, admin_id):
# # # #         """Create a new event"""
# # # #         errors = EventHelper.validate_data(data)
# # # #         if errors:
# # # #             logger.warning(f"Erreur validation événement: {errors}")
# # # #             return {'message': 'Erreur de validation', 'errors': errors}, 400
        
# # # #         event_data = EventHelper.prepare_data(data, admin_id)
# # # #         if 'event_date' in event_data:
# # # #             event_data['event_date'] = EventHelper.format_date(event_data['event_date'])
        
# # # #         logger.info(f"Préparation création événement avec données: {event_data}")
        
# # # #         event = Event(**event_data)
# # # #         db.session.add(event)
# # # #         db.session.commit()
        
# # # #         logger.info(f"✅ Événement créé: {event.title}")
# # # #         return {'data': event.to_dict()}, 201
    
# # # #     # ========== PUT ==========
# # # #     def put(self, route=None, item_id=None):
# # # #         """Route PUT dynamique unique"""
# # # #         try:
# # # #             current_admin = self.get_current_admin()
            
# # # #             if not current_admin:
# # # #                 return {'message': MSG_AUTH_REQUIRED}, 401
            
# # # #             if not item_id:
# # # #                 return {'message': MSG_ID_REQUIRED}, 400
            
# # # #             event = Event.query.get(item_id)
# # # #             if not event:
# # # #                 return {'message': MSG_EVENT_NOT_FOUND}, 404
            
# # # #             data = request.get_json()

# # # #             # --- 1. PUT /api/events/archive/<int:item_id> ---
# # # #             if route == 'archive':
# # # #                 event.status = data.get('status', 'archived')
# # # #                 db.session.commit()
# # # #                 action = "archivé" if event.status == 'archived' else "désarchivé"
# # # #                 logger.info(f"✅ Événement {action}: {event.title}")
# # # #                 return {'data': event.to_dict()}, 200
            
# # # #             # --- 2. Mise à jour des champs ---
# # # #             self._update_event_fields(event, data)
            
# # # #             db.session.commit()
# # # #             logger.info(f"✅ Événement modifié: {event.title}")
            
# # # #             return {'data': event.to_dict()}, 200
            
# # # #         except Exception as e:
# # # #             log_error(e, request, 'EventApi.put')
# # # #             db.session.rollback()
# # # #             return {'message': MSG_UPDATE_ERROR}, 500

# # # #     def _update_event_fields(self, event, data):
# # # #         """Update event fields"""
# # # #         updatable_fields = ['title', 'event_date', 'description', 'category', 'location', 'status']
# # # #         for field in updatable_fields:
# # # #             if field in data:
# # # #                 if field == 'event_date':
# # # #                     event.event_date = EventHelper.format_date(data.get('event_date'))
# # # #                 else:
# # # #                     setattr(event, field, data[field])
    
# # # #     # ========== DELETE ==========
# # # #     def delete(self, route=None, item_id=None):
# # # #         """Route DELETE dynamique unique"""
# # # #         try:
# # # #             current_admin = self.get_current_admin()
            
# # # #             if not current_admin:
# # # #                 return {'message': MSG_AUTH_REQUIRED}, 401
            
# # # #             if not item_id:
# # # #                 return {'message': MSG_ID_REQUIRED}, 400
            
# # # #             event = Event.query.get(item_id)
# # # #             if not event:
# # # #                 return {'message': MSG_EVENT_NOT_FOUND}, 404
            
# # # #             db.session.delete(event)
# # # #             db.session.commit()
            
# # # #             logger.info(f"✅ Événement supprimé: {event.title}")
# # # #             return {'data': {'message': 'Événement supprimé', 'id': item_id}}, 200
            
# # # #         except Exception as e:
# # # #             log_error(e, request, 'EventApi.delete')
# # # #             db.session.rollback()
# # # #             return {'message': MSG_DELETE_ERROR}, 500

# # # #     # ========== PATCH ==========
# # # #     def patch(self, route=None, item_id=None):
# # # #         """Route PATCH dynamique unique"""
# # # #         try:
# # # #             current_admin = self.get_current_admin()
            
# # # #             if not current_admin:
# # # #                 return {'message': MSG_AUTH_REQUIRED}, 401
            
# # # #             if not item_id:
# # # #                 return {'message': MSG_ID_REQUIRED}, 400
            
# # # #             event = Event.query.get(item_id)
# # # #             if not event:
# # # #                 return {'message': MSG_EVENT_NOT_FOUND}, 404
            
# # # #             data = request.get_json()
            
# # # #             self._update_event_fields(event, data)
            
# # # #             db.session.commit()
# # # #             logger.info(f"✅ Événement mis à jour (PATCH): {event.title}")
# # # #             return {'data': event.to_dict()}, 200
            
# # # #         except Exception as e:
# # # #             log_error(e, request, 'EventApi.patch')
# # # #             db.session.rollback()
# # # #             return {'message': MSG_UPDATE_ERROR}, 500
