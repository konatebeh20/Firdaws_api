from flask_restful import Resource
from flask import request
from logger.logger_config import get_logger
from helpers.auth_helper import admin_required, superadmin_required
from helpers.error_helper import ErrorHelper

logger = get_logger()

class ErrorsApi(Resource):
    """Resource unique pour TOUS les endpoints de gestion des erreurs"""
    
    # ========== GET ==========
    @admin_required
    def get(self, current_admin, route=None, item_id=None):
        """Route GET dynamique unique"""
        try:
            # 1. GET /api/errors/<int:item_id>
            if item_id:
                error = ErrorHelper.get_error_by_id(item_id)
                if not error:
                    return {'message': 'Erreur non trouvée'}, 404
                return error, 200
            
            # 2. GET /api/errors/stats
            if route == 'stats':
                return ErrorHelper.get_error_stats(), 200
            
            # 3. GET /api/errors (par défaut - liste)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            return ErrorHelper.get_errors(page, per_page), 200
            
        except Exception as e:
            logger.error(f"Erreur GET errors: {str(e)}")
            return {'message': 'Erreur serveur'}, 500

    # ========== POST ==========
    def post(self, route=None):
        """Log une nouvelle erreur (public ou interne)"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'Données manquantes'}, 400
            
            # Utilisation du helper pour logger l'erreur
            ErrorHelper.log_error(
                error_type=data.get('error_type', 'ClientError'),
                message=data.get('message', 'No message provided'),
                traceback=data.get('traceback'),
                file=data.get('file'),
                function=data.get('function'),
                line=data.get('line'),
                environment=data.get('environment', 'production')
            )
            
            return {'message': 'Erreur loggée avec succès'}, 201
            
        except Exception as e:
            logger.error(f"Erreur POST errors: {str(e)}")
            return {'message': 'Erreur lors du logging'}, 500

    # ========== DELETE ==========
    @superadmin_required
    def delete(self, current_admin, route=None, item_id=None):
        """Supprime des erreurs (superadmin uniquement)"""
        try:
            # 1. DELETE /api/errors/<int:item_id>
            if item_id:
                if ErrorHelper.delete_error(item_id):
                    return {'message': 'Erreur supprimée'}, 200
                return {'message': 'Erreur non trouvée'}, 404
            
            # 2. DELETE /api/errors/clear_all
            if route == 'clear_all':
                count = ErrorHelper.clear_all_errors()
                return {'message': f'{count} erreurs supprimées'}, 200
            
            return {'message': 'Action non spécifiée'}, 400
            
        except Exception as e:
            logger.error(f"Erreur DELETE errors: {str(e)}")
            return {'message': 'Erreur lors de la suppression'}, 500
