"""
FastAPI dependencies for authentication and authorization.

This module provides dependency functions that can be used in FastAPI route handlers
to enforce authentication and role-based access control.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import decode_token
from app.config import settings

# OAuth2 scheme for token extraction
# This tells FastAPI to look for the token in the Authorization header
# Note: tokenUrl is used for Swagger UI documentation, not actual token generation
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login",
    scheme_name="JWT",
    auto_error=True,
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    This dependency:
    1. Extracts the JWT token from the Authorization header
    2. Decodes and validates the token
    3. Retrieves the user from the database
    4. Returns the user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the token
    payload = decode_token(token, token_type="access")
    if payload is None:
        raise credentials_exception

    # Extract user_id from token
    user_id_raw = payload.get("sub")
    if not isinstance(user_id_raw, str) or user_id_raw is None:
        raise credentials_exception
    user_id: str = user_id_raw

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current authenticated and active user.

    This is a wrapper around get_current_user that also checks
    if the user account is active.

    Raises:
        HTTPException: If user account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return current_user
