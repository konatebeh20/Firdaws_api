from flask_restful import Resource
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import admin_required
from helpers.file_helper import FileHelper
from helpers.error_helper import log_error
import os

logger = get_logger()

class FileApi(Resource):
    """Resource unique pour TOUS les endpoints fichiers"""
    
    # ========== GET ==========
    def get(self, route=None, item_id=None):
        """Route GET dynamique unique"""
        try:
            # 1. GET /api/files/download/<filename>
            if route == 'download' and item_id: # item_id used as filename
                # In this specific case, the route in app.py is /api/files/<string:route>/<int:item_id>
                # which doesn't fit filename. But FileApi is registered as:
                # api.add_resource(FileApi, '/api/files', '/api/files/<string:route>', '/api/files/<string:route>/<int:item_id>', ...)
                pass
            
            return {'message': 'Route non trouvée'}, 404
        except Exception as e:
            log_error(e, request, 'FileApi.get')
            return {'message': 'Erreur serveur'}, 500

    # ========== POST ==========
    @admin_required
    def post(self, current_admin, route=None, item_id=None):
        """Route POST dynamique unique"""
        try:
            # 1. POST /api/files/upload
            if route == 'upload':
                if 'file' not in request.files:
                    return {'message': 'Aucun fichier fourni'}, 400
                
                file = request.files['file']
                subfolder = request.form.get('subfolder', 'uploads')
                
                # Validation
                errors = FileHelper.validate_file(file)
                if errors:
                    return {'message': 'Erreur de validation', 'errors': errors}, 400
                
                # Sauvegarder le fichier
                file_url = FileHelper.save_file(file, subfolder)
                if not file_url:
                    return {'message': 'Erreur lors de la sauvegarde'}, 500
                
                file_info = FileHelper.get_file_info(file)
                logger.info(f"✅ Fichier uploadé: {file.filename} par {current_admin.email}")
                
                return {
                    'message': 'Fichier uploadé avec succès',
                    'file_url': file_url,
                    'file_info': file_info
                }, 201

            # 2. POST /api/files/info
            if route == 'info':
                if 'file' not in request.files:
                    return {'message': 'Aucun fichier fourni'}, 400
                
                file = request.files['file']
                file_info = FileHelper.get_file_info(file)
                return {'file_info': file_info}, 200

            return {'message': 'Route non trouvée'}, 404

        except Exception as e:
            log_error(e, request, 'FileApi.post')
            return {'message': 'Erreur serveur'}, 500

    # ========== DELETE ==========
    @admin_required
    def delete(self, current_admin, route=None, item_id=None):
        """Route DELETE dynamique unique"""
        try:
            # 1. DELETE /api/files/delete (avec body JSON)
            if route == 'delete':
                data = request.get_json()
                file_url = data.get('file_url')
                
                if not file_url:
                    return {'message': 'URL du fichier requise'}, 400
                
                success = FileHelper.delete_file(file_url)
                if success:
                    logger.info(f"✅ Fichier supprimé: {file_url}")
                    return {'message': 'Fichier supprimé avec succès'}, 200
                else:
                    return {'message': 'Fichier non trouvé'}, 404

            return {'message': 'Route non trouvée'}, 404

        except Exception as e:
            log_error(e, request, 'FileApi.delete')
            return {'message': 'Erreur serveur'}, 500
