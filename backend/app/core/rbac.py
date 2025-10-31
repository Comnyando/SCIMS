"""
Role-Based Access Control (RBAC) utilities.

This module provides functions and dependencies for enforcing role-based
permissions throughout the application. The system supports four roles:
- owner: Full control over organization
- admin: Can manage members and settings
- member: Can create and edit inventory items
- viewer: Read-only access

Roles are stored in the organization_members table and checked dynamically.
"""

from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.core.dependencies import get_current_active_user
from app.database import get_db

# Role hierarchy (higher index = more permissions)
# Used for role comparison and permission checks
ROLE_HIERARCHY = {
    "viewer": 0,
    "member": 1,
    "admin": 2,
    "owner": 3,
}


def has_minimum_role(user_role: str, required_role: str) -> bool:
    """
    Check if a user's role meets the minimum required role level.

    Uses the role hierarchy to determine if the user has sufficient permissions.
    For example, an "admin" role satisfies requirements for "member" or "viewer".

    Args:
        user_role: The user's current role
        required_role: The minimum role required

    Returns:
        True if user has sufficient permissions, False otherwise

    Examples:
        >>> has_minimum_role("admin", "member")
        True
        >>> has_minimum_role("member", "admin")
        False
    """
    user_level = ROLE_HIERARCHY.get(user_role, -1)
    required_level = ROLE_HIERARCHY.get(required_role, 999)
    return user_level >= required_level


def get_user_organization_role(
    user_id: str,
    organization_id: str,
    db: Session,
) -> Optional[str]:
    """
    Get a user's role in a specific organization.

    Args:
        user_id: User UUID
        organization_id: Organization UUID
        db: Database session

    Returns:
        User's role string, or None if user is not a member
    """
    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == organization_id,
        )
        .first()
    )

    if membership is None:
        return None

    return membership.role


def require_organization_membership(
    organization_id: str,
    minimum_role: str = "member",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> OrganizationMember:
    """
    Dependency to ensure user is a member of an organization with required role.

    This dependency:
    1. Checks if the current user is a member of the specified organization
    2. Verifies the user has at least the minimum required role
    3. Returns the membership record if successful

    Args:
        organization_id: Organization UUID to check membership for
        minimum_role: Minimum role required (default: "member")
        current_user: Current authenticated user (from dependency)
        db: Database session (from dependency)

    Returns:
        OrganizationMember record

    Raises:
        HTTPException: If user is not a member or lacks required role
    """
    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == organization_id,
        )
        .first()
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this organization",
        )

    if not has_minimum_role(membership.role, minimum_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User role '{membership.role}' does not meet minimum requirement: '{minimum_role}'",
        )

    return membership


def require_organization_role(
    organization_id: str,
    required_role: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> OrganizationMember:
    """
    Dependency to ensure user has a specific role in an organization.

    Unlike require_organization_membership, this requires an exact role match.
    Use this when you need a specific role (e.g., "owner" for deletion).

    Args:
        organization_id: Organization UUID
        required_role: Exact role required
        current_user: Current authenticated user (from dependency)
        db: Database session (from dependency)

    Returns:
        OrganizationMember record

    Raises:
        HTTPException: If user doesn't have the exact role
    """
    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == organization_id,
        )
        .first()
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this organization",
        )

    if membership.role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User role '{membership.role}' does not match required role: '{required_role}'",
        )

    return membership
