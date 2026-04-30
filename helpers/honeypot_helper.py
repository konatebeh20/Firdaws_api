from flask import request
from datetime import datetime
import random
from config.constant import HONEYPOT_FIELDS, HONEYPOT_MESSAGES
from helpers.firewall_helper import FirewallHelper
from logger.logger_config import get_logger

logger = get_logger()

class HoneypotHelper:
    """Helper pour les champs honeypot anti-bots"""
    
    @staticmethod
    def check_honeypot(data):
        """
        Vérifie si un champ honeypot est rempli (signe de bot)
        Retourne (is_bot, message, details)
        """
        if not data:
            return False, None, None
        
        for field in HONEYPOT_FIELDS:
            if field in data and data[field] and str(data[field]).strip():
                # Bot détecté !
                details = {
                    'field': field,
                    'value': str(data[field])[:100],
                    'ip': FirewallHelper.get_client_ip(),
                    'fingerprint': FirewallHelper.generate_fingerprint(),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                message = random.choice(HONEYPOT_MESSAGES)
                
                # Log l'intrusion
                FirewallHelper.log_intrusion(
                    severity='MEDIUM',
                    attack_type='HONEYPOT_TRIGGERED',
                    details=details
                )
                
                logger.warning(f"🍯 HONEYPOT: {field} rempli - IP: {details['ip']}")
                
                return True, message, details
        
        return False, None, None
    
    @staticmethod
    def generate_honeypot_fields():
        """Génère des champs honeypot pour les formulaires"""
        fields = []
        for field_name in HONEYPOT_FIELDS:
            # 30% de chance d'inclure chaque champ
            if random.random() < 0.3:
                fields.append({
                    'name': field_name,
                    'class': 'honeypot-field',
                    'style': 'display:none;',
                    'tabindex': '-1',
                    'autocomplete': 'off'
                })
        
        return fields
