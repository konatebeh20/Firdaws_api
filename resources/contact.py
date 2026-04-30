from flask_restful import Resource
from flask import request
from model.firdaws_db import Mail
from config.db import db
from logger.logger_config import get_logger
from helpers.error_helper import log_error
from datetime import datetime

logger = get_logger()

class ContactApi(Resource):
    """Resource pour gérer les messages de contact"""
    
    def post(self):
        """Envoie un message de contact (enregistre dans la table Mail)"""
        try:
            data = request.get_json()
            
            # Validation simple
            if not data.get('email') or not data.get('subject') or not data.get('message'):
                return {'message': 'Champs obligatoires manquants'}, 400
                
            mail = Mail(
                recipient='support@mosquee-bel-aire.com', # Email du support
                subject=f"Contact: {data['subject']} (de {data.get('name', 'Anonyme')})",
                body=f"De: {data.get('name')} <{data['email']}>\n\nMessage:\n{data['message']}\n\nPhone: {data.get('phone', 'N/A')}",
                status='pending'
            )
            
            db.session.add(mail)
            db.session.commit()
            
            logger.info(f"✅ Nouveau message de contact de {data['email']}")
            return {'message': 'Message envoyé avec succès'}, 201
            
        except Exception as e:
            log_error(e, request, 'ContactApi.post')
            db.session.rollback()
            return {'message': 'Erreur lors de l\'envois du message'}, 500
