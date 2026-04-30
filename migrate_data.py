#!/usr/bin/env python3
"""
Script de migration des données depuis Supabase vers Xampp MySQL
Exécutez ce script après avoir créé la base de données MySQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import psycopg2
import pymysql
from datetime import datetime
import hashlib

# Configuration Supabase (à adapter avec vos vraies credentials)
SUPABASE_CONFIG = {
    'host': 'db.mlfqpvzvajjazsvttvds.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'firdaws_db1234',
    'port': 5432
}

# Configuration Xampp MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'firdaws_db',
    'port': 3306
}

def hash_password(password):
    """Hash un mot de passe (même méthode que l'API)"""
    return hashlib.sha256(password.encode()).hexdigest()

def migrate_users():
    """Migration des utilisateurs/administrateurs"""
    print("🔄 Migration des utilisateurs...")
    
    supabase_conn = None
    mysql_conn = None
    
    try:
        # Connexion à MySQL d'abord
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        
        # Ajouter les administrateurs par défaut directement
        admin_users = [
            {
                'username': 'admin',
                'email': 'admin@firdaws-banco.org',
                'password_hash': hash_password("firdaws123"),
                'first_name': 'Admin',
                'last_name': 'Firdaws',
                'role': 'admin',
                'is_active': True
            },
            {
                'username': 'admin_ci',
                'email': 'admin@firdaws-banco.ci',
                'password_hash': hash_password("firdaws123"),
                'first_name': 'Admin',
                'last_name': 'CI',
                'role': 'admin',
                'is_active': True
            }
        ]
        
        for admin in admin_users:
            query = """
            INSERT IGNORE INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at, updated_at)
            VALUES (%(username)s, %(email)s, %(password_hash)s, %(first_name)s, %(last_name)s, %(role)s, %(is_active)s, NOW(), NOW())
            """
            mysql_cursor.execute(query, admin)
        
        mysql_conn.commit()
        print("✅ Administrateurs par défaut ajoutés")
        
        # Tenter la migration depuis Supabase si possible
        try:
            supabase_conn = psycopg2.connect(**SUPABASE_CONFIG)
            supabase_cursor = supabase_conn.cursor()
            
            # Récupérer les utilisateurs depuis Supabase
            supabase_cursor.execute("SELECT * FROM users")
            users = supabase_cursor.fetchall()
            
            # Insérer dans MySQL
            for user in users:
                # Adapter selon la structure de votre table users dans Supabase
                user_data = {
                    'username': user[1] if len(user) > 1 else f"user_{user[0]}",
                    'email': user[2] if len(user) > 2 else f"user{user[0]}@example.com",
                    'password_hash': user[3] if len(user) > 3 else hash_password("firdaws123"),
                    'first_name': user[4] if len(user) > 4 else "User",
                    'last_name': user[5] if len(user) > 5 else f"#{user[0]}",
                    'phone': user[6] if len(user) > 6 else None,
                    'role': user[7] if len(user) > 7 else 'user',
                    'is_active': user[8] if len(user) > 8 else True
                }
                
                # Insérer dans MySQL
                query = """
                INSERT IGNORE INTO users (username, email, password_hash, first_name, last_name, phone, role, is_active, created_at, updated_at)
                VALUES (%(username)s, %(email)s, %(password_hash)s, %(first_name)s, %(last_name)s, %(phone)s, %(role)s, %(is_active)s, NOW(), NOW())
                """
                mysql_cursor.execute(query, user_data)
            
            mysql_conn.commit()
            print(f"✅ {len(users)} utilisateurs migrés depuis Supabase")
            
        except Exception as supabase_error:
            print(f"⚠️  Impossible de se connecter à Supabase: {supabase_error}")
            print("📝 Utilisation uniquement des administrateurs par défaut")
        
    except Exception as e:
        print(f"❌ Erreur migration utilisateurs: {e}")
    finally:
        if supabase_conn:
            supabase_conn.close()
        if mysql_conn:
            mysql_conn.close()

def migrate_events():
    """Migration des événements"""
    print("🔄 Migration des événements...")
    
    try:
        supabase_conn = psycopg2.connect(**SUPABASE_CONFIG)
        supabase_cursor = supabase_conn.cursor()
        
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        
        # Récupérer les événements depuis Supabase
        supabase_cursor.execute("SELECT * FROM events")
        events = supabase_cursor.fetchall()
        
        for event in events:
            # Adapter selon votre structure events dans Supabase
            event_data = {
                'id': event[0],
                'title': event[1] if len(event) > 1 else "Événement sans titre",
                'description': event[2] if len(event) > 2 else None,
                'event_date': event[3] if len(event) > 3 else datetime.now(),
                'end_date': event[4] if len(event) > 4 else None,
                'location': event[5] if len(event) > 5 else "Mosquée Firdaws",
                'category': event[6] if len(event) > 6 else "général",
                'status': event[7] if len(event) > 7 else 'published',
                'image_url': event[8] if len(event) > 8 else None,
                'max_participants': event[9] if len(event) > 9 else None,
                'current_participants': event[10] if len(event) > 10 else 0,
                'created_by': event[11] if len(event) > 11 else 1,
                'created_at': event[12] if len(event) > 12 else datetime.now(),
                'updated_at': event[13] if len(event) > 13 else datetime.now()
            }
            
            query = """
            INSERT INTO events (title, description, event_date, end_date, location, category, status, image_url, max_participants, current_participants, created_by, created_at, updated_at)
            VALUES (%(title)s, %(description)s, %(event_date)s, %(end_date)s, %(location)s, %(category)s, %(status)s, %(image_url)s, %(max_participants)s, %(current_participants)s, %(created_by)s, %(created_at)s, %(updated_at)s)
            """
            mysql_cursor.execute(query, event_data)
        
        mysql_conn.commit()
        print(f"✅ {len(events)} événements migrés")
        
    except Exception as e:
        print(f"❌ Erreur migration événements: {e}")
    finally:
        supabase_conn.close()
        mysql_conn.close()

def add_sample_events():
    """Ajouter des événements exemples si aucun événement n'existe"""
    print("🔄 Ajout d'événements exemples...")
    
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        
        # Vérifier s'il y a déjà des événements
        mysql_cursor.execute("SELECT COUNT(*) FROM events")
        count = mysql_cursor.fetchone()[0]
        
        if count == 0:
            sample_events = [
                {
                    'title': 'Prières du Ramadan 2026',
                    'description': 'Rejoignez-nous pour les prières spéciales du Ramadan',
                    'event_date': datetime(2026, 4, 15, 19, 0),
                    'location': 'Mosquée Firdaws - Cité Bel Aire',
                    'category': 'religieux',
                    'status': 'published',
                    'created_by': 1
                },
                {
                    'title': 'Cours de Coran pour enfants',
                    'description': 'Cours hebdomadaire de mémorisation du Coran pour les enfants',
                    'event_date': datetime(2026, 5, 1, 15, 0),
                    'location': 'Salle d\'étude - Mosquée Firdaws',
                    'category': 'éducation',
                    'status': 'published',
                    'created_by': 1
                },
                {
                    'title': 'Conférence sur la paix',
                    'description': 'Conférence sur l\'importance de la paix en Islam',
                    'event_date': datetime(2026, 5, 10, 16, 0),
                    'location': 'Mosquée Firdaws - Salle principale',
                    'category': 'conférence',
                    'status': 'published',
                    'created_by': 1
                }
            ]
            
            for event in sample_events:
                query = """
                INSERT INTO events (title, description, event_date, location, category, status, created_by, created_at, updated_at)
                VALUES (%(title)s, %(description)s, %(event_date)s, %(location)s, %(category)s, %(status)s, %(created_by)s, NOW(), NOW())
                """
                mysql_cursor.execute(query, event)
            
            mysql_conn.commit()
            print("✅ 3 événements exemples ajoutés")
        else:
            print(f"ℹ️  {count} événements déjà existants")
            
    except Exception as e:
        print(f"❌ Erreur ajout événements exemples: {e}")
    finally:
        mysql_conn.close()

def main():
    """Fonction principale de migration"""
    print("🚀 Début de la migration Supabase → Xampp MySQL")
    print("=" * 50)
    
    # 1. Créer les administrateurs par défaut
    migrate_users()
    
    # 2. Tenter de migrer les événements depuis Supabase
    try:
        migrate_events()
    except Exception as e:
        print(f"⚠️  Erreur migration depuis Supabase: {e}")
        print("🔄 Ajout d'événements exemples...")
        add_sample_events()
    
    print("=" * 50)
    print("✅ Migration terminée!")
    print("\n📝 Identifiants de connexion admin:")
    print("   Email: admin@firdaws-banco.org")
    print("   Mot de passe: firdaws123")
    print("\n   Email: admin@firdaws-banco.ci") 
    print("   Mot de passe: firdaws123")

if __name__ == "__main__":
    main()
