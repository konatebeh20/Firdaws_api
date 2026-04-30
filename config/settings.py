# Flask Configuration Classes - Production Ready

import os
from datetime import timedelta

class Config:
    """Base configuration - shared by all environments"""
    
    # App
    APP_NAME = "Firdaws API"
    APP_VERSION = "1.0.0"
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
    DEBUG = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = True
    
    # Database
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'firdaws_app'
        }
    }
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-this')
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # 30 days
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS - Restrict in production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:4200').split(',')
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_MAX_AGE = 3600
    
    # API
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    # Pagination
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 10
    MAX_PER_PAGE = 100
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_STORAGE_URL = 'memory://'
    RATE_LIMIT_STRATEGY = 'moving-window'
    
    # Session
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JS access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    SESSION_COOKIE_NAME = 'firdaws_session'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Email (optional)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@firdaws.com')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 10
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
    
    # Supabase (if using external auth)
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    
    @staticmethod
    def init_app(app):
        """Initialize application with this config"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    # Database - MySQL Xampp local
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost:3306/firdaws_db'
    )
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'false').lower() == 'true'
    
    # CORS - Allow localhost clients
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:4200,http://localhost:3000,http://127.0.0.1:4200'
    ).split(',')
    
    # Session
    SESSION_COOKIE_SECURE = False  # HTTP allowed in dev
    
    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Longer in dev for testing
    
    # Rate limiting
    RATE_LIMIT_ENABLED = False  # Disable in dev for easier testing
    
    # Logging
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Database - MUST use environment variable
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("⚠️  DATABASE_URL environment variable not set!")
    
    # CORS - Strict whitelist required
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://yourdomain.com').split(',')
    if 'http://localhost' in CORS_ORIGINS:
        raise ValueError("⚠️  Development origins found in production config!")
    
    # Session - Maximum security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # JWT - Shorter token lifespan
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # 1 hour max
    
    # Rate limiting - Enable for API protection
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')  # Use Redis if available
    
    # Hidden errors for security
    PROPAGATE_EXCEPTIONS = False
    
    # Logging - Detailed for debugging production issues
    LOG_LEVEL = 'INFO'
    
    @staticmethod
    def init_app(app):
        """Production-specific initialization"""
        import logging
        
        # Log to syslog in production
        syslog_handler = logging.handlers.SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


class TestingConfig(Config):
    """Testing configuration"""
    
    DEBUG = True
    TESTING = True
    ENV = 'testing'
    
    # In-memory SQLite for fast tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # JWT - Long expiration for test convenience
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Rate limiting - Disable for tests
    RATE_LIMIT_ENABLED = False
    
    # Session
    SESSION_COOKIE_SECURE = False
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    @staticmethod
    def init_app(app):
        """Test-specific initialization"""
        pass


# Config selector
def get_config(env=None):
    """Get configuration class based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development').lower()
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    return configs.get(env, DevelopmentConfig)
