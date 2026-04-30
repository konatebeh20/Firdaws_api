#!/usr/bin/env python3
"""
Seed complet pour remplir toutes les tables de la base de données Firdaws
Exécuter avec: python seed_complete.py
"""

import os
import sys
import json
from datetime import datetime
import bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Ajouter le chemin pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from model.firdaws_db import (
    Admin, Event, Video, Document, Info, Khutba, Training,
    Notification, Mail, Reading, Error, FirewallLog, BlockedIP, User
)

# Données seed complètes
SEED_DATA = {
    "users": [
        {
            "username": "konatebeh",
            "firstname": "Beh",
            "lastname": "Konaté",
            "email": "konatebeh20@gmail.com",
            "password": "test123!@#",  # Sera hashé
            "phone": "0789966662",
            "role": "superadmin",
            "is_active": True,
            "created_at": "2026-01-01T08:00:00Z"
        },
        {
            "username": "imam_diallo",
            "firstname": "Mamadou",
            "lastname": "Diallo",
            "email": "imam.diallo@firdaws-banco.org",
            "password": "test123!@#",
            "phone": "0102030405",
            "role": "admin",
            "is_active": True,
            "created_at": "2026-01-05T09:00:00Z"
        },
        {
            "username": "fatou_coulibaly",
            "firstname": "Fatou",
            "lastname": "Coulibaly",
            "email": "fatou.coulibaly@gmail.com",
            "password": "test123!@#",
            "phone": "0607080910",
            "role": "user",
            "is_active": True,
            "created_at": "2026-02-10T10:00:00Z"
        }
    ],
    "admins": [
        {
            "username": "AdminT",
            "email": "admin@firdaws-banco.org",
            "password": "admin123!@#",
            "role": "superadmin",
            "is_active": True,
            "created_at": "2026-01-01T07:00:00Z"
        }
    ],
    "events": [
        {
            "title": "Conférence Ramadan 2026",
            "description": "Grande conférence islamique sur les vertus du mois de Ramadan. Intervenants de renom venus de toute la sous-région.",
            "type": "Conférence",
            "date_start": "2026-03-20T18:00:00Z",
            "date_end": "2026-03-20T22:00:00Z",
            "location": "Mosquée Firdaws, Banco, Abidjan",
            "status": "Actif",
            "created_at": "2026-02-15T10:00:00Z"
        },
        {
            "title": "Cours hebdomadaire de Tafsir",
            "description": "Explication du Coran, chapitre Al-Baqara. Cours animé par l'Imam Diallo chaque vendredi après la prière de Dhuhr.",
            "type": "Khutba",
            "date_start": "2026-04-17T13:30:00Z",
            "date_end": "2026-04-17T15:00:00Z",
            "location": "Salle de cours — Mosquée Firdaws",
            "status": "Actif",
            "created_at": "2026-04-01T08:00:00Z"
        },
        {
            "title": "Journée Portes Ouvertes",
            "description": "La mosquée Firdaws ouvre ses portes à toute la communauté pour une journée de découverte et d'échanges.",
            "type": "Social",
            "date_start": "2026-05-10T09:00:00Z",
            "date_end": "2026-05-10T17:00:00Z",
            "location": "Mosquée Firdaws, Banco, Abidjan",
            "status": "Inactif",
            "created_at": "2026-04-10T09:00:00Z"
        }
    ],
    "documents": [
        {
            "title": "Programme Ramadan 2026",
            "description": "Calendrier complet des activités de la mosquée Firdaws durant le mois de Ramadan 2026.",
            "fileUrl": "https://storage.supabase.co/firdaws/docs/programme_ramadan_2026.pdf",
            "category": "Programme",
            "status": "Actif",
            "created_at": "2026-02-20T08:00:00Z"
        },
        {
            "title": "Guide du bon musulman",
            "description": "Livret d'introduction aux piliers de l'Islam destiné aux nouveaux convertis.",
            "fileUrl": "https://storage.supabase.co/firdaws/docs/guide_bon_musulman.pdf",
            "category": "Éducation",
            "status": "Actif",
            "created_at": "2026-01-10T09:00:00Z"
        }
    ],
    "infos": [
        {
            "title": "Horaires des prières — Avril 2026",
            "description": "Retrouvez les horaires officiels des cinq prières quotidiennes pour le mois d'Avril 2026 à Abidjan.",
            "content": "Fajr: 05:12 | Dhuhr: 13:00 | Asr: 16:45 | Maghrib: 19:18 | Isha: 20:45",
            "type": "Info",
            "status": "Actif",
            "created_at": "2026-04-01T06:00:00Z"
        },
        {
            "title": "Annonce — Collecte de Zakat Al-Fitr",
            "description": "La collecte de la Zakat Al-Fitr est ouverte à partir du 25 Ramadan. Venez contribuer à la mosquée ou par virement.",
            "content": "Compte bancaire: XXX-XXXX-XXXX",
            "type": "Annonce",
            "status": "Actif",
            "created_at": "2026-03-15T10:00:00Z"
        }
    ],
    "khutba": [
        {
            "title": "La patience face aux épreuves",
            "content": "Louange à Allah, Seigneur des mondes. Nous le remercions, demandons Son pardon et cherchons refuge en Lui. Aujourd'hui nous allons parler de As-Sabr, la patience, qui est l'une des plus grandes vertus en Islam...",
            "author": "Imam Mamadou Diallo",
            "date": "2026-04-11",
            "status": "Actif",
            "created_at": "2026-04-11T14:00:00Z"
        },
        {
            "title": "L'importance de la solidarité en Islam",
            "content": "Bismillah. Chers frères et sœurs en Islam, la solidarité (At-Takaful) est un fondement de notre communauté. Le Prophète ﷺ a dit : le croyant pour le croyant est comme un édifice dont les parties se soutiennent mutuellement...",
            "author": "Imam Mamadou Diallo",
            "date": "2026-04-04",
            "status": "Actif",
            "created_at": "2026-04-04T14:00:00Z"
        }
    ],
    "trainings": [
        {
            "title": "Formation — Mémorisation du Coran (Hifz)",
            "description": "Programme intensif de mémorisation du Coran sur 24 mois, ouvert aux enfants de 7 à 15 ans.",
            "instructor": "Cheikh Ibrahim Touré",
            "duration_weeks": 104,
            "level": "Débutant",
            "status": "Actif",
            "created_at": "2026-01-15T09:00:00Z"
        },
        {
            "title": "Apprentissage de l'Arabe classique",
            "description": "Cours d'arabe littéraire pour adultes, du niveau A1 au B2. Horaires flexibles en soirée.",
            "instructor": "Professeur Aïssa Bamba",
            "duration_weeks": 36,
            "level": "Tous niveaux",
            "status": "Actif",
            "created_at": "2026-02-01T08:00:00Z"
        }
    ]
}

