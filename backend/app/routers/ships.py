"""
Ships router for ship management.

This router provides endpoints for managing ships:
- List ships with filtering
- Create new ships (automatically creates cargo location)
- Get ship details
- Update ships (including moving between locations)
- Delete ships
"""

from typing import Optional
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid

from app.database import get_db
from app.models.ship import Ship
from app.models.location import Location
from app.models.organization_member import OrganizationMember
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.ship import ShipCreate, ShipUpdate, ShipResponse
from app.config import settings


router = APIRouter(prefix=f"{settings.api_v1_prefix}/ships", tags=["ships"])


def check_ship_access(
    ship: Ship,
    current_user: User,
    db: Session,
    require_minimum_role: str = "viewer",
) -> bool:
    """
    Check if current user has access to a ship based on ownership.

    Returns True if user has access, False otherwise.
    For organization-owned ships, checks membership and role.
    """
    # User-owned ships: user must be the owner
    if ship.owner_type == "user":
        return ship.owner_id == current_user.id

    # Organization-owned ships: user must be a member with required role
    if ship.owner_type == "organization":
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.organization_id == ship.owner_id,
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

    return False


@router.get("", response_model=dict)
async def list_ships(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    owner_type: Optional[str] = Query(None, description="Filter by owner type: user, organization"),
    owner_id: Optional[str] = Query(None, description="Filter by owner ID"),
    ship_type: Optional[str] = Query(None, description="Filter by ship type"),
    current_location_id: Optional[str] = Query(None, description="Filter by current location ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List ships accessible to the current user.

    By default, returns ships owned by the user or organizations they're a member of.
    Can be filtered by owner_type, owner_id, ship_type, and current_location_id.
    """
    query = db.query(Ship)

    # Apply filters
    if owner_type:
        query = query.filter(Ship.owner_type == owner_type)
    if owner_id:
        query = query.filter(Ship.owner_id == owner_id)
    if ship_type:
        query = query.filter(Ship.ship_type == ship_type)
    if current_location_id:
        query = query.filter(Ship.current_location_id == current_location_id)

    # Filter to only accessible ships
    # User-owned ships
    user_owned = Ship.owner_type == "user"
    user_owned = user_owned & (Ship.owner_id == current_user.id)

    # Organization-owned ships where user is a member
    org_memberships = (
        db.query(OrganizationMember.organization_id)
        .filter(OrganizationMember.user_id == current_user.id)
        .distinct()
        .all()
    )
    org_ids = [str(m[0]) for m in org_memberships]
    org_owned = Ship.owner_type == "organization"
    if org_ids:
        org_owned = org_owned & Ship.owner_id.in_(org_ids)
    else:
        from sqlalchemy import literal

        org_owned = literal(False)

    # Combine filters (user-owned OR org-owned)
    query = query.filter(or_(user_owned, org_owned))

    # Get total count
    total = query.count()

    # Apply pagination and order by name
    ships = query.order_by(Ship.name).offset(skip).limit(limit).all()

    # Filter in-memory for fine-grained access control
    accessible_ships = [
        ship for ship in ships if check_ship_access(ship, current_user, db, "viewer")
    ]

    return {
        "ships": [ShipResponse.model_validate(ship) for ship in accessible_ships],
        "total": len(accessible_ships),
        "skip": skip,
        "limit": limit,
        "pages": ceil(len(accessible_ships) / limit) if limit > 0 else 0,
    }


@router.post("", response_model=ShipResponse, status_code=status.HTTP_201_CREATED)
async def create_ship(
    ship_data: ShipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new ship.

    Automatically creates a cargo location for the ship.
    For user-owned ships: owner_id must match current user.
    For organization-owned ships: user must be a member with 'member' role or higher.
    """
    # Validate ownership
    if ship_data.owner_type == "user":
        if ship_data.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create ship owned by another user",
            )
    elif ship_data.owner_type == "organization":
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.organization_id == ship_data.owner_id,
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
                detail=f"User role '{membership.role}' does not have permission to create ships",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid owner_type: {ship_data.owner_type}. Must be 'user' or 'organization'",
        )

    # Validate current_location_id if provided
    if ship_data.current_location_id:
        location = db.query(Location).filter(Location.id == ship_data.current_location_id).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with id '{ship_data.current_location_id}' not found",
            )

    # Create cargo location for the ship
    cargo_location = Location(
        id=str(uuid.uuid4()),
        name=f"{ship_data.name} Cargo",
        type="ship",
        owner_type="ship",
        owner_id=str(uuid.uuid4()),  # Will be updated to ship.id after ship creation
        parent_location_id=ship_data.current_location_id,
        meta={"cargo_grid": True, "ship_name": ship_data.name},
    )
    db.add(cargo_location)
    db.flush()  # Flush to get cargo_location.id

    # Create ship with cargo_location_id
    new_ship = Ship(
        name=ship_data.name,
        ship_type=ship_data.ship_type,
        owner_type=ship_data.owner_type,
        owner_id=ship_data.owner_id,
        current_location_id=ship_data.current_location_id,
        cargo_location_id=cargo_location.id,
        meta=ship_data.metadata,
    )
    db.add(new_ship)
    db.flush()  # Flush to get ship.id

    # Update cargo location owner_id to reference the ship
    cargo_location.owner_id = new_ship.id
    db.commit()

    db.refresh(new_ship)
    db.refresh(cargo_location)

    return ShipResponse.model_validate(new_ship)


