import jwt
import bcrypt
import uuid
from typing import Optional, Dict, Any
from src.domain.models.auth_models import (
    UserRegisterRequest, UserLoginRequest, UserProfileResponse, AuthResponse
)
import logging
from datetime import datetime, timedelta
import os
from src.config import FIREBASE_CREDENTIALS_PATH

logger = logging.getLogger(__name__)

class AuthUseCases:
    """
    JWT authentication with Firestore user storage.
    """
    
    # JWT Configuration
    JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 30
    
    # Firestore service
    _firestore_service = None
    
    @classmethod
    def _get_firestore_service(cls):
        """Get Firestore service instance, initializing if needed."""
        if cls._firestore_service is None:
            try:
                from src.infrastructure.firebase.firestore_service import FirestoreService
                if FirestoreService.initialize(FIREBASE_CREDENTIALS_PATH):
                    cls._firestore_service = FirestoreService
                    logger.info("Firestore service initialized successfully")
                else:
                    logger.error("Failed to initialize Firestore service")
            except Exception as e:
                logger.error(f"Error initializing Firestore service: {e}")
        return cls._firestore_service
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def _verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def _generate_tokens(user_id: str, email: str) -> Dict[str, str]:
        """
        Generate JWT access token and refresh token.
        
        Args:
            user_id: User's unique identifier
            email: User's email
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        # Access token payload
        access_token_payload = {
            "sub": user_id,
            "email": email,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=AuthUseCases.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow()
        }
        
        # Refresh token payload
        refresh_token_payload = {
            "sub": user_id,
            "email": email,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=AuthUseCases.REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": datetime.utcnow()
        }
        
        # Generate tokens
        access_token = jwt.encode(
            access_token_payload, 
            AuthUseCases.JWT_SECRET, 
            algorithm=AuthUseCases.JWT_ALGORITHM
        )
        
        refresh_token = jwt.encode(
            refresh_token_payload, 
            AuthUseCases.JWT_SECRET, 
            algorithm=AuthUseCases.JWT_ALGORITHM
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    @staticmethod
    def _verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            token_type: Type of token ("access" or "refresh")
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token, 
                AuthUseCases.JWT_SECRET, 
                algorithms=[AuthUseCases.JWT_ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != token_type:
                logger.warning(f"Token type mismatch. Expected: {token_type}, Got: {payload.get('type')}")
                return None
            
            # Check if user still exists
            user_id = payload.get("sub")
            
            # Note: We don't check user existence here to avoid blocking token verification
            # User existence is checked in the specific use cases when needed
            # This allows for better performance and avoids blocking token verification
            
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
    
    @staticmethod
    async def register_user(request: UserRegisterRequest) -> Optional[AuthResponse]:
        """
        Register a new user account.
        """
        try:
            # Generate unique user ID
            user_id = str(uuid.uuid4())
            
            # Hash the password
            hashed_password = AuthUseCases._hash_password(request.password)
            
            # Create user data
            now = datetime.utcnow()
            user_data = {
                'uid': user_id,
                'email': request.email,
                'display_name': request.display_name,
                'email_verified': False,
                'created_at': now,
                'last_sign_in': now,
                'password_hash': hashed_password
            }
            
            # Get Firestore service
            firestore_service = AuthUseCases._get_firestore_service()
            if not firestore_service:
                logger.error("Firestore service not available")
                return None
            
            # Check if user already exists
            existing_user = await firestore_service.get_user_by_email(request.email)
            if existing_user:
                logger.warning(f"User already exists with email: {request.email}")
                return None
            
            # Store user in Firestore
            success = await firestore_service.create_user(user_data)
            if not success:
                logger.error(f"Failed to create user in Firestore: {user_id}")
                return None
            
            logger.info(f"Created user with UID: {user_id}")
            
            # Generate JWT tokens
            tokens = AuthUseCases._generate_tokens(user_id, request.email)
            
            # Convert to response model
            user_profile = UserProfileResponse(
                uid=user_data['uid'],
                email=user_data['email'],
                display_name=user_data['display_name'],
                email_verified=user_data['email_verified'],
                created_at=user_data['created_at'],
                last_sign_in=user_data['last_sign_in']
            )
            
            # Return user data with tokens
            return AuthResponse(
                user=user_profile,
                token=tokens.get("access_token", ""),
                refresh_token=tokens.get("refresh_token")
            )
            
        except Exception as e:
            logger.error(f"Error in register_user use case: {e}")
            return None
    
    @staticmethod
    async def login_user(request: UserLoginRequest) -> Optional[AuthResponse]:
        """
        Authenticate user login.
        """
        try:
            # Get Firestore service
            firestore_service = AuthUseCases._get_firestore_service()
            if not firestore_service:
                logger.error("Firestore service not available")
                return None
            
            # Find user by email
            user_data = await firestore_service.get_user_by_email(request.email)
            if not user_data:
                logger.warning(f"Login failed: User not found with email: {request.email}")
                return None
            
            user_id = user_data['uid']
            
            # Verify password
            if not AuthUseCases._verify_password(request.password, user_data['password_hash']):
                logger.warning(f"Login failed: Invalid password for email: {request.email}")
                return None
            
            # Update last sign in
            user_data['last_sign_in'] = datetime.utcnow()
            await firestore_service.update_user(user_id, {'last_sign_in': user_data['last_sign_in']})
            
            # Generate JWT tokens
            tokens = AuthUseCases._generate_tokens(user_id, request.email)
            
            user_profile = UserProfileResponse(
                uid=user_data['uid'],
                email=user_data['email'],
                display_name=user_data['display_name'],
                email_verified=user_data['email_verified'],
                created_at=user_data['created_at'],
                last_sign_in=user_data['last_sign_in']
            )
            
            return AuthResponse(
                user=user_profile,
                token=tokens.get("access_token", ""),
                refresh_token=tokens.get("refresh_token")
            )
            
        except Exception as e:
            logger.error(f"Error in login_user use case: {e}")
            return None
    
    @staticmethod
    async def get_user_profile(uid: str) -> Optional[UserProfileResponse]:
        """
        Get user profile by UID.
        """
        try:
            # Get Firestore service
            firestore_service = AuthUseCases._get_firestore_service()
            if not firestore_service:
                logger.error("Firestore service not available")
                return None
            
            # Get user from Firestore
            user_data = await firestore_service.get_user_by_uid(uid)
            if not user_data:
                logger.warning(f"User profile not found for UID: {uid}")
                return None
            
            return UserProfileResponse(
                uid=user_data['uid'],
                email=user_data['email'],
                display_name=user_data['display_name'],
                email_verified=user_data['email_verified'],
                created_at=user_data['created_at'],
                last_sign_in=user_data['last_sign_in']
            )
            
        except Exception as e:
            logger.error(f"Error in get_user_profile use case: {e}")
            return None
    
    @staticmethod
    async def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = AuthUseCases._verify_token(token, "access")
            if payload:
                logger.info(f"Token verified successfully for UID: {payload.get('sub')}")
            else:
                logger.warning("Token verification failed")
            return payload
            
        except Exception as e:
            logger.error(f"Error in verify_token use case: {e}")
            return None
    
    @staticmethod
    async def refresh_token(refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Refresh access token using refresh token.
        """
        try:
            # Verify refresh token
            payload = AuthUseCases._verify_token(refresh_token, "refresh")
            if not payload:
                logger.warning("Invalid refresh token")
                return None
            
            user_id = payload.get("sub")
            email = payload.get("email")
            
            # Check if user still exists
            firestore_service = AuthUseCases._get_firestore_service()
            if not firestore_service:
                logger.error("Firestore service not available")
                return None
            
            user_data = await firestore_service.get_user_by_uid(user_id)
            if not user_data:
                logger.warning(f"User not found for refresh token: {user_id}")
                return None
            
            # Generate new tokens
            tokens = AuthUseCases._generate_tokens(user_id, email)
            
            logger.info(f"Tokens refreshed successfully for UID: {user_id}")
            return tokens
            
        except Exception as e:
            logger.error(f"Error in refresh_token use case: {e}")
            return None 