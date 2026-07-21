from flask import request, jsonify
from flask_restful import Resource, reqparse
from helpers.mail import MailHelper
from helpers.firewall_helper import FirewallHelper
from logger.logger_config import get_logger

logger = get_logger()

class ContactMailApi(Resource):
    """API pour l'envoi d'emails de contact"""
    
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=True, help='Nom est requis')
        self.parser.add_argument('email', type=str, required=True, help='Email est requis')
        self.parser.add_argument('subject', type=str, required=True, help='Sujet est requis')
        self.parser.add_argument('message', type=str, required=True, help='Message est requis')
        self.mail_helper = MailHelper()
    
    def post(self):
        """Envoie un email de contact"""
        try:
            # Vérifier si l'IP est bloquée
            if FirewallHelper.is_ip_blocked():
                FirewallHelper.log_intrusion(
                    severity='HIGH',
                    attack_type='BLOCKED_IP_ATTEMPT',
                    details={'endpoint': '/api/mail/contact'}
                )
                return {'error': 'Accès refusé'}, 403
            
            # Parser les données
            args = self.parser.parse_args()
            name = args['name']
            email = args['email']
            subject = args['subject']
            message = args['message']
            
            # Validation basique
            if not name or len(name) < 2:
                return {'error': 'Nom invalide'}, 400
            
            if not email or '@' not in email:
                return {'error': 'Email invalide'}, 400
            
            if not subject or len(subject) < 3:
                return {'error': 'Sujet invalide'}, 400
            
            if not message or len(message) < 10:
                return {'error': 'Message trop court'}, 400
            
            # Vérifier le rate limiting (simple: max 5 emails par heure par IP)
            client_ip = FirewallHelper.get_client_ip()
            # Note: Pour une implémentation complète, ajouter une table de rate limiting dans la DB
            
            # Envoyer l'email
            result = self.mail_helper.send_contact_email(name, email, subject, message)
            
            if result['success']:
                # Envoyer également un email de confirmation
                self.mail_helper.send_confirmation_email(email, name)
                
                logger.info(f"✅ Email de contact envoyé par {email} ({name})")
                return {
                    'success': True,
                    'message': 'Message envoyé avec succès'
                }, 200
            else:
                logger.error(f"❌ Erreur envoi email: {result['error']}")
                return {'error': result['error']}, 500
                
        except Exception as e:
            logger.error(f"❌ Erreur ContactMailApi: {str(e)}")
            FirewallHelper.log_intrusion(
                severity='MEDIUM',
                attack_type='MAIL_API_ERROR',
                details={'error': str(e)}
            )
            return {'error': 'Erreur serveur'}, 500