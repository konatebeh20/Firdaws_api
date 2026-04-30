from flask_restful import Resource
from flask import request, jsonify
from logger.logger_config import get_logger
from helpers.email_helper import EmailHelper
from helpers.push_helper import PushHelper

logger = get_logger()

class SendEmail(Resource):
    """Endpoint pour l'envoi d'emails"""
    
    def post(self):
        """Envoie un email"""
        try:
            data = request.get_json()
            
            if not data:
                return {'success': False, 'message': 'Données manquantes'}, 400
            
            # Validation basique
            if not data.get('to') or not data.get('subject'):
                return {'success': False, 'message': 'Destinataire et sujet requis'}, 400
            
            # Envoi de l'email
            success, message = EmailHelper.send_email(data)
            
            if success:
                return {
                    'success': True,
                    'message': message,
                    'data': {
                        'to': data.get('to'),
                        'subject': data.get('subject'),
                        'sent_at': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                            'SendEmail', 20, __file__, 0, 'Email sent', (), None
                        )) if logger.handlers else None
                    }
                }, 200
            else:
                return {'success': False, 'message': message}, 500
                
        except Exception as e:
            logger.error(f"Erreur dans SendEmail.post: {str(e)}")
            return {'success': False, 'message': 'Erreur serveur'}, 500

class SendPush(Resource):
    """Endpoint pour l'envoi de notifications push"""
    
    def post(self):
        """Envoie une notification push"""
        try:
            data = request.get_json()
            
            if not data:
                return {'success': False, 'message': 'Données manquantes'}, 400
            
            # Validation basique
            if not data.get('title') or not data.get('body'):
                return {'success': False, 'message': 'Titre et message requis'}, 400
            
            # Envoi de la notification push
            success, message = PushHelper.send_push_notification(data)
            
            if success:
                # Stocker pour livraison WebSocket ultérieure
                notification = PushHelper.store_notification(data)
                
                return {
                    'success': True,
                    'message': message,
                    'data': {
                        'title': data.get('title'),
                        'target_users': data.get('target_users', []),
                        'priority': data.get('priority', 'normal'),
                        'notification_id': notification.get('id') if notification else None,
                        'sent_at': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                            'SendPush', 20, __file__, 0, 'Push sent', (), None
                        )) if logger.handlers else None
                    }
                }, 200
            else:
                return {'success': False, 'message': message}, 500
                
        except Exception as e:
            logger.error(f"Erreur dans SendPush.post: {str(e)}")
            return {'success': False, 'message': 'Erreur serveur'}, 500

class Contact(Resource):
    """Endpoint simple pour les messages de contact (alternative)"""
    
    def post(self):
        """Enregistre un message de contact simple"""
        try:
            data = request.get_json()
            
            if not data:
                return {'success': False, 'message': 'Données manquantes'}, 400
            
            # Validation
            required_fields = ['name', 'email', 'subject', 'message']
            for field in required_fields:
                if not data.get(field):
                    return {'success': False, 'message': f'Champ {field} requis'}, 400
            
            # Validation email
            if '@' not in data.get('email', ''):
                return {'success': False, 'message': 'Email invalide'}, 400
            
            # En mode développement, on simule l'enregistrement
            logger.info(f"Message de contact reçu:")
            logger.info(f"  Nom: {data.get('name')}")
            logger.info(f"  Email: {data.get('email')}")
            logger.info(f"  Sujet: {data.get('subject')}")
            logger.info(f"  Message: {data.get('message')[:100]}...")
            
            return {
                'success': True,
                'message': 'Message de contact enregistré avec succès',
                'data': {
                    'name': data.get('name'),
                    'email': data.get('email'),
                    'subject': data.get('subject'),
                    'received_at': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                        'Contact', 20, __file__, 0, 'Contact received', (), None
                    )) if logger.handlers else None
                }
            }, 200
                
        except Exception as e:
            logger.error(f"Erreur dans Contact.post: {str(e)}")
            return {'success': False, 'message': 'Erreur serveur'}, 500
