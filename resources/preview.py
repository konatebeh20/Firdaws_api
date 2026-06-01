# resources/preview.py
import os
from flask_restful import Resource
from flask import send_file, current_app, abort
from logger.logger_config import get_logger

logger = get_logger()

class DocumentPreviewApi(Resource):
    """API pour prévisualiser les documents en HTML"""
    
    def get(self, filename):
        """Servir un aperçu HTML d'un document"""
        try:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            
            # Chercher d'abord le HTML
            base_name = os.path.splitext(filename)[0]
            html_path = os.path.join(upload_folder, f"{base_name}.html")
            
            if os.path.exists(html_path):
                return send_file(html_path, mimetype='text/html')
            
            # Si pas de HTML, retourner le fichier original
            original_path = os.path.join(upload_folder, filename)
            if os.path.exists(original_path):
                # Déterminer le type MIME
                ext = os.path.splitext(filename)[1].lower()
                mime_types = {
                    '.pdf': 'application/pdf',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    '.jpg': 'image/jpeg',
                    '.png': 'image/png'
                }
                mimetype = mime_types.get(ext, 'application/octet-stream')
                
                response = send_file(original_path, mimetype=mimetype)
                response.headers['X-Frame-Options'] = 'ALLOWALL'
                return response
            
            abort(404, f"Fichier non trouvé: {filename}")
            
        except Exception as e:
            logger.error(f"Erreur dans preview: {str(e)}")
            abort(500, str(e))

# import os
# from flask_restful import Resource
# from flask import send_file, current_app, abort
# from logger.logger_config import get_logger

# logger = get_logger()

# class DocumentPreviewApi(Resource):
#     """API pour prévisualiser les documents en HTML"""
    
#     def get(self, filename):
#         """Servir un aperçu HTML d'un document"""
#         upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        
#         # Chercher d'abord le HTML
#         base_name = os.path.splitext(filename)[0]
#         html_path = os.path.join(upload_folder, f"{base_name}.html")
        
#         if os.path.exists(html_path):
#             return send_file(html_path, mimetype='text/html')
        
#         # Si pas de HTML, essayer de le générer
#         original_path = os.path.join(upload_folder, filename)
#         if os.path.exists(original_path):
#             ext = os.path.splitext(filename)[1].lower()
#             if ext in ['.docx', '.xlsx', '.pptx']:
#                 from helpers.document_converter import DocumentConverter
#                 html_path = DocumentConverter.convert_to_html(original_path, upload_folder)
#                 if html_path and os.path.exists(html_path):
#                     return send_file(html_path, mimetype='text/html')
        
#         abort(404, "Aperçu non disponible")