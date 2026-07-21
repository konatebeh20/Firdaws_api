from flask_restful import Resource
from flask import request
from helpers.auth_helper import (
    ForgotPassword,
    ResetPasswordWithToken,
    GenerateResetToken
)


class ForgotPasswordApi(Resource):
    """
    Endpoint pour la réinitialisation du mot de passe
    """

    # ========== POST ==========
    def post(self, route=None, item_id=None):
        """
        Route: /api/auth/forgot-password
        Body: { "email": "...", "role": "admin|user", "new_password": "..." }
        """
        if not route or route == "send":
            return ForgotPassword()

        if route == "generate-token":
            data = request.get_json() or {}
            email = data.get('email')
            role = data.get('role', 'admin')
            return GenerateResetToken(email, role)

        if route == "reset-with-token":
            return ResetPasswordWithToken()

        return {'status': 'error', 'message': 'Route non trouvée'}, 404


class ResetPasswordConfirmApi(Resource):
    """
    Endpoint pour vérifier un token de réinitialisation
    """

    # ========== GET ==========
    def get(self, token=None):
        """
        Route: /api/auth/reset-password/confirm/<token>
        Vérifie si le token est valide
        """
        if not token:
            return {'status': 'error', 'message': 'Token requis'}, 400

        from model.firdaws_db import ResetToken
        from datetime import datetime

        reset_token = ResetToken.query.filter_by(token=token).first()

        if not reset_token:
            return {'status': 'error', 'message': 'Token invalide'}, 400

        if reset_token.used:
            return {'status': 'error', 'message': 'Ce token a déjà été utilisé'}, 400

        if reset_token.expires_at < datetime.utcnow():
            return {'status': 'error', 'message': 'Ce token a expiré'}, 400

        return {
            'status': 'success',
            'message': 'Token valide',
            'email': reset_token.admin.email if reset_token.admin_id else None
        }, 200