import traceback
from datetime import datetime
from logger.logger_config import get_logger

logger = get_logger()
error_logger = get_logger('nour_firdaws_error')

def log_error(exception, request=None, endpoint=None):
    """
    Helper centralisé pour logger les erreurs
    À utiliser dans TOUS les try/except
    """
    error_details = {
        'timestamp': datetime.utcnow().isoformat(),
        'error_type': exception.__class__.__name__,
        'message': str(exception),
        'traceback': traceback.format_exc(),
        'endpoint': endpoint,
        'file': traceback.extract_tb(exception.__traceback__)[0][0] if exception.__traceback__ else None,
        'line': traceback.extract_tb(exception.__traceback__)[0][1] if exception.__traceback__ else None
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