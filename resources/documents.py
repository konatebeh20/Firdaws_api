import os
from flask_restful import Resource
from flask import request, current_app
from werkzeug.utils import secure_filename
from model.firdaws_db import Document, Admin
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import verify_token
from helpers.document_helper import DocumentHelper
from helpers.pagination_helper import PaginationHelper
from helpers.error_helper import log_error
from helpers.document_converter import convert_to_pdf, CONVERTIBLE

logger = get_logger()

# Constants for error messages
MSG_DOCUMENT_NOT_FOUND = 'Document non trouvé'
MSG_AUTH_REQUIRED = 'Authentification requise - Veuillez vous connecter'
MSG_ID_REQUIRED = 'ID manquant'
MSG_UPLOAD_ERROR = 'Erreur lors de l\'ajout du document'
MSG_DELETE_ERROR = 'Erreur lors de la suppression'
MSG_UPDATE_ERROR = 'Erreur lors de la modification'

class DocumentApi(Resource):
    """Resource unique pour TOUS les endpoints documents"""
    
    def get_current_admin(self):
        """Récupère l'admin depuis le token (supporte token admin ET token user-admin)"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return None

        logger.debug(f"Token payload reçu: {payload}")

        # Token Admin → clé 'admin_id'
        if 'admin_id' in payload:
            return Admin.query.get(payload['admin_id'])

        # Token User → vérifier si rôle admin/superadmin
        if 'user_id' in payload:
            from model.firdaws_db import User
            user = User.query.get(payload['user_id'])
            if user and user.role in ('admin', 'superadmin'):
                admin = Admin.query.filter_by(email=user.email).first()
                if admin:
                    return admin
                return user

        return None

    # ========== GET ==========
    def get(self, route=None, item_id=None):
        """Route GET dynamique unique"""
        try:
            # 1. GET /api/documents/<int:item_id>
            if item_id and not route:
                doc = Document.query.get(item_id)
                if not doc:
                    return {'message': MSG_DOCUMENT_NOT_FOUND}, 404
                return {'data': doc.to_dict()}, 200
            
            # 2. GET /api/documents/admin
            if route == 'admin':
                current_admin = self.get_current_admin()
                if not current_admin:
                    return {'message': MSG_AUTH_REQUIRED}, 401
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
            
            query = Document.query if include_archived else Document.query.filter_by(archived=False)
            query = query.order_by(Document.id.desc())
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
            current_admin = self.get_current_admin()
            
            if not current_admin:
                logger.warning("Tentative de téléversement sans authentification")
                return {'message': MSG_AUTH_REQUIRED}, 401

            # Mode fichier vs JSON
            if 'file' in request.files:
                return self._handle_file_upload(current_admin)
            else:
                return self._handle_json_upload(current_admin)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du document: {str(e)}", exc_info=True)
            log_error(e, request, 'DocumentApi.post')
            db.session.rollback()
            return {'message': f'{MSG_UPLOAD_ERROR}: {str(e)}'}, 500

    def _handle_file_upload(self, current_admin):
        """Handle multipart/form-data file upload with auto PDF conversion"""
        file = request.files['file']
        data = request.form.to_dict()
        
        logger.info(f"UPLOAD APPELÉ - File: {file.filename if file else 'None'}, Data: {data}")
        
        # Validation des champs
        errors = DocumentHelper.validate_data(data)
        if errors:
            logger.warning(f"Erreur validation document: {errors}")
            return {'message': 'Erreur de validation', 'errors': errors}, 400
        
        # Validation du fichier
        if not file or not DocumentHelper.allowed_file(file.filename):
            logger.warning("Fichier manquant ou extension non autorisée")
            return {'message': 'Extension de fichier non autorisée ou fichier manquant'}, 400
        
        original_filename = secure_filename(file.filename)
        
        # Sauvegarde physique
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        upload_path = os.path.join(upload_folder, original_filename)
        file.save(upload_path)
        logger.info(f"Fichier sauvegardé à: {upload_path}")
        
        # Récupération extension
        ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        file_size_bytes = os.path.getsize(upload_path)
        
        # Conversion automatique en PDF si fichier Office
        if ext in CONVERTIBLE:
            logger.info(f"Conversion en PDF: {original_filename}")
            pdf_path = convert_to_pdf(upload_path, upload_folder)
            
            if pdf_path:
                # Supprimer le fichier original, garder uniquement le PDF
                os.remove(upload_path)
                final_filename = os.path.basename(pdf_path)
                file_url = f"/uploads/{final_filename}"
                file_size_bytes = os.path.getsize(pdf_path)
                final_ext = 'PDF'
                logger.info(f"Converti en PDF: {final_filename}")
            else:
                # Conversion échouée → garder le fichier original
                logger.warning(f"Conversion échouée, fichier original conservé: {original_filename}")
                file_url = f"/uploads/{original_filename}"
                final_ext = ext.upper()
        else:
            # PDF, images → pas de conversion nécessaire
            file_url = f"/uploads/{original_filename}"
            final_ext = ext.upper()
        
        # Préparation données
        doc_data = {
            'title': data.get('title', '').strip(),
            'description': data.get('description', '').strip(),
            'author': data.get('author', '').strip() or 'Anonyme',
            'type': final_ext,
            'icon': DocumentHelper.get_file_icon(original_filename),
            'file_size': DocumentHelper.format_file_size(file_size_bytes),
            'file_url': file_url,
            'created_by': current_admin.id
        }
        
        logger.info(f"Préparation données document: {doc_data}")
        
        return self._save_document(doc_data)

    def _handle_json_upload(self, current_admin):
        """Handle JSON payload upload"""
        data = request.get_json() or {}
        
        logger.info(f"UPLOAD MODE JSON - Data: {data}")
        
        errors = DocumentHelper.validate_data(data)
        if errors:
            return {'message': 'Erreur de validation', 'errors': errors}, 400
        
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
        
        return self._save_document(doc_data)

    def _save_document(self, doc_data):
        """Save document to database"""
        doc = Document(**doc_data)
        doc.save()  # Utilise la méthode save() du modèle si elle existe
        logger.info(f"✅ Document enregistré avec succès: {doc.title}")
        return {'message': 'Document créé avec succès', 'data': doc.to_dict()}, 201

    # ========== PUT ==========
    def put(self, route=None, item_id=None):
        """Route PUT dynamique unique"""
        try:
            current_admin = self.get_current_admin()
            
            if not current_admin:
                return {'message': MSG_AUTH_REQUIRED}, 401
            
            if not item_id:
                return {'message': MSG_ID_REQUIRED}, 400
            
            doc = Document.query.get(item_id)
            if not doc:
                return {'message': MSG_DOCUMENT_NOT_FOUND}, 404
            
            data = request.get_json() or {}
            
            if route == 'archive':
                doc.archived = data.get('archived', True)
            else:
                for field in ['title', 'description', 'author', 'type', 'icon', 'file_size', 'file_url']:
                    if field in data:
                        setattr(doc, field, data[field])
            
            db.session.commit()
            logger.info(f"✅ Document mis à jour: {doc.title}")
            return {'data': doc.to_dict()}, 200
            
        except Exception as e:
            log_error(e, request, 'DocumentApi.put')
            db.session.rollback()
            return {'message': MSG_UPDATE_ERROR}, 500

    # ========== DELETE ==========
    def delete(self, route=None, item_id=None):
        """Route DELETE dynamique unique avec suppression physique du fichier"""
        try:
            current_admin = self.get_current_admin()
            
            if not current_admin:
                return {'message': MSG_AUTH_REQUIRED}, 401
            
            if not item_id:
                return {'message': MSG_ID_REQUIRED}, 400
                
            doc = Document.query.get(item_id)
            if not doc:
                return {'message': MSG_DOCUMENT_NOT_FOUND}, 404
            
            # Supprimer le fichier physique
            if doc.file_url and doc.file_url != '#':
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                file_path = os.path.join(upload_folder, doc.file_url.lstrip('/uploads/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Fichier supprimé: {file_path}")
                else:
                    logger.warning(f"Fichier non trouvé: {file_path}")
            
            db.session.delete(doc)
            db.session.commit()
            
            logger.info(f"✅ Document supprimé: {doc.title}")
            return {'message': 'Supprimé avec succès'}, 200
            
        except Exception as e:
            log_error(e, request, 'DocumentApi.delete')
            db.session.rollback()
            return {'message': MSG_DELETE_ERROR}, 500

    # ========== PATCH ==========
    def patch(self, route=None, item_id=None):
        """Route PATCH dynamique unique"""
        try:
            current_admin = self.get_current_admin()
            
            if not current_admin:
                return {'message': MSG_AUTH_REQUIRED}, 401
            
            if not item_id:
                return {'message': MSG_ID_REQUIRED}, 400
            
            doc = Document.query.get(item_id)
            if not doc:
                return {'message': MSG_DOCUMENT_NOT_FOUND}, 404
            
            data = request.get_json() or {}
            
            for field in ['title', 'description', 'author', 'type', 'icon', 'file_size', 'file_url', 'archived']:
                if field in data:
                    setattr(doc, field, data[field])
            
            db.session.commit()
            logger.info(f"✅ Document mis à jour (PATCH): {doc.title}")
            return {'data': doc.to_dict()}, 200
            
        except Exception as e:
            log_error(e, request, 'DocumentApi.patch')
            db.session.rollback()
            return {'message': MSG_UPDATE_ERROR}, 500


# import os
# from flask_restful import Resource
# from flask import request, current_app
# from werkzeug.utils import secure_filename
# from model.firdaws_db import Document, Admin
# from config.db import db
# from logger.logger_config import get_logger
# from helpers.auth_helper import admin_required, verify_token
# from helpers.document_helper import DocumentHelper
# from helpers.pagination_helper import PaginationHelper
# from helpers.error_helper import log_error

# logger = get_logger()

# # Constants for error messages
# MSG_DOCUMENT_NOT_FOUND = 'Document non trouvé'
# MSG_AUTH_REQUIRED = 'Authentification requise - Veuillez vous connecter'
# MSG_ID_REQUIRED = 'ID manquant'
# MSG_UPLOAD_ERROR = 'Erreur lors de l\'ajout du document'
# MSG_DELETE_ERROR = 'Erreur lors de la suppression'
# MSG_UPDATE_ERROR = 'Erreur lors de la modification'

# class DocumentApi(Resource):
#     """Resource unique pour TOUS les endpoints documents"""
    
#     def get_current_admin(self):
#         """Récupère l'admin depuis le token (supporte token admin ET token user-admin)"""
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return None

