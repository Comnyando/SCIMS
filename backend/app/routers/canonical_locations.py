"""
Canonical Locations router for managing public/canonical locations.

Canonical locations are public locations that many players reference,
such as game stations, planets, or major landmarks. These are read-only
for most users, but can be created/updated by admins/moderators.

This router provides:
- Public read endpoints (no auth required for listing/viewing)
- Admin endpoints for creating and managing canonical locations
"""

from typing import Optional
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Location
from app.core.dependencies import get_current_active_user, get_current_user
from app.models.user import User
from app.schemas.canonical_location import (
    CanonicalLocationCreate,
    CanonicalLocationUpdate,
    CanonicalLocationResponse,
)
from app.config import settings

router = APIRouter(
    prefix=f"{settings.api_v1_prefix}/canonical-locations",
    tags=["canonical-locations"],
)


def check_admin_permission(current_user: User) -> bool:
    """
    Check if user has admin permissions to manage canonical locations.

    For now, any authenticated user can create canonical locations.
    In the future, this can be restricted to admins/moderators based on RBAC.
    """
    # TODO: Implement proper admin/moderator role checking when RBAC is expanded
    return current_user.is_active


@router.get("", response_model=dict)
async def list_canonical_locations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    type: Optional[str] = Query(None, description="Filter by location type"),
    parent_location_id: Optional[str] = Query(
        None, description="Filter by parent canonical location ID"
    ),
    search: Optional[str] = Query(None, description="Search term for name"),
    db: Session = Depends(get_db),
):
    """
    List canonical locations (public read endpoint).

    No authentication required. Returns all canonical/public locations
    that players can reference when creating their own locations.
    """
    query = db.query(Location).filter(Location.is_canonical == True)

    # Apply filters
    if type:
        query = query.filter(Location.type == type)
    if parent_location_id:
        query = query.filter(Location.parent_location_id == parent_location_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(Location.name.ilike(search_pattern))

    # Get total count
    total = query.count()

    # Apply pagination and order by name
    locations = query.order_by(Location.name).offset(skip).limit(limit).all()

    return {
        "locations": [CanonicalLocationResponse.model_validate(loc) for loc in locations],
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }


@router.get("/{location_id}", response_model=CanonicalLocationResponse)
async def get_canonical_location(
    location_id: str,
    db: Session = Depends(get_db),
):
    """
    Get canonical location details by ID (public read endpoint).

    No authentication required.
    """
    location = (
        db.query(Location)
        .filter(
            Location.id == location_id,
            Location.is_canonical == True,
        )
        .first()
    )

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canonical location with id '{location_id}' not found",
        )

    return CanonicalLocationResponse.model_validate(location)


@router.post("", response_model=CanonicalLocationResponse, status_code=status.HTTP_201_CREATED)
async def create_canonical_location(
    location_data: CanonicalLocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new canonical location (admin only).

    Canonical locations are public locations that many players can reference.
    Only authenticated users with appropriate permissions can create them.
    """
    # Check admin permission
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied to create canonical locations",
        )

    # Validate parent_location_id if provided (must be canonical)
    if location_data.parent_location_id:
        parent = (
            db.query(Location)
            .filter(
                Location.id == location_data.parent_location_id,
                Location.is_canonical == True,
            )
            .first()
        )
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent canonical location with id '{location_data.parent_location_id}' not found",
            )

    # Check if canonical location with same name already exists
    existing = (
        db.query(Location)
        .filter(
            Location.name == location_data.name,
            Location.is_canonical == True,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Canonical location with name '{location_data.name}' already exists",
        )

    # Create canonical location
    # Canonical locations use owner_type="system" and a placeholder owner_id
    # In a production system, you might have a system user or handle this differently
    new_location = Location(
        name=location_data.name,
        type=location_data.type,
        owner_type="system",  # Canonical locations are system-owned
        owner_id="00000000-0000-0000-0000-000000000000",  # Placeholder system UUID
        parent_location_id=location_data.parent_location_id,
        is_canonical=True,
        created_by=current_user.id,
        meta=location_data.metadata,
    )

    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return CanonicalLocationResponse.model_validate(new_location)


@router.patch("/{location_id}", response_model=CanonicalLocationResponse)
async def update_canonical_location(
    location_id: str,
    location_data: CanonicalLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a canonical location (admin only).

    Only authenticated users with appropriate permissions can update canonical locations.
    """
    # Check admin permission
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied to update canonical locations",
        )

    location = (
        db.query(Location)
        .filter(
            Location.id == location_id,
            Location.is_canonical == True,
        )
        .first()
    )

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canonical location with id '{location_id}' not found",
        )

    # Validate parent_location_id if being updated
    if location_data.parent_location_id is not None:
        if location_data.parent_location_id != location.parent_location_id:
            if location_data.parent_location_id:  # Not clearing parent
                parent = (
                    db.query(Location)
                    .filter(
                        Location.id == location_data.parent_location_id,
                        Location.is_canonical == True,
                    )
                    .first()
                )
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Parent canonical location with id '{location_data.parent_location_id}' not found",
                    )
                # Prevent circular references
                if location_data.parent_location_id == location_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Canonical location cannot be its own parent",
                    )

    # Update fields
    update_data = location_data.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["meta"] = update_data.pop("metadata")

    for field, value in update_data.items():
        setattr(location, field, value)

    db.commit()
    db.refresh(location)

    return CanonicalLocationResponse.model_validate(location)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_canonical_location(
    location_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a canonical location (admin only).

    Only authenticated users with appropriate permissions can delete canonical locations.
    Note: This will set canonical_location_id to NULL for any locations referencing this canonical location.
    """
    # Check admin permission
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied to delete canonical locations",
        )

    location = (
        db.query(Location)
        .filter(
            Location.id == location_id,
            Location.is_canonical == True,
        )
        .first()
    )

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canonical location with id '{location_id}' not found",
        )

    # Check if any locations reference this canonical location
    referencing_count = (
        db.query(Location).filter(Location.canonical_location_id == location_id).count()
    )

    if referencing_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete canonical location: {referencing_count} location(s) reference it. Remove references first or update them.",
        )

    db.delete(location)
    db.commit()

    return None
