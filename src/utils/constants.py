"""
Application constants.
"""

# JWT Configuration
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# API Configuration
API_PREFIX = "/api/v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Validation Rules
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MIN_DISPLAY_NAME_LENGTH = 1
MAX_DISPLAY_NAME_LENGTH = 100

# HTTP Status Messages
HTTP_MESSAGES = {
    200: "Success",
    201: "Created",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    422: "Validation Error",
    500: "Internal Server Error"
}

# Error Messages
ERROR_MESSAGES = {
    # Authentication Errors
    "INVALID_TOKEN": "Invalid or expired token",
    "TOKEN_EXPIRED": "Token has expired",
    "MISSING_AUTHORIZATION": "Authorization header is required",
    "INVALID_AUTHORIZATION_FORMAT": "Invalid authorization header format. Use 'Bearer <token>'",
    "INVALID_CREDENTIALS": "Invalid email or password",
    "WEAK_PASSWORD": "Password is too weak",
    "INVALID_EMAIL": "Invalid email format",
    
    # User Errors
    "USER_NOT_FOUND": "User not found",
    "EMAIL_ALREADY_EXISTS": "User with this email already exists",
    "USER_ALREADY_EXISTS": "User with this email already exists",
    "PROFILE_NOT_FOUND": "User profile not found",
    
    # Service Errors
    "SERVICE_UNAVAILABLE": "Authentication service is temporarily unavailable",
    "FIRESTORE_ERROR": "Database service error",
    "INTERNAL_ERROR": "Internal server error",
    
    # Validation Errors
    "INVALID_USER_ID": "Invalid user ID format",
    "INVALID_DISPLAY_NAME": "Display name is invalid",
    "PASSWORD_TOO_SHORT": "Password must be at least 8 characters long",
    "PASSWORD_TOO_LONG": "Password must be less than 128 characters",
    "EMAIL_TOO_LONG": "Email address is too long",
    "DISPLAY_NAME_TOO_LONG": "Display name is too long"
}

# LLM Configuration
LLM_PROVIDERS = {
    "openai": "OpenAI",
    "anthropic": "Anthropic", 
    "google": "Google"
}

# Firestore Collections
FIRESTORE_COLLECTIONS = {
    "USERS": "users",
    "USER_AUTH": "user_auth"
}

# File Extensions
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}

# Time Formats
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S" 