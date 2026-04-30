import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from config.db import db
from model.firdaws_db import Admin, Event, Video, Info, Document, Khutba

def seed_data():
    print("\n🌱 DÉMARRAGE DU PEUPLEMENT DE LA BASE DE DONNÉES (SEEDING)\n")
    
    with app.app_context():
        # 1. Récupérer l'admin par défaut
        admin = Admin.query.first()
        admin_id = admin.id if admin else None
        print(f"👤 Utilisant l'admin ID: {admin_id}")

        # 2. SEEDING ÉVÉNEMENTS
        print("📅 Seeding Événements...")
        events_data = [
            {
                'title': "Prière du Vendredi (Jumu'a)",
                'type': "Événement",
                'description': "Venez nombreux pour la prière collective et le sermon hebdomadaire.",
                'location': "Grande Salle de Prière",
                'start_date': datetime.now().replace(hour=13, minute=0),
                'time': "13:00",
                'imam': "Sheikh Ahmed"
            },
            {
                'title': "Cours de Fiqh",
                'type': "Formation",
                'description': "Étude approfondie des règles de la jurisprudence islamique.",
                'location': "Salle d'Étude 1",
                'start_date': datetime.now() + timedelta(days=2),
                'time': "18:30",
                'imam': "Imam Rachid"
            },
            {
                'title': "Conférence : La Famille en Islam",
                'type': "Conférence",
                'description': "Une conférence sur les valeurs familiales et l'éducation des enfants.",
                'location': "Auditorium",
                'start_date': datetime.now() + timedelta(days=5),
                'time': "19:00",
                'imam': "Dr. Omar"
            }
        ]
        
        for e in events_data:
            if not Event.query.filter_by(title=e['title']).first():
                new_event = Event(**e, created_by=admin_id)
                db.session.add(new_event)
                print(f"   ✅ Ajouté: {e['title']}")
            else:
                print(f"   ⏩ Déjà existant: {e['title']}")

        # 3. SEEDING VIDÉOS
        print("🎥 Seeding Vidéos...")
        videos_data = [
            {
                'title': "Sermon : La générosité en Islam",
                'url': "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                'thumbnail_url': "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                'type': "Khutba",
                'imam': "Sheikh Ahmed",
                'date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'title': "Cours : Introduction au Tawhid",
                'url': "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
                'thumbnail_url': "https://img.youtube.com/vi/kJQP7kiw5Fk/maxresdefault.jpg",
                'type': "Formation",
                'imam': "Imam Rachid",
                'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            }
        ]
        
        for v in videos_data:
            if not Video.query.filter_by(title=v['title']).first():
                new_video = Video(**v, created_by=admin_id)
                db.session.add(new_video)
                print(f"   ✅ Ajouté: {v['title']}")
            else:
                print(f"   ⏩ Déjà existant: {v['title']}")

        # 4. SEEDING ANNONCES (INFOS)
        print("📢 Seeding Annonces...")
        infos_data = [
            {
                'title': "Travaux de rénovation",
                'content': "Des travaux de peinture seront effectués dans la salle principale lundi prochain.",
                'category': "Logistique"
            },
            {
                'title': "Collecte pour les nécessiteux",
                'content': "Une collecte de denrées non périssables est ouverte jusqu'à la fin du mois.",
                'category': "Social"
            }
        ]
        
        for i in infos_data:
            if not Info.query.filter_by(title=i['title']).first():
                new_info = Info(**i, created_by=admin_id)
                db.session.add(new_info)
                print(f"   ✅ Ajouté: {i['title']}")
            else:
                print(f"   ⏩ Déjà existant: {i['title']}")

        # 5. SEEDING DOCUMENTS
        print("📄 Seeding Documents...")
        docs_data = [
            {
                'title': "Calendrier des prières - Avril 2026",
                'description': "Horaires officiels pour le mois en cours.",
                'author': "Commission Religieuse",
                'file_url': "https://example.com/prieres_avril.pdf",
                'type': "PDF",
                'file_size': "1.2 MB"
            },
            {
                'title': "Formulaire d'adhésion",
                'description': "Devenez membre de l'association.",
                'author': "Secrétariat",
                'file_url': "https://example.com/adhesion.docx",
                'type': "DOCX",
                'file_size': "450 KB"
            }
        ]
        
        for d in docs_data:
            if not Document.query.filter_by(title=d['title']).first():
                new_doc = Document(**d, created_by=admin_id)
                db.session.add(new_doc)
                print(f"   ✅ Ajouté: {d['title']}")
            else:
                print(f"   ⏩ Déjà existant: {d['title']}")

        # 6. SEEDING KHUTBA (TEXTE)
        print("📜 Seeding Khutba (Texte)...")
        khutba_title = "La fraternité en Islam"
        if not Khutba.query.filter_by(title=khutba_title).first():
            new_khutba = Khutba(
                title=khutba_title,
                date=datetime.now().strftime('%Y-%m-%d'),
                imam="Sheikh Ahmed",
                content="""
                Chers frères et sœurs, la fraternité est l'un des piliers de notre foi...
                Allah dit dans le Coran : 'Les croyants ne sont que des frères'...
                Travaillons ensemble pour renforcer ces liens sacrés dans notre communauté.
                """,
                created_by=admin_id
            )
            db.session.add(new_khutba)
            print(f"   ✅ Ajouté: {khutba_title}")
        else:
            print(f"   ⏩ Déjà existant: {khutba_title}")

        db.session.commit()
        print("\n✨ TOUTES LES DONNÉES ONT ÉTÉ ENREGISTRÉES AVEC SUCCÈS !")

if __name__ == "__main__":
    seed_data()
