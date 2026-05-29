import bcrypt
from datetime import timedelta
from flask import request
from config.db import db
from model.firdaws_db import *
from werkzeug.security import check_password_hash


def CreateAdmin():
    try:
        data = request.get_json() or {}

        if not data.get('email') or not data.get('username'):
            return {'status': 'error', 'error_description': 'Données incomplètes'}, 400

        existing = Admin.query.filter_by(email=data.get('email')).first()
        if existing:
            return {'status': 'error', 'error_description': 'Email déjà utilisé'}, 409

        new_admin = Admin(
            username=data.get('username'),
            email=data.get('email'),
            phone=data.get('phone', '00000000'),
            role=data.get('role', 'admin')
        )
        new_admin.set_password(data.get('password', 'changeme'))

        db.session.add(new_admin)
        db.session.commit()

        response['status'] = 'success'
        response['admin_info'] = new_admin.to_dict()
        return response, 201

    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'error_description': str(e)}, 500


def GetAllAdmin():
    response = {}
    try:
        all_admin = Admin.query.all()
        response['status'] = 'success'
        response['admin'] = [admin.to_dict() for admin in all_admin]
        return response, 200
    except Exception as e:
        return {'status': 'error', 'error_description': str(e)}, 500


def GetSingleAdmin():
    response = {}
    try:
        admin_id = request.json.get('admin_id') if request.is_json else None
        if not admin_id:
            return {'status': 'error', 'error_description': 'ID admin manquant'}, 400

        admin = Admin.query.get(admin_id)
        if admin:
            response['status'] = 'success'
            response['admin'] = admin.to_dict()
            return response, 200
        else:
            return {'status': 'error', 'error_description': 'Admin non trouvé'}, 404
    except Exception as e:
        return {'status': 'error', 'error_description': str(e)}, 500


def UpdateAdmin():
    response = {}
    try:
        data = request.get_json() or {}
        admin_id = data.get('admin_id')
        admin_to_update = Admin.query.get(admin_id)
        if not admin_to_update:
            return {'status': 'error', 'error_description': 'Admin non trouvé'}, 404

        admin_to_update.username = data.get('username', admin_to_update.username)
        admin_to_update.email = data.get('email', admin_to_update.email)
        admin_to_update.role = data.get('role', admin_to_update.role)

        if data.get('password'):
            admin_to_update.set_password(data['password'])

        db.session.commit()

        response['status'] = 'success'
        response['admin_infos'] = admin_to_update.to_dict()
        return response, 200
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'error_description': str(e)}, 500


def DeleteAdmin():
    response = {}
    try:
        data = request.get_json() if request.is_json else {}
        admin_id = data.get('admin_id')
        admin_to_delete = Admin.query.get(admin_id)
        if admin_to_delete:
            db.session.delete(admin_to_delete)
            db.session.commit()
            response['status'] = 'success'
            return response, 200
        else:
            return {'status': 'error', 'error_description': 'Admin non trouvé'}, 404
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'error_description': str(e)}, 500


def LoginAdmin():
    response = {}
    try:
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')

        admin = Admin.query.filter_by(email=email).first()
        if not admin:
            return {'status': 'error', 'message': 'Email ou mot de passe incorrect'}, 401

        if not admin.check_password(password):
            return {'status': 'error', 'message': 'Email ou mot de passe incorrect'}, 401

        if not admin.is_active:
            return {'status': 'error', 'message': 'Compte désactivé'}, 403

        token = admin.generate_token()

        response['status'] = 'success'
        response['admin_infos'] = admin.to_dict()
        response['access_token'] = token
        return response, 200

    except Exception as e:
        return {'status': 'error', 'error_description': str(e)}, 500
