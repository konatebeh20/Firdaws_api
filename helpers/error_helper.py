import traceback
from datetime import datetime
from logger.logger_config import get_logger
from flask import request
from logger.logger_config import get_logger, get_error_logger 

logger = get_logger()
# error_logger = get_logger('nour_firdaws_error')
error_logger = get_error_logger()

class ErrorHelper:
    """Helper pour la gestion des erreurs"""
    
    @staticmethod
    def log_error(exception=None, request=None, endpoint=None, **kwargs):
        """
        Helper centralisé pour logger les erreurs
        """
        error_details = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': kwargs.get('error_type', exception.__class__.__name__ if exception else 'UnknownError'),
            'message': kwargs.get('message', str(exception) if exception else 'No message'),
            'traceback': kwargs.get('traceback', traceback.format_exc()),
            'endpoint': endpoint or kwargs.get('function'),
            'file': kwargs.get('file', traceback.extract_tb(exception.__traceback__)[0][0] if exception and exception.__traceback__ else None),
            'line': kwargs.get('line', traceback.extract_tb(exception.__traceback__)[0][1] if exception and exception.__traceback__ else None)
        }
        
        if request:
            error_details.update({
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': str(request.user_agent)
            })
        
        # Log dans le fichier d'erreurs
        error_logger.error(f"❌ {error_details['error_type']}: {error_details['message']}")
        
        # Log détaillé
        logger.debug(f"Traceback: {error_details['traceback']}")
        
        return error_details

    @staticmethod
    def log_success(message, endpoint=None, admin=None):
        """Helper pour logger les succès"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'message': message,
            'endpoint': endpoint
        }
        
        if admin:
            log_data['admin'] = admin.email
        
        logger.info(f"✅ {message}")
        return log_data

# Pour compatibilité avec l'ancien code qui importe log_error directement
def log_error(*args, **kwargs):
    return ErrorHelper.log_error(*args, **kwargs)
