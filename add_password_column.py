#!/usr/bin/env python3
"""
Script pour ajouter la colonne password (en clair) à la table users
et mettre à jour les utilisateurs existants
"""

import pymysql

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'firdaws_db'
}

def add_password_column():
    """Ajouter la colonne password et mettre à jour les utilisateurs"""
    print("🔄 Ajout de la colonne password à la table users...")
    
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("SHOW COLUMNS FROM users LIKE 'password'")
        result = cursor.fetchone()
        
        if result:
            print("✅ La colonne 'password' existe déjà dans la table users")
        else:
            # Ajouter la colonne password
            cursor.execute("ALTER TABLE users ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT '' AFTER email")
            conn.commit()
            print("✅ Colonne 'password' ajoutée avec succès")
        
        # Mettre à jour les utilisateurs existants avec le mot de passe en clair
        print("🔄 Mise à jour des utilisateurs avec le mot de passe en clair...")
        cursor.execute("UPDATE users SET password = 'firdaws123' WHERE email IN ('admin@firdaws-banco.org', 'admin@firdaws-banco.ci')")
        conn.commit()
        
        # Vérifier les résultats
        cursor.execute("SELECT id, username, email, password FROM users WHERE role = 'admin'")
        admins = cursor.fetchall()
        
        print(f"✅ {len(admins)} administrateurs mis à jour :")
        for admin in admins:
            print(f"   - ID: {admin[0]}, Username: {admin[1]}, Email: {admin[2]}, Password: {admin[3]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    add_password_column()
