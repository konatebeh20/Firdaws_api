#!/usr/bin/env python3
"""
Script pour re-hacher les mots de passe avec bcrypt
"""

import pymysql
import bcrypt

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'firdaws_db'
}

def fix_passwords():
    """Re-hacher les mots de passe avec bcrypt"""
    print("🔄 Re-hachage des mots de passe avec bcrypt...")
    
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Récupérer tous les utilisateurs
        cursor.execute("SELECT id, username, email, password_hash FROM users")
        users = cursor.fetchall()
        
        for user in users:
            user_id, username, email, current_hash = user
            
            # Le mot de passe original est "firdaws123" pour les admins
            if email in ['admin@firdaws-banco.org', 'admin@firdaws-banco.ci']:
                password = 'firdaws123'
                salt = bcrypt.gensalt()
                new_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                
                # Mettre à jour le hash
                cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
                print(f"✅ Mot de passe re-haché pour {username} ({email})")
        
        conn.commit()
        print("✅ Tous les mots de passe ont été re-hachés avec bcrypt")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    fix_passwords()
