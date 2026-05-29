from flask_restful import Resource
from flask import request
from model.firdaws_db import Dons
from config.db import db


class DonsAPI(Resource):

    # ========== GET ==========
    def get(self, route=None, item_id=None):
        if route == 'all' or (route is None and item_id is None):
            dons = Dons.query.order_by(Dons.created_at.desc()).all()
            return {
                'status': 'success',
                'dons': [don.to_dict() for don in dons],
                'total': len(dons)
            }, 200

        if item_id:
            don = Dons.query.get(item_id)
            if not don:
                return {'status': 'error', 'message': 'Don introuvable'}, 404
            return {'status': 'success', 'don': don.to_dict()}, 200

        return {'status': 'error', 'message': 'Route invalide'}, 404

    # ========== POST ==========
    def post(self, route=None, item_id=None):
        data = request.get_json() or {}

        if not data.get('donor_name') or not data.get('amount'):
            return {'status': 'error', 'message': 'Nom du donateur et montant requis'}, 400

        don = Dons(
            donor_name=data.get('donor_name'),
            type=data.get('type', 'Sadaqah'),
            purpose=data.get('purpose'),
            amount=float(data.get('amount')),
            canal=data.get('canal', 'Physique'),
            transaction_ref=data.get('transaction_ref'),
            payment_method=data.get('payment_method'),
            phone=data.get('phone'),
            note=data.get('note'),
            is_anonymous=data.get('is_anonymous', False),
            user_id=data.get('user_id')
        )

        db.session.add(don)
        db.session.commit()

        return {
            'status': 'success',
            'message': 'Don enregistré avec succès',
            'don': don.to_dict()
        }, 201

    # ========== PUT ==========
    def put(self, item_id=None, route=None):
        don = Dons.query.get(item_id)
        if not don:
            return {'status': 'error', 'message': 'Don introuvable'}, 404

        data = request.get_json() or {}

        don.donor_name = data.get('donor_name', don.donor_name)
        don.type = data.get('type', don.type)
        don.purpose = data.get('purpose', don.purpose)
        don.amount = float(data.get('amount', don.amount))
        don.canal = data.get('canal', don.canal)
        don.phone = data.get('phone', don.phone)
        don.note = data.get('note', don.note)
        don.status = data.get('status', don.status)

        db.session.commit()

        return {
            'status': 'success',
            'message': 'Don modifié',
            'don': don.to_dict()
        }, 200

    # ========== PATCH ==========
    def patch(self, item_id=None, route=None):
        return self.put(item_id=item_id, route=route)

    # ========== DELETE ==========
    def delete(self, item_id=None, route=None):
        don = Dons.query.get(item_id)
        if not don:
            return {'status': 'error', 'message': 'Don introuvable'}, 404

        db.session.delete(don)
        db.session.commit()

        return {'status': 'success', 'message': 'Don supprimé'}, 200
