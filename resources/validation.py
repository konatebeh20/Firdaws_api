from flask_restful import Resource
from flask import request
from helpers.validation_helper import ValidationHelper

class ValidationApi(Resource):
    """Resource unique pour valider différents types de données"""
    
    # ========== GET ==========
    def get(self, route=None):
        """Documentation des validations disponibles ou test spécifique"""
        return {
            'types': ['email', 'phone', 'password', 'date', 'url'],
            'description': 'POST avec {"type": "...", "value": "..."}',
            'examples': {
                'email': 'user@example.com',
                'phone': '0612345678',
                'password': 'Test1234!',
                'date': '2025-03-28',
                'url': 'https://youtube.com/watch?v=123'
            }
        }, 200

    # ========== POST ==========
    def post(self, route=None):
        """Valide des données selon le type demandé"""
        data = request.get_json()
        validation_type = data.get('type')
        value = data.get('value')
        
        if not validation_type or not value:
            return {'message': 'Type et valeur requis'}, 400
        
        result = {'valid': False, 'message': ''}
        
        if validation_type == 'email':
            result['valid'] = ValidationHelper.email(value)
            result['message'] = 'Email valide' if result['valid'] else 'Email invalide'
        
        elif validation_type == 'phone':
            result['valid'] = ValidationHelper.phone(value)
            result['message'] = 'Téléphone valide' if result['valid'] else 'Téléphone invalide'
        
        elif validation_type == 'password':
            valid, message = ValidationHelper.password(value)
            result['valid'] = valid
            result['message'] = message
        
        elif validation_type == 'date':
            result['valid'] = ValidationHelper.date(value)
            result['message'] = 'Date valide' if result['valid'] else 'Date invalide (format YYYY-MM-DD)'
        
        elif validation_type == 'url':
            result['valid'] = ValidationHelper.url(value)
            result['message'] = 'URL valide' if result['valid'] else 'URL invalide'
        
        else:
            return {'message': f'Type de validation inconnu: {validation_type}'}, 400
        
        return result, 200