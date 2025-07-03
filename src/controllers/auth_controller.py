from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Optional
from src.domain.models.auth_models import (
    UserRegisterRequest, UserLoginRequest, UserProfileResponse, AuthResponse, RefreshTokenRequest
)
from src.use_cases.auth_use_cases import AuthUseCases
from src.utils.constants import ERROR_MESSAGES
from src.utils.jwt_utils import JWTManager
from src.utils.exceptions import (
    AuthenticationError, InvalidCredentialsError, UserNotFoundError, 
    UserAlreadyExistsError, WeakPasswordError, InvalidTokenError,
    MissingAuthorizationError, InvalidAuthorizationFormatError,
    ServiceUnavailableError, InvalidEmailError
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

async def get_current_user(request: Request) -> dict:
    """
    Dependency to get current authenticated user from token.
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["MISSING_AUTHORIZATION"]
        )
    
    try:
        # Extract token from "Bearer <token>" format
        token = JWTManager.extract_token_from_header(authorization)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES["INVALID_AUTHORIZATION_FORMAT"]
            )
        
        # Verify token
        decoded_token = await AuthUseCases.verify_token(token)
        return decoded_token
        
    except HTTPException:
        raise
    except AuthenticationError as e:
        logger.warning(f"Authentication error in get_current_user: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterRequest):
    """
    Register a new user account.
    
    Args:
        request: User registration data
        
    Returns:
        User data and authentication tokens
    """
    try:
        result = await AuthUseCases.register_user(request)
        return result
        
    except HTTPException:
        raise
    except UserAlreadyExistsError as e:
        logger.warning(f"Registration failed - user already exists: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except (WeakPasswordError, InvalidEmailError) as e:
        logger.warning(f"Registration failed - validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ServiceUnavailableError as e:
        logger.error(f"Registration failed - service unavailable: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Unexpected error in register_user endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(request: UserLoginRequest):
    """
    Authenticate user login.
    
    Args:
        request: User login credentials
        
    Returns:
        User data and authentication tokens
    """
    try:
        result = await AuthUseCases.login_user(request)
        return result
        
    except HTTPException:
        raise
    except InvalidCredentialsError as e:
        logger.warning(f"Login failed - invalid credentials: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except ServiceUnavailableError as e:
        logger.error(f"Login failed - service unavailable: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Unexpected error in login_user endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user's profile from Bearer token.
    
    Args:
        current_user: Current authenticated user (from token)
        
    Returns:
        User profile data
    """
    try:
        # Get user ID from JWT token (sub field)
        uid = current_user.get('sub')
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        result = await AuthUseCases.get_user_profile(uid)
        return result
        
    except HTTPException:
        raise
    except UserNotFoundError as e:
        logger.warning(f"Profile fetch failed - user not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except ServiceUnavailableError as e:
        logger.error(f"Profile fetch failed - service unavailable: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_profile endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching profile"
        )

@router.post("/refresh-token")
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        
    Returns:
        New access token and refresh token
    """
    try:
        result = await AuthUseCases.refresh_token(request.refresh_token)
        
        return {
            "access_token": result.get("access_token"),
            "refresh_token": result.get("refresh_token"),
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except (InvalidTokenError, UserNotFoundError) as e:
        logger.warning(f"Token refresh failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except ServiceUnavailableError as e:
        logger.error(f"Token refresh failed - service unavailable: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Unexpected error in refresh_token endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while refreshing token"
        ) 