def hash_password(password):
    """Hash un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def seed_database():
    """Remplit la base de données avec les données seed"""
    with app.app_context():
        try:
            print("🌱 Démarrage du seed de la base de données...")
            
            # 1. Créer les users
            print("\n📝 Création des utilisateurs...")
            for user_data in SEED_DATA["users"]:
                existing = User.query.filter_by(username=user_data["username"]).first()
                if not existing:
                    user = User(
                        username=user_data["username"],
                        firstname=user_data["firstname"],
                        lastname=user_data["lastname"],
                        email=user_data["email"],
                        password_hash=hash_password(user_data["password"]),
                        phone=user_data["phone"],
                        role=user_data["role"],
                        is_active=user_data["is_active"],
                        created_at=user_data["created_at"]
                    )
                    db.session.add(user)
                    print(f"  ✓ User créé: {user_data['username']}")
                else:
                    print(f"  ⊘ User existe déjà: {user_data['username']}")
            
            # 2. Créer les admins
            print("\n👤 Création des administrateurs...")
            for admin_data in SEED_DATA["admins"]:
                existing = Admin.query.filter_by(username=admin_data["username"]).first()
                if not existing:
                    admin = Admin(
                        username=admin_data["username"],
                        email=admin_data["email"],
                        password_hash=hash_password(admin_data["password"]),
                        role=admin_data["role"],
                        is_active=admin_data["is_active"],
                        created_at=admin_data["created_at"]
                    )
                    db.session.add(admin)
                    print(f"  ✓ Admin créé: {admin_data['username']}")
                else:
                    print(f"  ⊘ Admin existe déjà: {admin_data['username']}")
            
            # 3. Créer les événements
            print("\n📅 Création des événements...")
            for event_data in SEED_DATA["events"]:
                existing = Event.query.filter_by(title=event_data["title"]).first()
                if not existing:
                    event = Event(
                        title=event_data["title"],
                        description=event_data["description"],
                        type=event_data["type"],
                        date_start=event_data["date_start"],
                        date_end=event_data["date_end"],
                        location=event_data["location"],
                        status=event_data["status"],
                        created_at=event_data["created_at"]
                    )
                    db.session.add(event)
                    print(f"  ✓ Événement créé: {event_data['title']}")
                else:
                    print(f"  ⊘ Événement existe déjà: {event_data['title']}")
            
            # 4. Créer les documents
            print("\n📄 Création des documents...")
            for doc_data in SEED_DATA["documents"]:
                existing = Document.query.filter_by(title=doc_data["title"]).first()
                if not existing:
                    doc = Document(
                        title=doc_data["title"],
                        description=doc_data["description"],
                        fileUrl=doc_data["fileUrl"],
                        category=doc_data["category"],
                        status=doc_data["status"],
                        created_at=doc_data["created_at"]
                    )
                    db.session.add(doc)
                    print(f"  ✓ Document créé: {doc_data['title']}")
                else:
                    print(f"  ⊘ Document existe déjà: {doc_data['title']}")
            
            # 6. Créer les infos
            print("\n📢 Création des informations...")
            for info_data in SEED_DATA["infos"]:
                existing = Info.query.filter_by(title=info_data["title"]).first()
                if not existing:
                    info = Info(
                        title=info_data["title"],
                        description=info_data["description"],
                        content=info_data["content"],
                        type=info_data["type"],
                        status=info_data["status"],
                        created_at=info_data["created_at"]
                    )
                    db.session.add(info)
                    print(f"  ✓ Info créée: {info_data['title']}")
                else:
                    print(f"  ⊘ Info existe déjà: {info_data['title']}")
            
            # 7. Créer les khutbas
            print("\n📖 Création des khutbas...")
            for khutba_data in SEED_DATA["khutba"]:
                existing = Khutba.query.filter_by(title=khutba_data["title"]).first()
                if not existing:
                    khutba = Khutba(
                        title=khutba_data["title"],
                        content=khutba_data["content"],
                        author=khutba_data["author"],
                        date=khutba_data["date"],
                        status=khutba_data["status"],
                        created_at=khutba_data["created_at"]
                    )
                    db.session.add(khutba)
                    print(f"  ✓ Khutba créée: {khutba_data['title']}")
                else:
                    print(f"  ⊘ Khutba existe déjà: {khutba_data['title']}")
            
            # 8. Créer les formations
            print("\n🎓 Création des formations...")
            for training_data in SEED_DATA["trainings"]:
                existing = Training.query.filter_by(title=training_data["title"]).first()
                if not existing:
                    training = Training(
                        title=training_data["title"],
                        description=training_data["description"],
                        instructor=training_data["instructor"],
                        duration_weeks=training_data["duration_weeks"],
                        level=training_data["level"],
                        status=training_data["status"],
                        created_at=training_data["created_at"]
                    )
                    db.session.add(training)
                    print(f"  ✓ Formation créée: {training_data['title']}")
                else:
                    print(f"  ⊘ Formation existe déjà: {training_data['title']}")
            
            # Commit toutes les modifications
            db.session.commit()
            print("\n✅ Seed complétée avec succès!")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur lors du seed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    seed_database()
