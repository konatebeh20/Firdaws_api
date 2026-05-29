import bcrypt
# from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
from flask import request, jsonify
from config.db import db
from model.firdaws_db import *
from werkzeug.security import check_password_hash



def CreateAdmin():
    response = {}

    password = request.json.get('password')
    
    new_admin = Admin()
    new_admin.username = request.json.get('username')
    new_admin.email = request.json.get('email')
    new_admin.phone = request.json.get('phone', '00000000')
    new_admin.role = request.json.get('role', 'admin')
    new_admin.set_password(password)

    db.session.add(new_admin)
    db.session.commit()

    rs = {}
    rs['admin_id'] = new_admin.id
    rs['username'] = new_admin.username
    rs['email'] = new_admin.email
    rs['role'] = new_admin.role
    rs['status'] = 'active' if new_admin.is_active else 'inactive'

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
                'admin_id': admin.id,
                'username': admin.username,
                'email': admin.email,
                'role': admin.role,
                'status': 'active' if admin.is_active else 'inactive',
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
        single_admin = Admin.query.filter_by(id=admin_id).first()
        if single_admin:
            info_admin = {
                'admin_id': single_admin.id,
                'username': single_admin.username,
                'email': single_admin.email,
                'role': single_admin.role,
                'status': 'active' if single_admin.is_active else 'inactive',
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
    admin_to_update = Admin.query.filter_by(id=admin_id).first()
    if admin_to_update:
        admin_to_update.username = request.json.get('username', admin_to_update.username)
        admin_to_update.email = request.json.get('email', admin_to_update.email)
        admin_to_update.role = request.json.get('role', admin_to_update.role)
        admin_to_update.phone = request.json.get('phone', admin_to_update.phone)
        
        if request.json.get('password'):
            admin_to_update.set_password(request.json.get('password'))

        db.session.commit()

        rs = {}
        rs['admin_id'] = admin_to_update.id
        rs['username'] = admin_to_update.username
        rs['email'] = admin_to_update.email
        rs['role'] = admin_to_update.role
        rs['status'] = 'active' if admin_to_update.is_active else 'inactive'

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
        admin_to_delete = Admin.query.filter_by(id=admin_id).first()
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
        password = request.json.get('password')
        login_admin = Admin.query.filter_by(email=email).first()

        
        if login_admin and login_admin.check_password(password):
            admin_infos = {
                'admin_id': login_admin.id,
                'username': login_admin.username,
                'email': login_admin.email,  
                'role': login_admin.role,  
                'status': 'active' if login_admin.is_active else 'inactive',              
            }

            # Use the new JWT system from the model
            token = login_admin.generate_token()

            reponse['status'] = 'success'
            reponse['admin_infos'] = admin_infos
            reponse['access_token'] = token

        else:
            reponse['status'] = 'error'
            reponse['message'] = 'Invalid email or password'

    except Exception as e:
        reponse['error_description'] = str(e)
        reponse['status'] = 'error'

    return reponse
