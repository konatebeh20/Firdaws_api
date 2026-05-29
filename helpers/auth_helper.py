from functools import wraps
from flask import request
import jwt
import bcrypt
from datetime import datetime, timedelta
from config.constant import Config
from logger.logger_config import get_logger

logger = get_logger()

# ========== FONCTIONS DE VÉRIFICATION ==========
def verify_token(token):
    """Vérifie et décode un token JWT"""
    try:
        secret = Config.JWT_SECRET_KEY
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("Token verification failed: Signature has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"Token verification failed: {str(e)}")
        return None

# ========== DÉCORATEURS ==========
def token_required(f):
    """Décorateur pour routes nécessitant un token user"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'Token manquant'}, 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return {'message': 'Token invalide ou expiré'}, 401
        
        from model.firdaws_db import User
        user = User.query.get(payload.get('user_id'))
        if not user or not user.is_active:
            return {'message': 'Utilisateur introuvable ou inactif'}, 401
        
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
        
        from model.firdaws_db import Admin
        admin = Admin.query.get(payload.get('admin_id'))
        if not admin or not admin.is_active:
            return {'message': 'Admin introuvable ou inactif'}, 401
        
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
        
        from model.firdaws_db import Admin
        admin = Admin.query.get(payload.get('admin_id'))
        if not admin or not admin.is_active:
            return {'message': 'Admin introuvable'}, 401
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

# ========== CLASSE AUTHHELPER ==========
class AuthHelper:
    """Helper pour les opérations d'authentification"""
    
    @staticmethod
    def hash_password(password):
        """Hache un mot de passe avec bcrypt"""
        rounds = Config.BCRYPT_ROUNDS
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(hashed_password, password):
        """Vérifie un mot de passe par rapport à son hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error checking password: {str(e)}")
            return False

    @staticmethod
    def generate_token(admin):
        """Génère un token JWT pour un admin"""
        expires = Config.JWT_ACCESS_TOKEN_EXPIRES
        payload = {
            'admin_id': admin.id,
            'email': admin.email,
            'role': admin.role,
            'exp': datetime.utcnow() + expires
        }
        secret = Config.JWT_SECRET_KEY
        return jwt.encode(payload, secret, algorithm='HS256')

    @staticmethod
    def validate_registration(data):
        """Valide les données d'inscription d'un admin"""
        errors = {}
        if not data.get('username') or len(data['username']) < 3:
            errors['username'] = "Le nom d'utilisateur doit avoir au moins 3 caractères"
        
        if not data.get('email') or '@' not in data['email']:
            errors['email'] = "L'adresse email est invalide"
            
        if not data.get('password') or len(data['password']) < 8:
            errors['password'] = "Le mot de passe doit avoir au moins 8 caractères"
            
        return errors

# from functools import wraps
# from flask import request
# import jwt
# from config.constant import Config
# from logger.logger_config import get_logger

# logger = get_logger()

# def verify_token(token):
#     """Vérifie et décode un token JWT"""
#     try:
#         secret = Config.JWT_SECRET_KEY
#         payload = jwt.decode(token, secret, algorithms=['HS256'])
#         return payload
#     except jwt.ExpiredSignatureError:
#         logger.debug("Token verification failed: Signature has expired")
#         return None
#     except jwt.InvalidTokenError as e:
#         logger.debug(f"Token verification failed: {str(e)}")
#         return None

# def token_required(f):
#     """Décorateur pour routes nécessitant un token user"""
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             # ⚠️ Retourner TUPLE (dict, status) - PAS jsonify()
#             return {'message': 'Token manquant'}, 401
        
#         token = auth_header.split(' ')[1]
#         payload = verify_token(token)
#         if not payload:
#             return {'message': 'Token invalide ou expiré'}, 401
        
#         from model.firdaws_db import User
#         user = User.query.get(payload.get('user_id'))
#         if not user or not user.is_active:
#             return {'message': 'Utilisateur introuvable ou inactif'}, 401
        
#         return f(*args, current_user=user, **kwargs)
#     return decorated

# def admin_required(f):
#     """Décorateur pour routes nécessitant un token admin"""
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             # ⚠️ Retourner TUPLE (dict, status) - PAS jsonify()
#             return {'message': 'Token admin manquant'}, 401
        
#         token = auth_header.split(' ')[1]
#         payload = verify_token(token)
#         if not payload:
#             return {'message': 'Token invalide ou expiré — veuillez vous reconnecter'}, 401
        
#         from model.firdaws_db import Admin
#         admin = Admin.query.get(payload.get('admin_id'))
#         if not admin or not admin.is_active:
#             return {'message': 'Admin introuvable ou inactif'}, 401
        
#         return f(*args, current_admin=admin, **kwargs)
#     return decorated

# def superadmin_required(f):
#     """Décorateur pour routes nécessitant un superadmin"""
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return {'message': 'Token superadmin manquant'}, 401
        
#         token = auth_header.split(' ')[1]
#         payload = verify_token(token)
#         if not payload:
#             return {'message': 'Token invalide ou expiré'}, 401
        
#         from model.firdaws_db import Admin
#         admin = Admin.query.get(payload.get('admin_id'))
#         if not admin or not admin.is_active:
#             return {'message': 'Admin introuvable'}, 401
#         if admin.role != 'superadmin':
#             return {'message': 'Droits superadmin requis'}, 403
        
#         return f(*args, current_admin=admin, **kwargs)
#     return decorated


# # from functools import wraps
# # from flask import request, jsonify, current_app
# # import jwt
# # import bcrypt
# # from datetime import datetime, timedelta
# # import secrets

# # from model.firdaws_db import Admin, ResetToken
# # from logger.logger_config import get_logger

# # from config.db import db

# # logger = get_logger()

# # def verify_token(token):
# #     """Vérifie et décode un token JWT"""
# #     try:
# #         secret = current_app.config.get('JWT_SECRET_KEY', 'nour-firdaws-2025-super-secret-key-change-in-production')
# #         payload = jwt.decode(token, secret, algorithms=['HS256'])
# #         return payload
# #     except Exception as e:
# #         logger.debug(f"Token verification failed: {str(e)}")
# #         return None

# # def token_required(f):
# #     """Décorateur pour vérifier le token JWT"""
# #     @wraps(f)
# #     def decorated(*args, **kwargs):
# #         token = None
# #         auth_header = request.headers.get('Authorization')
# #         if auth_header and auth_header.startswith('Bearer '):
# #             token = auth_header.split(' ')[1]
        
# #         if not token:
# #             return jsonify({'message': 'Token manquant!'}), 401
        
# #         payload = verify_token(token)
# #         if not payload:
# #             return jsonify({'message': 'Token invalide ou expiré!'}), 401
            
# #         from model.firdaws_db import Admin, User
# #         current_admin = None
        
# #         if 'admin_id' in payload:
# #             current_admin = Admin.query.get(payload['admin_id'])
# #         elif 'user_id' in payload:
# #             current_admin = User.query.get(payload['user_id'])
            
# #         if not current_admin:
# #             return jsonify({'message': 'Admin ou Utilisateur non trouvé!'}), 401
        
# #         if not current_admin.is_active:
# #             return jsonify({'message': 'Compte désactivé!'}), 403
            
# #         return f(current_admin, *args, **kwargs)
# #     return decorated

# # def admin_required(f):
# #     """Décorateur pour vérifier le rôle admin"""
# #     @wraps(f)
# #     @token_required
# #     def decorated(current_admin, *args, **kwargs):
# #         if current_admin.role not in ['admin', 'superadmin']:
# #             return jsonify({'message': 'Accès non autorisé!'}), 403
# #         return f(current_admin, *args, **kwargs)
# #     return decorated

# # def superadmin_required(f):
# #     """Décorateur pour vérifier le rôle superadmin"""
# #     @wraps(f)
# #     @token_required
# #     def decorated(current_admin, *args, **kwargs):
# #         if current_admin.role != 'superadmin':
# #             return jsonify({'message': 'Accès superadmin requis!'}), 403
# #         return f(current_admin, *args, **kwargs)
# #     return decorated

# # def honeypot_check(f):
# #     """Décorateur pour vérifier le honeypot anti-bot"""
# #     @wraps(f)
# #     def decorated(*args, **kwargs):
# #         data = request.get_json() if request.is_json else request.form
# #         if data:
# #             from helpers.honeypot_helper import HoneypotHelper
# #             is_bot, message, _ = HoneypotHelper.check_honeypot(data)
# #             if is_bot:
# #                 return jsonify({'message': message}), 400
# #         return f(*args, **kwargs)
# #     return decorated

# # class AuthHelper:
# #     """Helper pour les opérations d'authentification"""
    
# #     @staticmethod
# #     def hash_password(password):
# #         """Hache un mot de passe avec bcrypt"""
# #         rounds = current_app.config.get('BCRYPT_ROUNDS', 12)
# #         salt = bcrypt.gensalt(rounds=rounds)
# #         return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# #     @staticmethod
# #     def check_password(hashed_password, password):
# #         """Vérifie un mot de passe par rapport à son hash"""
# #         try:
# #             return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
# #         except Exception as e:
# #             logger.error(f"Error checking password: {str(e)}")
# #             return False

# #     @staticmethod
# #     def generate_token(admin):
# #         """Génère un token JWT pour un admin"""
# #         expires = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))
# #         payload = {
# #             'admin_id': admin.id,
# #             'email': admin.email,
# #             'role': admin.role,
# #             'exp': datetime.utcnow() + expires
# #         }
# #         secret = current_app.config.get('JWT_SECRET_KEY', 'nour-firdaws-2025-super-secret-key-change-in-production')
# #         return jwt.encode(payload, secret, algorithm='HS256')

# #     @staticmethod
# #     def validate_registration(data):
# #         """Valide les données d'inscription d'un admin"""
# #         errors = {}
# #         if not data.get('username') or len(data['username']) < 3:
# #             errors['username'] = "Le nom d'utilisateur doit avoir au moins 3 caractères"
        
# #         if not data.get('email') or '@' not in data['email']:
# #             errors['email'] = "L'adresse email est invalide"
            
# #         if not data.get('password') or len(data['password']) < 8:
# #             errors['password'] = "Le mot de passe doit avoir au moins 8 caractères"
            
# #         return errors
