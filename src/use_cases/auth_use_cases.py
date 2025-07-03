import uuid
from typing import Optional, Dict, Any
from src.domain.models.auth_models import (
    UserRegisterRequest, UserLoginRequest, UserProfileResponse, AuthResponse
)
import logging
from datetime import datetime
from src.utils.security import hash_password, verify_password
from src.utils.validation import validate_password_strength
from src.utils.jwt_utils import JWTManager
from src.utils.exceptions import (
    InvalidCredentialsError, UserNotFoundError, UserAlreadyExistsError,
    WeakPasswordError, ServiceUnavailableError, InvalidTokenError, InvalidEmailError
)
from src.infrastructure.services.service_factory import ServiceFactory
from src.utils.validation import validate_email

logger = logging.getLogger(__name__)

class AuthUseCases:
    """
    JWT authentication with Firestore user storage.
    """
    
    @staticmethod
    def _validate_registration_data(request: UserRegisterRequest) -> None:
        """
        Validate registration data.
        
        Args:
            request: Registration request
            
        Raises:
            WeakPasswordError: If password is too weak
            InvalidEmailError: If email format is invalid
        """
        # Validate email format
        if not validate_email(request.email):
            raise InvalidEmailError("Invalid email format")
        
        # Validate password strength
        is_valid, error_message = validate_password_strength(request.password)
        if not is_valid:
            raise WeakPasswordError(error_message)
    

    
    @staticmethod
    async def register_user(request: UserRegisterRequest) -> AuthResponse:
        """
        Register a new user account.
        
        Args:
            request: User registration data
            
        Returns:
            AuthResponse with user data and tokens
            
        Raises:
            UserAlreadyExistsError: If user already exists
            WeakPasswordError: If password is too weak
            InvalidEmailError: If email format is invalid
            ServiceUnavailableError: If Firestore service is unavailable
        """
        try:
            # Validate registration data
            AuthUseCases._validate_registration_data(request)
            
            # Generate unique user ID
            user_id = str(uuid.uuid4())
            
            # Hash the password
            hashed_password = hash_password(request.password)
            
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
            firestore_service = ServiceFactory.get_firestore_service()
            if not firestore_service:
                logger.error("Firestore service not available")
                raise ServiceUnavailableError("Database service is temporarily unavailable")
            
            # Check if user already exists
            existing_user = await firestore_service.get_user_by_email(request.email)
            if existing_user:
                logger.warning(f"User already exists with email: {request.email}")
                raise UserAlreadyExistsError(f"User with email '{request.email}' already exists")
            
            # Store user in Firestore
            success = await firestore_service.create_user(user_data)
            if not success:
                logger.error(f"Failed to create user in Firestore: {user_id}")
                raise ServiceUnavailableError("Failed to create user account")
            
            logger.info(f"Created user with UID: {user_id}")
            
            # Generate JWT tokens
            tokens = JWTManager.generate_tokens(user_id, request.email)
            
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
            
        except (UserAlreadyExistsError, WeakPasswordError, InvalidEmailError, ServiceUnavailableError):
            # Re-raise authentication exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in register_user: {e}")
            raise ServiceUnavailableError("An unexpected error occurred during registration")
    
    @staticmethod
    async def login_user(request: UserLoginRequest) -> AuthResponse:
        """
        Authenticate user login.
        
        Args:
            request: User login credentials
            
        Returns:
            AuthResponse with user data and tokens
            
        Raises:
            InvalidCredentialsError: If email or password is invalid
            ServiceUnavailableError: If Firestore service is unavailable
        """
        try:
            # Get Firestore service
            firestore_service = ServiceFactory.get_firestore_service()
            if not firestore_service:
                logger.error("Firestore service not available")
                raise ServiceUnavailableError("Database service is temporarily unavailable")
            
            # Find user by email
            user_data = await firestore_service.get_user_by_email(request.email)
            if not user_data:
                logger.warning(f"Login failed: User not found with email: {request.email}")
                raise InvalidCredentialsError("Invalid email or password")
            
            user_id = user_data['uid']
            
            # Verify password
            if not verify_password(request.password, user_data['password_hash']):
                logger.warning(f"Login failed: Invalid password for email: {request.email}")
                raise InvalidCredentialsError("Invalid email or password")
            
            # Update last sign in
            user_data['last_sign_in'] = datetime.utcnow()
            await firestore_service.update_user(user_id, {'last_sign_in': user_data['last_sign_in']})
            
            # Generate JWT tokens
            tokens = JWTManager.generate_tokens(user_id, request.email)
            
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
            
        except (InvalidCredentialsError, ServiceUnavailableError):
            # Re-raise authentication exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in login_user: {e}")
            raise ServiceUnavailableError("An unexpected error occurred during login")
    
    @staticmethod
    async def get_user_profile(uid: str) -> UserProfileResponse:
        """
        Get user profile by UID.
        
        Args:
            uid: User's unique identifier
            
        Returns:
            UserProfileResponse with user data
            
        Raises:
            UserNotFoundError: If user is not found
            ServiceUnavailableError: If Firestore service is unavailable
        """
        try:
            # Get Firestore service
            firestore_service = ServiceFactory.get_firestore_service()
            if not firestore_service:
                logger.error("Firestore service not available")
                raise ServiceUnavailableError("Database service is temporarily unavailable")
            
            # Get user from Firestore
            user_data = await firestore_service.get_user_by_uid(uid)
            if not user_data:
                logger.warning(f"User profile not found for UID: {uid}")
                raise UserNotFoundError(f"User with ID '{uid}' not found")
            
            return UserProfileResponse(
                uid=user_data['uid'],
                email=user_data['email'],
                display_name=user_data['display_name'],
                email_verified=user_data['email_verified'],
                created_at=user_data['created_at'],
                last_sign_in=user_data['last_sign_in']
            )
            
        except (UserNotFoundError, ServiceUnavailableError):
            # Re-raise authentication exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_user_profile: {e}")
            raise ServiceUnavailableError("An unexpected error occurred while fetching profile")
    
    @staticmethod
    async def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Decoded token data
            
        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        try:
            payload = JWTManager.verify_token(token, "access")
            if payload:
                logger.info(f"Token verified successfully for UID: {payload.get('sub')}")
                return payload
            else:
                logger.warning("Token verification failed")
                raise InvalidTokenError("Invalid or expired token")
            
        except InvalidTokenError:
            # Re-raise token exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in verify_token: {e}")
            raise InvalidTokenError("Token verification failed")
    
    @staticmethod
    async def refresh_token(refresh_token: str) -> Dict[str, str]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            Dictionary with new access_token and refresh_token
            
        Raises:
            InvalidTokenError: If refresh token is invalid
            UserNotFoundError: If user no longer exists
            ServiceUnavailableError: If Firestore service is unavailable
        """
        try:
            # Verify refresh token
            payload = JWTManager.verify_token(refresh_token, "refresh")
            if not payload:
                logger.warning("Invalid refresh token")
                raise InvalidTokenError("Invalid refresh token")
            
            user_id = payload.get("sub")
            email = payload.get("email")
            
            # Check if user still exists
            firestore_service = ServiceFactory.get_firestore_service()
            if not firestore_service:
                logger.error("Firestore service not available")
                raise ServiceUnavailableError("Database service is temporarily unavailable")
            
            user_data = await firestore_service.get_user_by_uid(user_id)
            if not user_data:
                logger.warning(f"User not found for refresh token: {user_id}")
                raise UserNotFoundError("User no longer exists")
            
            # Generate new tokens
            tokens = JWTManager.generate_tokens(user_id, email)
            
            logger.info(f"Tokens refreshed successfully for UID: {user_id}")
            return tokens
            
        except (InvalidTokenError, UserNotFoundError, ServiceUnavailableError):
            # Re-raise authentication exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in refresh_token: {e}")
            raise ServiceUnavailableError("An unexpected error occurred while refreshing token") 