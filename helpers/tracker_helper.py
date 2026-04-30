from datetime import datetime
from helpers.backlog_helper import BacklogHelper
from helpers.firewall_helper import FirewallHelper
from helpers.error_helper import ErrorHelper
from logger.logger_config import get_logger

logger = get_logger()

class TrackerHelper:
    """Helper pour le suivi des activités et du système"""
    
    @staticmethod
    def get_system_status():
        """Récupère l'état général du système"""
        return {
            'status': 'online',
            'timestamp': datetime.utcnow().isoformat(),
            'backlog': BacklogHelper.get_backlog_stats()
        }
    
    @staticmethod
    def get_recent_activities(limit=10):
        """Récupère les activités récentes depuis le backlog"""
        backlog = BacklogHelper.read_backlog()
        return sorted(backlog, key=lambda x: x.get('registeredAt', ''), reverse=True)[:limit]
