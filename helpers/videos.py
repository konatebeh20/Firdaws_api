from model.firdaws_db import Video
from logger.logger_config import get_logger

logger = get_logger()

class VideoHelper:
    """Helpers pour la gestion des vidéos"""
    
    @staticmethod
    def format_video_data(data, admin_id=None):
        """Formate et valide les données d'une vidéo"""
        formatted = {
            'title': data.get('title', '').strip(),
            'imam': data.get('imam', '').strip(),
            'date': data.get('date', ''),
            'duration': data.get('duration', ''),
            'video_url': data.get('video_url', '#'),
            'thumbnail_url': data.get('thumbnail_url', ''),
            'type': data.get('type', 'Khutba'),
        }
        
        errors = {}
        if not formatted['title']:
            errors['title'] = 'Le titre est requis'
        if not formatted['video_url'] or formatted['video_url'] == '#':
            errors['video_url'] = 'L\'URL de la vidéo est requise'
        
        if admin_id:
            formatted['created_by'] = admin_id
        
        return formatted, errors
    
    @staticmethod
    def extract_youtube_id(url):
        """Extrait l'ID YouTube d'une URL"""
        if 'youtube.com/watch?v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1]
        elif 'youtube.com/embed/' in url:
            return url.split('embed/')[1]
        return None
    
    @staticmethod
    def get_thumbnail_url(url):
        """Génère l'URL de la miniature YouTube"""
        video_id = VideoHelper.extract_youtube_id(url)
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        return None
    
    @staticmethod
    def get_video_stats():
        """Statistiques des vidéos"""
        total = Video.query.count()
        active = Video.query.filter_by(archived=False).count()
        archived = Video.query.filter_by(archived=True).count()
        khutba = Video.query.filter_by(type='Khutba', archived=False).count()
        formations = Video.query.filter_by(type='Formation', archived=False).count()
        
        return {
            'total': total,
            'active': active,
            'archived': archived,
            'khutba': khutba,
            'formations': formations
        }