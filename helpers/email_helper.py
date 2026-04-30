from flask import jsonify, request
from logger.logger_config import get_logger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis config.env
load_dotenv('config.env')

logger = get_logger()

class EmailHelper:
    """Helper pour l'envoi d'emails"""
    
    @staticmethod
    def send_email(data):
        """Envoie un email"""
        try:
            # Configuration SMTP (à adapter selon vos besoins)
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME', 'contact@firdaws-mosque.ci')
            smtp_password = os.getenv('SMTP_PASSWORD', '')
            
            # Données de l'email
            to_email = data.get('to', 'contact@firdaws-mosque.ci')
            subject = data.get('subject', 'Message de contact')
            template = data.get('template', 'simple')
            template_data = data.get('data', {})
            reply_to = data.get('reply_to')
            
            # Création du message avec headers anti-spam
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_username
            msg['To'] = to_email
            
            # Headers anti-spam et professionnels
            msg['X-Priority'] = '3'
            msg['X-MSMail-Priority'] = 'Normal'
            msg['X-Mailer'] = 'Firdaws Mosque Website'
            msg['X-MimeOLE'] = 'Produced By Firdaws Mosque'
            
            if reply_to:
                msg['Reply-To'] = reply_to
                msg['X-Reply-To'] = reply_to
            
            # Génération du contenu selon le template
            if template == 'contact_message':
                html_content = EmailHelper._generate_contact_template(template_data)
            else:
                html_content = EmailHelper._generate_simple_template(template_data)
            
            # Ajout du contenu HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Envoi de l'email (si configuration SMTP disponible)
            if smtp_password and os.getenv('SMTP_ENABLED', 'false').lower() == 'true':
                try:
                    # Connexion SMTP avec timeout et retry
                    server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    
                    # Envoi avec vérification
                    server.send_message(msg)
                    server.quit()
                    
                    logger.info(f"Email envoyé avec succès à {to_email}")
                    return True, "Email envoyé avec succès"
                    
                except smtplib.SMTPAuthenticationError as e:
                    logger.error(f"Erreur d'authentification SMTP: {str(e)}")
                    return False, "Erreur de configuration SMTP - vérifiez vos identifiants"
                except smtplib.SMTPRecipientsRefused as e:
                    logger.error(f"Destinataire refusé: {str(e)}")
                    return False, "Adresse email invalide"
                except Exception as smtp_error:
                    logger.error(f"Erreur SMTP: {str(smtp_error)}")
                    return False, f"Erreur lors de l'envoi: {str(smtp_error)}"
            else:
                # Mode développement : juste logger
                logger.info(f"Mode dev - Email non envoyé: {subject} à {to_email}")
                logger.info(f"Contenu: {html_content[:200]}...")
                return True, "Email enregistré (mode développement)"
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
            return False, f"Erreur lors de l'envoi de l'email: {str(e)}"
    
    @staticmethod
    def _generate_contact_template(data):
        """Génère le template HTML pour les messages de contact"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Nouveau message de contact</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #0a4b4a 0%, #0c5e5c 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px 0; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #0a4b4a; }}
                .value {{ margin-top: 5px; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #0a4b4a; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🕌 Nouveau Message de Contact</h1>
                    <p>Mosquée Firdaws - Cité Bel Aire</p>
                </div>
                <div class="content">
                    <div class="field">
                        <div class="label">Nom:</div>
                        <div class="value">{data.get('name', 'Non renseigné')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Email:</div>
                        <div class="value">{data.get('email', 'Non renseigné')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Téléphone:</div>
                        <div class="value">{data.get('phone', 'Non renseigné')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Sujet:</div>
                        <div class="value">{data.get('subject', 'Non renseigné')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Message:</div>
                        <div class="value">{data.get('message', 'Non renseigné').replace(chr(10), '<br>')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Date:</div>
                        <div class="value">{data.get('date', 'Non renseigné')}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>Ce message a été envoyé depuis le site web de la Mosquée Firdaws</p>
                    <p><a href="https://firdaws-mosque.ci">firdaws-mosque.ci</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _generate_simple_template(data):
        """Génère un template HTML simple"""
        title = data.get('title', 'Notification')
        content = data.get('content', 'Message')
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }}
                .header {{ background: #0a4b4a; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                </div>
                <div class="content">
                    {content.replace(chr(10), '<br>')}
                </div>
            </div>
        </body>
        </html>
        """
