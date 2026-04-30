import json
import hashlib
from datetime import datetime, timedelta
from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import func

from config.constant import *
from config.db import db
from logger.logger_config import get_logger
from helpers.auth import token_required, admin_required, superadmin_required
from helpers.firewall_helper import FirewallHelper
from helpers.honeypot_helper import HoneypotHelper
from helpers.backlog_helper import BacklogHelper
from helpers.error_helper import log_error

from model.firdaws_db import (
    Event, Video, Document, Info, Khutba, Admin,
    FirewallLog, BlockedIP
)

logger = get_logger()

class TrackerApi(Resource):
    """
    Tracker unique pour TOUS les événements, vidéos, documents, admins, erreurs, firewall
    Architecture: 1 resource = TOUS les endpoints de tracking
    """
    
    # ========== GET ==========
    def get(self, route):
        """GET - Récupération de données"""
        
        # 📊 STATISTIQUES GLOBALES
        if route == 'get_dashboard_stats':
            return self.get_dashboard_stats()
        
        # 👥 ADMINS
        if route == 'get_all_admins':
            return self.get_all_admins()
        if route == 'get_admin_count':
            return self.get_admin_count()
        if route == 'get_backlog':
            return self.get_backlog()
        
        # 📅 ÉVÉNEMENTS
        if route == 'get_events_stats':
            return self.get_events_stats()
        if route == 'get_events_archived':
            return self.get_events_archived()
        
        # 🎥 VIDÉOS
        if route == 'get_videos_stats':
            return self.get_videos_stats()
        if route == 'get_videos_archived':
            return self.get_videos_archived()
        
        # 📄 DOCUMENTS
        if route == 'get_documents_stats':
            return self.get_documents_stats()
        if route == 'get_documents_archived':
            return self.get_documents_archived()
        
        # 🔥 FIREWALL & INTRUSIONS
        if route == 'get_firewall_logs':
            return self.get_firewall_logs()
        if route == 'get_blocked_ips':
            return self.get_blocked_ips()
        if route == 'get_intrusion_stats':
            return self.get_intrusion_stats()
        
        # ❌ ERREURS
        if route == 'get_errors':
            return self.get_errors()
        if route == 'get_errors_stats':
            return self.get_errors_stats()
        
        return {'message': f'Route {route} non trouvée'}, 404
    
    # ========== POST ==========
    @admin_required
    def post(self, current_admin, route):
        """POST - Création et actions"""
        
        # 🔥 FIREWALL & HONEYPOT
        if route == 'check_honeypot':
            return self.check_honeypot()
        if route == 'block_ip':
            return self.block_ip()
        if route == 'unblock_ip':
            return self.unblock_ip()
        if route == 'log_intrusion':
            return self.log_intrusion()
        
        # 📊 BACKLOG
        if route == 'export_backlog':
            return self.export_backlog()
        if route == 'sync_backlog':
            return self.sync_backlog()
        
        # 📅 ARCHIVAGE
        if route == 'archive_event':
            return self.archive_event()
        if route == 'archive_video':
            return self.archive_video()
        if route == 'archive_document':
            return self.archive_document()
        if route == 'archive_info':
            return self.archive_info()
        if route == 'archive_khutba':
            return self.archive_khutba()
        
        # 🔄 DÉSARCHIVAGE
        if route == 'unarchive_event':
            return self.unarchive_event()
        if route == 'unarchive_video':
            return self.unarchive_video()
        if route == 'unarchive_document':
            return self.unarchive_document()
        if route == 'unarchive_info':
            return self.unarchive_info()
        if route == 'unarchive_khutba':
            return self.unarchive_khutba()
        
        return {'message': f'Route {route} non trouvée'}, 404
    
    # ========== DELETE ==========
    @superadmin_required
    def delete(self, current_admin, route):
        """DELETE - Suppression définitive"""
        
        if route == 'clear_firewall_logs':
            return self.clear_firewall_logs()
        if route == 'clear_blocked_ips':
            return self.clear_blocked_ips()
        if route == 'clear_backlog':
            return self.clear_backlog()
        
        return {'message': f'Route {route} non trouvée'}, 404
    
    # ========== MÉTHODES STATISTIQUES GLOBALES ==========
    
    def get_dashboard_stats(self):
        """Stats complètes pour le dashboard admin"""
        try:
            stats = {
                'admins': {
                    'total': Admin.query.count(),
                    'active': Admin.query.filter_by(is_active=True).count(),
                    'backlog': BacklogHelper.get_backlog_stats()
                },
                'events': {
                    'total': Event.query.count(),
                    'active': Event.query.filter_by(archived=False).count(),
                    'archived': Event.query.filter_by(archived=True).count(),
                    'upcoming': Event.query.filter(
                        Event.date >= datetime.now().date(),
                        Event.archived == False
                    ).count()
                },
                'videos': {
                    'total': Video.query.count(),
                    'active': Video.query.filter_by(archived=False).count(),
                    'archived': Video.query.filter_by(archived=True).count(),
                    'khotbas': Video.query.filter_by(type='Khutba', archived=False).count(),
                    'formations': Video.query.filter_by(type='Formation', archived=False).count()
                },
                'documents': {
                    'total': Document.query.count(),
                    'active': Document.query.filter_by(archived=False).count(),
                    'archived': Document.query.filter_by(archived=True).count()
                },
                'infos': {
                    'total': Info.query.count(),
                    'active': Info.query.filter_by(archived=False).count(),
                    'archived': Info.query.filter_by(archived=True).count()
                },
                'khotbas': {
                    'total': Khutba.query.count(),
                    'active': Khutba.query.filter_by(archived=False).count(),
                    'archived': Khutba.query.filter_by(archived=True).count()
                },
                'firewall': {
                    'blocked_ips': BlockedIP.query.count(),
                    'intrusions': FirewallLog.query.count(),
                    'last_24h': FirewallLog.query.filter(
                        FirewallLog.created_at >= datetime.utcnow() - timedelta(hours=24)
                    ).count()
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {'data': stats}, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_dashboard_stats')
            return {'message': 'Erreur récupération stats'}, 500
    
    # ========== MÉTHODES ADMIN & BACKLOG ==========
    
    @superadmin_required
    def get_all_admins(self, current_admin):
        """Liste tous les admins avec leurs infos"""
        try:
            admins = Admin.query.all()
            backlog = BacklogHelper.read_backlog()
            
            # Fusionner les données DB et backlog
            result = []
            for admin in admins:
                backlog_entry = next(
                    (b for b in backlog if b['email'] == admin.email),
                    None
                )
                admin_data = admin.to_dict()
                if backlog_entry:
                    admin_data['backlog'] = backlog_entry
                result.append(admin_data)
            
            return {
                'data': result,
                'total': len(result),
                'backlog_stats': BacklogHelper.get_backlog_stats()
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_all_admins')
            return {'message': 'Erreur récupération admins'}, 500
    
    def get_admin_count(self):
        """Compte le nombre d'admins (public pour backlog.txt)"""
        try:
            backlog = BacklogHelper.read_backlog()
            db_count = Admin.query.count()
            
            return {
                'backlog_count': len(backlog),
                'database_count': db_count,
                'total_admins': max(len(backlog), db_count),
                'backlog': backlog  # Retourne le backlog complet
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_admin_count')
            return {'message': 'Erreur récupération count'}, 500
    
    @superadmin_required
    def get_backlog(self, current_admin):
        """Récupère le backlog.txt complet et déchiffré"""
        try:
            backlog = BacklogHelper.read_backlog()
            stats = BacklogHelper.get_backlog_stats()
            
            return {
                'backlog': backlog,
                'stats': stats,
                'encrypted': False  # Déjà déchiffré
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_backlog')
            return {'message': 'Erreur récupération backlog'}, 500
    
    @superadmin_required
    def export_backlog(self, current_admin):
        """Exporte le backlog en JSON"""
        try:
            backlog = BacklogHelper.read_backlog()
            
            return {
                'backlog': backlog,
                'exported_at': datetime.utcnow().isoformat(),
                'exported_by': current_admin.email,
                'count': len(backlog)
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.export_backlog')
            return {'message': 'Erreur export backlog'}, 500
    
    @superadmin_required
    def sync_backlog(self, current_admin):
        """Synchronise la base de données avec le backlog"""
        try:
            backlog = BacklogHelper.read_backlog()
            admins = Admin.query.all()
            
            synced = 0
            for backlog_admin in backlog:
                existing = next(
                    (a for a in admins if a.email == backlog_admin['email']),
                    None
                )
                if not existing:
                    # Créer l'admin depuis le backlog
                    new_admin = Admin(
                        username=backlog_admin['username'],
                        email=backlog_admin['email'],
                        phone=backlog_admin['phone'],
                        role=backlog_admin.get('role', 'admin')
                    )
                    # Le password_hash est déjà stocké
                    new_admin.password_hash = backlog_admin['passwordHash']
                    db.session.add(new_admin)
                    synced += 1
            
            db.session.commit()
            
            logger.info(f"✅ Backlog synchronisé: {synced} admins créés")
            
            return {
                'message': f'{synced} admins synchronisés',
                'synced': synced,
                'total_backlog': len(backlog),
                'total_db': Admin.query.count()
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.sync_backlog')
            db.session.rollback()
            return {'message': 'Erreur synchronisation backlog'}, 500
    
    @superadmin_required
    def clear_backlog(self, current_admin):
        """Efface le backlog (superadmin uniquement)"""
        try:
            if os.path.exists(BACKLOG_FILE):
                os.remove(BACKLOG_FILE)
            
            # Créer un nouveau backlog vide
            BacklogHelper.write_backlog([])
            
            logger.warning(f"⚠️ Backlog effacé par {current_admin.email}")
            
            return {
                'message': 'Backlog effacé avec succès',
                'cleared_at': datetime.utcnow().isoformat(),
                'cleared_by': current_admin.email
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.clear_backlog')
            return {'message': 'Erreur suppression backlog'}, 500
    
    # ========== MÉTHODES STATISTIQUES PAR CATÉGORIE ==========
    
    def get_events_stats(self):
        """Statistiques détaillées des événements"""
        try:
            total = Event.query.count()
            active = Event.query.filter_by(archived=False).count()
            archived = Event.query.filter_by(archived=True).count()
            
            today = datetime.now().date()
            upcoming = Event.query.filter(
                Event.date >= today,
                Event.archived == False
            ).count()
            
            # Événements par type
            types = db.session.query(
                Event.type, func.count(Event.id)
            ).filter(
                Event.archived == False
            ).group_by(Event.type).all()
            
            return {
                'total': total,
                'active': active,
                'archived': archived,
                'upcoming': upcoming,
                'by_type': dict(types),
                'completion_rate': round((active / total * 100) if total > 0 else 0, 2)
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_events_stats')
            return {'message': 'Erreur récupération stats événements'}, 500
    
    def get_events_archived(self):
        """Liste tous les événements archivés"""
        try:
            events = Event.query.filter_by(archived=True).order_by(
                Event.date.desc()
            ).all()
            
            return {
                'events': [e.to_dict() for e in events],
                'count': len(events)
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_events_archived')
            return {'message': 'Erreur récupération archives'}, 500
    
    def get_videos_stats(self):
        """Statistiques détaillées des vidéos"""
        try:
            total = Video.query.count()
            active = Video.query.filter_by(archived=False).count()
            archived = Video.query.filter_by(archived=True).count()
            
            khotbas = Video.query.filter_by(type='Khutba', archived=False).count()
            formations = Video.query.filter_by(type='Formation', archived=False).count()
            
            return {
                'total': total,
                'active': active,
                'archived': archived,
                'khotbas': khotbas,
                'formations': formations,
                'completion_rate': round((active / total * 100) if total > 0 else 0, 2)
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_videos_stats')
            return {'message': 'Erreur récupération stats vidéos'}, 500
    
    def get_videos_archived(self):
        """Liste toutes les vidéos archivées"""
        try:
            videos = Video.query.filter_by(archived=True).order_by(
                Video.id.desc()
            ).all()
            
            return {
                'videos': [v.to_dict() for v in videos],
                'count': len(videos)
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_videos_archived')
            return {'message': 'Erreur récupération archives'}, 500
    
    def get_documents_stats(self):
        """Statistiques détaillées des documents"""
        try:
            total = Document.query.count()
            active = Document.query.filter_by(archived=False).count()
            archived = Document.query.filter_by(archived=True).count()
            
            return {
                'total': total,
                'active': active,
                'archived': archived,
                'completion_rate': round((active / total * 100) if total > 0 else 0, 2)
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_documents_stats')
            return {'message': 'Erreur récupération stats documents'}, 500
    
    def get_documents_archived(self):
        """Liste tous les documents archivés"""
        try:
            docs = Document.query.filter_by(archived=True).order_by(
                Document.id.desc()
            ).all()
            
            return {
                'documents': [d.to_dict() for d in docs],
                'count': len(docs)
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_documents_archived')
            return {'message': 'Erreur récupération archives'}, 500
    
    # ========== MÉTHODES ARCHIVAGE/DÉSARCHIVAGE ==========
    
    @admin_required
    def archive_event(self, current_admin):
        """Archive un événement"""
        try:
            data = request.get_json()
            event_id = data.get('id')
            
            if not event_id:
                return {'message': 'ID requis'}, 400
            
            event = Event.query.get(event_id)
            if not event:
                return {'message': 'Événement non trouvé'}, 404
            
            event.archived = True
            db.session.commit()
            
            logger.info(f"📦 Événement archivé: {event.title} par {current_admin.email}")
            
            return {
                'message': 'Événement archivé avec succès',
                'event': event.to_dict()
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.archive_event')
            db.session.rollback()
            return {'message': 'Erreur archivage'}, 500
    
    @admin_required
    def unarchive_event(self, current_admin):
        """Désarchive un événement"""
        try:
            data = request.get_json()
            event_id = data.get('id')
            
            if not event_id:
                return {'message': 'ID requis'}, 400
            
            event = Event.query.get(event_id)
            if not event:
                return {'message': 'Événement non trouvé'}, 404
            
            event.archived = False
            db.session.commit()
            
            logger.info(f"📦 Événement désarchivé: {event.title} par {current_admin.email}")
            
            return {
                'message': 'Événement désarchivé avec succès',
                'event': event.to_dict()
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.unarchive_event')
            db.session.rollback()
            return {'message': 'Erreur désarchivage'}, 500
    
    # ========== MÉTHODES FIREWALL & HONEYPOT ==========
    
    def check_honeypot(self):
        """Vérifie les champs honeypot dans une requête"""
        try:
            data = request.get_json()
            is_bot, message, details = HoneypotHelper.check_honeypot(data)
            
            if is_bot:
                return {
                    'is_bot': True,
                    'message': message,
                    'details': details
                }, 403
            
            return {'is_bot': False}, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.check_honeypot')
            return {'message': 'Erreur vérification honeypot'}, 500
    
    @admin_required
    def block_ip(self, current_admin):
        """Bloque manuellement une IP"""
        try:
            data = request.get_json()
            ip = data.get('ip')
            reason = data.get('reason', 'Blocage manuel')
            duration = data.get('duration_hours', 24)
            
            if not ip:
                return {'message': 'IP requise'}, 400
            
            blocked = FirewallHelper.block_ip(ip, reason, duration)
            
            logger.warning(f"🚫 IP bloquée manuellement: {ip} par {current_admin.email}")
            
            return {
                'message': f'IP {ip} bloquée',
                'blocked_ip': blocked.to_dict()
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.block_ip')
            return {'message': 'Erreur blocage IP'}, 500
    
    @admin_required
    def unblock_ip(self, current_admin):
        """Débloque une IP"""
        try:
            data = request.get_json()
            ip = data.get('ip')
            
            if not ip:
                return {'message': 'IP requise'}, 400
            
            blocked = BlockedIP.query.filter_by(ip=ip).first()
            if blocked:
                db.session.delete(blocked)
                db.session.commit()
                
                logger.info(f"✅ IP débloquée: {ip} par {current_admin.email}")
                
                return {'message': f'IP {ip} débloquée'}, 200
            
            return {'message': f'IP {ip} non trouvée'}, 404
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.unblock_ip')
            db.session.rollback()
            return {'message': 'Erreur déblocage IP'}, 500
    
    def log_intrusion(self):
        """Log une tentative d'intrusion détectée"""
        try:
            data = request.get_json()
            severity = data.get('severity', 'MEDIUM')
            attack_type = data.get('attack_type', 'UNKNOWN')
            details = data.get('details', {})
            
            log = FirewallHelper.log_intrusion(severity, attack_type, details)
            
            return {
                'message': 'Intrusion loggée',
                'log': log.to_dict() if log else None
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.log_intrusion')
            return {'message': 'Erreur log intrusion'}, 500
    
    def get_firewall_logs(self):
        """Récupère les logs du firewall"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            severity = request.args.get('severity')
            
            query = FirewallLog.query.order_by(FirewallLog.created_at.desc())
            
            if severity:
                query = query.filter_by(severity=severity)
            
            logs = query.limit(per_page).offset((page - 1) * per_page).all()
            total = query.count()
            
            return {
                'logs': [l.to_dict() for l in logs],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_firewall_logs')
            return {'message': 'Erreur récupération logs'}, 500
    
    def get_blocked_ips(self):
        """Récupère les IPs bloquées"""
        try:
            blocked = BlockedIP.query.filter(
                BlockedIP.expires_at > datetime.utcnow()
            ).order_by(BlockedIP.expires_at).all()
            
            return {
                'blocked_ips': [b.to_dict() for b in blocked],
                'count': len(blocked)
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_blocked_ips')
            return {'message': 'Erreur récupération IPs bloquées'}, 500
    
    def get_intrusion_stats(self):
        """Statistiques des intrusions"""
        try:
            total = FirewallLog.query.count()
            
            # Par sévérité
            severity = db.session.query(
                FirewallLog.severity, func.count(FirewallLog.id)
            ).group_by(FirewallLog.severity).all()
            
            # Par type d'attaque
            attacks = db.session.query(
                FirewallLog.attack_type, func.count(FirewallLog.id)
            ).group_by(FirewallLog.attack_type).order_by(
                func.count(FirewallLog.id).desc()
            ).limit(10).all()
            
            # Dernières 24h
            last_24h = FirewallLog.query.filter(
                FirewallLog.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            # Top IPs malveillantes
            top_ips = db.session.query(
                FirewallLog.ip, func.count(FirewallLog.id)
            ).group_by(FirewallLog.ip).order_by(
                func.count(FirewallLog.id).desc()
            ).limit(10).all()
            
            return {
                'total_intrusions': total,
                'last_24h': last_24h,
                'by_severity': dict(severity),
                'top_attacks': dict(attacks),
                'top_malicious_ips': dict(top_ips),
                'currently_blocked': BlockedIP.query.filter(
                    BlockedIP.expires_at > datetime.utcnow()
                ).count()
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_intrusion_stats')
            return {'message': 'Erreur récupération stats intrusions'}, 500
    
    @superadmin_required
    def clear_firewall_logs(self, current_admin):
        """Efface tous les logs du firewall"""
        try:
            count = FirewallLog.query.delete()
            db.session.commit()
            
            logger.warning(f"⚠️ Logs firewall effacés par {current_admin.email}")
            
            return {
                'message': f'{count} logs supprimés',
                'deleted_count': count
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.clear_firewall_logs')
            db.session.rollback()
            return {'message': 'Erreur suppression logs'}, 500
    
    @superadmin_required
    def clear_blocked_ips(self, current_admin):
        """Débloque toutes les IPs"""
        try:
            count = BlockedIP.query.delete()
            db.session.commit()
            
            logger.warning(f"⚠️ Toutes les IPs débloquées par {current_admin.email}")
            
            return {
                'message': f'{count} IPs débloquées',
                'unblocked_count': count
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.clear_blocked_ips')
            db.session.rollback()
            return {'message': 'Erreur déblocage IPs'}, 500
    
    # ========== MÉTHODES ERREURS ==========
    
    def get_errors(self):
        """Récupère les logs d'erreurs"""
        try:
            from model.firdaws_db import ErrorLog
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            
            errors = ErrorLog.query.order_by(
                ErrorLog.created_at.desc()
            ).limit(per_page).offset((page - 1) * per_page).all()
            
            total = ErrorLog.query.count()
            
            return {
                'errors': [e.to_dict() for e in errors],
                'total': total,
                'page': page,
                'per_page': per_page
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_errors')
            return {'message': 'Erreur récupération erreurs'}, 500
    
    def get_errors_stats(self):
        """Statistiques des erreurs"""
        try:
            from model.firdaws_db import ErrorLog
            from sqlalchemy import func
            
            total = ErrorLog.query.count()
            
            # Par type d'erreur
            by_type = db.session.query(
                ErrorLog.error_type, func.count(ErrorLog.id)
            ).group_by(ErrorLog.error_type).order_by(
                func.count(ErrorLog.id).desc()
            ).limit(10).all()
            
            # Dernières 24h
            last_24h = ErrorLog.query.filter(
                ErrorLog.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            return {
                'total_errors': total,
                'last_24h': last_24h,
                'by_type': dict(by_type)
            }, 200
            
        except Exception as e:
            log_error(e, request, 'TrackerApi.get_errors_stats')
            return {'message': 'Erreur récupération stats erreurs'}, 500