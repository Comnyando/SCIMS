"""
Commons-specific dependencies for authorization checks.
"""

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.dependencies import get_current_active_user
from app.database import get_db


async def require_moderator(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to require moderator/admin permissions.

    For now, we'll use a simple check - in the future this could be
    extended to check roles (is_moderator, is_admin, etc.).

    TODO: Implement proper role-based access control
    """
    # For MVP: Allow all active users as moderators
    # In production, add role checks (is_moderator, is_admin, etc.)
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account must be active to moderate",
        )

    # TODO: Add role checking when roles are implemented
    # if not (current_user.is_moderator or current_user.is_admin):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Moderator permissions required",
    #     )

    return current_user
