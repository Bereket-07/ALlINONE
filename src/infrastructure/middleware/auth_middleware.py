from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Optional
from src.use_cases.auth_use_cases import AuthUseCases
from src.utils.jwt_utils import JWTManager
from src.utils.exceptions import AuthenticationError
from src.utils.constants import ERROR_MESSAGES
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware:
    """
    Authentication middleware for protecting routes.
    """
    
    @staticmethod
    async def verify_token_middleware(request: Request, call_next):
        """
        Middleware to verify authentication token for protected routes.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint
            
        Returns:
            Response from next middleware or endpoint
        """
        # Skip authentication for public endpoints
        public_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh-token"
        ]
        
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Check for authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": ERROR_MESSAGES["MISSING_AUTHORIZATION"]}
            )
        
        try:
            # Extract token from "Bearer <token>" format
            token = JWTManager.extract_token_from_header(authorization)
            if not token:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": ERROR_MESSAGES["INVALID_AUTHORIZATION_FORMAT"]}
                )
            
            # Verify token
            decoded_token = await AuthUseCases.verify_token(token)
            
            # Add user info to request state for use in endpoints
            request.state.user = decoded_token
            
            return await call_next(request)
            
        except AuthenticationError as e:
            logger.warning(f"Authentication error in middleware: {e.message}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": e.message}
            )
        except Exception as e:
            logger.error(f"Unexpected error in auth middleware: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication failed"}
            )

def get_current_user_from_request(request: Request) -> dict:
    """
    Get current user from request state (set by middleware).
    
    Args:
        request: FastAPI request object
        
    Returns:
        User data from token
        
    Raises:
        HTTPException: If user not found in request state
    """
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    return user 