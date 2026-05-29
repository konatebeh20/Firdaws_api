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

            if quiz_id:
                quiz = Quiz.query.get(quiz_id)
                if not quiz:
                    return {'message': 'Quiz non trouvé'}, 404
                return {'data': QuizHelper.format_quiz(quiz)}, 200

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

    # ========== POST ==========
    @admin_required
    def post(self, current_admin, route=None):
        """Génère un quiz à partir d'un document"""
        try:
            data = request.get_json()
            document_title = data.get('title', 'Document')
            document_text = data.get('text', document_title)
            document_id = data.get('document_id')
            nb_questions = min(int(data.get('nb_questions', 5)), 20)

            questions = self._generate_questions(document_title, document_text, nb_questions)

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

    # ========== PUT ==========
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
            "l'apprentissage", 'la pratique', 'les valeurs islamiques',
            'le Coran', 'la Sunna', 'les bonnes actions'
        ]

        questions = []
        for i in range(min(nb, 10)):
            topic = topics[i % len(topics)]

            if i % 3 == 0:
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
                questions.append({
                    "id": i + 1,
                    "type": "vrai-faux",
                    "question": f"Le document '{title}' affirme que {topic} est essentiel pour tout musulman.",
                    "options": ["Vrai", "Faux"],
                    "correct": "Vrai",
                    "explanation": f"En effet, {topic} est un pilier important de notre foi et de notre pratique."
                })
            else:
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
