from flask_restful import Resource
from flask import request
from helpers.pagination_helper import PaginationHelper

class PaginationApi(Resource):
    """Resource unique pour les tests et exemples de pagination"""
    
    # ========== GET ==========
    def get(self, route=None):
        """Exemple d'utilisation de la pagination"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # 1. Exemple avec une liste statique
            sample_items = list(range(1, 101))  # 1 à 100
            result = PaginationHelper.paginate_list(sample_items, page, per_page)
            
            return {
                'items': result['items'],
                'pagination': {
                    'page': result['page'],
                    'per_page': result['per_page'],
                    'total': result['total'],
                    'pages': result['pages'],
                    'has_prev': result['has_prev'],
                    'has_next': result['has_next']
                }
            }, 200
        except Exception as e:
            return {'message': 'Erreur serveur'}, 500