# Test & Initialisation DB

Ce dossier contient des scripts pour initialiser la base PostgreSQL utilisée par l'API.

Étapes (PowerShell) :

1. Se placer dans le dossier du projet :

   cd "D:\Company's\Holding\TechZone\firdaws_masdjid\Firdaws_api"

2. Activer l'environnement virtuel :

   venv\Scripts\activate

3. Lancer le script d'initialisation :

   python test/init_db.py

4. Vérifier dans DBeaver (host=localhost port=5433 database=firdaws_db user=postgres)

Flask-Migrate (si tu veux utiliser les migrations) :

1. Initialiser :
   flask db init
2. Créer une migration :
   flask db migrate -m "Initial migration"
3. Appliquer :
   flask db upgrade