#         token = auth_header.split(' ')[1]
#         payload = verify_token(token)
#         if not payload:
#             return None

#         # Log temporaire pour déboguer — à retirer après
#         logger.debug(f"Token payload reçu: {payload}")

#         # Token Admin → clé 'admin_id'
#         if 'admin_id' in payload:
#             return Admin.query.get(payload['admin_id'])

#         # Token User → vérifier si rôle admin/superadmin
#         if 'user_id' in payload:
#             from model.firdaws_db import User
#             user = User.query.get(payload['user_id'])
#             if user and user.role in ('admin', 'superadmin'):
#                 # Chercher d'abord dans admins par email
#                 admin = Admin.query.filter_by(email=user.email).first()
#                 if admin:
#                     return admin
#                 # Sinon retourner le user directement (il a les droits)
#                 return user

#         return None

#         # if 'user_id' in payload:
#         #     from model.firdaws_db import User
#         #     user = User.query.get(payload['user_id'])
#         #     if user and user.role in ('admin', 'superadmin'):
#         #         return Admin.query.filter_by(email=user.email).first()

#         # return None

#     # def get_current_admin(self):
#     #     """Récupère l'admin si token présent"""
#     #     auth_header = request.headers.get('Authorization')
#     #     if auth_header and auth_header.startswith('Bearer '):
#     #         token = auth_header.split(' ')[1]
#     #         payload = verify_token(token)
#     #         if payload:
#     #             return Admin.query.get(payload['admin_id'])
#     #     return None

