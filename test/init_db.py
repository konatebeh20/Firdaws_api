import sys
import traceback
from sqlalchemy import inspect

from app import app
from config.db import db


def main():
    with app.app_context():
        try:
            # Affiche l'URL de connexion utilisée par SQLAlchemy
            print("DB URL:", db.engine.url)

            # Vérifier la connexion
            conn = db.engine.connect()
            print("✅ Connexion à PostgreSQL réussie !")

            # Forcer la création des tables définies par les models
            print("Création des tables (db.create_all())...")
            db.create_all()
            print("✅ db.create_all() exécuté")

            # Lister les tables créées
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tables dans la base: {tables}")

        except Exception as e:
            print("❌ Erreur lors de la création des tables:")
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
