import os
import json
import hashlib
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from config.constant import BACKLOG_FILE, BACKLOG_ENCRYPTION_KEY
from logger.logger_config import get_logger

logger = get_logger()

class BacklogHelper:
    """Helper pour le backlog sécurisé (simulation fichier txt)"""
    
    @staticmethod
    def _get_cipher():
        """Crée un cipher Fernet pour le chiffrement"""
        # Dériver une clé de 32 bytes depuis la clé de configuration
        key = hashlib.sha256(BACKLOG_ENCRYPTION_KEY.encode()).digest()
        key = base64.urlsafe_b64encode(key[:32])
        return Fernet(key)
    
    @staticmethod
    def encrypt_data(data):
        """Chiffre les données"""
        cipher = BacklogHelper._get_cipher()
        json_str = json.dumps(data, default=str)
        return cipher.encrypt(json_str.encode()).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data):
        """Déchiffre les données"""
        try:
            cipher = BacklogHelper._get_cipher()
            decrypted = cipher.decrypt(encrypted_data.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Erreur déchiffrement backlog: {e}")
            return []
    
    @staticmethod
    def read_backlog():
        """Lit le backlog chiffré"""
        if not os.path.exists(BACKLOG_FILE):
            return []
        
        try:
            with open(BACKLOG_FILE, 'r') as f:
                encrypted = f.read()
                if encrypted:
                    return BacklogHelper.decrypt_data(encrypted)
                return []
        except Exception as e:
            logger.error(f"Erreur lecture backlog: {e}")
            return []
    
    @staticmethod
    def write_backlog(data):
        """Écrit le backlog chiffré"""
        try:
            encrypted = BacklogHelper.encrypt_data(data)
            with open(BACKLOG_FILE, 'w') as f:
                f.write(encrypted)
            return True
        except Exception as e:
            logger.error(f"Erreur écriture backlog: {e}")
            return False
    
    @staticmethod
    def add_admin(admin_data):
        """Ajoute un admin au backlog"""
        backlog = BacklogHelper.read_backlog()
        
        # Ne pas stocker le mot de passe en clair
        secure_admin = {
            'id': len(backlog) + 1,
            'username': admin_data['username'],
            'email': admin_data['email'],
            'phone': admin_data['phone'],
            'passwordHash': admin_data['password_hash'],
            'registeredAt': datetime.utcnow().isoformat(),
            'role': admin_data.get('role', 'admin'),
            'lastLogin': None,
            'isActive': True
        }
        
        backlog.append(secure_admin)
        BacklogHelper.write_backlog(backlog)
        
        logger.info(f"✅ Admin ajouté au backlog: {admin_data['email']}")
        return secure_admin
    
    @staticmethod
    def get_backlog_stats():
        """Statistiques du backlog"""
        backlog = BacklogHelper.read_backlog()
        
        admins = [a for a in backlog if a.get('role') == 'admin']
        superadmins = [a for a in backlog if a.get('role') == 'superadmin']
        
        return {
            'total_entries': len(backlog),
            'total_admins': len(admins),
            'total_superadmins': len(superadmins),
            'last_update': datetime.utcnow().isoformat(),
            'file_exists': os.path.exists(BACKLOG_FILE),
            'file_size': os.path.getsize(BACKLOG_FILE) if os.path.exists(BACKLOG_FILE) else 0
        }
