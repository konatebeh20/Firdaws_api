# Flask App Factory Pattern - Main entry point

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Flasgger
from config.settings import DevelopmentConfig, ProductionConfig, TestingConfig
from firdaws.middleware.error_handler import register_error_handlers
from firdaws.middleware.logging import init_logging
import os

# Initialize extensions (don't pass app yet)
db = SQLAlchemy()
cors = CORS()
swagger = Flasgger()


def create_app(config_name=None):
    """Application factory pattern"""
    
    # Determine config
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_map.get(config_name, DevelopmentConfig)
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['*']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    swagger.init_app(app)
    
    # Initialize logging
    init_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register database context
    with app.app_context():
        # Import models AFTER db init
        from firdaws.models import (
            User, Event, Info, Khutba, Document, Video
        )
        
        # Create tables
        db.create_all()
    
    # Register blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check for monitoring"""
        from utils.response import APIResponse
        return APIResponse.success({
            "status": "healthy",
            "version": "1.0.0",
            "environment": app.config.get('FLASK_ENV', 'unknown')
        }, "API is healthy", 200)
    
    # CLI commands
    setup_cli(app)
    
    return app


def register_blueprints(app):
    """Register all route blueprints"""
    from firdaws.routes import (
        auth_bp, events_bp, infos_bp, khutba_bp, 
        documents_bp, videos_bp, admin_bp, users_bp
    )
    
    # Register with URL prefix
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(events_bp, url_prefix='/api/v1/events')
    app.register_blueprint(infos_bp, url_prefix='/api/v1/infos')
    app.register_blueprint(khutba_bp, url_prefix='/api/v1/khutba')
    app.register_blueprint(documents_bp, url_prefix='/api/v1/documents')
    app.register_blueprint(videos_bp, url_prefix='/api/v1/videos')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    
    # Admin routes (protected)
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')


def setup_cli(app):
    """Setup Flask CLI commands"""
    
    @app.cli.command()
    def init_db():
        """Initialize the database"""
        db.create_all()
        print("✅ Database initialized")
    
    @app.cli.command()
    def seed_db():
        """Seed database with example data"""
        from firdaws.seed import seed_all
        seed_all(db)
        print("✅ Database seeded")
    
    @app.cli.command()
    def drop_db():
        """Drop all tables"""
        if input("⚠️  Drop all tables? (yes/no): ").lower() == 'yes':
            db.drop_all()
            print("✅ Database dropped")
        else:
            print("❌ Aborted")


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
