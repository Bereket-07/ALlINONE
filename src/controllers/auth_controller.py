from fastapi import APIRouter, HTTPException, status, Depends, Header, Request
from typing import Optional
from src.domain.models.auth_models import (
    UserRegisterRequest, UserLoginRequest, UserProfileResponse, AuthResponse, RefreshTokenRequest
)
from src.use_cases.auth_use_cases import AuthUseCases
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
            detail="Authorization header is required"
        )
    
    try:
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Use 'Bearer <token>'"
            )
        
        token = authorization.split(" ")[1]
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is required"
            )
        
        # Verify token
        decoded_token = await AuthUseCases.verify_token(token)
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return decoded_token
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
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
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. User may already exist or invalid data provided."
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in register_user endpoint: {e}")
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
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login_user endpoint: {e}")
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
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_profile endpoint: {e}")
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
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return {
            "access_token": result.get("access_token"),
            "refresh_token": result.get("refresh_token"),
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh_token endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while refreshing token"
        ) 