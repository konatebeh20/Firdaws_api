from functools import wraps
from flask import request, jsonify
import jwt
from config.constant import Config
from model.firdaws_db import Admin
from logger.logger_config import get_logger
from config.db import db

logger = get_logger()

def token_required(f):
    """Décorateur pour vérifier le token JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Récupérer le token du header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token manquant!'}), 401
        
        try:
            # Décoder le token
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_admin = Admin.query.filter_by(id=data['admin_id']).first()
            
            if not current_admin:
                return jsonify({'message': 'Admin non trouvé!'}), 401
            
            if not current_admin.is_active:
                return jsonify({'message': 'Compte désactivé!'}), 403
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expiré!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalide!'}), 401
        
        return f(current_admin, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Décorateur pour vérifier le rôle admin"""
    @wraps(f)
    @token_required
    def decorated(current_admin, *args, **kwargs):
        if current_admin.role not in ['admin', 'superadmin']:
            return jsonify({'message': 'Accès non autorisé!'}), 403
        return f(current_admin, *args, **kwargs)
    return decorated

def superadmin_required(f):
    """Décorateur pour vérifier le rôle superadmin"""
    @wraps(f)
    @token_required
    def decorated(current_admin, *args, **kwargs):
        if current_admin.role != 'superadmin':
            return jsonify({'message': 'Accès superadmin requis!'}), 403
        return f(current_admin, *args, **kwargs)
    return decorated

def honeypot_check(f):
    """Décorateur pour vérifier le honeypot anti-bot"""
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json() if request.is_json else request.form
        
        # Vérifier si le champ honeypot est rempli (bot)
        if data and data.get('honeypot'):
            logger.warning(f"🚨 Honeypot déclenché - IP: {request.remote_addr}")
            return jsonify({'message': 'Bot détecté!'}), 400
        
        return f(*args, **kwargs)
    return decorated