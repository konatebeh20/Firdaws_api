from flask_restful import Resource
from flask import request, jsonify, current_app
from model.firdaws_db import User, Admin, ResetToken
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import AuthHelper, token_required, superadmin_required, honeypot_check, verify_token
from helpers.validation_helper import ValidationHelper
from helpers.error_helper import log_error
from datetime import datetime

logger = get_logger()

class AuthApi(Resource):
    """Resource unique pour TOUS les endpoints d'authentification"""
    
    def get_current_admin(self):
        """R\u00e9cup\u00e8re l'admin si token pr\u00e9sent"""
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
        """Route GET dynamique unique"""
        try:
            current_admin = self.get_current_admin()
            
            # 1. GET /api/auth/profile
            if route == 'profile':
                if not current_admin:
                    return {'message': 'Authentification requise'}, 401
                return current_admin.to_dict(), 200
            
            # 2. GET /api/auth/verify (test de validité du token)
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
        """Route POST dynamique unique"""
        try:
            data = request.get_json()
            
            # 1. POST /api/auth/register
            if route == 'register':
                logger.info(f"📝 Register attempt: {data.get('email', 'no email')}")

                # Validation des champs requis
                required_fields = ['username', 'email', 'password']
                missing_fields = [f for f in required_fields if not data.get(f)]
                if missing_fields:
                    logger.warning(f"❌ Register failed - missing fields: {missing_fields}")
                    return {'message': f'Champs requis manquants: {", ".join(missing_fields)}'}, 400

                # Validation email
                if not ValidationHelper.validate_email(data['email']):
                    logger.warning(f"❌ Register failed - invalid email: {data['email']}")
                    return {'message': 'Format email invalide'}, 400

                # Validation mot de passe
                is_valid, password_errors = ValidationHelper.validate_password(data['password'])
                if not is_valid:
                    logger.warning(f"❌ Register failed - weak password: {password_errors}")
                    return {'message': 'Mot de passe trop faible', 'errors': password_errors}, 400

                # Vérifier si email déjà utilisé dans les utilisateurs
                if User.query.filter_by(email=data['email']).first():
                    logger.warning(f"❌ Register failed - email already exists: {data['email']}")
                    return {'message': 'Cet email est déjà utilisé'}, 409

                # Crée un utilisateur normal par défaut. Si un rôle admin est explicitement demandé,
                # on pourra étendre cette logique plus tard.
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
                logger.info(f"✅ Nouvel utilisateur créé: {data['email']}")

                return {'data': user.to_dict(), 'message': 'Compte créé avec succès'}, 201

            # 2. POST /api/auth/login
            if route == 'login':
                email = data.get('email')
                password = data.get('password')
                logger.info(f"Login attempt for: {email}")

                if not email or not password:
                    logger.warning(f"Login failed - missing email or password")
                    return {'message': 'Email et mot de passe requis'}, 400

                account = User.query.filter_by(email=email).first()
                if not account:
                    account = Admin.query.filter_by(email=email).first()

                if not account:
                    logger.warning(f"Login failed - no account found for email: {email}")
                    return {'message': 'Email ou mot de passe incorrect'}, 401

                logger.info(f"Account found: {account.email}, checking password...")
                if not account.check_password(password):
                    logger.warning(f"Login failed - invalid password for: {email}")
                    return {'message': 'Email ou mot de passe incorrect'}, 401

                logger.info(f"Password valid for: {email}")

                if not account.is_active:
                    logger.warning(f"Login failed - account disabled: {email}")
                    return {'message': 'Compte désactivé'}, 403

                account.last_login = datetime.utcnow()
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
                # La déconnexion est principalement gérée côté client (suppression token)
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
                
                if not reset or reset.expires_at < datetime.utcnow():
                    return {'message': 'Token invalide ou expiré'}, 400
                
                admin = Admin.query.get(reset.admin_id)
                admin.password_hash = AuthHelper.hash_password(new_password)
                reset.used = True
                db.session.commit()
                return {'message': 'Mot de passe réinitialisé'}, 200

            return {'message': 'Route non trouvée'}, 404

        except Exception as e:
            log_error(e, request, 'AuthApi.post')
            db.session.rollback()
            return {'message': 'Erreur serveur'}, 500

    # ========== PUT ==========
    @token_required
    def put(self, current_admin, route=None, item_id=None):
        """Route PUT dynamique unique"""
        try:
            # 1. PUT /api/auth/profile
            if route == 'profile':
                data = request.get_json()
                if 'username' in data: current_admin.username = data['username']
                if 'phone' in data: current_admin.phone = data['phone']
                if 'password' in data: current_admin.password_hash = AuthHelper.hash_password(data['password'])
                
                db.session.commit()
                return {'data': current_admin.to_dict(), 'message': 'Profil mis à jour'}, 200
                
            return {'message': 'Route non trouvée'}, 404

        except Exception as e:
            log_error(e, request, 'AuthApi.put')
            db.session.rollback()
            return {'message': 'Erreur serveur'}, 500
