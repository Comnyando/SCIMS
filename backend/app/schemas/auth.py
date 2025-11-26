"""
Authentication schemas for request/response validation.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.core.validators import DevEmailStr
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: DevEmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(None, max_length=100, description="Optional username")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "securepassword123",
            }
        }
    )


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: DevEmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str = Field(..., description="Refresh token to exchange for new access token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }
    )


class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""

    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword456",
            }
        }
    )


class DeleteAccountRequest(BaseModel):
    """Schema for account deletion request."""

    password: str = Field(..., description="Current password for verification")
    confirm: bool = Field(..., description="Confirmation that user wants to delete account")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "password": "currentpassword123",
                "confirm": True,
            }
        }
    )


class Token(BaseModel):
    """Schema for token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )


class TokenData(BaseModel):
    """Schema for decoded token data."""

    user_id: Optional[str] = None
    email: Optional[str] = None


class LoginResponse(BaseModel):
    """Schema for successful login response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "username": "johndoe",
                    "is_active": True,
                    "is_verified": False,
                },
            }
        }
    )


class RegisterResponse(BaseModel):
    """Schema for successful registration response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "username": "johndoe",
                    "is_active": True,
                    "is_verified": False,
                },
            }
        }
    )
