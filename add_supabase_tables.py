#!/usr/bin/env python3
"""
Script pour ajouter les tables manquantes de Supabase dans MySQL
Tables: blocked_ips, firewall_logs, mails, notifications, readings, reset_tokens, trainings, videos
"""

import pymysql

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'firdaws_db'
}

def create_supabase_tables():
    """Créer les tables manquantes de Supabase"""
    print("🔄 Création des tables manquantes de Supabase...")
    
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Table blocked_ips
        print("📋 Création de la table blocked_ips...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocked_ips (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ip_address VARCHAR(45) UNIQUE NOT NULL,
                reason TEXT,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                blocked_by INT,
                expires_at TIMESTAMP NULL,
                is_permanent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Table firewall_logs
        print("📋 Création de la table firewall_logs...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS firewall_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ip_address VARCHAR(45),
                request_method VARCHAR(10),
                request_path VARCHAR(500),
                status_code INT,
                user_agent TEXT,
                blocked BOOLEAN DEFAULT FALSE,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table videos (mise à jour de la table existante)
        print("📋 Mise à jour de la table videos...")
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
        
        # Table reset_tokens
        print("📋 Création de la table reset_tokens...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reset_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                used_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Table trainings
        print("📋 Création de la table trainings...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trainings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                content TEXT,
                instructor VARCHAR(100),
                level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
                duration_hours INT,
                start_date TIMESTAMP NULL,
                end_date TIMESTAMP NULL,
                image_url VARCHAR(500),
                category VARCHAR(50),
                status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
                enrollment_count INT DEFAULT 0,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        conn.commit()
        print("✅ Tables manquantes créées avec succès")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    create_supabase_tables()
