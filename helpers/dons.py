from model.firdaws_db import Dons  # Modèle importé depuis ton fichier unique
from config.db import db
from sqlalchemy import func
from flask import request

def CreateManualDon():
    response = {}
    try:
        data = request.get_json() or {}
        montant = data.get('montant')
        donateur = data.get('donateur', '').strip()
        type_don = data.get('type', 'Sadaqah')
        canal = data.get('canal', 'Physique')
        
        if not montant or float(montant) <= 0:
            response['status'] = 'error'
            response['error_description'] = 'Le montant doit être supérieur à 0.'
            return response
        
        # Création du don avec les bons noms de champs
        new_don = Dons(
            donor_name=donateur if donateur else 'Anonyme', 
            #donateur=data.get('donateur', '').strip() or None, 
            amount=float(montant), 
            #phone=data.get('phone'),
            type=type_don, 
            #type=data.get('type', 'Sadaqah'),
            # montant=float(montant),
            canal=canal, 
            # canal=data.get('canal', 'Physique'),
            status='completed'
        )
        # Ajouter le téléphone si présent
        if data.get('phone'):
            
            new_don.phone = data.get('phone')
            
        db.session.add(new_don)
        db.session.commit()
        
        # Préparer la réponse avec les bons champs pour le frontend
        response['status'] = 'success'
        response['message'] = 'Dons enregistré avec succès !'
        response['don'] = new_don.to_dict() if hasattr(new_don, 'to_dict') else {
            'id': new_don.id,
            'donateur': new_don.donor_name,
            'phone': new_don.phone,
            'type': new_don.type,
            'montant': new_don.amount,
            'canal': new_don.canal,
            'status': new_don.status,
            'date': new_don.created_at.isoformat() if new_don.created_at else None,
        }
    except Exception as e:
        db.session.rollback()
        response['status'] = 'error'
        response['error_description'] = str(e)
        
    return response


def GetFinanceStats():
    response = {}
    try:
        total_global = db.session.query(func.sum(Dons.amount)).filter(Dons.status == 'completed').scalar() or 0
        
        stats_by_type = db.session.query(
            Dons.type, 
            func.sum(Dons.amount)
        ).filter(Dons.status == 'completed').group_by(Dons.type).all()
        
        categories_dict = {'Sadaqah': 0, 'Zakat': 0, 'Projet': 0, 'Fitr': 0}
        for row in stats_by_type:
            if row[0] in categories_dict:
                categories_dict[row[0]] = float(row[1])
                
        response['status'] = 'success'
        response['global_total'] = float(total_global)
        response['by_category'] = categories_dict
    except Exception as e:
        response['status'] = 'error'
        response['error_description'] = str(e)
        
    return response


def GetDonationsByMonth():
    response = {}
    try:
        # strftime convient pour SQLite. Remplace par func.to_char(Dons.created_at, 'YYYY-MM') si tu es sur PostgreSQL
        stats_months = db.session.query(
            func.strftime('%Y-%m', Dons.created_at).label('month'),
            func.sum(Dons.amount)
        ).filter(Dons.status == 'completed').group_by('month').order_by('month').all()
        
        response['status'] = 'success'
        response['data'] = [{'month': row[0], 'total': float(row[1])} for row in stats_months]
    except Exception as e:
        response['status'] = 'error'
        response['error_description'] = str(e)
        
    return response


def GetTopDonors():
    response = {}
    try:
        # Récupère par défaut le top 5
        top_donors = db.session.query(
            Dons.donor_name,
            Dons.phone,
            func.sum(Dons.amount).label('total_donated')
        ).filter(
                Dons.status == 'completed',
                Dons.donor_name != None,
                Dons.donor_name != ''
            ).group_by(
            Dons.donor_name, Dons.phone
        ).order_by(func.sum(Dons.amount).desc()).limit(5).all()
        
        response['status'] = 'success'
        response['data'] = [{'donateur': row[0], 'phone': row[1], 'total': float(row[2])} for row in top_donors]
    except Exception as e:
        response['status'] = 'error'
        response['error_description'] = str(e)
        
    return response