from flask_restful import Resource
from flask import request
from helpers.dons import CreateManualDon, GetFinanceStats, GetDonationsByMonth, GetTopDonors
from model.firdaws_db import Dons
from config.db import db

class DonsAPI(Resource):
    
    # ========== GET ==========
    def get(self, route=None, item_id=None):
        # Si appel standard à la racine /api/dons -> Historique global des transactions
        # GET ALL - /api/dons ou /api/dons/all
        if (route is None and item_id is None) or route in ['all', 'getall']:
            dons = Dons.query.order_by(Dons.created_at.desc()).limit(50).all()
            
            # Convertir les données pour le frontend
            dons_list = []
            for d in dons:
                dons_list.append({
                    'id': d.id,
                    'donateur': d.donor_name,
                    'phone': d.phone,
                    'type': d.type,
                    'montant': d.amount,
                    'canal': d.canal,
                    'status': d.status,
                    'date': d.created_at.isoformat() if d.created_at else None
                })
            
            
            return {
                'status': 'success',
                # 'dons': [d.to_dict() for d in dons] if hasattr(Dons, 'to_dict') else [],
                'dons': dons_list,
                'total': len(dons_list)
            }, 200
            
        if route == "getfinancestats":
            return GetFinanceStats(), 200
        if route in ["by-month", "getdonationsbymonth"]:
            return GetDonationsByMonth(), 200
        # if route == "by-month" or route == "getdonationsbymonth":
        #     return GetDonationsByMonth(), 200
        if route in ["top-donors", "gettopdonors"]:
            return GetTopDonors(), 200
        # if route == "top-donors" or route == "gettopdonors":
        #     return GetTopDonors(), 200
        
        # GET SINGLE DONATION BY ID
        if item_id is not None:
            don = Dons.query.get(item_id)
            if not don:
                return {'status': 'error', 'message': 'Don introuvable'}, 404
            return {
                'status': 'success', 
                'don': {
                    'id': don.id,
                    'donateur': don.donor_name,
                    'phone': don.phone,
                    'type': don.type,
                    'montant': don.amount,
                    'canal': don.canal,
                    'status': don.status,
                    'date': don.created_at.isoformat() if don.created_at else None
                }
                # don.to_dict() if hasattr(don, 'to_dict') else {}
            }, 200
            
        return {'message': 'Route non trouvée'}, 404

    # ========== POST ==========
    def post(self, route=None, item_id=None):
        # POST à la racine /api/dons sans route explicite
        if not route and not item_id:
            return CreateManualDon(), 201
            
        # POST avec route explicite comme ton format 'createadmin'
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
            
            
            # # Mise à jour partielle dynamique
            # don.donateur = data.get('donateur', don.donateur)
            # don.phone = data.get('phone', don.phone)
            # don.type = data.get('type', don.type)
            # don.canal = data.get('canal', don.canal)
            # if data.get('montant'):
            #     don.montant = float(data.get('montant'))

            db.session.commit()
            return {'status': 'success', 'message': 'Don mis à jour avec succès'}, 200
            
        return {'message': 'Route non trouvée'}, 404

    # ========== DELETE ==========
    def delete(self, route=None, item_id=None):
        # Réalignement si l'identifiant est passé dans la variable route (ex: /api/dons/12)
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