from flask_restful import Resource
from flask import request
from model.firdaws_db import User
from config.db import db


class UsersApi(Resource):

<<<<<<< HEAD
    # ================= GET =================
    def get(self, route=None, item_id=None):

        # GET ALL USERS
        if route == 'all':
            users = User.query.all()
            return {
                "status": "success",
                "users": [user.to_dict() for user in users],
                'data': [user.to_dict() for user in users]
            }, 200

        # GET SINGLE USER
        if item_id:
            user = User.query.get(item_id)
            if not user:
                return {
                    "status": "error",
                    'message': 'Utilisateur introuvable'
                }, 404

            return {
                "status": "success",
                "user": user.to_dict()
            }, 200

        return {
            "status": "error",
            'message': 'Route invalide'
        }, 404

    # ================= POST =================
    def post(self, route=None, item_id=None):
        data = request.get_json()

        # Vérification si l'utilisateur existe déjà
        if User.query.filter_by(email=data.get("email")).first():
            return {"status": "error", "message": "Cet email est déjà utilisé"}, 400
        if User.query.filter_by(username=data.get("username")).first():
            return {"status": "error", "message": "Ce nom d'utilisateur est déjà pris"}, 400
=======
    # ========== GET ==========
    def get(self, route=None, item_id=None):
        if route == 'all' or (route is None and item_id is None):
            users = User.query.all()
            return {
                'status': 'success',
                'users': [user.to_dict() for user in users],
                'data': [user.to_dict() for user in users]
            }, 200

        if item_id:
            user = User.query.get(item_id)
            if not user:
                return {'status': 'error', 'message': 'Utilisateur introuvable'}, 404
            return {'status': 'success', 'user': user.to_dict()}, 200

        return {'status': 'error', 'message': 'Route invalide'}, 404

    # ========== POST ==========
    def post(self, route=None, item_id=None):
        data = request.get_json() or {}

        if not data.get('email') or not data.get('username') or not data.get('password'):
            return {'status': 'error', 'message': 'Champs obligatoires manquants'}, 400

        if User.query.filter_by(email=data.get('email')).first():
            return {'status': 'error', 'message': 'Cet email est déjà utilisé'}, 400
        if User.query.filter_by(username=data.get('username')).first():
            return {'status': 'error', 'message': "Ce nom d'utilisateur est déjà pris"}, 400
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309

        user = User(
            username=data.get('username'),
            email=data.get('email'),
<<<<<<< HEAD
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone=data.get("phone"),
            role=data.get('role', 'user')
        )

        # Génère le password_hash avec bcrypt
=======
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role=data.get('role', 'user')
        )
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309
        user.set_password(data.get('password'))

        db.session.add(user)
        db.session.commit()

        return {
<<<<<<< HEAD
            "status": "success",
=======
            'status': 'success',
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309
            'message': 'Utilisateur créé',
            'data': user.to_dict()
        }, 201

<<<<<<< HEAD
    # ================= PUT =================
    def put(self, item_id=None, route=None):
        user = User.query.get(item_id)
        if not user:
            return {"status": "error", 'message': 'Utilisateur introuvable'}, 404

        data = request.get_json()

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.phone = data.get("phone", user.phone)
        user.role = data.get('role', user.role)

        if data.get('password'):
            # user.password = data.get("password")
=======
    # ========== PUT ==========
    def put(self, item_id=None, route=None):
        user = User.query.get(item_id)
        if not user:
            return {'status': 'error', 'message': 'Utilisateur introuvable'}, 404

        data = request.get_json() or {}

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.phone = data.get('phone', user.phone)
        user.role = data.get('role', user.role)

        if data.get('password'):
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309
            user.set_password(data.get('password'))

        db.session.commit()

        return {
<<<<<<< HEAD
            "status": "success",
=======
            'status': 'success',
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309
            'message': 'Utilisateur modifié',
            'data': user.to_dict()
        }, 200

<<<<<<< HEAD
    # ================= DELETE =================
    def delete(self, item_id=None, route=None):
        user = User.query.get(item_id)
        if not user:
            return {"status": "error", 'message': 'Utilisateur introuvable'}, 404
=======
    # ========== PATCH ==========
    def patch(self, item_id=None, route=None):
        return self.put(item_id=item_id, route=route)

    # ========== DELETE ==========
    def delete(self, item_id=None, route=None):
        user = User.query.get(item_id)
        if not user:
            return {'status': 'error', 'message': 'Utilisateur introuvable'}, 404
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309

        db.session.delete(user)
        db.session.commit()

<<<<<<< HEAD
        return {
            "status": "success",
            'message': 'Utilisateur supprimé'
        }, 200
=======
        return {'status': 'success', 'message': 'Utilisateur supprimé'}, 200
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309
