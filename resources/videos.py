from flask_restful import Resource
from flask import request
from datetime import datetime
from sqlalchemy import or_
from model.firdaws_db import Video, Admin
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import admin_required, verify_token
from helpers.video_helper import VideoHelper
from helpers.pagination_helper import PaginationHelper
from helpers.error_helper import log_error

logger = get_logger()

class VideoApi(Resource):
    """Resource unique pour TOUS les endpoints vidéos"""
    
    def get_current_admin(self):
        """Récupère l'admin si token présent"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if payload:
                return Admin.query.get(payload['admin_id'])
        return None

    # ========== GET ==========
    def get(self, route=None, item_id=None):
        """Route GET dynamique unique"""
        try:
            current_admin = self.get_current_admin()
            
            # 1. GET /api/videos/<int:item_id>
            if item_id and not route:
                video = Video.query.get(item_id)
                if not video:
                    return {'message': 'Vidéo non trouvée'}, 404
                return {'data': video.to_dict()}, 200
            
            # 2. GET /api/videos/admin
            if route == 'admin':
                if not current_admin:
                    return {'message': 'Authentification requise'}, 401
                videos = Video.query.order_by(Video.archived, Video.id.desc()).all()
                return {
                    'data': [v.to_dict() for v in videos],
                    'total': len(videos),
                    'active': len([v for v in videos if not v.archived]),
                    'archived': len([v for v in videos if v.archived])
                }, 200

            # 3. GET /api/videos/recent
            if route == 'recent':
                limit = request.args.get('limit', 3, type=int)

                def format_published_at(dt):
                    if not dt:
                        return None
                    months = [
                        'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
                    ]
                    return f"{dt.day} {months[dt.month - 1]} {dt.year}"

                recent_videos = (
                    Video.query
                    .filter(Video.archived == False)
                    .filter(
                        or_(
                            Video.type.ilike('%khut%'),
                            Video.category.ilike('%khut%')
                        )
                    )
                    .order_by(Video.published_at.desc())
                    .limit(limit)
                    .all()
                )

                return {
                    'data': [
                        {
                            'id': video.id,
                            'title': video.title,
                            'published_at': format_published_at(video.published_at),
                            'url': video.url,
                            'thumbnail': video.thumbnail_url,
                        }
                        for video in recent_videos
                    ],
                    'count': len(recent_videos),
                    'limit': limit,
                }, 200

            # 4. GET /api/videos/type/<string:video_type>
            if route == 'type' and item_id: # item_id used as string route here if needed, or check request args
                pass

            # 4. GET /api/videos (par défaut)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 100, type=int)
            video_type = request.args.get('type')
            include_archived = request.args.get('include_archived', 'false').lower() == 'true'
            
            query = Video.query
            if not include_archived:
                query = query.filter_by(archived=False)
            if video_type:
                query = query.filter_by(type=video_type)
            
            query = query.order_by(Video.id.desc())
            result = PaginationHelper.paginate(query, page, per_page)
            
            return {
                'data': [v.to_dict() for v in result['items']],
                'pagination': {k: v for k, v in result.items() if k != 'items'},
                'stats': VideoHelper.get_stats()
            }, 200

        except Exception as e:
            log_error(e, request, 'VideoApi.get')
            return {'message': 'Erreur lors de la récupération'}, 500

    # ========== POST ==========
    @admin_required
    def post(self, current_admin, route=None, item_id=None):
        """Route POST dynamique unique"""
        try:
            data = request.get_json()
            
            # Validation
            errors = VideoHelper.validate_data(data)
            if errors:
                return {'message': 'Erreur de validation', 'errors': errors}, 400
            
            # Miniature YouTube
            if 'youtube' in data.get('video_url', '') or 'youtu.be' in data.get('video_url', ''):
                thumbnail = VideoHelper.get_thumbnail_url(data['video_url'])
                if thumbnail:
                    data['thumbnail_url'] = thumbnail
            
            video_data = VideoHelper.prepare_data(data, current_admin.id)
            video = Video(**video_data)
            
            db.session.add(video)
            db.session.commit()
            
            logger.info(f"✅ Vidéo ajoutée: {video.title}")
            return {'data': video.to_dict()}, 201
            
        except Exception as e:
            log_error(e, request, 'VideoApi.post')
            db.session.rollback()
            return {'message': 'Erreur lors de l\'ajout'}, 500

    # ========== PUT ==========
    @admin_required
    def put(self, current_admin, route=None, item_id=None):
        """Route PUT dynamique unique"""
        try:
            if not item_id:
                return {'message': 'ID manquant'}, 400
            
            video = Video.query.get(item_id)
            if not video:
                return {'message': 'Vidéo non trouvée'}, 404
            
            data = request.get_json()
            
            # 1. Archive / Désarchive
            if route == 'archive':
                video.archived = data.get('archived', True)
            else:
                # 2. Mise à jour classique
                for field in ['title', 'imam', 'date', 'duration', 'url', 'video_url', 'thumbnail_url', 'type', 'description', 'category', 'instructor']:
                    if field in data:
                        setattr(video, 'url' if field == 'video_url' else field, data[field])
            
            db.session.commit()
            logger.info(f"✅ Vidéo mise à jour: {video.title}")
            return {'data': video.to_dict()}, 200
            
        except Exception as e:
            log_error(e, request, 'VideoApi.put')
            db.session.rollback()
            return {'message': 'Erreur lors de la modification'}, 500

    # ========== DELETE ==========
    @admin_required
    def delete(self, current_admin, route=None, item_id=None):
        """Route DELETE dynamique unique"""
        try:
            if not item_id:
                return {'message': 'ID manquant'}, 400
                
            video = Video.query.get(item_id)
            if not video:
                return {'message': 'Vidéo non trouvée'}, 404
            
            db.session.delete(video)
            db.session.commit()
            
            logger.info(f"✅ Vidéo supprimée: {video.title}")
            return {'data': {'message': 'Vidéo supprimée', 'id': item_id}}, 200
            
        except Exception as e:
            log_error(e, request, 'VideoApi.delete')
            db.session.rollback()
            return {'message': 'Erreur lors de la suppression'}, 500
