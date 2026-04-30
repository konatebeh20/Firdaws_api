from flask_restful import Resource
from flask import request
from model.firdaws_db import Document, Admin
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import admin_required, verify_token
from helpers.document_helper import DocumentHelper
from helpers.pagination_helper import PaginationHelper
from helpers.error_helper import log_error

logger = get_logger()

class DocumentApi(Resource):
    """Resource unique pour TOUS les endpoints documents"""
    
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
    def get(self, route=None, item_id=None):
        """Route GET dynamique unique"""
        try:
            current_admin = self.get_current_admin()
            
            # 1. GET /api/documents/<int:item_id>
            if item_id and not route:
                doc = Document.query.get(item_id)
                if not doc:
                    return {'message': 'Document non trouvé'}, 404
                return {'data': doc.to_dict()}, 200
            
            # 2. GET /api/documents/admin
            if route == 'admin':
                if not current_admin:
                    return {'message': 'Authentification requise'}, 401
                docs = Document.query.order_by(Document.archived, Document.id.desc()).all()
                return {
                    'data': [d.to_dict() for d in docs],
                    'total': len(docs),
                    'active': len([d for d in docs if not d.archived]),
                    'archived': len([d for d in docs if d.archived])
                }, 200

            # 3. GET /api/documents (par défaut)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 100, type=int)
            include_archived = request.args.get('include_archived', 'false').lower() == 'true'
            
            if include_archived:
                query = Document.query.order_by(Document.id.desc())
            else:
                query = Document.query.filter_by(archived=False).order_by(Document.id.desc())
            result = PaginationHelper.paginate(query, page, per_page)
            
            return {
                'data': [d.to_dict() for d in result['items']],
                'pagination': {k: v for k, v in result.items() if k != 'items'}
            }, 200

        except Exception as e:
            log_error(e, request, 'DocumentApi.get')
            return {'message': 'Erreur lors de la récupération'}, 500

    # ========== POST ==========
    @admin_required
    def post(self, current_admin, route=None, item_id=None):
        """Route POST dynamique unique"""
        try:
            data = request.get_json()
            
            # Validation
            errors = DocumentHelper.validate_data(data)
            if errors:
                return {'message': 'Erreur de validation', 'errors': errors}, 400
            
            doc_data = DocumentHelper.prepare_data(data, current_admin.id)
            doc = Document(**doc_data)
            
            db.session.add(doc)
            db.session.commit()
            
            logger.info(f"✅ Document ajouté: {doc.title}")
            return {'data': doc.to_dict()}, 201
            
        except Exception as e:
            log_error(e, request, 'DocumentApi.post')
            db.session.rollback()
            return {'message': 'Erreur lors de l\'ajout'}, 500

    # ========== PUT ==========
    @admin_required
    def put(self, current_admin, route=None, item_id=None):
        """Route PUT dynamique unique"""
        try:
            if not item_id:
                return {'message': 'ID manquant'}, 400
            
            doc = Document.query.get(item_id)
            if not doc:
                return {'message': 'Document non trouvé'}, 404
            
            data = request.get_json()
            
            # 1. Archive / Désarchive
            if route == 'archive':
                doc.archived = data.get('archived', True)
            else:
                # 2. Mise à jour classique
                for field in ['title', 'description', 'author', 'type', 'icon', 'file_size', 'file_url']:
                    if field in data:
                        setattr(doc, field, data[field])
            
            db.session.commit()
            logger.info(f"✅ Document mise à jour: {doc.title}")
            return {'data': doc.to_dict()}, 200
            
        except Exception as e:
            log_error(e, request, 'DocumentApi.put')
            db.session.rollback()
            return {'message': 'Erreur lors de la modification'}, 500

    # ========== DELETE ==========
    @admin_required
    def delete(self, current_admin, route=None, item_id=None):
        """Route DELETE dynamique unique"""
        try:
            if not item_id:
                return {'message': 'ID manquant'}, 400
                
            doc = Document.query.get(item_id)
            if not doc:
                return {'message': 'Document non trouvé'}, 404
            
            db.session.delete(doc)
            db.session.commit()
            
            logger.info(f"✅ Document supprimé: {doc.title}")
            return {'data': {'message': 'Document supprimé', 'id': item_id}}, 200
            
        except Exception as e:
            log_error(e, request, 'DocumentApi.delete')
            db.session.rollback()
            return {'message': 'Erreur lors de la suppression'}, 500
