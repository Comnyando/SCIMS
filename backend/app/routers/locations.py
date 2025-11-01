"""
Locations router for storage location management.

This router provides endpoints for managing storage locations:
- List locations with filtering (by owner, type, etc.)
- Create new locations
- Get location details
- Update locations
- Delete locations

Locations can be owned by users, organizations, or ships.
"""

from typing import Optional
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.location import Location
from app.models.organization_member import OrganizationMember
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse
from app.config import settings


router = APIRouter(prefix=f"{settings.api_v1_prefix}/locations", tags=["locations"])


def check_location_access(
    location: Location,
    current_user: User,
    db: Session,
    require_minimum_role: str = "viewer",
) -> bool:
    """
    Check if current user has access to a location based on ownership.

    Returns True if user has access, False otherwise.
    For organization-owned locations, checks membership and role.
    """
    # User-owned locations: user must be the owner
    if location.owner_type == "user":
        return location.owner_id == current_user.id

    # Organization-owned locations: user must be a member with required role
    if location.owner_type == "organization":
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.organization_id == location.owner_id,
            )
            .first()
        )
        if not membership:
            return False

        # Check role hierarchy
        from app.core.rbac import has_minimum_role, ROLE_HIERARCHY

        user_level = ROLE_HIERARCHY.get(membership.role, -1)
        required_level = ROLE_HIERARCHY.get(require_minimum_role, 999)
        return user_level >= required_level

    # Ship-owned locations: check ship ownership (delegated to ship router)
    # For now, return False (should check ship ownership separately)
    if location.owner_type == "ship":
        # TODO: Check ship ownership when ship router is implemented
        return False

    return False