@router.get("/{ship_id}", response_model=ShipResponse)
async def get_ship(
    ship_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get ship details by ID.
    """
    ship = db.query(Ship).filter(Ship.id == ship_id).first()

    if ship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ship with id '{ship_id}' not found",
        )

    # Check access
    if not check_ship_access(ship, current_user, db, "viewer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this ship",
        )

    return ShipResponse.model_validate(ship)


@router.patch("/{ship_id}", response_model=ShipResponse)
async def update_ship(
    ship_id: str,
    ship_data: ShipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a ship by ID.

    Supports moving ships between locations by updating current_location_id.
    Requires 'member' role or higher for organization-owned ships.
    Only the owner can update user-owned ships.
    """
    ship = db.query(Ship).filter(Ship.id == ship_id).first()

    if ship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ship with id '{ship_id}' not found",
        )

    # Check access (require 'member' role for updates)
    required_role = "viewer" if ship.owner_type == "user" else "member"
    if not check_ship_access(ship, current_user, db, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to update this ship",
        )

    # Validate current_location_id if being updated (moving ship)
    if ship_data.current_location_id is not None:
        if ship_data.current_location_id != ship.current_location_id:
            if ship_data.current_location_id:  # Not clearing location (ship in transit)
                location = (
                    db.query(Location).filter(Location.id == ship_data.current_location_id).first()
                )
                if not location:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Location with id '{ship_data.current_location_id}' not found",
                    )
            # Update cargo location's parent_location_id to match ship's new location
            if ship.cargo_location_id:
                cargo_location = (
                    db.query(Location).filter(Location.id == ship.cargo_location_id).first()
                )
                if cargo_location:
                    cargo_location.parent_location_id = ship_data.current_location_id

    # Update fields
    update_data = ship_data.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["meta"] = update_data.pop("metadata")

    for field, value in update_data.items():
        setattr(ship, field, value)

    db.commit()
    db.refresh(ship)

    return ShipResponse.model_validate(ship)


@router.delete("/{ship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ship(
    ship_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a ship by ID.

    This will also delete the associated cargo location and all items in it.
    Requires 'admin' role or higher for organization-owned ships.
    Only the owner can delete user-owned ships.
    """
    ship = db.query(Ship).filter(Ship.id == ship_id).first()

    if ship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ship with id '{ship_id}' not found",
        )

    # Check access (require 'admin' role for deletion)
    required_role = "viewer" if ship.owner_type == "user" else "admin"
    if not check_ship_access(ship, current_user, db, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to delete this ship",
        )

    # Delete cargo location (will cascade delete item_stocks and item_history)
    if ship.cargo_location_id:
        cargo_location = db.query(Location).filter(Location.id == ship.cargo_location_id).first()
        if cargo_location:
            db.delete(cargo_location)

    # Delete ship
    db.delete(ship)
    db.commit()

    return None
