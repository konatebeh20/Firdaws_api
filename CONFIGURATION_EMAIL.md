# Configuration Email SMTP - Guide d'Installation

## 📧 Configuration pour éviter les spams

### Étape 1: Configuration Gmail SMTP

1. **Activer l'authentification à deux facteurs** sur votre compte Gmail
2. **Générer un mot de passe d'application**:
   - Allez sur: https://myaccount.google.com/apppasswords
   - Sélectionnez "Autre (nom personnalisé)"
   - Nommez-le "Firdaws Mosque Website"
   - Copiez le mot de passe généré (16 caractères)

### Étape 2: Mettre à jour le fichier config.env

```env
# Configuration Email SMTP
SMTP_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=contact@firdaws-mosque.ci
SMTP_PASSWORD=votre_mot_de_passe_gmail_ici
```

**Important**: Remplacez `votre_mot_de_passe_gmail_ici` par le mot de passe d'application de 16 caractères.

### Étape 3: Redémarrer le backend

```bash
# Arrêter le backend (Ctrl+C)
# Redémarrer
python app.py
```

### Étape 4: Tester l'envoi d'emails

Le formulaire de contact enverra maintenant des emails réels à:
- **Destinataire principal**: contact@firdaws-mosque.ci
- **Avec reply-to**: L'email de l'utilisateur qui a rempli le formulaire

## 🔐 Mesures Anti-Spam Implémentées

1. **Headers professionnels**:
   - X-Mailer: Firdaws Mosque Website
   - X-MimeOLE: Produced By Firdaws Mosque
   - X-Priority: 3 (Normal)
   - Reply-To correctement configuré

2. **Template HTML professionnel**:
   - Design responsive
   - Informations complètes du contact
   - Branding de la mosquée

3. **Configuration SMTP optimisée**:
   - TLS encryption
   - Timeout de 30 secondes
   - Gestion d'erreurs détaillée

## 📧 Alternative: Microsoft Outlook

Si Gmail ne fonctionne pas, vous pouvez utiliser Outlook:

```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=votre_email@outlook.com
SMTP_PASSWORD=votre_mot_de_passe
```

## 🛠️ Dépannage

### Erreur: "Erreur de configuration SMTP"
- Vérifiez que le mot de passe d'application est correct (16 caractères)
- Assurez-vous que l'authentification à deux facteurs est activée

### Erreur: "Adresse email invalide"
- Vérifiez que l'email destinataire existe
- Assurez-vous qu'il n'y a pas de faute de frappe

### Les emails arrivent en spam
- Vérifiez le domaine de l'expéditeur
- Ajoutez l'email expéditeur à vos contacts
- Marquez un email comme "Non spam" pour entraîner le filtre

## ✅ Test de Configuration

Après configuration, testez avec le formulaire de contact:
1. Allez sur: http://localhost:4200/main/contact-us
2. Remplissez le formulaire
3. Vérifiez votre boîte mail (y compris le dossier spam)

Le message devrait apparaître dans votre boîte de réception principale!
