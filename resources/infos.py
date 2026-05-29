from flask_restful import Resource
from flask import request
from model.firdaws_db import Info, Admin
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import admin_required, verify_token
from helpers.info_helper import InfoHelper
from helpers.pagination_helper import PaginationHelper
from helpers.error_helper import log_error

logger = get_logger()

class InfoApi(Resource):
    """Resource unique pour TOUS les endpoints informations"""
    
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

    # ========== GET ==========
    def get(self, route=None, item_id=None):
        try:
            current_admin = self.get_current_admin()
            
            # 1. GET /api/infos/<int:item_id>
            if item_id and not route:
                info = Info.query.get(item_id)
                if not info:
                    return {'message': 'Information non trouvée'}, 404
                return {'data': info.to_dict()}, 200
            
            # 2. GET /api/infos/admin
            if route == 'admin':
                if not current_admin:
                    return {'message': 'Authentification requise'}, 401
                infos = Info.query.order_by(Info.created_at.desc()).all()
                return {
                    'data': [i.to_dict() for i in infos],
                    'total': len(infos),
                    'active': len([i for i in infos if i.status != 'archived']),
                    'archived': len([i for i in infos if i.status == 'archived'])
                }, 200

            # 3. GET /api/infos (par défaut)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 100, type=int)
            include_archived = request.args.get('include_archived', 'false').lower() == 'true'
            
            if include_archived:
                query = Info.query.order_by(Info.created_at.desc())
            else:
                query = Info.query.filter(
                    Info.status.in_(['published', 'draft'])
                ).order_by(Info.created_at.desc())
            
            result = PaginationHelper.paginate(query, page, per_page)
            
            return {
                'data': [i.to_dict() for i in result['items']],
                'pagination': {k: v for k, v in result.items() if k != 'items'}
            }, 200

        except Exception as e:
            log_error(e, request, 'InfoApi.get')
            return {'message': 'Erreur lors de la récupération'}, 500
    
    # ========== POST ==========
    def post(self, route=None, item_id=None):
        try:
            data = request.get_json()
            errors = InfoHelper.validate_data(data)
            if errors:
                return {'message': 'Erreur de validation', 'errors': errors}, 400
            current_admin = self.get_current_admin()
            admin_id = current_admin.id if current_admin else 1
            info_data = InfoHelper.prepare_data(data, admin_id)
            info = Info(**info_data)
            db.session.add(info)
            db.session.commit()
            return {'data': info.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    # ========== PUT ==========
    def put(self, route=None, item_id=None):
        try:
            if not item_id:
                return {'message': 'ID manquant'}, 400
            info = Info.query.get(item_id)
            if not info:
                return {'message': 'Information non trouvée'}, 404
            data = request.get_json()
            if route == 'archive':
                info.status = 'archived' if data.get('archived', True) else 'published'
            else:
                if 'title' in data:
                    info.title = data['title']
                if 'content' in data:
                    info.content = data['content']
                if 'category' in data:
                    info.priority = data['category']
                if 'is_published' in data:
                    info.status = 'published' if data['is_published'] else 'draft'
            db.session.commit()
            return {'data': info.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    # ========== DELETE ==========
    def delete(self, route=None, item_id=None):
        try:
            if not item_id:
                return {'message': 'ID manquant'}, 400
            info = Info.query.get(item_id)
            if not info:
                return {'message': 'Information non trouvée'}, 404
            db.session.delete(info)
            db.session.commit()
            return {'data': {'message': 'Information supprimée', 'id': item_id}}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500