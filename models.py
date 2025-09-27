from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., min_length=1, max_length=50, description="Username")
    password: str = Field(..., min_length=1, max_length=100, description="Password")
    user_timezone: str = Field(..., min_length=1, max_length=50, description="User timezone")


class User(BaseModel):
    """User model"""
    username: str
    password: str
    timezone: Optional[str] = None


class UserResponse(BaseModel):
    """User response model (without password)"""
    username: str
    timezone: str


class TokenData(BaseModel):
    """JWT token data model"""
    sub: Optional[str] = None
    timezone: Optional[str] = None


class MessageRequest(BaseModel):
    """Message creation request model"""
    message: str = Field(..., min_length=1, max_length=500, description="Message content")


class MessageResponse(BaseModel):
    """Message response model"""
    text: str
    timestamp: str


class LoginSuccessResponse(BaseModel):
    """Login success response model"""
    username: str
    message: str = "Login successful!"
    redirect_url: str = "/msgs"


class LoginErrorResponse(BaseModel):
    """Login error response model"""
    error: str
    message: str = "Login failed"
