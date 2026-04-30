#!/usr/bin/env python3
"""
Script pour créer les utilisateurs administrateurs demandés
"""

import pymysql
import bcrypt

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'firdaws_db'
}

def create_admin_users():
    """Créer les utilisateurs administrateurs demandés"""
    print("🔄 Création des utilisateurs administrateurs...")
    
    admins = [
        {
            'username': 'admin_firdaws_banco',
            'email': 'admin@firdaws-banco.org',
            'phone': '00000000',
            'password': 'firdaws123',
            'role': 'superadmin'
        },
        {
            'username': 'admin_firdaws_ci',
            'email': 'admin@firdaws-banco.ci',
            'phone': '00000000',
            'password': 'firdaws123',
            'role': 'superadmin'
        },
        {
            'username': 'AdminTrs',
            'email': 'admin@admintrs.com',
            'phone': '00000000',
            'password': 'firdaws123',
            'role': 'admin'
        }
    ]
    
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        for admin_data in admins:
            # Vérifier si l'utilisateur existe déjà
            cursor.execute("SELECT id FROM admins WHERE email = %s", (admin_data['email'],))
            existing = cursor.fetchone()
            
            # Hasher le mot de passe
            password_bytes = admin_data['password'].encode('utf-8')
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            
            if existing:
                # Mettre à jour l'utilisateur existant
                cursor.execute("""
                    UPDATE admins 
                    SET username = %s, phone = %s, password_hash = %s, role = %s, is_active = TRUE
                    WHERE email = %s
                """, (
                    admin_data['username'],
                    admin_data['phone'],
                    password_hash,
                    admin_data['role'],
                    admin_data['email']
                ))
                print(f"✅ Admin mis à jour: {admin_data['email']}")
            else:
                # Créer un nouvel utilisateur
                cursor.execute("""
                    INSERT INTO admins (username, email, phone, password_hash, role, is_active)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                """, (
                    admin_data['username'],
                    admin_data['email'],
                    admin_data['phone'],
                    password_hash,
                    admin_data['role']
                ))
                print(f"✅ Admin créé: {admin_data['email']}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ Tous les administrateurs ont été créés/mis à jour avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    create_admin_users()
