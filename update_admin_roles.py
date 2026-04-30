#!/usr/bin/env python3
"""
Script pour mettre à jour les utilisateurs existants avec le rôle admin
"""

import pymysql

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'firdaws_db'
}

def update_admin_roles():
    """Mettre à jour les utilisateurs existants avec le rôle admin"""
    print("🔄 Mise à jour des utilisateurs avec le rôle admin...")
    
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Mettre à jour les administrateurs existants
        cursor.execute("UPDATE users SET role = 'admin' WHERE email IN ('admin@firdaws-banco.org', 'admin@firdaws-banco.ci')")
        conn.commit()
        
        # Vérifier les résultats
        cursor.execute("SELECT id, username, email, role FROM users WHERE role = 'admin'")
        admins = cursor.fetchall()
        
        print(f"✅ {len(admins)} administrateurs mis à jour :")
        for admin in admins:
            print(f"   - ID: {admin[0]}, Username: {admin[1]}, Email: {admin[2]}, Role: {admin[3]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    update_admin_roles()
