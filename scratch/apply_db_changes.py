import sys
import os
from sqlalchemy import text

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from config.db import db

def apply_changes():
    print("\n🛠️ APPLICATION MANUELLE DES CHANGEMENTS DE BASE DE DONNÉES\n")
    
    with app.app_context():
        try:
            # Ajouter la colonne 'author' si elle n'existe pas
            print("⏳ Ajout de la colonne 'author' à la table 'documents'...")
            db.session.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS author VARCHAR(100)"))
            
            # Ajouter la colonne 'type' si elle n'existe pas
            print("⏳ Ajout de la colonne 'type' à la table 'documents'...")
            db.session.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS type VARCHAR(50) DEFAULT 'PDF'"))
            
            db.session.commit()
            print("✅ Changements appliqués avec succès !")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'application des changements : {str(e)}")

if __name__ == "__main__":
    apply_changes()
