import hashlib
import json
from datetime import datetime, timedelta
from flask import request
from config.db import db
from model.firdaws_db import FirewallLog, BlockedIP
from logger.logger_config import get_logger

logger = get_logger()

class FirewallHelper:
    """Helper pour le pare-feu et la détection d'intrusions"""
    
    @staticmethod
    def get_client_ip():
        """Récupère l'IP réelle du client"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
        return request.remote_addr
    
    @staticmethod
    def get_client_info():
        """Récupère toutes les informations du client"""
        return {
            'ip': FirewallHelper.get_client_ip(),
            'user_agent': request.headers.get('User-Agent', ''),
            'referer': request.headers.get('Referer', ''),
            'origin': request.headers.get('Origin', ''),
            'host': request.headers.get('Host', ''),
            'method': request.method,
            'path': request.path,
            'timestamp': datetime.utcnow().isoformat(),
            'headers': dict(request.headers),
            'cookies': dict(request.cookies),
            'args': dict(request.args),
            'form': dict(request.form) if request.form else {}
        }
    
    @staticmethod
    def generate_fingerprint():
        """Génère une empreinte unique du client"""
        info = FirewallHelper.get_client_info()
        fingerprint_string = f"{info['ip']}{info['user_agent']}{info['host']}"
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    @staticmethod
    def is_ip_blocked(ip=None):
        """Vérifie si une IP est bloquée"""
        if not ip:
            ip = FirewallHelper.get_client_ip()
        
        blocked = BlockedIP.query.filter(
            BlockedIP.ip == ip,
            BlockedIP.expires_at > datetime.utcnow()
        ).first()
        
        return blocked is not None
    
    @staticmethod
    def block_ip(ip, reason, duration_hours=24):
        """Bloque une IP"""
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        blocked = BlockedIP(
            ip=ip,
            reason=reason,
            expires_at=expires_at,
            fingerprint=FirewallHelper.generate_fingerprint()
        )
        
        db.session.add(blocked)
        db.session.commit()
        
        logger.warning(f"🚫 IP BLOQUÉE: {ip} - {reason}")
        return blocked
    
    @staticmethod
    def log_intrusion(severity, attack_type, details):
        """Log une tentative d'intrusion"""
        log = FirewallLog(
            ip=FirewallHelper.get_client_ip(),
            fingerprint=FirewallHelper.generate_fingerprint(),
            severity=severity,
            attack_type=attack_type,
            details=json.dumps(details),
            user_agent=request.headers.get('User-Agent'),
            path=request.path,
            method=request.method,
            created_at=datetime.utcnow()
        )
        
        db.session.add(log)
        db.session.commit()
        
        # Si sévérité haute, bloquer l'IP
        if severity in ['HIGH', 'CRITICAL']:
            FirewallHelper.block_ip(
                log.ip,
                f"Intrusion détectée: {attack_type}",
                24
            )
        
        logger.critical(f"🔥 INTRUSION: {severity} - {attack_type} - {log.ip}")
        return log