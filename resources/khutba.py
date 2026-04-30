from flask_restful import Resource
from flask import request
from model.firdaws_db import Khutba, Admin
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import admin_required, verify_token
from helpers.khutba_helper import KhutbaHelper
from helpers.pagination_helper import PaginationHelper

logger = get_logger()

class KhutbaApi(Resource):
    """Resource unique pour TOUS les endpoints khotbas"""

    def get_current_admin(self):
        """Récupère l'admin si token présent"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if payload:
                return Admin.query.get(payload['admin_id'])
        return None

    # ========== GET ==========
    def get(self, route=None, item_id=None, imam_name=None):
        """Route GET dynamique unique"""
        try:
            current_admin = self.get_current_admin()

            # 1. GET /api/khutba/<int:item_id>
            if item_id and not route:
                khutba = Khutba.query.get(item_id)
                if not khutba:
                    return {'message': 'Khutba non trouvée'}, 404
                return khutba.to_dict(), 200

            # 2. GET /api/khutba/admin
            if route == 'admin':
                if not current_admin:
                    return {'message': 'Authentification requise'}, 401
                khotbas = Khutba.query.order_by(Khutba.archived, Khutba.created_at.desc()).all()
                return {
                    'data': [k.to_dict() for k in khotbas],
                    'total': len(khotbas),
                    'active': len([k for k in khotbas if not k.archived]),
                    'archived': len([k for k in khotbas if k.archived])
                }, 200

            # 3. GET /api/khutba/imam/<string:imam_name>
            if route == 'imam' and imam_name:
                khotbas = KhutbaHelper.get_by_imam(imam_name)
                return {
                    'khotbas': [k.to_dict() for k in khotbas],
                    'count': len(khotbas)
                }, 200

            # 4. GET /api/khutba/latest
            if route == 'latest':
                limit = request.args.get('limit', 5, type=int)
                khotbas = KhutbaHelper.get_latest(limit)
                return {
                    'khotbas': [k.to_dict() for k in khotbas],
                    'count': len(khotbas)
                }, 200

            # 5. GET /api/khutba (par défaut - public)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 100, type=int)
            include_archived = request.args.get('include_archived', 'false').lower() == 'true'
            
            if include_archived:
                query = Khutba.query.order_by(Khutba.created_at.desc())
            else:
                query = Khutba.query.filter_by(archived=False).order_by(Khutba.created_at.desc())
            result = PaginationHelper.paginate(query, page, per_page)
            
            return {
                'data': [k.to_dict() for k in result['items']],
                'pagination': {k: v for k, v in result.items() if k != 'items'}
            }, 200

        except Exception as e:
            logger.error(f"Erreur GET khutba: {str(e)}")
            return {'message': 'Erreur serveur'}, 500

    # ========== POST ==========
    @admin_required
    def post(self, current_admin, route=None):
        """Route POST dynamique unique"""
        try:
            data = request.get_json()
            
            # 1. Validation
            errors = KhutbaHelper.validate_data(data)
            if errors:
                return {'message': 'Erreur de validation', 'errors': errors}, 400
            
            # 2. Préparer les données
            khutba_data = KhutbaHelper.prepare_data(data, current_admin.id)
            
            khutba = Khutba(**khutba_data)
            db.session.add(khutba)
            db.session.commit()
            
            logger.info(f"✅ Khutba ajoutée: {khutba.title}")
            return {'data': khutba.to_dict()}, 201
            
        except Exception as e:
            logger.error(f"Erreur POST khutba: {str(e)}")
            db.session.rollback()
            return {'message': 'Erreur serveur'}, 500

    # ========== PUT ==========
    @admin_required
    def put(self, current_admin, route=None, item_id=None):
        """Route PUT dynamique unique"""
        try:
            if not item_id:
                return {'message': 'ID requis'}, 400
                
            khutba = Khutba.query.get(item_id)
            if not khutba:
                return {'message': 'Khutba non trouvée'}, 404
            
            data = request.get_json()

            # 1. PUT /api/khutba/archive/<int:item_id>
            if route == 'archive':
                khutba.archived = data.get('archived', True)
                db.session.commit()
                action = "archivée" if khutba.archived else "désarchivée"
                logger.info(f"✅ Khutba {action}: {khutba.title}")
                return {'data': khutba.to_dict()}, 200
            
            # 2. Mise à jour des champs
            for field in ['title', 'date', 'imam', 'content']:
                if field in data:
                    setattr(khutba, field, data[field])
            
            db.session.commit()
            logger.info(f"✅ Khutba modifiée: {khutba.title}")
            return {'data': khutba.to_dict()}, 200
            
        except Exception as e:
            logger.error(f"Erreur PUT khutba: {str(e)}")
            db.session.rollback()
            return {'message': 'Erreur serveur'}, 500

    # ========== DELETE ==========
    @admin_required
    def delete(self, current_admin, route=None, item_id=None):
        """Route DELETE dynamique unique"""
        try:
            if not item_id:
                return {'message': 'ID requis'}, 400
                
            khutba = Khutba.query.get(item_id)
            if not khutba:
                return {'message': 'Khutba non trouvée'}, 404
            
            db.session.delete(khutba)
            db.session.commit()
            
            logger.info(f"✅ Khutba supprimée: {khutba.title}")
            return {'data': {'message': 'Khutba supprimée', 'id': item_id}}, 200
            
        except Exception as e:
            logger.error(f"Erreur DELETE khutba: {str(e)}")
            db.session.rollback()
            return {'message': 'Erreur serveur'}, 500