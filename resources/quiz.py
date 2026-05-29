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
