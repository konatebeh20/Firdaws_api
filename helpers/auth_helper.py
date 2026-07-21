import jwt
import bcrypt
import secrets
from config.db import db
from functools import wraps
from flask import request, current_app
from logger.logger_config import get_logger
from datetime import datetime, timedelta, timezone
from model.firdaws_db import Admin, User, ResetToken


logger = get_logger()


def verify_token(token):
    """Vérifie et décode un token JWT"""
    try:
        secret = current_app.config.get('JWT_SECRET_KEY')
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("Verification du token échouée : La signature a expiré")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"Verification du token échouée : {str(e)}")
        return None


def token_required(f):
    """Décorateur pour routes nécessitant un token utilisateur simple"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'Token manquant'}, 401
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return {'message': 'Token invalide ou expiré'}, 401

        current_account = None
        if 'admin_id' in payload:
            current_account = Admin.query.get(payload['admin_id'])
        elif 'user_id' in payload:
            current_account = User.query.get(payload['user_id'])

        user = User.query.get(user_id)
        if not user:
            return {'message': 'Compte non trouvé'}, 401

        if not user.is_active:
            return {'message': 'Compte désactivé'}, 403

        return f(*args, current_user=user, **kwargs)
    return decorated


def admin_required(f):
    """Décorateur pour routes nécessitant un token admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'Token admin manquant'}, 401
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return {'message': 'Token invalide ou expiré — veuillez vous reconnecter'}, 401

        admin = Admin.query.get(payload.get('admin_id'))
        if not admin or not admin.is_active:
            return {'message': 'Admin introuvable ou inactif'}, 401

        # Sécurité : On vérifie que le rôle est bien autorisé
        if admin.role not in ['admin', 'superadmin']:
            return {'message': 'Accès non autorisé'}, 403

        return f(*args, current_admin=admin, **kwargs)
    return decorated


