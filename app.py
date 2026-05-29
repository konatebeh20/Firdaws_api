import os
import traceback

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_socketio import SocketIO

from config.constant import DevelopmentConfig, ProductionConfig
from config.db import db
from logger.logger_config import get_logger

# ========== IMPORT DES RESSOURCES ==========
from resources.admin_auth import AuthApi
from resources.admin import AdminsApi
from resources.users import UsersApi
from resources.events import EventApi
from resources.videos import VideoApi
from resources.documents import DocumentApi
from resources.infos import InfoApi
from resources.khutba import KhutbaApi
from resources.file_upload import FileApi
from resources.search import SearchApi
from resources.validation import ValidationApi
from resources.pagination import PaginationApi
from resources.errors import ErrorsApi
from resources.tracker import TrackerApi
from resources.contact import ContactApi
from resources.helpers import SendEmail, SendPush, Contact
from resources.dons import DonsAPI
from resources.quiz import QuizApi

<<<<<<< HEAD
from resources.users import UsersApi
from resources.admin import AdminsApi
from resources.dons import DonsAPI

from resources.quiz import QuizApi


from helpers.auth_helper import token_required, admin_required, superadmin_required
from helpers.error_helper import log_error

=======
from helpers.error_helper import log_error
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309

# Logger
logger = get_logger()

# ========== INITIALISATION FLASK ==========
app = Flask(__name__,
    static_folder='template/static',
    template_folder='template'
)

env = os.environ.get('FLASK_ENV', 'development')
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

app.config.from_object(config_map.get(env, DevelopmentConfig))
app.secret_key = app.config['SECRET_KEY']
BASE_URL = app.config.get('BASE_URL', '/api')

