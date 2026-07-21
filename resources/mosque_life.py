from flask_restful import Resource
from flask import request
from model.firdaws_db import MosqueLife, Admin
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import verify_token
from helpers.pagination_helper import PaginationHelper
from helpers.error_helper import log_error

logger = get_logger()

MSG_NOT_FOUND = 'Actualité non trouvée'
MSG_AUTH_REQUIRED = 'Authentification requise'
MSG_CREATE_ERROR = 'Erreur lors de la création'
MSG_UPDATE_ERROR = 'Erreur lors de la modification'
MSG_DELETE_ERROR = 'Erreur lors de la suppression'


class MosqueLifeApi(Resource):
    """Resource pour gérer la vie active de la mosquée (Actualités)"""
    
    def get_current_admin(self):
        """Récupère l'admin si token présent"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if payload:
                admin_id = payload.get('admin_id')
                if admin_id:
                    return Admin.query.get(admin_id)
        return None

    def get(self, route=None, item_id=None):
        """Route GET dynamique"""
        try:
            current_admin = self.get_current_admin()
            
            # 1. GET /api/mosque-life/<int:item_id>
            if item_id and not route:
                item = MosqueLife.query.get(item_id)
                if not item:
                    return {'message': MSG_NOT_FOUND}, 404
                return {'data': item.to_dict()}, 200
            
            # 2. GET /api/mosque-life/admin
            if route == 'admin':
                if not current_admin:
                    return {'message': MSG_AUTH_REQUIRED}, 401
                items = MosqueLife.query.order_by(MosqueLife.date.desc()).all()
                return {
                    'data': [i.to_dict() for i in items],
                    'total': len(items),
                    'active': len([i for i in items if not i.archived]),
                    'archived': len([i for i in items if i.archived])
                }, 200

            # 3. GET /api/mosque-life (par défaut)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 100, type=int)
            include_archived = request.args.get('include_archived', 'false').lower() == 'true'
            
            if include_archived:
                query = MosqueLife.query.order_by(MosqueLife.date.desc())
            else:
                query = MosqueLife.query.filter_by(archived=False).order_by(MosqueLife.date.desc())
            
            result = PaginationHelper.paginate(query, page, per_page)
            
            return {
                'data': [i.to_dict() for i in result['items']],
                'pagination': {k: v for k, v in result.items() if k != 'items'}
            }, 200

        except Exception as e:
            log_error(e, request, 'MosqueLifeApi.get')
            return {'message': 'Erreur lors de la récupération'}, 500

    def post(self, route=None, item_id=None):
        """Créer une nouvelle actualité"""
        try:
            current_admin = self.get_current_admin()
            if not current_admin:
                return {'message': MSG_AUTH_REQUIRED}, 401
            
            data = request.get_json() or {}
            
            # Validation
            if not data.get('title') or not data.get('content') or not data.get('date'):
                return {'message': 'Données invalides: title, content et date sont requis'}, 400
            
            admin_id = current_admin.id if current_admin else 1
            
            item_data = {
                'title': data.get('title'),
                'content': data.get('content'),
                'category': data.get('category', 'general'),
                'image_url': data.get('image_url'),
                'date': data.get('date'),
                'location': data.get('location'),
                'status': data.get('status', 'published'),
                'archived': data.get('archived', False),
                'created_by': admin_id
            }
            
            item = MosqueLife(**item_data)
            item.save()
            
            logger.info(f"Actualité créée: {item.id} - {item.title}")
            return {'message': 'Actualité créée avec succès', 'data': item.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            log_error(e, request, 'MosqueLifeApi.post')
            return {'message': f'{MSG_CREATE_ERROR}: {str(e)}'}, 500

    def put(self, route=None, item_id=None):
        """Mettre à jour une actualité"""
        try:
            if not item_id:
                return {'message': 'ID requis'}, 400
            
            current_admin = self.get_current_admin()
            if not current_admin:
                return {'message': MSG_AUTH_REQUIRED}, 401
            
            item = MosqueLife.query.get(item_id)
            if not item:
                return {'message': MSG_NOT_FOUND}, 404
            
            data = request.get_json() or {}
            
            if route == 'archive':
                item.archived = data.get('archived', True)
            else:
                for field in ['title', 'content', 'category', 'image_url', 'date', 'location', 'status']:
                    if field in data:
                        setattr(item, field, data[field])
            
            db.session.commit()
            logger.info(f"Actualité mise à jour: {item.id}")
            return {'message': 'Mis à jour avec succès', 'data': item.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            log_error(e, request, 'MosqueLifeApi.put')
            return {'message': MSG_UPDATE_ERROR}, 500

    def delete(self, route=None, item_id=None):
        """Supprimer une actualité"""
        try:
            if not item_id:
                return {'message': 'ID requis'}, 400
            
            current_admin = self.get_current_admin()
            if not current_admin:
                return {'message': MSG_AUTH_REQUIRED}, 401
            
            item = MosqueLife.query.get(item_id)
            if not item:
                return {'message': MSG_NOT_FOUND}, 404
            
            item.delete()
            logger.info(f"Actualité supprimée: {item_id}")
            return {'message': 'Supprimé avec succès'}, 200
            
        except Exception as e:
            db.session.rollback()
            log_error(e, request, 'MosqueLifeApi.delete')
            return {'message': MSG_DELETE_ERROR}, 500
