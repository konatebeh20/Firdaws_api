# 🔧 Guide complet : Configuration PostgreSQL Docker pour Firdaws_api

## 📋 RÉSUMÉ DES CORRECTIONS EFFECTUÉES

### 1. ✅ config.env corrigé
<!-- - **Avant** : `DATABASE_URL=postgresql://postgres:firdaws_pass@localhost:5433/firdaws_db` -->
- **Avant** : `DATABASE_URL=postgresql://postgres:firdaws_pass@localhost:5432/firdaws_db`
- **Après** : `DATABASE_URL=postgresql://postgres:firdaws_pass@db:5432/firdaws_db`
- **Pourquoi** : Dans Docker, les conteneurs communiquent par nom de service, pas par localhost

### 2. ✅ app.py corrigé
- Ajout de l'import de tous les modèles SQLAlchemy avant `db.create_all()`
- **Pourquoi** : SQLAlchemy doit connaître les modèles avant de créer les tables

### 3. ✅ migrations/env.py corrigé
- Ajout de l'import des modèles pour Flask-Migrate
- **Pourquoi** : Alembic doit détecter les modèles pour générer les migrations

---

## 🚀 COMMANDES À EXÉCUTER (DANS L'ORDRE)

### ÉTAPE 1 : Nettoyer et reconstruire les conteneurs

```powershell
# Naviguer vers Firdaws_api
cd D:\Company's\Holding\TechZone\firdaws_masdjid\Firdaws_api

# Arrêter et supprimer les conteneurs et volumes
docker-compose down -v

# Supprimer le dossier migrations existant (optionnel mais recommandé)
Remove-Item -Recurse -Force migrations

# Reconstruire et démarrer
docker-compose up --build -d
```

### ÉTAPE 2 : Initialiser Flask-Migrate

```powershell
# Exécuter dans le conteneur backend
docker exec -it firdaws_api_backend_1 flask db init
```

### ÉTAPE 3 : Générer la migration initiale

```powershell
# Exécuter dans le conteneur backend
docker exec -it firdaws_api_backend_1 flask db migrate -m "Migration initiale"
```

### ÉTAPE 4 : Appliquer la migration

```powershell
# Exécuter dans le conteneur backend
docker exec -it firdaws_api_backend_1 flask db upgrade
```

### ÉTAPE 5 : Vérifier les tables dans PostgreSQL

```powershell
# Se connecter au conteneur PostgreSQL
docker exec -it postgres_db psql -U postgres -d firdaws_db

# Dans psql, lister les tables
\dt

# Quitter psql
\q
```

### ÉTAPE 6 : Vérifier les admins par défaut

```powershell
# Se connecter à PostgreSQL
docker exec -it postgres_db psql -U postgres -d firdaws_db

# Vérifier la table admins
SELECT * FROM admins;

# Quitter psql
\q
```

---

## 🔍 VÉRIFICATIONS DANS DBeaver

### 1. Connexion DBeaver
- **Host** : `localhost`
<!-- - **Port** : `5433` -->
- **Port** : `5432`
- **Database** : `firdaws_db`
- **Username** : `postgres`
- **Password** : `firdaws_pass`

### 2. Vérifier les tables
Dans DBeaver, naviguez vers :
```
firdaws_db
└── public
    └── Tables
```

Vous devriez voir :
- `admins`
- `users`
- `documents`
- `quizzes`
- `events`
- `errors`
- `informations`
- `mails`
- `notifications`
- `readings`
- `trainings`
- `videos`
- `khutba`
- `reset_tokens`
- `firewall_logs`
- `blocked_ips`
- `dons`

### 3. Vérifier les admins
Clic droit sur table `admins` → "Edit Data" → vous devriez voir :
- `admin@firdaws-banco.org`
- `admin@firdaws-banco.ci`

---

## 🎯 WORKFLOW POUR LES FUTURES MIGRATIONS

### Quand modifier les modèles ?
1. Modifier `model/firdaws_db.py`
2. Générer une migration : `docker exec -it firdaws_api_backend_1 flask db migrate -m "Description"`
3. Appliquer la migration : `docker exec -it firdaws_api_backend_1 flask db upgrade`

### Commandes utiles

```powershell
# Voir l'historique des migrations
docker exec -it firdaws_api_backend_1 flask db history

# Annuler la dernière migration
docker exec -it firdaws_api_backend_1 flask db downgrade

# Vérifier l'état de la base
docker exec -it firdaws_api_backend_1 flask db current
```

---

## ❓ QUEL CONTENEUR UTILISER ?

Pour le projet Firdaws_api (Mosquée) :
- **Utiliser uniquement** : `D:\Firdaws_api\docker-compose.yml`
- **Commande** : `docker-compose up -d` (depuis `D:\Firdaws_api`)
<!-- - **Conteneur** : `postgres_db` (port 5433) -->
- **Conteneur** : `postgres_db` (port 5432)
- **Base** : `firdaws_db`

---

## 🐛 DÉPANNAGE

### Problème : "Connection refused"
**Cause** : Conteneur PostgreSQL non démarré
**Solution** :
```powershell
docker-compose up -d
docker logs postgres_db
```

### Problème : "No module named 'model.firdaws_db'"
**Cause** : Import incorrect dans app.py ou env.py
**Solution** : Vérifier que les imports sont corrects (déjà corrigés)

### Problème : Tables non créées
**Cause** : Migration non appliquée
**Solution** :
```powershell
docker exec -it firdaws_api_backend_1 flask db upgrade
```

### Problème : Admins non créés
**Cause** : seed_default_admins() non exécuté
**Solution** :
```powershell
# Exécuter manuellement le seed
docker exec -it firdaws_api_backend_1 python -c "from app import seed_default_admins; from app import app; seed_default_admins()"
```

---

## ✅ CHECKLIST FINALE

- [ ] config.env corrigé (db:5432)
- [ ] app.py avec imports des modèles
- [ ] migrations/env.py avec imports des modèles
- [ ] Conteneurs Docker reconstruits
- [ ] Flask-Migrate initialisé
- [ ] Migration générée
- [ ] Migration appliquée
- [ ] Tables visibles dans DBeaver
- [ ] Admins créés
- [ ] API accessible sur http://127.0.0.1:5000

---

## 📝 NOTES IMPORTANTES

1. **Ne jamais utiliser localhost** dans les variables d'environnement Docker pour les connexions inter-conteneurs
2. **Toujours importer les modèles** avant db.create_all() ou flask db migrate
3. **Utiliser Flask-Migrate** pour les modifications de schéma (pas db.create_all() en production)
