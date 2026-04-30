# Standardized API Response Format

from flask import jsonify
from datetime import datetime
from typing import Any, Dict, Optional


class APIResponse:
    """Standardized API response format for all endpoints"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        pagination: Optional[Dict] = None
    ) -> tuple:
        """
        Success response format
        
        Args:
            data: Response data (dict, list, etc.)
            message: Success message
            status_code: HTTP status code
            pagination: Optional pagination info {page, per_page, total, pages}
        
        Returns:
            Flask jsonify response with status code
        """
        response = {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if pagination:
            response["pagination"] = pagination
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(
        error_code: str,
        error_message: str,
        details: Optional[Dict] = None,
        status_code: int = 400
    ) -> tuple:
        """
        Error response format
        
        Args:
            error_code: Machine-readable error code (e.g., 'INVALID_INPUT')
            error_message: Human-readable error message
            details: Additional error details
            status_code: HTTP status code
        
        Returns:
            Flask jsonify response with status code
        """
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": error_message,
                "details": details or {}
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return jsonify(response), status_code
    
    @staticmethod
    def paginated(
        items: list,
        page: int,
        per_page: int,
        total: int,
        message: str = "Items retrieved",
        status_code: int = 200
    ) -> tuple:
        """
        Paginated response format
        
        Args:
            items: List of items
            page: Current page number
            per_page: Items per page
            total: Total number of items
            message: Success message
            status_code: HTTP status code
        
        Returns:
            Flask jsonify response with pagination metadata
        """
        pages = (total + per_page - 1) // per_page
        
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }
        
        response = {
            "success": True,
            "data": items,
            "pagination": pagination,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return jsonify(response), status_code


# Common error responses (for convenience)
class APIError:
    """Pre-defined error responses"""
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized"):
        return APIResponse.error(
            "UNAUTHORIZED",
            message,
            {},
            401
        )
    
    @staticmethod
    def forbidden(message: str = "Forbidden"):
        return APIResponse.error(
            "FORBIDDEN",
            message,
            {},
            403
        )
    
    @staticmethod
    def not_found(resource_name: str = "Resource"):
        return APIResponse.error(
            "NOT_FOUND",
            f"{resource_name} not found",
            {},
            404
        )
    
    @staticmethod
    def validation_error(details: Dict):
        return APIResponse.error(
            "VALIDATION_ERROR",
            "Invalid input",
            {"fields": details},
            422
        )
    
    @staticmethod
    def internal_error(details: str = "Internal server error"):
        return APIResponse.error(
            "INTERNAL_ERROR",
            details,
            {},
            500
        )
    
    @staticmethod
    def conflict(message: str = "Resource already exists"):
        return APIResponse.error(
            "CONFLICT",
            message,
            {},
            409
        )
    
    @staticmethod
    def rate_limited(message: str = "Too many requests"):
        return APIResponse.error(
            "RATE_LIMIT_EXCEEDED",
            message,
            {},
            429
        )
