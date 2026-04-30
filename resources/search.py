from flask_restful import Resource
from flask import request
from logger.logger_config import get_logger
from helpers.search_helper import SearchHelper

logger = get_logger()

class SearchApi(Resource):
    """Resource unique pour TOUS les endpoints de recherche"""
    
    # ========== GET ==========
    def get(self, route=None):
        """Route GET dynamique unique"""
        try:
            query = request.args.get('q', '')
            
            # 1. GET /api/search/suggestions
            if route == 'suggestions':
                if len(query) < 2:
                    return {'suggestions': []}, 200
                
                suggestions = SearchHelper.get_search_suggestions(query)
                return {
                    'query': query,
                    'suggestions': suggestions
                }, 200

            # 2. GET /api/search (par défaut - global)
            limit = request.args.get('limit', 5, type=int)
            
            if len(query) < 2:
                return {
                    'query': query,
                    'results': {},
                    'total': 0
                }, 200
            
            results = SearchHelper.search_all(query, limit)
            
            return {
                'query': query,
                'results': results,
                'total': results.get('total', 0)
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur GET search: {str(e)}")
            return {'message': 'Erreur serveur'}, 500