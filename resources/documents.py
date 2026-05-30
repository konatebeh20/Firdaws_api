import os
from flask_restful import Resource
from flask import request, current_app
from werkzeug.utils import secure_filename
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
                } or {}, 200

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
    def post(self, route=None, item_id=None):
        """Route POST dynamique unique acceptant JSON ou Multipart/Form-Data (Fichiers)"""
        try:
            # Récupérer l'utilisateur actuel (admin)
            current_admin = self.get_current_admin()
            
            if not current_admin:
                return {'message': 'Authentification requise - Veuillez vous connecter'}, 401

            # 1. Détection du type de contenu (Fichier vs JSON)
            if 'file' in request.files:
                # Mode : Upload de fichier (multipart/form-data)
                file = request.files['file']
                data = request.form.to_dict()  # Convertit l'ImmutableMultiDict en dict standard
                
                # Validation des champs texte
                errors = DocumentHelper.validate_data(data)
                if errors:
                    return {'message': 'Erreur de validation', 'errors': errors}, 400
                
                # Validation du fichier
                if not file or not DocumentHelper.allowed_file(file.filename):
                    return {'message': 'Extension de fichier non autorisée ou fichier manquant'}, 400
                
                filename = secure_filename(file.filename)
                
                # --- Traitement et Sauvegarde physique du fichier ---
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                # Sécurité : création du dossier s'il n'existe pas encore
                os.makedirs(upload_folder, exist_ok=True)
                
                upload_path = os.path.join(upload_folder, filename)
                file.save(upload_path)
                
                # Récupération des métadonnées réelles après sauvegarde
                file_url = f"/uploads/{filename}"
                file_size_bytes = os.path.getsize(upload_path)
                
                # Préparation des données structurées via ton Helper
                doc_data = DocumentHelper.prepare_data(
                    data=data,
                    filename=filename,
                    size_bytes=file_size_bytes,
                    file_url=file_url,
                    admin_id=current_admin.id if current_admin else None
                )
            else:
                # Mode classique : Payload purement JSON
                data = request.get_json() or {}
                
                errors = DocumentHelper.validate_data(data)
                if errors:
                    return {'message': 'Erreur de validation', 'errors': errors}, 400
                
                # Construction manuelle du dictionnaire si pas de fichier physique traité par le helper
                doc_data = {
                    'title': data.get('title', '').strip(),
                    'description': data.get('description', '').strip(),
                    'author': data.get('author', 'Anonyme').strip(),
                    'type': data.get('type', 'PDF').upper(),
                    'icon': data.get('icon', '📄'),
                    'file_size': data.get('file_size', '0.0 B'),
                    'file_url': data.get('file_url', '#'),
                    'created_by': current_admin.id if current_admin else None
                }

            # 2. Insertion en base de données commune
            doc = Document(**doc_data)
            db.session.add(doc)
            db.session.commit()
            
            logger.info(f"✅ Document enregistré avec succès: {doc.title}")
            return {'data': doc.to_dict()}, 201
            
        except Exception as e:
            log_error(e, request, 'DocumentApi.post')
            db.session.rollback()
            return {'message': 'Erreur lors de l\'ajout du document'}, 500

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
            
            data = request.get_json() or {}
            
            # 1. Archive / Désarchive
            if route == 'archive':
                doc.archived = data.get('archived', True)
            else:
                # 2. Mise à jour classique
                for field in ['title', 'description', 'author', 'type', 'icon', 'file_size', 'file_url']:
                    if field in data:
                        setattr(doc, field, data[field])
            
            db.session.commit()
            logger.info(f"✅ Document mis à jour: {doc.title}")
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
            log_error(e, request, 'DocumentA… (11 chars truncated)
        except Exception as e:
            log_error(e, request, 'DocumentApi.delete')
            db.session.rollback()
            return {'message': 'Erreur lors de la suppression'}, 500

    # ========== PATCH ==========
    @admin_required
    def patch(self, current_admin, route=None, item_id=None):
        """Route PATCH dynamique unique"""
        try:
            if not item_id:
                return {'message': 'ID manquant'}, 400
            
            doc = Document.query.get(item_id)
            if not doc:
                return {'message': 'Document non trouvé'}, 404
            
            data = request.get_json() or {}
            
            # Mise à jour partielle (patch)
            for field in ['title', 'description', 'author', 'type', 'icon', 'file_size', 'file_url', 'archived']:
                if field in data:
                    setattr(doc, field, data[field])
            
            db.session.commit()
            logger.info(f"✅ Document mis à jour (PATCH): {doc.title}")
            return {'data': doc.to_dict()}, 200
            
        except Exception as e:
            log_error(e, request, 'DocumentApi.patch')
            db.session.rollback()
            return {'message': 'Erreur lors de la modification'}, 500

    # ========== SEARCH ==========
    def get_search(self):
        """Recherche full-text de documents"""
        try:
            query = request.args.get('q', '').strip()
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            if not query:
                return {'data': [], 'total': 0, 'query': query}, 200
            
            # Recherche dans le titre, description et auteur
            search = f"%{query}%"
            docs = Document.query.filter(
                (Document.title.ilike(search)) |
                (Document.description.ilike(search)) |
                (Document.author.ilike(search))
            ).filter_by(archived=False).all()
            
            result = PaginationHelper.paginate(
                Document.query.filter(
                    (Document.title.ilike(search)) |
                    (Document.description.ilike(search)) |
                    (Document.author.ilike(search))
                ).filter_by(archived=False),
                page, per_page
            )
            
            return {
                'data': [d.to_dict() for d in result['items']],
                'pagination': {k: v for k, v in result.items() if k != 'items'},
                'total': result['total'],
                'query': query
            }, 200
            
        except Exception as e:
            log_error(e, request, 'DocumentApi.get_search')
            return {'message': 'Erreur lors de la recherche'}, 500

    # ========== STATISTICS ==========
    def get_stats(self):
        """Statistiques sur les documents"""
        try:
            return {
                'total': Document.query.count(),
                'active': Document.query.filter_by(archived=False).count(),
                'archived': Document.query.filter_by(archived=True).count(),
                'recent_uploads': Document.query.filter_by(archived=False).order_by(Document.created_at.desc()).limit(5).count()
            }, 200
        except Exception as e:
            log_error(e, request, 'DocumentApi.get_stats')
            return {'message': 'Erreur lors de la récupération des statistiques'}, 500
