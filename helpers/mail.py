import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from logger.logger_config import get_logger

logger = get_logger()

class MailHelper:
    """Helper pour l'envoi d'emails via SendGrid"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@firdaws-mosque.ci')
        self.from_name = os.getenv('SENDGRID_FROM_NAME', 'Mosquée Firdaws')
    
    def send_contact_email(self, name, email, subject, message):
        """Envoie un email de contact"""
        try:
            if not self.api_key:
                logger.error("❌ SENDGRID_API_KEY non configuré")
                return {'success': False, 'error': 'Configuration email manquante'}
            
            sg = SendGridAPIClient(self.api_key)
            
            # Email à l'administrateur
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@firdaws-mosque.ci')
            
            html_content = f"""
            <html>
            <body>
                <h2>Nouveau message de contact</h2>
                <p><strong>Nom:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Sujet:</strong> {subject}</p>
                <p><strong>Message:</strong></p>
                <p>{message}</p>
                <hr>
                <p><em>Envoyé depuis le formulaire de contact de la mosquée Firdaws</em></p>
                <p><em>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=self.from_email,
                to_emails=admin_email,
                subject=f"[Contact Mosquée] {subject}",
                html_content=html_content
            )
            
            # Ajouter le reply-to
            message.reply_to = email
            
            response = sg.send(message)
            
            if response.status_code in [200, 202]:
                logger.info(f"✅ Email envoyé avec succès à {admin_email}")
                return {'success': True, 'message': 'Email envoyé avec succès'}
            else:
                logger.error(f"❌ Erreur SendGrid: {response.status_code} - {response.body}")
                return {'success': False, 'error': 'Erreur lors de l\'envoi de l\'email'}
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi de l'email: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_confirmation_email(self, to_email, name):
        """Envoie un email de confirmation au contactant"""
        try:
            if not self.api_key:
                logger.error("❌ SENDGRID_API_KEY non configuré")
                return {'success': False, 'error': 'Configuration email manquante'}
            
            sg = SendGridAPIClient(self.api_key)
            
            html_content = f"""
            <html>
            <body>
                <h2>Merci pour votre message</h2>
                <p>Bonjour {name},</p>
                <p>Nous avons bien reçu votre message et nous vous répondrons dans les plus brefs délais.</p>
                <p>Cordialement,</p>
                <p><strong>L'équipe de la Mosquée Firdaws</strong></p>
                <hr>
                <p><em>Ce message a été envoyé automatiquement, merci de ne pas y répondre.</em></p>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject="Confirmation de réception - Mosquée Firdaws",
                html_content=html_content
            )
            
            response = sg.send(message)
            
            if response.status_code in [200, 202]:
                logger.info(f"✅ Email de confirmation envoyé à {to_email}")
                return {'success': True, 'message': 'Email de confirmation envoyé'}
            else:
                logger.error(f"❌ Erreur SendGrid: {response.status_code} - {response.body}")
                return {'success': False, 'error': 'Erreur lors de l\'envoi de l\'email'}
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi de l'email de confirmation: {str(e)}")
            return {'success': False, 'error': str(e)}
