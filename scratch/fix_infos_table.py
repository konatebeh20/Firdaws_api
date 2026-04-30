import sys
import os
from sqlalchemy import text

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from config.db import db

def fix_infos_table():
    print("\n🛠️ CRÉATION DE LA TABLE INFOS\n")
    
    with app.app_context():
        try:
            # Vérifier si la table existe
            print("⏳ Vérification de l'existence de la table 'infos'...")
            result = db.session.execute(text("SHOW TABLES LIKE 'infos'"))
            table_exists = result.fetchone()
            
            if table_exists:
                print("✅ Table 'infos' existe déjà - vérification de la structure...")
                result = db.session.execute(text("DESCRIBE infos"))
                columns = result.fetchall()
                print(f"📋 Colonnes actuelles: {[col[0] for col in columns]}")
                
                # Compter les colonnes created_by
                created_by_count = sum(1 for col in columns if col[0] == 'created_by')
                
                if created_by_count > 1:
                    print(f"⚠️ {created_by_count} colonnes 'created_by' trouvées - correction nécessaire")
                    # Recréer la table
                    db.session.execute(text("DROP TABLE IF EXISTS infos"))
                else:
                    print("✅ Structure correcte - aucune action nécessaire")
                    return
            else:
                print("⚠️ Table 'infos' n'existe pas - création nécessaire")
            
            # Créer la table avec la structure correcte
            print("⏳ Création de la table 'infos'...")
            db.session.execute(text("""
                CREATE TABLE infos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR(50),
                    is_published BOOLEAN DEFAULT TRUE,
                    archived BOOLEAN DEFAULT FALSE,
                    published_at DATETIME,
                    created_by INT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES admins(id)
                )
            """))
            
            db.session.commit()
            print("✅ Table 'infos' créée avec succès !")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la création : {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_infos_table()