def superadmin_required(f):
    """Décorateur pour routes nécessitant un superadmin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'Token superadmin manquant'}, 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return {'message': 'Token invalide ou expiré'}, 401

        admin = Admin.query.get(payload.get('admin_id'))
        if not admin or not admin.is_active:
            return {'message': 'Admin introuvable ou inactif'}, 401
            
        if admin.role != 'superadmin':
            return {'message': 'Droits superadmin requis'}, 403
        return f(*args, current_admin=admin, **kwargs)
    return decorated


def honeypot_check(f):
    """Décorateur pour vérifier le honeypot anti-bot"""
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json() if request.is_json else request.form
        if data:
            from helpers.honeypot_helper import HoneypotHelper
            is_bot, message, _ = HoneypotHelper.check_honeypot(data)
            if is_bot:
                return {'message': message}, 400
        return f(*args, **kwargs)
    return decorated


class AuthHelper:
    """Helper pour les opérations d'authentification (Hachage, Tokens)"""

    @staticmethod
    def hash_password(password):
        """Hache un mot de passe avec bcrypt"""
        rounds = current_app.config.get('BCRYPT_ROUNDS', 12)
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(hashed_password, password):
        """Vérifie un mot de passe par rapport à son hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du mot de passe: {str(e)}")
            return False

    @staticmethod
    def generate_token(admin):
        """Génère un token JWT pour un administrateur"""
        expires = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))
        payload = {
            'admin_id': admin.id,
            'email': admin.email,
            'role': admin.role,
            'exp': datetime.now(timezone.utc) + expires
        }
        secret = current_app.config.get('JWT_SECRET_KEY')
        return jwt.encode(payload, secret, algorithm='HS256')

    @staticmethod
    def generate_reset_token(admin_id):
        """Génère un token sécurisé de réinitialisation de mot de passe (valable 1h)"""
        token_value = secrets.token_urlsafe(64)
        reset = ResetToken(
            admin_id=admin_id,
            token=token_value,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        return reset, token_value

    @staticmethod
    def validate_registration(data):
        """Valide les champs requis pour une inscription"""
        errors = {}
        if not data.get('username') or len(data['username']) < 3:
            errors['username'] = "Le nom d'utilisateur doit avoir au moins 3 caractères"

        if not data.get('email') or '@' not in data['email']:
            errors['email'] = "L'adresse email est invalide"

        if not data.get('password') or len(data['password']) < 8:
            errors['password'] = "Le mot de passe doit avoir au moins 8 caractères"

        return errors


def ForgotPassword():
    """
    Réinitialise le mot de passe d'un admin ou d'un utilisateur
    """
    try:
        data = request.get_json() or {}
        email = data.get('email')
        role = data.get('role', 'admin')
        new_password = data.get('new_password')  # Optionnel: si on fournit un nouveau mot de passe

        if not email:
            return {'status': 'error', 'message': 'Email requis'}, 400

        # Rechercher selon le rôle
        if role == 'admin':
            user = Admin.query.filter_by(email=email).first()
            if not user:
                return {'status': 'error', 'message': 'Aucun administrateur trouvé avec cet email'}, 404
        else:
            user = User.query.filter_by(email=email).first()
            if not user:
                return {'status': 'error', 'message': 'Aucun utilisateur trouvé avec cet email'}, 404

        # Générer un nouveau mot de passe
        if not new_password:
            new_password = secrets.token_urlsafe(10)

        # Hacher le nouveau mot de passe
        user.set_password(new_password)
        db.session.commit()

        return {
            'status': 'success',
            'message': f'Mot de passe réinitialisé avec succès pour {email}',
            'role': role,
            'new_password': new_password  # À supprimer en production (envoyer par email)
        }, 200

    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}, 500


def ResetPasswordWithToken():
    """
    Réinitialise le mot de passe avec un token de réinitialisation
    """
    try:
        data = request.get_json() or {}
        token = data.get('token')
        new_password = data.get('new_password')
        email = data.get('email')

        if not token or not new_password or not email:
            return {'status': 'error', 'message': 'Token, email et nouveau mot de passe requis'}, 400

        # Vérifier le token
        reset_token = ResetToken.query.filter_by(token=token).first()
        if not reset_token:
            return {'status': 'error', 'message': 'Token invalide'}, 400

        if reset_token.used:
            return {'status': 'error', 'message': 'Ce token a déjà été utilisé'}, 400

        if reset_token.expires_at < datetime.utcnow():
            return {'status': 'error', 'message': 'Ce token a expiré'}, 400

        # Trouver l'utilisateur (admin ou user)
        admin = Admin.query.filter_by(email=email).first()
        user = User.query.filter_by(email=email).first()

        if admin:
            admin.set_password(new_password)
            db.session.commit()
        elif user:
            user.set_password(new_password)
            db.session.commit()
        else:
            return {'status': 'error', 'message': 'Utilisateur non trouvé'}, 404

        # Marquer le token comme utilisé
        reset_token.used = True
        db.session.commit()

        return {
            'status': 'success',
            'message': 'Mot de passe réinitialisé avec succès'
        }, 200

    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}, 500


def GenerateResetToken(email, role='admin'):
    """
    Génère un token de réinitialisation pour un admin ou un utilisateur
    """
    try:
        if role == 'admin':
            user = Admin.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()

        if not user:
            return {'status': 'error', 'message': 'Utilisateur non trouvé'}, 404

        # Supprimer les anciens tokens non utilisés
        ResetToken.query.filter_by(admin_id=user.id, used=False).delete()

        # Générer un nouveau token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        reset_token = ResetToken(
            admin_id=user.id if role == 'admin' else None,
            token=token,
            expires_at=expires_at,
            used=False
        )

        db.session.add(reset_token)
        db.session.commit()

        # TODO: Envoyer l'email avec le lien
        reset_link = f"http://localhost:4200/reset-password/confirm?token={token}&email={email}"
        print(f"🔗 Lien de réinitialisation: {reset_link}")
        print(f"📝 Token: {token}")

        return {
            'status': 'success',
            'message': 'Email de réinitialisation envoyé',
            'reset_link': reset_link,  # Pour test (à supprimer en prod)
            'token': token  # Pour test (à supprimer en prod)
        }, 200

    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}, 500
