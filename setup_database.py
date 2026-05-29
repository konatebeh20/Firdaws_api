#!/usr/bin/env python3
"""
Script pour créer la base de données MySQL et les tables
Exécutez ce script pour initialiser la base de données Xampp
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pymysql
from datetime import datetime
import hashlib

# Configuration Xampp MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'port': 3306
}

def hash_password(password):
    """Hash un mot de passe (même méthode que l'API)"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_database():
    """Créer la base de données firdaws_db"""
    print("🔄 Création de la base de données...")
    
    try:
        # Connexion sans spécifier de base de données
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Créer la base de données si elle n'existe pas
        cursor.execute("CREATE DATABASE IF NOT EXISTS firdaws_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Base de données 'firdaws_db' créée avec succès")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création base de données: {e}")
        return False

def create_tables():
    """Créer toutes les tables nécessaires"""
    print("🔄 Création des tables...")
    
    try:
        # Connexion à la base de données firdaws_db
        config = MYSQL_CONFIG.copy()
        config['database'] = 'firdaws_db'
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL DEFAULT '',
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                phone VARCHAR(20),
                role ENUM('admin', 'moderator', 'user') DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
        """)
        
        # Table des événements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                event_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NULL,
                location VARCHAR(200),
                category VARCHAR(50),
                status ENUM('draft', 'published', 'cancelled') DEFAULT 'draft',
                image_url VARCHAR(500),
                max_participants INT,
                current_participants INT DEFAULT 0,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Table des documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                file_path VARCHAR(500),
                file_name VARCHAR(255),
                file_size INT,
                file_type VARCHAR(50),
                category VARCHAR(50),
                status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
                download_count INT DEFAULT 0,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Table des vidéos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                video_url VARCHAR(500) NOT NULL,
                thumbnail_url VARCHAR(500),
                duration INT,
                category VARCHAR(50),
                status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
                view_count INT DEFAULT 0,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Table des informations/annonces
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS informations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                type ENUM('announcement', 'information', 'urgent') DEFAULT 'information',
                status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
                priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
                publish_date TIMESTAMP NULL,
                expire_date TIMESTAMP NULL,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Table des khutbas (sermons)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS khutbas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                speaker VARCHAR(100),
                date TIMESTAMP NOT NULL,
                audio_url VARCHAR(500),
                pdf_url VARCHAR(500),
                category VARCHAR(50),
                status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Table des contacts/messages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                subject VARCHAR(200),
                message TEXT NOT NULL,
                status ENUM('new', 'read', 'replied', 'archived') DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Table des paramètres de configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                key_name VARCHAR(100) UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
                updated_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        conn.commit()
        print("✅ Tables créées avec succès")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création tables: {e}")
        return False

def insert_default_data():
    """Insérer les données par défaut"""
    print("🔄 Insertion des données par défaut...")
    
    try:
        # Connexion à la base de données firdaws_db
        config = MYSQL_CONFIG.copy()
        config['database'] = 'firdaws_db'
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        # Insérer les administrateurs par défaut
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
            cursor.execute("""
                INSERT IGNORE INTO users (username, email, password_hash, first_name, last_name, role, is_active, created_at, updated_at)
                VALUES (%(username)s, %(email)s, %(password_hash)s, %(first_name)s, %(last_name)s, %(role)s, %(is_active)s, NOW(), NOW())
            """, admin)
        
        # Insérer des événements exemples
        sample_events = [
            {
                'title': 'Prières du Ramadan 2026',
                'description': 'Rejoignez-nous pour les prières spéciales du Ramadan avec toute la communauté',
                'event_date': datetime(2026, 4, 15, 19, 0),
                'location': 'Mosquée Firdaws - Cité Bel Aire',
                'category': 'religieux',
                'status': 'published',
                'created_by': 1
            },
            {
                'title': 'Cours de Coran pour enfants',
                'description': 'Cours hebdomadaire de mémorisation du Coran pour les enfants de 7 à 15 ans',
                'event_date': datetime(2026, 5, 1, 15, 0),
                'location': 'Salle d\'étude - Mosquée Firdaws',
                'category': 'éducation',
                'status': 'published',
                'created_by': 1
            },
            {
                'title': 'Conférence sur la paix et l\'harmonie',
                'description': 'Conférence sur l\'importance de la paix en Islam et dans la société moderne',
                'event_date': datetime(2026, 5, 10, 16, 0),
                'location': 'Mosquée Firdaws - Salle principale',
                'category': 'conférence',
                'status': 'published',
                'created_by': 1
            },
            {
                'title': 'Soirée de rupture du jeûne communautaire',
                'description': 'Venez partager l\'Iftar avec vos frères et sœurs en musulman',
                'event_date': datetime(2026, 5, 5, 18, 30),
                'location': 'Mosquée Firdaws - Espace extérieur',
                'category': 'social',
                'status': 'published',
                'created_by': 1
            }
        ]
        
        for event in sample_events:
            cursor.execute("""
                INSERT INTO events (title, description, event_date, location, category, status, created_by, created_at, updated_at)
                VALUES (%(title)s, %(description)s, %(event_date)s, %(location)s, %(category)s, %(status)s, %(created_by)s, NOW(), NOW())
            """, event)
        
        # Insérer les paramètres de base
        settings_data = [
            {
                'key_name': 'site_name',
                'value': 'Mosquée Firdaws',
                'description': 'Nom du site',
                'type': 'string'
            },
            {
                'key_name': 'site_description',
                'value': 'Mosquée Firdaws - Cité Bel Aire du Banco',
                'description': 'Description du site',
                'type': 'string'
            },
            {
                'key_name': 'contact_email',
                'value': 'contact@firdaws-mosque.ci',
                'description': 'Email de contact',
                'type': 'string'
            },
            {
                'key_name': 'phone_number',
                'value': '+225 00 00 00 00',
                'description': 'Numéro de téléphone',
                'type': 'string'
            },
            {
                'key_name': 'address',
                'value': 'Cité Bel Aire du Banco, Abidjan, Côte d\'Ivoire',
                'description': 'Adresse',
                'type': 'string'
            },
            {
                'key_name': 'maintenance_mode',
                'value': 'false',
                'description': 'Mode maintenance',
                'type': 'boolean'
            }
        ]
        
        for setting in settings_data:
            cursor.execute("""
                INSERT IGNORE INTO settings (key_name, value, description, type, created_at, updated_at)
                VALUES (%(key_name)s, %(value)s, %(description)s, %(type)s, NOW(), NOW())
            """, setting)
        
        conn.commit()
        print("✅ Données par défaut insérées avec succès")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur insertion données par défaut: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Initialisation de la base de données MySQL Xampp")
    print("=" * 50)
    
    # 1. Créer la base de données
    if not create_database():
        print("❌ Échec de la création de la base de données")
        return
    
    # 2. Créer les tables
    if not create_tables():
        print("❌ Échec de la création des tables")
        return
    
    # 3. Insérer les données par défaut
    if not insert_default_data():
        print("❌ Échec de l'insertion des données par défaut")
        return
    
    print("=" * 50)
    print("✅ Base de données initialisée avec succès!")
    print("\n📝 Identifiants de connexion admin:")
    print("   Email: admin@firdaws-banco.org")
    print("   Mot de passe: firdaws123")
    print("\n   Email: admin@firdaws-banco.ci") 
    print("   Mot de passe: firdaws123")
    print(f"\n📊 Événements créés: 4 événements exemples")
    print("🔧 Base de données: firdaws_db sur MySQL Xampp")

if __name__ == "__main__":
    main()
