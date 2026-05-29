from flask_restful import Resource
from flask import request
from helpers.dons import CreateManualDon, GetFinanceStats, GetDonationsByMonth, GetTopDonors
from model.firdaws_db import Dons
from config.db import db


class DonsAPI(Resource):

    # ========== GET ==========
    def get(self, route=None, item_id=None):
        if (route is None and item_id is None) or route in ['all', 'getall']:
            dons = Dons.query.order_by(Dons.created_at.desc()).limit(50).all()
            return {
                'status': 'success',
                'dons': [d.to_dict() for d in dons],
                'total': len(dons)
            }, 200

        if route == "getfinancestats":
            return GetFinanceStats(), 200
        if route in ["by-month", "getdonationsbymonth"]:
            return GetDonationsByMonth(), 200
        if route in ["top-donors", "gettopdonors"]:
            return GetTopDonors(), 200

        if item_id is not None:
            don = Dons.query.get(item_id)
            if not don:
                return {'status': 'error', 'message': 'Don introuvable'}, 404
            return {'status': 'success', 'don': don.to_dict()}, 200

        return {'message': 'Route non trouvée'}, 404

    # ========== POST ==========
    def post(self, route=None, item_id=None):
        if not route and not item_id:
            return CreateManualDon(), 201

        if route == "createdon":
            return CreateManualDon(), 201

        return {'message': 'Route non trouvée'}, 404

    # ========== PUT / PATCH ==========
    def put(self, route=None, item_id=None):
        return self.patch(route=route, item_id=item_id)

    def patch(self, route=None, item_id=None):
        if item_id is not None:
            don = Dons.query.get(item_id)
            if not don:
                return {'message': 'Don non trouvé'}, 404

            data = request.get_json() or {}

            if 'donateur' in data:
                don.donor_name = data['donateur']
            if 'phone' in data:
                don.phone = data['phone']
            if 'type' in data:
                don.type = data['type']
            if 'canal' in data:
                don.canal = data['canal']
            if 'montant' in data:
                don.amount = float(data['montant'])

            db.session.commit()
            return {'status': 'success', 'message': 'Don mis à jour avec succès'}, 200

        return {'message': 'Route non trouvée'}, 404

    # ========== DELETE ==========
    def delete(self, route=None, item_id=None):
        if route and route.isdigit():
            item_id = int(route)
            route = None

        if item_id and not route:
            don = Dons.query.get(item_id)
            if not don:
                return {'message': 'Dons non trouvé'}, 404

            db.session.delete(don)
            db.session.commit()
            return {'status': 'success', 'message': 'Enregistrement du don supprimé avec succès'}, 200

        return {'message': 'Route non trouvée'}, 404
