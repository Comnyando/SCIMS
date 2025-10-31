"""
Authentication router for user registration, login, and token management.

This router provides endpoints for:
- User registration
- User login
- Token refresh
- Current user information
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.dependencies import get_current_active_user
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    LoginResponse,
    RegisterResponse,
    Token,
)
from app.schemas.user import UserResponse
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/auth", tags=["authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.

    Creates a new user with the provided email, username (optional), and password.
    The password is hashed before storage. Upon successful registration, returns
    JWT access and refresh tokens along with user information.

    Args:
        request: Registration request with email, optional username, and password
        db: Database session

    Returns:
        RegisterResponse with access token, refresh token, and user information

    Raises:
        HTTPException: If email or username already exists
    """
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username is provided and if it already exists
    if request.username:
        existing_username = db.query(User).filter(User.username == request.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    # Create new user
    hashed_password = hash_password(request.password)
    new_user = User(
        email=request.email,
        username=request.username,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,  # Email verification will be added in future
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Email or username may already be in use.",
        )

    # Create tokens (convert UUID to string for JWT)
    access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    return RegisterResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return JWT tokens.

    Verifies the user's email and password, then returns access and refresh tokens.
    Only active users can log in.

    Args:
        request: Login request with email and password
        db: Database session

    Returns:
        LoginResponse with access token, refresh token, and user information

    Raises:
        HTTPException: If credentials are invalid or user is inactive
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        # Use same error message to prevent email enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not user.hashed_password or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create tokens (convert UUID to string for JWT)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Exchange a refresh token for a new access token.

    Validates the provided refresh token and issues a new access token
    without requiring the user to log in again.

    Args:
        request: Refresh token request with refresh token
        db: Database session

    Returns:
        Token with new access token and refresh token

    Raises:
        HTTPException: If refresh token is invalid or user not found
    """
    # Decode and validate refresh token
    payload = decode_token(request.refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Get user_id from token
    user_id_raw = payload.get("sub")
    if not isinstance(user_id_raw, str) or user_id_raw is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user_id: str = user_id_raw

    # Verify user exists and is active
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    # Optionally rotate refresh token for better security
    new_refresh_token = create_refresh_token(data={"sub": user.id})

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user information.

    Returns the user information for the currently authenticated user
    based on their JWT access token.

    Args:
        current_user: Current authenticated user (from dependency)

    Returns:
        UserResponse with user information
    """
    return UserResponse.model_validate(current_user)
