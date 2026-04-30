import re
from datetime import datetime

class ValidationHelper:
    """Helper pour la validation des données"""
    
    @staticmethod
    def validate_email(email):
        """Valide une adresse email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Valide un numéro de téléphone français"""
        # Accepte 0123456789, 01 23 45 67 89, +33123456789
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        pattern = r'^(?:(?:\+|00)33|0)[1-9]\d{8}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_password(password):
        """Valide la force d'un mot de passe"""
        errors = []
        
        if len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères")
        if not re.search(r'[A-Z]', password):
            errors.append("Le mot de passe doit contenir au moins une majuscule")
        if not re.search(r'[a-z]', password):
            errors.append("Le mot de passe doit contenir au moins une minuscule")
        if not re.search(r'[0-9]', password):
            errors.append("Le mot de passe doit contenir au moins un chiffre")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_date(date_str):
        """Valide une date au format YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_url(url):
        """Valide une URL"""
        pattern = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
        return re.match(pattern, url) is not None
