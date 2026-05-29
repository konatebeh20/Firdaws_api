from flask_restful import Resource
from flask import request
from helpers.admin import CreateAdmin, GetAllAdmin, GetSingleAdmin, UpdateAdmin, DeleteAdmin, LoginAdmin
from model.firdaws_db import Admin
from config.db import db


class AdminsApi(Resource):

    # ========== GET ==========
    def get(self, route=None, item_id=None):
        if route in ['all', 'getall'] or (route is None and item_id is None):
            admins = Admin.query.all()
            return {
                'admins': [admin.to_dict() for admin in admins],
                'total': len(admins)
            }, 200

        if route == "getalladmin":
            return GetAllAdmin()

        if item_id is not None:
            admin = Admin.query.get(item_id)
            if not admin:
                return {'message': 'Admin non trouvé'}, 404
            return admin.to_dict(), 200

        return {'message': 'Route non trouvée'}, 404

    # ========== POST ==========
    def post(self, route=None, item_id=None):
        if not route and not item_id:
            data = request.get_json() or {}

            if not data.get('email') or not data.get('username'):
                return {'message': 'Données incomplètes (email/username requis)'}, 400

            existing = Admin.query.filter_by(email=data.get('email')).first()
            if existing:
                return {'message': 'Cet email existe déjà'}, 409

            admin = Admin(
                username=data.get('username'),
                email=data.get('email'),
                phone=data.get('phone', '00000000'),
                role=data.get('role', 'admin')
            )
            admin.set_password(data.get('password', 'changeme'))

            db.session.add(admin)
            db.session.commit()

            return {
                'admin': admin.to_dict(),
                'message': 'Administrateur créé avec succès'
            }, 201

        if route == "createadmin":
            return CreateAdmin()
        if route == "loginadmin":
            return LoginAdmin()

        return {'message': 'Route non trouvée'}, 404

    # ========== PUT / PATCH ==========
    def put(self, route=None, item_id=None):
        return self.patch(route=route, item_id=item_id)

    def patch(self, route=None, item_id=None):
        if route == "updateadmin":
            return UpdateAdmin()
        return {'message': 'Route non trouvée'}, 404

    # ========== DELETE ==========
    def delete(self, route=None, item_id=None):
        if route and route.isdigit():
            item_id = int(route)
            route = None

        if item_id and not route:
            admin = Admin.query.get(item_id)
            if not admin:
                return {'message': 'Admin non trouvé'}, 404

            if admin.role == 'superadmin':
                superadmin_count = Admin.query.filter_by(role='superadmin').count()
                if superadmin_count <= 1:
                    return {'message': 'Impossible de supprimer le dernier super administrateur'}, 400

            db.session.delete(admin)
            db.session.commit()
            return {'message': 'Administrateur supprimé avec succès'}, 200

        if route == "deleteadmin":
            return DeleteAdmin()

        return {'message': 'Route non trouvée'}, 404
