# Firdaws API - Backend

## Description
API RESTful pour la gestion de la mosquée Firdaws Cité Bel Aire du Banco.

## Base de données
**IMPORTANT : Ce projet utilise désormais MySQL via Xampp au lieu de Supabase PostgreSQL.**

### Configuration MySQL (Xampp)
- **Hôte** : localhost
- **Port** : 3306
- **Utilisateur** : root
- **Mot de passe** : (vide)
- **Base de données** : firdaws_db

### Configuration
La configuration de la base de données est définie dans `config/constant.py` :
```python
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'firdaws_db'
```

### Installation de Xampp
1. Télécharger Xampp depuis https://www.apachefriends.org/
2. Installer Xampp avec MySQL et Apache
3. Démarrer le service MySQL depuis le Xampp Control Panel
4. La base de données `firdaws_db` sera créée automatiquement lors du premier lancement

## Installation

### Prérequis
- Python 3.8+
- Xampp (MySQL)
- pip

### Étapes d'installation

1. Cloner le repository
```bash
git clone <repository-url>
cd Firdaws_api
```

2. Créer un environnement virtuel
```bash
python -m venv venv
venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Démarrer Xampp et MySQL

5. Exécuter le script de configuration de la base de données
```bash
python setup_database.py
```

6. Lancer l'application
```bash
python app.py
```

L'API sera accessible sur http://127.0.0.1:5000

## Configuration SMTP

La configuration SMTP est définie dans `config/constant.py` :

```python
SMTP_ENABLED = True
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'contact@firdaws-mosque.ci'
SMTP_PASSWORD = 'xxxx-xxxx-xxxx-xxxx'  # Remplacer par un vrai mot de passe d'application Gmail
```

**IMPORTANT :** Pour Gmail, vous devez générer un mot de passe d'application de 16 caractères depuis :
https://myaccount.google.com/apppasswords

## Comptes administrateurs par défaut

Deux comptes administrateurs sont créés automatiquement :

1. **Email** : admin@firdaws-banco.org
   **Mot de passe** : firdaws123

2. **Email** : admin@firdaws-banco.ci
   **Mot de passe** : firdaws123

## Structure de la base de données

### Tables principales
- **users** : Utilisateurs (incluant les administrateurs avec role='admin')
- **events** : Événements de la mosquée
- **documents** : Documents et ressources
- **videos** : Vidéos et contenu multimédia
- **infos** : Informations et annonces
- **trainings** : Formations et cours

### Tables additionnelles
- **blocked_ips** : Adresses IP bloquées
- **firewall_logs** : Logs de sécurité
- **reset_tokens** : Tokens de réinitialisation de mot de passe

## API Endpoints

### Authentification
- `POST /api/auth/login` - Connexion admin
- `GET /api/auth/profile` - Profil admin (requiert authentification)

### Événements
- `GET /api/events` - Liste des événements
- `GET /api/events/<id>` - Détail d'un événement
- `POST /api/events` - Créer un événement (admin)
- `PUT /api/events/<id>` - Modifier un événement (admin)
- `DELETE /api/events/<id>` - Supprimer un événement (admin)

### Documents
- `GET /api/documents` - Liste des documents
- `POST /api/documents` - Ajouter un document (admin)

### Vidéos
- `GET /api/videos` - Liste des vidéos
- `POST /api/videos` - Ajouter une vidéo (admin)

## Sécurité

- Authentification par token JWT
- Hachage des mots de passe avec bcrypt
- Protection contre les attaques CSRF
- Validation des données

## Développement

### Mode développement
Le mode développement est activé par défaut dans `config/constant.py` :
```python
FLASK_ENV = 'development'
DEBUG = True
```

### Logs
Les logs sont enregistrés dans le dossier `logs/`

## Migration depuis Supabase

Si vous migrez depuis Supabase vers Xampp MySQL :

1. Exécuter le script de migration :
```bash
python migrate_data.py
```

2. Le script va :
   - Connecter à Supabase PostgreSQL
   - Récupérer les données (événements, utilisateurs)
   - Les insérer dans MySQL Xampp
   - Hacher les mots de passe avec bcrypt

## Support

Pour toute question ou problème, contactez l'équipe technique.

## License

Copyright © 2026 Firdaws Mosque Cité Bel Aire du Banco
