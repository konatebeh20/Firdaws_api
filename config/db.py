from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import os

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialise la base de données avec l'application Flask"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Base de données initialisée avec succès")

def get_db():
    """Retourne l'instance de base de données"""
    return db