# CORS
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/helpers/*": {"origins": "*"}
}, supports_credentials=True)

# Base de données
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()
<<<<<<< HEAD
    print("✅ Tables vérifiées / créées")

CORS(app)


=======
    print("Tables vérifiées / créées")
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309

# API Restful
api = Api(app)

# WebSocket
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'threading')
)

if not hasattr(app, 'extensions'):
    app.extensions = {}
app.extensions['socketio'] = socketio

# ========== ROUTES API ==========

# AUTHENTIFICATION
api.add_resource(AuthApi,
    '/api/auth/<string:route>',
    '/api/auth/<string:route>/<int:item_id>',
    endpoint='auth',
    methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])

# USERS
api.add_resource(UsersApi,
    '/api/users',
    '/api/users/<int:item_id>',
    '/api/users/<string:route>',
    '/api/users/<string:route>/<int:item_id>',
    endpoint='users',
    methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])

# ADMINS
api.add_resource(AdminsApi,
    '/api/admins',
    '/api/admins/<int:item_id>',
    '/api/admins/<string:route>',
    '/api/admins/<string:route>/<int:item_id>',
    endpoint='admins',
    methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])

# USERS
api.add_resource( UsersApi, '/api/users', '/api/users/<int:item_id>', '/api/users/<string:route>', '/api/users/<string:route>/<int:item_id>', endpoint='users', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])

# ADMINS (pour le dashboard)
api.add_resource(AdminsApi, '/api/admins', '/api/admins/<int:item_id>', '/api/admins/<string:route>', '/api/admins/<string:route>/<int:item_id>', endpoint='admins', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])

# ÉVÉNEMENTS
api.add_resource(EventApi,
    '/api/events',
    '/api/events/<int:item_id>',
    '/api/events/<string:route>',
    '/api/events/<string:route>/<int:item_id>',
    endpoint='events',
    methods=['GET', 'POST', 'PUT', 'DELETE'])

# VIDÉOS
api.add_resource(VideoApi,
    '/api/videos',
    '/api/videos/<int:item_id>',
    '/api/videos/<string:route>',
    '/api/videos/<string:route>/<int:item_id>',
    endpoint='videos',
    methods=['GET', 'POST', 'PUT', 'DELETE'])

# DOCUMENTS
api.add_resource(DocumentApi,
    '/api/documents',
    '/api/documents/<int:item_id>',
    '/api/documents/<string:route>',
    '/api/documents/<string:route>/<int:item_id>',
    endpoint='documents',
    methods=['GET', 'POST', 'PUT', 'DELETE'])

# QUIZ
api.add_resource(QuizApi,
    '/api/quiz',
    '/api/quiz/<int:quiz_id>',
    endpoint='quiz',
    methods=['GET', 'POST', 'PUT', 'DELETE'])

# Quiz
api.add_resource(QuizApi, '/api/quiz', '/api/quiz/<int:quiz_id>', endpoint='quiz', methods=['GET', 'POST', 'PUT', 'DELETE'])
api.add_resource(QuizApi, '/api/quiz/generate', endpoint='quiz_generate', methods=['POST'])


# INFORMATIONS
api.add_resource(InfoApi,
    '/api/infos',
    '/api/infos/<int:item_id>',
    '/api/infos/<string:route>',
    '/api/infos/<string:route>/<int:item_id>',
    endpoint='infos',
    methods=['GET', 'POST', 'PUT', 'DELETE'])

# ANNONCES (alias de /api/infos)
api.add_resource(InfoApi,
    '/api/annonces',
    '/api/annonces/<int:item_id>',
    '/api/annonces/<string:route>',
    '/api/annonces/<string:route>/<int:item_id>',
    endpoint='annonces',
    methods=['GET', 'POST', 'PUT', 'DELETE'])

# ANNONCES (alias de /api/infos pour le dashboard Angular)
api.add_resource(InfoApi, '/api/annonces', '/api/annonces/<int:item_id>', '/api/annonces/<string:route>', '/api/annonces/<string:route>/<int:item_id>', endpoint='annonces', methods=['GET', 'POST', 'PUT', 'DELETE'])

# KHOTBAS
api.add_resource(KhutbaApi,
    '/api/khotbas',
    '/api/khotbas/<int:item_id>',
    '/api/khotbas/<string:route>',
    '/api/khotbas/<string:route>/<int:item_id>',
    endpoint='khotbas',
    methods=['GET', 'POST', 'PUT', 'DELETE'])

# FICHIERS
api.add_resource(FileApi,
    '/api/files',
    '/api/files/<string:route>',
    '/api/files/<string:route>/<int:item_id>',
    endpoint='files',
    methods=['GET', 'POST', 'PUT', 'DELETE'])

# RECHERCHE
api.add_resource(SearchApi,
    '/api/search',
    '/api/search/<string:route>',
    endpoint='search',
    methods=['GET'])

# VALIDATION
api.add_resource(ValidationApi,
    '/api/validate',
    '/api/validate/<string:route>',
    endpoint='validate',
    methods=['GET', 'POST'])

# PAGINATION
api.add_resource(PaginationApi,
    '/api/pagination',
    '/api/pagination/<string:route>',
    endpoint='pagination',
    methods=['GET'])

<<<<<<< HEAD
# ERREURS -User TrackerApi
api.add_resource(ErrorsApi, '/api/errors', '/api/errors/<string:route>', '/api/errors/<string:route>/<int:item_id>', endpoint='errors', methods=['GET', 'POST', 'DELETE'])

# TRACKER
#User Project
api.add_resource(TrackerApi, '/api/tracker/<string:route>', '/api/tracker/<string:route>/<int:item_id>', endpoint='tracker', methods=['GET', 'POST', 'PUT', 'DELETE'])
=======
# ERREURS
api.add_resource(ErrorsApi,
    '/api/errors',
    '/api/errors/<string:route>',
    '/api/errors/<string:route>/<int:item_id>',
    endpoint='errors',
    methods=['GET', 'POST', 'DELETE'])

# TRACKER
api.add_resource(TrackerApi,
    '/api/tracker/<string:route>',
    '/api/tracker/<string:route>/<int:item_id>',
    endpoint='tracker',
    methods=['GET', 'POST', 'PUT', 'DELETE'])
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309

# CONTACT
api.add_resource(ContactApi, '/api/contact', endpoint='contact', methods=['POST'])

# HELPERS
api.add_resource(SendEmail, '/helpers/send_email', endpoint='send_email', methods=['POST'])
api.add_resource(SendPush, '/helpers/send_push', endpoint='send_push', methods=['POST'])
api.add_resource(Contact, '/api/contact_simple', endpoint='contact_simple', methods=['POST'])

# DONS
api.add_resource(DonsAPI,
    '/api/dons',
    '/api/dons/<int:item_id>',
    '/api/dons/<string:route>',
    '/api/dons/<string:route>/<int:item_id>',
    endpoint='dons',
    methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])


<<<<<<< HEAD
#User Auth
api.add_resource(AuthApi, '/api/auth/<string:route>', endpoint='auth_all', methods=["GET","POST"])
api.add_resource(AuthApi, '/api/auth/<string:route>', endpoint='auth_all_patch', methods=["PATCH","DELETE"])

# DONS
api.add_resource(DonsAPI, '/api/dons', '/api/dons/<int:item_id>', '/api/dons/<string:route>', '/api/dons/<string:route>/<int:item_id>', endpoint='dons', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])



=======
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309
# ========== ROUTES FRONTEND ==========
@app.route(BASE_URL + '/')
@app.route(BASE_URL + '/<path:path>')
def serve_frontend(path='index.html'):
    if path.startswith('static/'):
        return send_from_directory('template', path)
    if path.startswith('uploads/'):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                  path.replace('uploads/', ''))
    return send_from_directory('template', 'index.html')

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ========== GESTIONNAIRE D'ERREURS ==========
@app.errorhandler(404)
def not_found(e):
    return jsonify({'message': 'Route non trouvée'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Erreur 500: {str(e)}")
    return jsonify({'message': 'Erreur interne du serveur'}), 500

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'OK',
        'message': 'Firdaws API est en ligne',
        'version': '1.0.0'
    }), 200


def seed_default_admins():
    """Crée les administrateurs par défaut s'ils n'existent pas."""
    from model.firdaws_db import Admin

    default_admins = [
        {
            'username': 'admin_firdaws_banco',
            'email': 'admin@firdaws-banco.org',
            'phone': '00000000',
            'role': 'superadmin',
            'password': 'firdaws123'
        },
        {
            'username': 'admin_firdaws_ci',
            'email': 'admin@firdaws-banco.ci',
            'phone': '00000000',
            'role': 'superadmin',
            'password': 'firdaws123'
        }
    ]

    for admin_data in default_admins:
        existing = Admin.query.filter_by(email=admin_data['email']).first()
        if not existing:
            admin = Admin(
                username=admin_data['username'],
                email=admin_data['email'],
                phone=admin_data['phone'],
                role=admin_data['role']
            )
            admin.set_password(admin_data['password'])
            db.session.add(admin)
            db.session.commit()
            print(f"Admin créé: {admin_data['email']}")
        else:
            existing.set_password(admin_data['password'])
            existing.username = admin_data['username']
            existing.role = admin_data['role']
            existing.is_active = True
            db.session.commit()
            print(f"Admin mis à jour: {admin_data['email']}")
    print("Seed des administrateurs terminé!")


if __name__ == '__main__':
    with app.app_context():
<<<<<<< HEAD
        # db.create_all()
=======
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309
        seed_default_admins()
        logger.info("Base de données initialisée")

    logger.info("Démarrage de Firdaws API avec WebSockets")
    print("\n" + "="*50)
    print("FIRDAWS API - Mosquee Firdaws Backend")
    print("="*50)
    print(f"Environnement: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Base de données: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print("="*50)
    print("Serveur démarré sur http://127.0.0.1:5000")
    print("WebSocket disponible sur ws://127.0.0.1:5000")
    print("="*50 + "\n")

    socketio.run(app, debug=app.config['DEBUG'], host="0.0.0.0", port=5000)
