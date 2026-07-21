import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from model.firdaws_db import db, Event, Document, Info, MosqueLife, Admin
from app import app

def add_test_data():
    with app.app_context():
        admin = Admin.query.first()
        if not admin:
            print("Aucun admin trouve")
            return
        
        admin_id = admin.id
        print(f"Admin ID: {admin_id}")
        
        # Event
        event = Event(
            title='Prières du Ramadan',
            date=datetime.now() + timedelta(days=7),
            time='18:30',
            imam='Imam Ibrahim',
            description='Prières spéciales du Ramadan avec Iftar communautaire.',
            type='Khutba',
            created_by=admin_id
        )
        event.save()
        print("Event ajoute")
        
        # Document
        doc = Document(
            title='Guide des prières',
            description='Guide complet pour les 5 prières quotidiennes.',
            file_url='https://example.com/guide.pdf',
            file_size='2.5 MB',
            file_type='PDF',
            icon='bi-file-pdf',
            created_by=admin_id
        )
        doc.save()
        print("Document ajoute")
        
        # Info
        info = Info(
            title='Nouveaux horaires de prières',
            content='Les horaires de prières ont ete mis a jour.',
            priority='high',
            category='Annonces',
            created_by=admin_id
        )
        info.save()
        print("Info ajoutee")
        
        # MosqueLife
        life = MosqueLife(
            title='Inauguration de la nouvelle bibliotheque',
            content='Ouverture de notre nouvelle bibliotheque islamique.',
            category='community',
            date=datetime.now().date(),
            location='Mosquee Firdaws',
            status='published',
            created_by=admin_id
        )
        life.save()
        print("MosqueLife ajoute")
        
        print("Donnees de test ajoutees avec succes!")

if __name__ == '__main__':
    add_test_data()
