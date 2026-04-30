# 🚨 Résolution Erreur 535 Gmail - Guide Complet

## ❌ Problème Actuel
```
Erreur 535: Username and Password not accepted
```

**Cause**: Vous utilisez un mot de passe normal au lieu d'un mot de passe d'application Gmail.

## ✅ Solution Immédiate

### Étape 1: Activer l'Authentification à Deux Facteurs
1. Allez sur: https://myaccount.google.com/security
2. Cherchez "Authentification à deux facteurs"
3. Cliquez sur "Activer"
4. Suivez les instructions (téléphone, application, etc.)

### Étape 2: Générer un Mot de Passe d'Application
1. Allez sur: https://myaccount.google.com/apppasswords
2. Sous "Sélectionner une application", choisissez "Autre (nom personnalisé)"
3. Nommez-le: `Firdaws Mosque Website`
4. Cliquez sur "Générer"
5. **COPIEZ** le mot de passe de 16 caractères (ex: `abcd efgh ijkl mnop`)

### Étape 3: Mettre à jour config.env
```env
SMTP_PASSWORD=abcd efgh ijkl mnop
```
**Important**: Remplacez `abcd efgh ijkl mnop` par VOTRE mot de passe de 16 caractères.

### Étape 4: Redémarrer le Backend
```bash
# Arrêter le backend (Ctrl+C)
# Puis redémarrer
python app.py
```

## 🔍 Vérification

Après configuration, testez avec le formulaire de contact:
1. Allez sur: http://localhost:4200/main/contact-us
2. Remplissez le formulaire
3. Vous devriez voir: "Email envoyé avec succès"

## ⚠️ Points Importants

- **N'utilisez PAS** votre mot de passe Gmail normal
- **Utilisez OBLIGATOIREMENT** un mot de passe d'application de 16 caractères
- **Le mot de passe** ressemble à: `xxxx xxxx xxxx xxxx` (avec espaces)
- **Conservez-le** en lieu sûr

## 🛠️ Si Ça Ne Fonctionne Toujours Pas

1. **Vérifiez** que l'authentification à deux facteurs est bien activée
2. **Vérifiez** que vous utilisez bien le mot de passe de 16 caractères
3. **Essayez** de régénérer un nouveau mot de passe d'application
4. **Contactez-moi** si le problème persiste

## 📧 Alternative: Microsoft Outlook

Si Gmail ne fonctionne pas:
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=votre_email@outlook.com
SMTP_PASSWORD=votre_mot_de_passe_outlook
```

Une fois configuré correctement, les emails arriveront directement dans votre boîte de réception!