#     # ========== GET ==========
#     def get(self, route=None, item_id=None):
#         """Route GET dynamique unique"""
#         try:
#             current_admin = self.get_current_admin()
            
#             # 1. GET /api/documents/<int:item_id>
#             if item_id and not route:
#                 doc = Document.query.filter_by(id=item_id).first()
#                 if doc is None:
#                     return {'message': MSG_DOCUMENT_NOT_FOUND}, 404
#                 return {'data': doc.to_dict()}, 200
            
#             # 2. GET /api/documents/admin
#             if route == 'admin':
#                 if not current_admin:
#                     return {'message': MSG_AUTH_REQUIRED}, 401
#                 docs = Document.query.order_by(Document.archived, Document.id.desc()).all()
#                 return {
#                     'data': [d.to_dict() for d in docs],
#                     'total': len(docs),
#                     'active': len([d for d in docs if not d.archived]),
#                     'archived': len([d for d in docs if d.archived])
#                 } or {}, 200

#             # 3. GET /api/documents (par défaut)
#             page = request.args.get('page', 1, type=int)
#             per_page = request.args.get('per_page', 100, type=int)
#             include_archived = request.args.get('include_archived', 'false').lower() == 'true'
            
#             if include_archived:
#                 query = Document.query.order_by(Document.id.desc())
#             else:
#                 query = Document.query.filter_by(archived=False).order_by(Document.id.desc())
#             result = PaginationHelper.paginate(query, page, per_page)
            
