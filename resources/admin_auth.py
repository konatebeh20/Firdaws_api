from flask_restful import Resource
from flask import request
from model.firdaws_db import User, Admin, ResetToken
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import AuthHelper, token_required, admin_required, superadmin_required, honeypot_check, verify_token
from helpers.validation_helper import ValidationHelper
from helpers.error_helper import log_error
from datetime import datetime, timezone

logger = get_logger()


class AuthApi(Resource):
    """Resource unique pour TOUS les endpoints d'authentification"""

    def get_current_admin(self):
        """Récupère l'admin ou user connecté via le token"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if payload:
                if 'admin_id' in payload:
                    return Admin.query.get(payload['admin_id'])
                elif 'user_id' in payload:
                    return User.query.get(payload['user_id'])
        return None

    # ========== GET ==========
    def get(self, route=None, item_id=None):
        try:
            current_admin = self.get_current_admin()

            if route == 'profile':
                if not current_admin:
                    return {'message': 'Authentification requise'}, 401
                return current_admin.to_dict(), 200

            if route == 'verify':
                if not current_admin:
                    return {'valid': False}, 401
                return {'valid': True, 'admin': current_admin.to_dict()}, 200

            return {'message': 'Route non trouvée'}, 404

        except Exception as e:
            log_error(e, request, 'AuthApi.get')
            return {'message': 'Erreur serveur'}, 500

    # ========== POST ==========
    @honeypot_check
    def post(self, route=None, item_id=None):
        try:
            data = request.get_json()

            # 1. POST /api/auth/register
            if route == 'register':
                logger.info(f"Register attempt: {data.get('email', 'no email')}")

                required_fields = ['username', 'email', 'password']
                missing_fields = [f for f in required_fields if not data.get(f)]
                if missing_fields:
                    return {'message': f'Champs requis manquants: {", ".join(missing_fields)}'}, 400

                if not ValidationHelper.validate_email(data['email']):
                    return {'message': 'Format email invalide'}, 400

                is_valid, password_errors = ValidationHelper.validate_password(data['password'])
                if not is_valid:
                    return {'message': 'Mot de passe trop faible', 'errors': password_errors}, 400

                if User.query.filter_by(email=data['email']).first():
                    return {'message': 'Cet email est déjà utilisé'}, 409
                if Admin.query.filter_by(email=data['email']).first():
                    return {'message': 'Cet email est déjà utilisé'}, 409

                user = User(
                    username=data['username'],
                    email=data['email'],
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    phone=data.get('phone'),
                    role='user'
                )
                user.set_password(data['password'])

                db.session.add(user)
                db.session.commit()
                logger.info(f"Nouvel utilisateur créé: {data['email']}")

                return {'data': user.to_dict(), 'message': 'Compte créé avec succès'}, 201

            # 2. POST /api/auth/login
            if route == 'login':
                email = data.get('email')
                password = data.get('password')
                logger.info(f"Login attempt for: {email}")

                if not email or not password:
                    return {'message': 'Email et mot de passe requis'}, 400

                account = Admin.query.filter_by(email=email).first()
                if not account:
                    account = User.query.filter_by(email=email).first()

                if not account:
                    logger.warning(f"Login failed - no account found for: {email}")
                    return {'message': 'Email ou mot de passe incorrect'}, 401

                if not account.check_password(password):
                    logger.warning(f"Login failed - invalid password for: {email}")
                    return {'message': 'Email ou mot de passe incorrect'}, 401

                if not account.is_active:
                    return {'message': 'Compte désactivé'}, 403

                account.last_login = datetime.now(timezone.utc)
                db.session.commit()

                token = account.generate_token()
                logger.info(f"Login successful for: {email}")
                return {
                    'message': 'Connexion réussie',
                    'token': token,
                    'user': account.to_dict()
                }, 200

            # 3. POST /api/auth/logout
            if route == 'logout':
                return {'message': 'Déconnexion réussie'}, 200

            # 4. POST /api/auth/forgot_password
            if route == 'forgot_password':
                email = data.get('email')
                admin = Admin.query.filter_by(email=email).first()
                if not admin:
                    return {'message': 'Aucun compte trouvé'}, 404

                reset, token = AuthHelper.generate_reset_token(admin.id)
                db.session.add(reset)
                db.session.commit()
                return {'message': 'Email envoyé', 'reset_token': token}, 200

            # 5. POST /api/auth/reset_password
            if route == 'reset_password':
                token = data.get('token')
                new_password = data.get('password')
                reset = ResetToken.query.filter_by(token=token, used=False).first()

                if not reset or reset.expires_at < datetime.now(timezone.utc):
                    return {'message': 'Token invalide ou expiré'}, 400

                admin = Admin.query.get(reset.admin_id)
                admin.set_password(new_password)
                reset.used = True
                db.session.commit()
                return {'message': 'Mot de passe réinitialisé'}, 200

            return {'message': 'Route non trouvée'}, 404

        except Exception as e:
            log_error(e, request, 'AuthApi.post')
            db.session.rollback()
            return {'message': 'Erreur serveur'}, 500

    # ========== PUT ==========
    def put(self, route=None, item_id=None):
        try:
            current_account = self.get_current_admin()
            if not current_account:
                return {'message': 'Token invalide ou expiré'}, 401

            if route == 'profile':
                data = request.get_json()
                if 'username' in data:
                    current_account.username = data['username']
                if 'phone' in data:
                    current_account.phone = data['phone']
                if 'password' in data:
                    current_account.set_password(data['password'])

                db.session.commit()
                return {'data': current_account.to_dict(), 'message': 'Profil mis à jour'}, 200

            return {'message': 'Route non trouvée'}, 404

        except Exception as e:
            log_error(e, request, 'AuthApi.put')
            db.session.rollback()
            return {'message': 'Erreur serveur'}, 500
