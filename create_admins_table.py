#!/usr/bin/env python3
"""
Script pour créer la table admins dans MySQL
"""

import pymysql

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'firdaws_db'
}

def create_admins_table():
    """Créer la table admins"""
    print("🔄 Création de la table admins...")
    
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Supprimer la table si elle existe
        cursor.execute("DROP TABLE IF EXISTS admins")
        
        # Créer la table admins
        create_table_sql = """
        CREATE TABLE admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            phone VARCHAR(20) NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            role VARCHAR(20) DEFAULT 'admin',
            photo_url VARCHAR(500),
            is_active BOOLEAN DEFAULT TRUE,
            last_login DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        print("✅ Table admins créée avec succès")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    create_admins_table()
