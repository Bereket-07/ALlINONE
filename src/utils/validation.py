"""
Validation utilities for common validation tasks.
"""
import re
from typing import Optional, Tuple
from datetime import datetime
from src.utils.constants import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH

def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
    
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password must be less than {MAX_PASSWORD_LENGTH} characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for common weak patterns
    if password.lower() in ['password', '123456', 'qwerty', 'admin']:
        return False, "Password is too common, please choose a stronger password"
    
    # Check for repeated characters
    if len(set(password)) < len(password) * 0.6:
        return False, "Password contains too many repeated characters"
    
    return True, "Password meets strength requirements"

def validate_uuid(uuid_string: str) -> bool:
    """
    Validate UUID format.
    
    Args:
        uuid_string: UUID string to validate
        
    Returns:
        True if valid UUID, False otherwise
    """
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_string.lower()))

def sanitize_string(input_string: str) -> str:
    """
    Sanitize string input by removing potentially dangerous characters.
    
    Args:
        input_string: String to sanitize
        
    Returns:
        Sanitized string
    """
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', input_string)
    # Remove extra whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean 