from functools import wraps
from flask import request, current_app
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
import secrets

from model.firdaws_db import Admin, User, ResetToken
from logger.logger_config import get_logger

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
<<<<<<< HEAD
        
=======

>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return {'message': 'Token invalide ou expiré'}, 401
<<<<<<< HEAD
        
        # On récupère l'utilisateur classique via l'ID présent dans le token
        user_id = payload.get('user_id')
        if not user_id:
            return {'message': 'Token invalide pour un utilisateur'}, 401
=======

        current_account = None
        if 'admin_id' in payload:
            current_account = Admin.query.get(payload['admin_id'])
        elif 'user_id' in payload:
            current_account = User.query.get(payload['user_id'])
>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c

        user = User.query.get(user_id)
        if not user:
            return {'message': 'Compte non trouvé'}, 401

        if not user.is_active:
            return {'message': 'Compte désactivé'}, 403

        return f(*args, current_user=user, **kwargs)
    return decorated


def admin_required(f):
<<<<<<< HEAD
    """Décorateur pour routes nécessitant un rôle Admin ou Superadmin"""
=======
    """Décorateur pour routes nécessitant un token admin"""
>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'Token admin manquant'}, 401
<<<<<<< HEAD
        
=======

>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return {'message': 'Token invalide ou expiré — veuillez vous reconnecter'}, 401
<<<<<<< HEAD
        
        admin_id = payload.get('admin_id')
        if not admin_id:
            return {'message': 'Token invalide pour un administrateur'}, 401

        admin = Admin.query.get(admin_id)
=======

        admin = Admin.query.get(payload.get('admin_id'))
>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c
        if not admin or not admin.is_active:
            return {'message': 'Admin introuvable ou inactif'}, 401

        # Sécurité : On vérifie que le rôle est bien autorisé
        if admin.role not in ['admin', 'superadmin']:
<<<<<<< HEAD
            return {'message': 'Accès restreint aux administrateurs'}, 403
=======
            return {'message': 'Accès non autorisé'}, 403
>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c

        return f(*args, current_admin=admin, **kwargs)
    return decorated


def superadmin_required(f):
<<<<<<< HEAD
    """Décorateur pour routes nécessitant strictement un superadmin"""
=======
    """Décorateur pour routes nécessitant un superadmin"""
>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'Token superadmin manquant'}, 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return {'message': 'Token invalide ou expiré'}, 401
<<<<<<< HEAD
        
        admin_id = payload.get('admin_id')
        admin = Admin.query.get(admin_id) if admin_id else None
        
=======

        admin = Admin.query.get(payload.get('admin_id'))
>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c
        if not admin or not admin.is_active:
            return {'message': 'Admin introuvable ou inactif'}, 401
            
        if admin.role != 'superadmin':
            return {'message': 'Droits superadmin requis'}, 403
<<<<<<< HEAD
            
=======

>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c
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
<<<<<<< HEAD
        """Hache un mot de passe de manière sécurisée avec bcrypt"""
        try:
            rounds = current_app.config.get('BCRYPT_ROUNDS', 12)
            salt = bcrypt.gensalt(rounds=rounds)
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except Exception as e:
            logger.error(f"Erreur lors du hachage du mot de passe: {str(e)}")
            return None

    @staticmethod
    def check_password(hashed_password, password):
        """Vérifie un mot de passe par rapport à sa version hachée"""
=======
        """Hache un mot de passe avec bcrypt"""
        rounds = current_app.config.get('BCRYPT_ROUNDS', 12)
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(hashed_password, password):
        """Vérifie un mot de passe par rapport à son hash"""
>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c
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

<<<<<<< HEAD
        return errors
=======
        return errors
>>>>>>> 4bda93c1b4226b5530e350945aec7583b717078c
