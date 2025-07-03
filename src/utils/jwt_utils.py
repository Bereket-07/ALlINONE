"""
JWT utilities for token generation and verification.
"""
import jwt
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os
from src.utils.constants import JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

logger = logging.getLogger(__name__)

class JWTManager:
    """
    JWT token management utility.
    """
    
    # JWT Configuration
    JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
    JWT_ALGORITHM = JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = REFRESH_TOKEN_EXPIRE_DAYS
    
    @classmethod
    def generate_tokens(cls, user_id: str, email: str) -> Dict[str, str]:
        """
        Generate JWT access token and refresh token.
        
        Args:
            user_id: User's unique identifier
            email: User's email
            
        Returns:
            Dictionary with access_token and refresh_token
            
        Raises:
            ValueError: If user_id or email is invalid
        """
        if not user_id or not email:
            raise ValueError("User ID and email are required")
        
        try:
            # Access token payload
            access_token_payload = {
                "sub": user_id,
                "email": email,
                "type": "access",
                "exp": datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES),
                "iat": datetime.utcnow()
            }
            
            # Refresh token payload
            refresh_token_payload = {
                "sub": user_id,
                "email": email,
                "type": "refresh",
                "exp": datetime.utcnow() + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS),
                "iat": datetime.utcnow()
            }
            
            # Generate tokens
            access_token = jwt.encode(
                access_token_payload, 
                cls.JWT_SECRET, 
                algorithm=cls.JWT_ALGORITHM
            )
            
            refresh_token = jwt.encode(
                refresh_token_payload, 
                cls.JWT_SECRET, 
                algorithm=cls.JWT_ALGORITHM
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            
        except Exception as e:
            logger.error(f"Error generating tokens: {e}")
            raise ValueError("Failed to generate authentication tokens")
    
    @classmethod
    def verify_token(cls, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            token_type: Type of token ("access" or "refresh")
            
        Returns:
            Decoded token payload or None if invalid
        """
        if not token:
            return None
        
        try:
            payload = jwt.decode(
                token, 
                cls.JWT_SECRET, 
                algorithms=[cls.JWT_ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != token_type:
                logger.warning(f"Token type mismatch. Expected: {token_type}, Got: {payload.get('type')}")
                return None
            
            # Validate required fields
            if not payload.get("sub") or not payload.get("email"):
                logger.warning("Token missing required fields (sub or email)")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    @classmethod
    def extract_token_from_header(cls, authorization_header: str) -> Optional[str]:
        """
        Extract token from Authorization header.
        
        Args:
            authorization_header: Authorization header value
            
        Returns:
            Token string or None if invalid format
        """
        if not authorization_header:
            return None
        
        try:
            if not authorization_header.startswith("Bearer "):
                return None
            
            token = authorization_header.split(" ")[1]
            if not token:
                return None
            
            return token
            
        except Exception as e:
            logger.error(f"Error extracting token from header: {e}")
            return None
    
    @classmethod
    def is_token_expired(cls, token: str) -> bool:
        """
        Check if a token is expired without verifying signature.
        
        Args:
            token: JWT token to check
            
        Returns:
            True if expired, False otherwise
        """
        try:
            # Decode without verification to check expiration
            payload = jwt.decode(
                token, 
                options={"verify_signature": False}
            )
            
            exp = payload.get("exp")
            if not exp:
                return True
            
            return datetime.utcnow().timestamp() > exp
            
        except Exception:
            return True 