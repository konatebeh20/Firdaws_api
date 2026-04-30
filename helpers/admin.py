import bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
from flask import request, jsonify
from config.db import db
from model.flotys import *
from werkzeug.security import check_password_hash



def CreateAdmin():
    response = {}

    password_hash = request.json.get('password_hash')
    
    new_admin = Admin()
    new_admin.username = request.json.get('username')
    new_admin.password_hash = bcrypt.hashpw(password_hash.encode('utf-8'), bcrypt.gensalt())  # Assurez-vous de hacher le mot de passe
    new_admin.email = request.json.get('email')
    new_admin.role = request.json.get('role')
    new_admin.status = request.json.get('status')

    db.session.add(new_admin)
    db.session.commit()

    rs = {}
    rs['admin_id'] = new_admin.admin_id
    rs['username'] = new_admin.username
    rs['email'] = new_admin.email
    rs['role'] = new_admin.role
    rs['status'] = new_admin.status

    response['status'] = 'Success'
    response['admin_info'] = rs

    return response


def GetAllAdmin():
    response = {}
    try:
        all_admin = Admin.query.all()
        admin_info = []
        for admin in all_admin:
            info_admin = {
                'admin_id': admin.admin_id,
                'username': admin.username,
                'email': admin.email,
                'role': admin.role,
                'status': admin.status,
            }
            admin_info.append(info_admin)
        response['status'] = 'success'
        response['admin'] = admin_info

    except Exception as e:
        response['status'] = 'error'
        response['error_description'] = str(e)

    return response


def GetSingleAdmin():
    response = {}

    try:
        admin_id = request.json.get('admin_id')
        single_admin = Admin.query.filter_by(admin_id=admin_id).first()
        if single_admin:
            info_admin = {
                'admin_id': single_admin.admin_id,
                'username': single_admin.username,
                'email': single_admin.email,
                'role': single_admin.role,
                'status': single_admin.status,
            }
            response['status'] = 'success'
            response['admin'] = info_admin
        else:
            response['status'] = 'error'
            response['error_description'] = 'Admin not found'

    except Exception as e:
        response['status'] = 'error'
        response['error_description'] = str(e)

    return response


def UpdateAdmin():
    response = {}
    admin_id = request.json.get('admin_id')
    admin_to_update = Admin.query.filter_by(admin_id=admin_id).first()
    if admin_to_update:
        admin_to_update.username = request.json.get('username', admin_to_update.username)
        admin_to_update.password_hash = request.json.get('password_hash', admin_to_update.password_hash)  # Hachez le mot de passe si nécessaire
        admin_to_update.email = request.json.get('email', admin_to_update.email)
        admin_to_update.role = request.json.get('role', admin_to_update.role)
        admin_to_update.status = request.json.get('status', admin_to_update.status)

        db.session.commit()

        rs = {}
        rs['admin_id'] = admin_to_update.admin_id
        rs['username'] = admin_to_update.username
        rs['email'] = admin_to_update.email
        rs['role'] = admin_to_update.role
        rs['status'] = admin_to_update.status

        response['status'] = 'Success'
        response['admin_infos'] = rs
    else:
        response['status'] = 'error'
        response['error_description'] = 'Admin not found'

    return response


def DeleteAdmin():
    response = {}
    try:
        admin_id = request.json.get('admin_id')
        admin_to_delete = Admin.query.filter_by(admin_id=admin_id).first()
        if admin_to_delete:
            db.session.delete(admin_to_delete)
            db.session.commit()
            response['status'] = 'success'
        else:
            response['status'] = 'error'
            response['error_description'] = 'User not found'

    except Exception as e:
        response['error_description'] = str(e)
        response['status'] = 'error'

    return response


def LoginAdmin():
    reponse = {}
    try:
        email = request.json.get('email')
        password_hash = request.json.get('password_hash')
        login_admin = Admin.query.filter_by(email=email).first()
        admin_infos = {
            'admin_id': login_admin.admin_id,
            'username': login_admin.username,
            'email': login_admin.email,  
            'role': login_admin.role,  
            'status': login_admin.status,              
        }
        if login_admin and bcrypt.checkpw(password_hash.encode('utf-8'), login_admin.password_hash.encode('utf-8')):
            expires = timedelta(hours=1)
            access_token = create_access_token(identity=email)

            reponse['status'] = 'success'
            reponse['admin_infos'] = admin_infos
            reponse['access_token'] = access_token

        else:
            reponse['status'] = 'error'
            reponse['message'] = 'Invalid email or password'

    except Exception as e:
        reponse['error_description'] = str(e)
        reponse['status'] = 'error'

    return reponse
