"""
Security utilities for password hashing and JWT token management.

This module provides functions for:
- Password hashing and verification (bcrypt)
- JWT token generation and validation
- Token payload creation and parsing
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, cast
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    hashed = pwd_context.hash(password)
    return cast(str, hashed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    result = pwd_context.verify(plain_password, hashed_password)
    return cast(bool, result)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing the data to encode in the token (typically user_id, email)
        expires_delta: Optional custom expiration time. If None, uses settings default

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return cast(str, encoded_jwt)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.

    Refresh tokens have a longer expiration time than access tokens
    and are used to obtain new access tokens without re-authentication.

    Args:
        data: Dictionary containing the data to encode in the token (typically user_id)

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return cast(str, encoded_jwt)


def decode_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string to decode
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload as dictionary, or None if invalid/expired
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        payload_dict = cast(Dict[str, Any], payload)

        # Verify token type matches expected type
        if payload_dict.get("type") != token_type:
            return None

        return payload_dict
    except JWTError:
        return None