#             return {
#                 'data': [d.to_dict() for d in result['items']],
#                 'pagination': {k: v for k, v in result.items() if k != 'items'}
#             }, 200

#         except Exception as e:
#             log_error(e, request, 'DocumentApi.get')
#             return {'message': 'Erreur lors de la récupération'}, 500

#     # ========== POST ==========
#     def post(self, route=None, item_id=None):
#         """Route POST dynamique unique acceptant JSON ou Multipart/Form-Data (Fichiers)"""
#         try:
#             current_admin = self.get_current_admin()
            
#             if not current_admin:
#                 logger.warning("Tentative de téléversement sans authentification")
#                 return {'message': MSG_AUTH_REQUIRED}, 401

#             # Mode fichier vs JSON
#             self._handle_file_upload() if 'file' in request.files else self._handle_json_upload()
            
#         except Exception as e:
#             logger.error(f"Erreur lors de l'ajout du document: {str(e)}", exc_info=True)
#             log_error(e, request, 'DocumentApi.post')
#             db.session.rollback()
#             return {'message': f'{MSG_UPLOAD_ERROR}: {str(e)}'}, 500

#     def _handle_file_upload(self):
#         """Handle multipart/form-data file upload"""
#         file = request.files['file']
#         data = request.form.to_dict()
        
#         logger.info(f"UPLOAD APPELÉ - File: {file.filename if file else 'None'}, Data: {data}")
        
#         # Validation des champs
#         errors = DocumentHelper.validate_data(data)
#         if errors:
#             logger.warning(f"Erreur validation document: {errors}")
#             return {'message': 'Erreur de validation', 'errors': errors}, 400
        
#         # Validation du fichier
#         if not file or not DocumentHelper.allowed_file(file.filename):
#             logger.warning("Fichier manquant ou extension non autorisée")
#             return {'message': 'Extension de fichier non autorisée ou fichier manquant'}, 400
        
#         filename = secure_filename(file.filename)
        
#         # Sauvegarde physique
#         upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
#         os.makedirs(upload_folder, exist_ok=True)
        
#         upload_path = os.path.join(upload_folder, filename)
#         file.save(upload_path)
#         logger.info(f"Fichier sauvegardé à: {upload_path}")
        
#         # Récupération métadonnées
#         file_url = f"/uploads/{filename}"
#         file_size_bytes = os.path.getsize(upload_path)
        
#         # Préparation données
#         doc_data = DocumentHelper.prepare_data(
#             data=data,
#             filename=filename,
#             size_bytes=file_size_bytes,
#             file_url=file_url,
#             admin_id=self.get_current_admin().id if self.get_current_admin() else None
#         )
#         logger.info(f"Préparation données document: {doc_data}")
        
#         self._save_document(doc_data)

#     def _handle_json_upload(self):
#         """Handle JSON payload upload"""
#         data = request.get_json() or {}
        
#         logger.info(f"UPLOAD MODE JSON - Data: {data}")
        
