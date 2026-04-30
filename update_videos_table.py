#!/usr/bin/env python3
"""
Script pour mettre à jour la table videos pour stocker seulement les métadonnées YouTube
"""

import pymysql

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'firdaws_db'
}

def update_videos_table():
    """Mettre à jour la table videos"""
    print("🔄 Mise à jour de la table videos...")
    
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Vérifier les colonnes existantes
        cursor.execute("SHOW COLUMNS FROM videos")
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Colonnes existantes: {existing_columns}")
        
        # Supprimer les colonnes obsolètes si elles existent
        columns_to_drop = ['instructor', 'imam', 'date', 'url']
        for column in columns_to_drop:
            if column in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE videos DROP COLUMN {column}")
                    print(f"✅ Colonne {column} supprimée")
                except pymysql.err.OperationalError as e:
                    print(f"❌ Erreur suppression {column}: {e}")
            else:
                print(f"ℹ️  Colonne {column} n'existe pas")
        
        # Ajouter les nouvelles colonnes si elles n'existent pas
        columns_to_add = [
            ("video_url", "VARCHAR(500) NOT NULL"),
            ("video_id", "VARCHAR(100)"),
            ("type", "VARCHAR(50) DEFAULT 'khutbah'"),
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE videos ADD COLUMN {column_name} {column_type}")
                    print(f"✅ Colonne {column_name} ajoutée")
                except pymysql.err.OperationalError as e:
                    print(f"❌ Erreur ajout {column_name}: {e}")
            else:
                print(f"ℹ️  Colonne {column_name} existe déjà")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ Table videos mise à jour avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    update_videos_table()
