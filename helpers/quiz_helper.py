from model.firdaws_db import Quiz
from logger.logger_config import get_logger
import json

logger = get_logger()

class QuizHelper:
    """Helper pour la gestion des quiz"""
    
    @staticmethod
    def validate_quiz_data(data):
        """Valide les données d'un quiz"""
        errors = {}
        if not data.get('title'):
            errors['title'] = 'Le titre est requis'
        if not data.get('questions'):
            errors['questions'] = 'Les questions sont requises'
        return errors
    
    @staticmethod
    def prepare_quiz_data(data, admin_id=None):
        """Prépare les données pour l'insertion"""
        questions = data.get('questions', [])
        return {
            'title': data.get('title', 'Quiz sans titre'),
            'description': data.get('description', ''),
            'document_id': data.get('document_id'),
            'document_title': data.get('document_title', ''),
            'questions': json.dumps(questions, ensure_ascii=False),
            'total_questions': len(questions),
            'created_by': admin_id
        }
    
    @staticmethod
    def format_quiz(quiz):
        """Formate un quiz pour l'export"""
        if not quiz:
            return None
        data = quiz.to_dict()
        data['questions'] = json.loads(quiz.questions) if quiz.questions else []
        return data
    
    @staticmethod
    def calculate_score(quiz, user_answers):
        """Calcule le score d'un quiz"""
        questions = json.loads(quiz.questions) if quiz.questions else []
        correct = 0
        for i, q in enumerate(questions):
            if str(i) in user_answers and user_answers[str(i)] == q.get('correct'):
                correct += 1
        score = int((correct / len(questions)) * 100) if questions else 0
        return score