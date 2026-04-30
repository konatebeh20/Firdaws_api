#!/usr/bin/env python3
"""
Script pour ajouter la colonne role à la table users
"""

import pymysql

# Configuration Xampp MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'firdaws_db'
}

def add_role_column():
    """Ajouter la colonne role à la table users"""
    print("🔄 Ajout de la colonne role à la table users...")
    
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("SHOW COLUMNS FROM users LIKE 'role'")
        result = cursor.fetchone()
        
        if result:
            print("✅ La colonne 'role' existe déjà dans la table users")
        else:
            # Ajouter la colonne role
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
            conn.commit()
            print("✅ Colonne 'role' ajoutée avec succès")
            
            # Mettre à jour les administrateurs existants
            cursor.execute("UPDATE users SET role = 'admin' WHERE email IN ('admin@firdaws-banco.org', 'admin@firdaws-banco.ci')")
            conn.commit()
            print("✅ Administrateurs existants mis à jour avec le rôle 'admin'")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    add_role_column()
