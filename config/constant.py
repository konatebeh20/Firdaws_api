import os
from datetime import timedelta

# ========== ENVIRONNEMENT ==========
FLASK_ENV = os.environ.get('FLASK_ENV', 'development').lower()
DEBUG = os.environ.get('DEBUG', 'true').lower() == 'true'

# ========== CORS ==========
CORS_ORIGINS = ['http://localhost:4200', 'http://localhost:5000', 'http://127.0.0.1:5000']
BASE_URL = '/api'

# ========== UPLOAD ==========
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# ========== EMAIL SMTP (directement configuré) ==========
SMTP_ENABLED = True
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'contact@firdaws-mosque.ci'
SMTP_PASSWORD = 'xxxx-xxxx-xxxx-xxxx'  # À remplacer par un vrai mot de passe d'application Gmail

# Configuration alternative (si Gmail ne fonctionne pas)
# SMTP_SERVER = 'smtp.office365.com'
# SMTP_PORT = 587

MAIL_SERVER = SMTP_SERVER
MAIL_PORT = SMTP_PORT
MAIL_USE_TLS = True
MAIL_USERNAME = SMTP_USERNAME
MAIL_PASSWORD = SMTP_PASSWORD

# ========== SÉCURITÉ ==========
SECRET_KEY = os.environ.get('SECRET_KEY') or 'firdaws-super-ultra-secret-app-key-2026-secure'
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'firdaws-super-ultra-secret-jwt-key-2026-secure'
BCRYPT_ROUNDS = 12

# ========== JWT ==========
# En développement : 24h, en production : 1h
if FLASK_ENV == 'production':
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)   # Production: 1 heure
else:
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)    # Développement: 7 jours

JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# ========== PAGINATION ==========
ITEMS_PER_PAGE = 10

# ========== BASE DE DONNÉES ==========
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_SQLITE_DB = os.path.join(BASE_DIR, 'firdaws.db')

# DEFAULT_SQLITE_DB_URI : Xampp
DEFAULT_SQLITE_DB_URI = f"sqlite:///{DEFAULT_SQLITE_DB.replace(chr(92), '/')}"
# DEFAULT_SQLITE_DB_URI = f"sqlite:///{DEFAULT_SQLITE_DB.replace(chr(92), '/')}"

# ========== CHOIX DE LA BASE DE DONNÉES ==========
# Priorité : Variable d'environnement > Fallback local

# ========== BASE DE DONNÉES MySQL (Xampp) - directement configuré ==========
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'firdaws_db'

# FORCER MySQL Xampp - ignorer les autres configurations
LIEN_BASE_DE_DONNEES = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
# LIEN_BASE_DE_DONNEES = 'mysql+pymysql://root:@localhost/mapxpress'

# C'EST TOUT ! LIEN_BASE_DE_DONNEES est maintenant défini

SQL_DB_URL = LIEN_BASE_DE_DONNEES
SQLALCHEMY_TRACK_MODIFICATIONS = False
SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE', 'threading').lower()

# Engine options selon type de base
if SQL_DB_URL.startswith('sqlite'):
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'check_same_thread': False}
    }
elif SQL_DB_URL.startswith('mongodb'):
    raise ValueError(
        ' MongoDB n\'est pas supporté par Flask-SQLAlchemy. '
        'Utilisez PostgreSQL, MySQL ou SQLite.'
    )
else:  # MySQL, PostgreSQL, etc.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

# ========== HONEYPOT ==========
HONEYPOT_FIELDS = ['honeypot', 'website', 'url', 'confirm_email']
HONEYPOT_MESSAGES = [
    ' Bot détecté - IP bloquée',
    ' Accès non autorisé',
    ' Activité suspecte détectée'
]

# ========== FIREWALL ==========
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT_MINUTES = 15
BLOCKLIST_DURATION_HOURS = 24

# ========== BACKLOG ==========
BACKLOG_FILE = 'backlog.txt'
BACKLOG_ENCRYPTION_KEY = 'nour-firdaws-backlog-encryption-key-2026'

# ========== CONFIG CLASS ==========
class Config:
    """Base configuration."""
    SECRET_KEY = SECRET_KEY
    DEBUG = DEBUG
    BASE_URL = BASE_URL
    SQLALCHEMY_DATABASE_URI = SQL_DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = SQLALCHEMY_TRACK_MODIFICATIONS
    SQLALCHEMY_ENGINE_OPTIONS = SQLALCHEMY_ENGINE_OPTIONS
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH
    CORS_ORIGINS = CORS_ORIGINS
    MAIL_SERVER = MAIL_SERVER
    MAIL_PORT = MAIL_PORT
    MAIL_USE_TLS = MAIL_USE_TLS
    MAIL_USERNAME = MAIL_USERNAME
    MAIL_PASSWORD = MAIL_PASSWORD
    JWT_SECRET_KEY = JWT_SECRET_KEY
    SOCKETIO_ASYNC_MODE = SOCKETIO_ASYNC_MODE
    JWT_ACCESS_TOKEN_EXPIRES = JWT_ACCESS_TOKEN_EXPIRES
    JWT_REFRESH_TOKEN_EXPIRES = JWT_REFRESH_TOKEN_EXPIRES
    BCRYPT_ROUNDS = BCRYPT_ROUNDS
    HONEYPOT_FIELDS = HONEYPOT_FIELDS
    HONEYPOT_MESSAGES = HONEYPOT_MESSAGES
    MAX_LOGIN_ATTEMPTS = MAX_LOGIN_ATTEMPTS
    LOGIN_TIMEOUT_MINUTES = LOGIN_TIMEOUT_MINUTES
    BLOCKLIST_DURATION_HOURS = BLOCKLIST_DURATION_HOURS
    BACKLOG_FILE = BACKLOG_FILE
    BACKLOG_ENCRYPTION_KEY = BACKLOG_ENCRYPTION_KEY
    ITEMS_PER_PAGE = ITEMS_PER_PAGE

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/firdaws_db"

# ========== VALIDATION ==========
def validate_env():
    """Valide les variables d'environnement requises."""
    if FLASK_ENV == 'production':
        required = ['SECRET_KEY', 'JWT_SECRET_KEY']
        missing = [var for var in required if not os.environ.get(var)]
        if missing:
            raise Exception(
                f"\n VARIABLES MANQUANTES EN PRODUCTION : {', '.join(missing)}\n"
                f"👉 Définis ces variables dans ton environnement ou .env\n"
            )
    else:
        missing = []
        if not os.environ.get('SECRET_KEY'):
            missing.append('SECRET_KEY')
        if not os.environ.get('JWT_SECRET_KEY'):
            missing.append('JWT_SECRET_KEY')
        if missing:
            print(
                f"\n  Variables manquantes : {', '.join(missing)}\n"
                f"   Utilisation des valeurs de développement par défaut.\n"
            )
    
    # Affiche la base utilisée
    print(f"\nBase de données : {SQL_DB_URL}")
    print(f"Environnement : {FLASK_ENV}\n")

validate_env()