#         errors = DocumentHelper.validate_data(data)
#         if errors:
#             return {'message': 'Erreur de validation', 'errors': errors}, 400
        
#         admin = self.get_current_admin()
#         doc_data = {
#             'title': data.get('title', '').strip(),
#             'description': data.get('description', '').strip(),
#             'author': data.get('author', 'Anonyme').strip(),
#             'type': data.get('type', 'PDF').upper(),
#             'icon': data.get('icon', '📄'),
#             'file_size': data.get('file_size', '0.0 B'),
#             'file_url': data.get('file_url', '#'),
#             'created_by': admin.id if admin else None
#         }
        
#         self._save_document(doc_data)

#     def _save_document(self, doc_data):
#         """Save document to database"""
#         doc = Document(**doc_data)
#         db.session.add(doc)
#         db.session.commit()
#         logger.info(f"✅ Document enregistré avec succès: {doc.title}")
#         return {'data': doc.to_dict()}, 201

#     # ========== PUT ==========
#     def put(self, route=None, item_id=None):
#         """Route PUT dynamique unique"""
#         try:
#             current_admin = self.get_current_admin()
            
#             if not current_admin:
#                 return {'message': MSG_AUTH_REQUIRED}, 401
            
#             if not item_id:
#                 return {'message': MSG_ID_REQUIRED}, 400
            
#             doc = Document.query.get(item_id)
#             if not doc:
#                 return {'message': MSG_DOCUMENT_NOT_FOUND}, 404
            
#             data = request.get_json() or {}
            
#             if route == 'archive':
#                 doc.archived = data.get('archived', True)
#             else:
#                 for field in ['title', 'description', 'author', 'type', 'icon', 'file_size', 'file_url']:
#                     if field in data:
#                         setattr(doc, field, data[field])
            
#             db.session.commit()
#             logger.info(f"✅ Document mis à jour: {doc.title}")
#             return {'data': doc.to_dict()}, 200
            
#         except Exception as e:
#             log_error(e, request, 'DocumentApi.put')
#             db.session.rollback()
#             return {'message': MSG_UPDATE_ERROR}, 500

#     # ========== DELETE ==========
#     def delete(self, route=None, item_id=None):
#         """Route DELETE dynamique unique"""
#         try:
#             current_admin = self.get_current_admin()
            
#             if not current_admin:
#                 return {'message': MSG_AUTH_REQUIRED}, 401
            
#             if not item_id:
#                 return {'message': MSG_ID_REQUIRED}, 400
                
#             doc = Document.query.get(item_id)
#             if not doc:
#                 return {'message': MSG_DOCUMENT_NOT_FOUND}, 404
            
#             db.session.delete(doc)
#             db.session.commit()
            
#             logger.info(f"✅ Document supprimé: {doc.title}")
#             return {'data': {'message': 'Document supprimé', 'id': item_id}}, 200
            
#         except Exception as e:
#             log_error(e, request, 'DocumentApi.delete')
#             db.session.rollback()
#             return {'message': MSG_DELETE_ERROR}, 500

#     # ========== PATCH ==========
#     def patch(self, route=None, item_id=None):
#         """Route PATCH dynamique unique"""
#         try:
#             current_admin = self.get_current_admin()
            
#             if not current_admin:
#                 return {'message': MSG_AUTH_REQUIRED}, 401
            
#             if not item_id:
#                 return {'message': MSG_ID_REQUIRED}, 400
            
#             doc = Document.query.get(item_id)
#             if not doc:
#                 return {'message': MSG_DOCUMENT_NOT_FOUND}, 404
            
#             data = request.get_json() or {}
            
#             for field in ['title', 'description', 'author', 'type', 'icon', 'file_size', 'file_url', 'archived']:
#                 if field in data:
#                     setattr(doc, field, data[field])
            
#             db.session.commit()
#             logger.info(f"✅ Document mis à jour (PATCH): {doc.title}")
#             return {'data': doc.to_dict()}, 200
            
#         except Exception as e:
#             log_error(e, request, 'DocumentApi.patch')
#             db.session.rollback()
#             return {'message': MSG_UPDATE_ERROR}, 500
