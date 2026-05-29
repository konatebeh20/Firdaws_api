import bcrypt
# from flask_jwt_extended import create_access_token
from datetime import timedelta
from flask import request
from config.db import db
from model.firdaws_db import User

def CreateUser():
    response = {}
    try:
        data = request.get_json() or {}
        password = data.get('password')

        # Vérification des champs requis
        if not data.get('username') or not data.get('email') or not password:
            return {'status': 'error', 'error_description': 'Champs obligatoires manquants'}, 400

        # Vérification si l'utilisateur existe déjà
        if User.query.filter_by(email=data.get('email')).first():
            return {'status': 'error', 'error_description': 'Cet email est déjà utilisé'}, 400

        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            # password=password,  # Mot de passe en clair (selon ton modèle)
            password_hash= '',  # Le hash sera généré par la méthode set_password
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role=data.get('role', 'user')  # Par défaut 'user' pour l'espace public
        )
        
        # Génération du password_hash via la méthode du modèle
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        response['status'] = 'success'
        response['message'] = 'Utilisateur créé avec succès'
        response['user_info'] = new_user.to_dict()
        return response, 201

    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'error_description': str(e)}, 500


def GetAllUsers():
    response = {}
    try:
        all_users = User.query.all()
        users_list = [user.to_dict() for user in all_users]
        
        response['status'] = 'success'
        response['users'] = users_list
        response['data'] = users_list  # Double sécurité pour l'intégration Angular
        return response, 200
    except Exception as e:
        return {'status': 'error', 'error_description': str(e)}, 500


def GetSingleUser(user_id=None):
    response = {}
    try:
        # Récupération depuis les arguments de l'URL ou du JSON
        id_to_find = user_id or request.json.get('user_id') if request.is_json else None
        
        if not id_to_find:
            return {'status': 'error', 'error_description': 'ID utilisateur manquant'}, 400

        user = User.query.get(id_to_find)
        if user:
            response['status'] = 'success'
            response['user'] = user.to_dict()
            return response, 200
        else:
            return {'status': 'error', 'error_description': 'Utilisateur introuvable'}, 404
    except Exception as e:
        return {'status': 'error', 'error_description': str(e)}, 500


def UpdateUser(user_id=None):
    response = {}
    try:
        data = request.get_json() or {}
        id_to_update = user_id or data.get('user_id')
        
        user_to_update = User.query.get(id_to_update)
        if not user_to_update:
            return {'status': 'error', 'error_description': 'Utilisateur introuvable'}, 404

        # Mise à jour des champs s'ils sont fournis
        user_to_update.username = data.get('username', user_to_update.username)
        user_to_update.email = data.get('email', user_to_update.email)
        user_to_update.first_name = data.get('first_name', user_to_update.first_name)
        user_to_update.last_name = data.get('last_name', user_to_update.last_name)
        user_to_update.phone = data.get('phone', user_to_update.phone)
        user_to_update.role = data.get('role', user_to_update.role)

        # Si le mot de passe change, on met à jour le hash
        if data.get('password'):
            user_to_update.set_password(data.get('password'))

        db.session.commit()

        response['status'] = 'success'
        response['message'] = 'Utilisateur mis à jour'
        response['user_info'] = user_to_update.to_dict()
        return response, 200
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'error_description': str(e)}, 500


def DeleteUser(user_id=None):
    response = {}
    try:
        data = request.get_json() if request.is_json else {}
        id_to_delete = user_id or data.get('user_id')

        user_to_delete = User.query.get(id_to_delete)
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            response['status'] = 'success'
            response['message'] = 'Utilisateur supprimé'
            return response, 200
        else:
            return {'status': 'error', 'error_description': 'Utilisateur introuvable'}, 404
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'error_description': str(e)}, 500


def LoginUser():
    response = {}
    try:
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        # Utilisation de la méthode check_password native de ton modèle User
        if user and user.check_password(password):
            if not user.is_active:
                return {'status': 'error', 'message': 'Ce compte est désactivé'}, 403

            user_infos = user.to_dict()
            
            # Use the new JWT system from the model
            token = user.generate_token()

            response['status'] = 'success'
            response['user_infos'] = user_infos
            response['access_token'] = token
            return response, 200
        else:
            return {'status': 'error', 'message': 'Email ou mot de passe incorrect'}, 401

    except Exception as e:
        return {'status': 'error', 'error_description': str(e)}, 500