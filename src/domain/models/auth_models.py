from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserRegisterRequest(BaseModel):
    """Model for user registration request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, max_length=128, description="User's password (min 6 characters)")
    display_name: Optional[str] = Field(None, max_length=100, description="User's display name")
    
class UserLoginRequest(BaseModel):
    """Model for user login request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class UserProfileResponse(BaseModel):
    """Model for user profile response."""
    uid: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    display_name: Optional[str] = Field(None, description="User's display name")
    email_verified: bool = Field(..., description="Whether user's email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_sign_in: Optional[datetime] = Field(None, description="Last sign-in timestamp")
    
class AuthResponse(BaseModel):
    """Model for authentication response."""
    user: UserProfileResponse = Field(..., description="User profile information")
    token: str = Field(..., description="JWT access token for authentication")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")

class RefreshTokenRequest(BaseModel):
    """Model for refresh token request."""
    refresh_token: str = Field(..., description="JWT refresh token") 