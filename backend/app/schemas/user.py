"""
Pydantic schemas for User model validation.

These schemas define the structure for user-related API requests and responses.
They provide type safety and automatic validation for FastAPI endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.core.validators import DevEmailStr


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: DevEmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(None, max_length=100, description="Optional username")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, description="User password (min 8 characters)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "securepassword123",
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[DevEmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(None, max_length=100, description="Optional username")
    password: Optional[str] = Field(None, min_length=8, description="New password (if updating)")
    is_active: Optional[bool] = Field(None, description="Whether the user account is active")
    is_verified: Optional[bool] = Field(None, description="Whether the email is verified")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "newusername",
                "is_verified": True,
            }
        }
    )


class UserResponse(UserBase):
    """Schema for user API responses."""

    id: str = Field(..., description="User UUID")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_verified: bool = Field(..., description="Whether the email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,  # Allows conversion from SQLAlchemy models
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "johndoe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        },
    )
