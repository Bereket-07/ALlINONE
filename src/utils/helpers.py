"""
Helper utilities for common operations.
"""
import hashlib
import secrets
import string
from typing import Optional
from datetime import datetime, timezone

def generate_random_string(length: int = 32) -> str:
    """
    Generate a random string of specified length.
    
    Args:
        length: Length of the string to generate
        
    Returns:
        Random string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_api_key() -> str:
    """
    Generate a secure API key.
    
    Returns:
        Secure API key
    """
    return secrets.token_urlsafe(32)

def hash_string(input_string: str, algorithm: str = 'sha256') -> str:
    """
    Hash a string using specified algorithm.
    
    Args:
        input_string: String to hash
        algorithm: Hashing algorithm (md5, sha1, sha256, etc.)
        
    Returns:
        Hashed string
    """
    hash_func = getattr(hashlib, algorithm)
    return hash_func(input_string.encode()).hexdigest()

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)

def parse_datetime(date_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parse datetime string to datetime object.
    
    Args:
        date_string: Date string to parse
        format_str: Format string
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(date_string, format_str)
    except ValueError:
        return None

def get_utc_now() -> datetime:
    """
    Get current UTC datetime.
    
    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def safe_get_nested(data: dict, *keys, default=None):
    """
    Safely get nested dictionary value.
    
    Args:
        data: Dictionary to search
        *keys: Keys to traverse
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current 