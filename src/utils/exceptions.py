"""
Custom exceptions for authentication and authorization.
"""
from typing import Optional, Dict, Any

class AuthenticationError(Exception):
    """Base class for authentication errors."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class InvalidCredentialsError(AuthenticationError):
    """Raised when user credentials are invalid."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, "INVALID_CREDENTIALS")

class UserNotFoundError(AuthenticationError):
    """Raised when user is not found."""
    
    def __init__(self, message: str = "User not found"):
        super().__init__(message, "USER_NOT_FOUND")

class UserAlreadyExistsError(AuthenticationError):
    """Raised when trying to create a user that already exists."""
    
    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(message, "USER_ALREADY_EXISTS")

class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, "INVALID_TOKEN")

class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, "TOKEN_EXPIRED")

class MissingAuthorizationError(AuthenticationError):
    """Raised when authorization header is missing."""
    
    def __init__(self, message: str = "Authorization header is required"):
        super().__init__(message, "MISSING_AUTHORIZATION")

class InvalidAuthorizationFormatError(AuthenticationError):
    """Raised when authorization header format is invalid."""
    
    def __init__(self, message: str = "Invalid authorization header format. Use 'Bearer <token>'"):
        super().__init__(message, "INVALID_AUTHORIZATION_FORMAT")

class WeakPasswordError(AuthenticationError):
    """Raised when password doesn't meet strength requirements."""
    
    def __init__(self, message: str = "Password is too weak"):
        super().__init__(message, "WEAK_PASSWORD")

class InvalidEmailError(AuthenticationError):
    """Raised when email format is invalid."""
    
    def __init__(self, message: str = "Invalid email format"):
        super().__init__(message, "INVALID_EMAIL")

class ServiceUnavailableError(AuthenticationError):
    """Raised when authentication service is unavailable."""
    
    def __init__(self, message: str = "Authentication service is temporarily unavailable"):
        super().__init__(message, "SERVICE_UNAVAILABLE")

def get_error_response(exception: AuthenticationError) -> Dict[str, Any]:
    """
    Convert authentication exception to error response format.
    
    Args:
        exception: Authentication exception
        
    Returns:
        Error response dictionary
    """
    return {
        "error": {
            "code": exception.error_code,
            "message": exception.message,
            "details": exception.details
        }
    } 