@router.get("", response_model=dict)
async def list_locations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    owner_type: Optional[str] = Query(
        None, description="Filter by owner type: user, organization, ship"
    ),
    owner_id: Optional[str] = Query(None, description="Filter by owner ID"),
    type: Optional[str] = Query(None, alias="location_type", description="Filter by location type"),
    location_type: Optional[str] = Query(None, description="Filter by location type (deprecated, use 'type')"),
    parent_location_id: Optional[str] = Query(None, description="Filter by parent location ID"),
    search: Optional[str] = Query(None, description="Search term for location name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List locations accessible to the current user.

    By default, returns locations owned by the user or organizations they're a member of.
    Can be filtered by owner_type, owner_id, location_type, and parent_location_id.
    """
    query = db.query(Location)

    # Apply filters
    if owner_type:
        query = query.filter(Location.owner_type == owner_type)
    if owner_id:
        query = query.filter(Location.owner_id == owner_id)
    # Support both 'type' and 'location_type' for backwards compatibility
    location_type_filter = type or location_type
    if location_type_filter:
        query = query.filter(Location.type == location_type_filter)
    if parent_location_id:
        query = query.filter(Location.parent_location_id == parent_location_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(Location.name.ilike(search_pattern))

    # Filter to only accessible locations
    # Canonical locations are always accessible (public read)
    canonical_locations = Location.is_canonical == True

    # User-owned locations
    user_owned = Location.owner_type == "user"
    user_owned = user_owned & (Location.owner_id == current_user.id)

    # Organization-owned locations where user is a member
    org_memberships = (
        db.query(OrganizationMember.organization_id)
        .filter(OrganizationMember.user_id == current_user.id)
        .distinct()
        .all()
    )
    org_ids = [str(m[0]) for m in org_memberships]  # Extract organization IDs
    org_owned = Location.owner_type == "organization"
    if org_ids:
        org_owned = org_owned & Location.owner_id.in_(org_ids)
    else:
        from sqlalchemy import literal

        org_owned = literal(False)

    # Combine filters (canonical OR user-owned OR org-owned)
    query = query.filter(or_(canonical_locations, user_owned, org_owned))

    # Get total count
    total = query.count()

    # Apply pagination and order by name
    locations = query.order_by(Location.name).offset(skip).limit(limit).all()

    # Filter in-memory for fine-grained access control
    accessible_locations = [
        loc for loc in locations if check_location_access(loc, current_user, db, "viewer")
    ]

    return {
        "locations": [LocationResponse.model_validate(loc) for loc in accessible_locations],
        "total": len(accessible_locations),
        "skip": skip,
        "limit": limit,
        "pages": ceil(len(accessible_locations) / limit) if limit > 0 else 0,
    }


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new location.

    For user-owned locations: owner_id must match current user.
    For organization-owned locations: user must be a member with 'member' role or higher.
    """
    # Validate ownership
    if location_data.owner_type == "user":
        if location_data.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create location owned by another user",
            )
    elif location_data.owner_type == "organization":
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.organization_id == location_data.owner_id,
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this organization",
            )
        from app.core.rbac import has_minimum_role

        if not has_minimum_role(membership.role, "member"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{membership.role}' does not have permission to create locations",
            )
    elif location_data.owner_type == "ship":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot directly create ship-owned locations. Create a ship instead.",
        )

    # Validate parent_location_id if provided
    if location_data.parent_location_id:
        parent = db.query(Location).filter(Location.id == location_data.parent_location_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent location with id '{location_data.parent_location_id}' not found",
            )
        # Verify access to parent location
        if not check_location_access(parent, current_user, db, "viewer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access parent location",
            )

    # Validate canonical_location_id if provided
    if location_data.canonical_location_id:
        canonical = (
            db.query(Location)
            .filter(
                Location.id == location_data.canonical_location_id,
                Location.is_canonical == True,
            )
            .first()
        )
        if not canonical:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Canonical location with id '{location_data.canonical_location_id}' not found or is not canonical",
            )

    new_location = Location(
        name=location_data.name,
        type=location_data.type,
        owner_type=location_data.owner_type,
        owner_id=location_data.owner_id,
        parent_location_id=location_data.parent_location_id,
        canonical_location_id=location_data.canonical_location_id,
        is_canonical=False,  # User-created locations are never canonical
        meta=location_data.metadata,
    )

    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return LocationResponse.model_validate(new_location)


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get location details by ID.
    """
    location = db.query(Location).filter(Location.id == location_id).first()

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id '{location_id}' not found",
        )

    # Canonical locations are always accessible (public read)
    if not location.is_canonical:
        # Check access for non-canonical locations
        if not check_location_access(location, current_user, db, "viewer"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this location",
            )

    return LocationResponse.model_validate(location)


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: str,
    location_data: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a location by ID.

    Requires 'member' role or higher for organization-owned locations.
    Only the owner can update user-owned locations.
    """
    location = db.query(Location).filter(Location.id == location_id).first()

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id '{location_id}' not found",
        )

    # Canonical locations cannot be updated through this endpoint (use canonical locations API)
    if location.is_canonical:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update canonical locations through this endpoint. Use /api/v1/canonical-locations",
        )

    # Check access (require 'member' role for updates)
    required_role = "viewer" if location.owner_type == "user" else "member"
    if not check_location_access(location, current_user, db, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to update this location",
        )

    # Validate canonical_location_id if being updated
    if location_data.canonical_location_id is not None:
        if location_data.canonical_location_id != location.canonical_location_id:
            canonical = (
                db.query(Location)
                .filter(
                    Location.id == location_data.canonical_location_id,
                    Location.is_canonical == True,
                )
                .first()
            )
            if not canonical:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Canonical location with id '{location_data.canonical_location_id}' not found or is not canonical",
                )

    # Validate parent_location_id if being updated
    if location_data.parent_location_id is not None:
        if location_data.parent_location_id != location.parent_location_id:
            if location_data.parent_location_id:  # Not clearing parent
                parent = (
                    db.query(Location)
                    .filter(Location.id == location_data.parent_location_id)
                    .first()
                )
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Parent location with id '{location_data.parent_location_id}' not found",
                    )
                # Prevent circular references (location cannot be its own ancestor)
                # Simple check: prevent setting parent to itself
                if location_data.parent_location_id == location_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Location cannot be its own parent",
                    )
                # Verify access to new parent
                if not check_location_access(parent, current_user, db, "viewer"):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cannot access parent location",
                    )

    # Update fields
    update_data = location_data.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["meta"] = update_data.pop("metadata")

    for field, value in update_data.items():
        setattr(location, field, value)

    db.commit()
    db.refresh(location)

    return LocationResponse.model_validate(location)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a location by ID.

    Requires 'admin' role or higher for organization-owned locations.
    Only the owner can delete user-owned locations.
    """
    location = db.query(Location).filter(Location.id == location_id).first()

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id '{location_id}' not found",
        )

    # Check access (require 'admin' role for deletion)
    required_role = "viewer" if location.owner_type == "user" else "admin"
    if not check_location_access(location, current_user, db, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to delete this location",
        )

    db.delete(location)
    db.commit()

    return None
