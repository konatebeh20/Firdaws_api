<<<<<<< HEAD
from flask_restful import Resource
from flask import request
from model.firdaws_db import Quiz, Document, Admin
from config.db import db
from logger.logger_config import get_logger
from helpers.auth_helper import admin_required
from helpers.quiz_helper import QuizHelper
import json

logger = get_logger()

class QuizApi(Resource):
    """API pour la gestion des quiz"""
    
    def get_current_admin(self):
        """Récupère l'admin connecté"""
        from helpers.auth_helper import verify_token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if payload:
                return Admin.query.get(payload.get('admin_id'))
        return None
    
    # ========== GET ==========
    def get(self, quiz_id=None):
        """Récupère les quiz"""
        try:
            current_admin = self.get_current_admin()
            
            # GET /api/quizzes/<id>
            if quiz_id:
                quiz = Quiz.query.get(quiz_id)
                if not quiz:
                    return {'message': 'Quiz non trouvé'}, 404
                return {'data': QuizHelper.format_quiz(quiz)}, 200
            
            # GET /api/quizzes
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            document_id = request.args.get('document_id', type=int)
            
            query = Quiz.query
            if document_id:
                query = query.filter_by(document_id=document_id)
            
            quizzes = query.order_by(Quiz.id.desc()).paginate(page=page, per_page=per_page)
            
            return {
                'data': [QuizHelper.format_quiz(q) for q in quizzes.items],
                'pagination': {
                    'total': quizzes.total,
                    'page': quizzes.page,
                    'per_page': quizzes.per_page,
                    'pages': quizzes.pages
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur GET Quiz: {str(e)}")
            return {'message': 'Erreur lors de la récupération'}, 500
    
    # ========== POST - Générer un quiz ==========
    @admin_required
    def post(self, current_admin, route=None):
        """Génère un quiz à partir d'un document"""
        try:
            data = request.get_json()
            document_title = data.get('title', 'Document')
            document_text = data.get('text', document_title)
            document_id = data.get('document_id')
            nb_questions = min(int(data.get('nb_questions', 5)), 20)
            
            # Génération des questions
            questions = self._generate_questions(document_title, document_text, nb_questions)
            
            # Création du quiz
            quiz_data = {
                'title': f'Quiz sur {document_title}',
                'description': f'Quiz généré à partir du document "{document_title}"',
                'document_id': document_id,
                'document_title': document_title,
                'questions': questions
            }
            
            prepared = QuizHelper.prepare_quiz_data(quiz_data, current_admin.id)
            quiz = Quiz(**prepared)
            quiz.save()
            
            logger.info(f"Quiz généré: {quiz.title}")
            return {
                'data': QuizHelper.format_quiz(quiz),
                'quiz_title': quiz.title,
                'questions': questions
            }, 201
            
        except Exception as e:
            logger.error(f"Erreur POST Quiz: {str(e)}")
            return {'message': 'Erreur lors de la génération du quiz'}, 500
    
    # ========== PUT - Soumettre un quiz ==========
    def put(self, quiz_id):
        """Soumet les réponses d'un quiz et calcule le score"""
        try:
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return {'message': 'Quiz non trouvé'}, 404
            
            data = request.get_json()
            user_answers = data.get('answers', {})
            
            score = QuizHelper.calculate_score(quiz, user_answers)
            quiz.score = score
            quiz.is_completed = True
            quiz.save()
            
            return {
                'data': QuizHelper.format_quiz(quiz),
                'score': score,
                'message': 'Quiz soumis avec succès'
            }, 200
            
        except Exception as e:
            logger.error(f"Erreur PUT Quiz: {str(e)}")
            return {'message': 'Erreur lors de la soumission'}, 500
    
    # ========== DELETE ==========
    @admin_required
    def delete(self, current_admin, quiz_id):
        """Supprime un quiz"""
        try:
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return {'message': 'Quiz non trouvé'}, 404
            
            quiz.delete()
            logger.info(f"Quiz supprimé: {quiz.title}")
            return {'message': 'Quiz supprimé', 'id': quiz_id}, 200
            
        except Exception as e:
            logger.error(f"Erreur DELETE Quiz: {str(e)}")
            return {'message': 'Erreur lors de la suppression'}, 500
    
    # ========== Génération de questions ==========
    def _generate_questions(self, title, text, nb):
        """Génère des questions basées sur le document"""
        topics = [
            'le sens de la vie', 'la spiritualité', 'la communauté', 
            'l\'apprentissage', 'la pratique', 'les valeurs islamiques',
            'le Coran', 'la Sunna', 'les bonnes actions'
        ]
        
        questions = []
        for i in range(min(nb, 10)):
            topic = topics[i % len(topics)]
            
            if i % 3 == 0:
                # QCM
                questions.append({
                    "id": i + 1,
                    "type": "qcm",
                    "question": f"Que nous enseigne le document '{title}' concernant {topic} ?",
                    "options": [
                        "A. Une leçon importante à méditer",
                        "B. Un point de vue différent à respecter", 
                        "C. Une mise en garde à prendre en compte",
                        "D. Un encouragement à persévérer"
                    ],
                    "correct": "A",
                    "explanation": f"Le document '{title}' met l'accent sur l'importance de {topic} dans notre vie quotidienne."
                })
            elif i % 3 == 1:
                # Vrai/Faux
                questions.append({
                    "id": i + 1,
                    "type": "vrai-faux",
                    "question": f"Le document '{title}' affirme que {topic} est essentiel pour tout musulman.",
                    "options": ["Vrai", "Faux"],
                    "correct": "Vrai",
                    "explanation": f"En effet, {topic} est un pilier important de notre foi et de notre pratique."
                })
            else:
                # Question à choix unique
                questions.append({
                    "id": i + 1,
                    "type": "unique",
                    "question": f"Selon le document '{title}', quelle est la meilleure approche concernant {topic} ?",
                    "options": [
                        "A. La modération et la régularité",
                        "B. L'intensité et l'effort maximum",
                        "C. L'apprentissage progressif",
                        "D. La recherche de connaissances"
                    ],
                    "correct": "A",
                    "explanation": f"La modération et la régularité sont clés dans la pratique de {topic}."
                })
        
        return questions
    
    
# from flask_restful import Resource
# from flask import request
# from logger.logger_config import get_logger
# import json

# logger = get_logger()

# class QuizApi(Resource):
#     def post(self):
#         try:
#             data = request.get_json()
#             document_title = data.get('title', 'Document')
#             document_text = data.get('text', document_title)
#             nb_questions = min(int(data.get('nb_questions', 5)), 20)
            
#             # Version simplifiée - génère des questions basées sur le document
#             questions = self._generate_questions(document_title, document_text, nb_questions)
            
#             return {
#                 'quiz_title': f'Quiz sur {document_title}',
#                 'questions': questions
#             }, 200
            
#         except Exception as e:
#             logger.error(f"Erreur QuizApi: {str(e)}")
#             return self._generate_fallback_quiz(document_title, 5), 200
    
#     def _generate_questions(self, title, text, nb):
#         questions = []
#         topics = ['le sens de la vie', 'la spiritualité', 'la communauté', 'l\'apprentissage', 'la pratique']
        
#         for i in range(min(nb, 8)):
#             topic = topics[i % len(topics)]
#             questions.append({
#                 "id": i + 1,
#                 "type": "qcm" if i % 2 == 0 else "vrai-faux",
#                 "question": f"Que nous enseigne le document '{title}' concernant {topic} ?",
#                 "options": [
#                     "A. Une leçon importante sur le sujet",
#                     "B. Un point de vue différent", 
#                     "C. Une mise en garde",
#                     "D. Un encouragement"
#                 ] if i % 2 == 0 else ["Vrai", "Faux"],
#                 "correct": "A" if i % 2 == 0 else "Vrai",
#                 "explanation": f"Le document aborde ce sujet de manière approfondie pour nous guider."
#             })
#         return questions
    
#     def _generate_fallback_quiz(self, title, nb):
#         return {
#             'quiz_title': f'Quiz sur {title}',
#             'questions': self._generate_questions(title, '', nb)
#         }
        

# # from flask_restful import Resource
# # from flask import request, jsonify
# # from logger.logger_config import get_logger
# # import json
# # import os

# # logger = get_logger()

# # class QuizApi(Resource):

# #     def post(self):
# #         try:
# #             from anthropic import Anthropic
# #             client = Anthropic()

# #             data = request.get_json()
# #             document_title = data.get('title', 'Document')
# #             document_text = data.get('text', document_title)
# #             nb_questions = min(int(data.get('nb_questions', 5)), 20)

# #             prompt = f"""Tu es un assistant pédagogique islamique.
# # À partir du document intitulé "{document_title}", génère exactement {nb_questions} questions de quiz en JSON.

# # Contenu disponible : {document_text[:2000]}

# # Réponds UNIQUEMENT avec ce JSON valide, sans texte avant ni après :
# # {{
# #   "quiz_title": "Quiz sur {document_title}",
# #   "questions": [
# #     {{
# #       "id": 1,
# #       "type": "qcm",
# #       "question": "...",
# #       "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
# #       "correct": "A",
# #       "explanation": "..."
# #     }}
# #   ]
# # }}"""

# #             message = client.messages.create(
# #                 model="claude-sonnet-4-6",
# #                 max_tokens=2000,
# #                 messages=[{"role": "user", "content": prompt}]
# #             )

# #             raw = message.content[0].text.strip()
# #             # Nettoie les backticks éventuels
# #             if raw.startswith('```'):
# #                 raw = raw.split('```')[1]
# #                 if raw.startswith('json'):
# #                     raw = raw[4:]
            
# #             quiz_data = json.loads(raw.strip())
# #             return quiz_data, 200

# #         except json.JSONDecodeError:
# #             logger.error("Erreur parsing JSON du quiz")
# #             return {'message': 'Erreur lors de la génération du quiz'}, 500
# #         except Exception as e:
# #             logger.error(f"Erreur QuizApi: {str(e)}")
# #             return {'message': str(e)}, 500
=======
import json
from flask_restful import Resource
from flask import request
from model.firdaws_db import Quiz
from config.db import db


class QuizApi(Resource):

    # ========== GET ==========
    def get(self, quiz_id=None):
        if quiz_id:
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return {'status': 'error', 'message': 'Quiz introuvable'}, 404
            return {'status': 'success', 'quiz': quiz.to_dict()}, 200

        quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
        return {
            'status': 'success',
            'quizzes': [q.to_dict() for q in quizzes],
            'total': len(quizzes)
        }, 200

    # ========== POST ==========
    def post(self, quiz_id=None):
        data = request.get_json() or {}

        if not data.get('title') or not data.get('questions'):
            return {'status': 'error', 'message': 'Titre et questions requis'}, 400

        questions = data.get('questions')
        if isinstance(questions, list):
            questions = json.dumps(questions)

        quiz = Quiz(
            title=data.get('title'),
            description=data.get('description'),
            document_id=data.get('document_id'),
            document_title=data.get('document_title'),
            questions=questions,
            total_questions=data.get('total_questions', 0),
            created_by=data.get('created_by')
        )

        db.session.add(quiz)
        db.session.commit()

        return {
            'status': 'success',
            'message': 'Quiz créé avec succès',
            'quiz': quiz.to_dict()
        }, 201

    # ========== PUT ==========
    def put(self, quiz_id=None):
        if not quiz_id:
            return {'status': 'error', 'message': 'ID quiz requis'}, 400

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'status': 'error', 'message': 'Quiz introuvable'}, 404

        data = request.get_json() or {}

        quiz.title = data.get('title', quiz.title)
        quiz.description = data.get('description', quiz.description)
        quiz.score = data.get('score', quiz.score)
        quiz.is_completed = data.get('is_completed', quiz.is_completed)

        if data.get('questions'):
            questions = data.get('questions')
            if isinstance(questions, list):
                questions = json.dumps(questions)
            quiz.questions = questions
            quiz.total_questions = data.get('total_questions', quiz.total_questions)

        db.session.commit()

        return {
            'status': 'success',
            'message': 'Quiz modifié',
            'quiz': quiz.to_dict()
        }, 200

    # ========== DELETE ==========
    def delete(self, quiz_id=None):
        if not quiz_id:
            return {'status': 'error', 'message': 'ID quiz requis'}, 400

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'status': 'error', 'message': 'Quiz introuvable'}, 404

        db.session.delete(quiz)
        db.session.commit()

        return {'status': 'success', 'message': 'Quiz supprimé'}, 200
>>>>>>> 8c5c6fa7d104168d47c468287bfbccfb3bfe0309
