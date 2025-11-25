"""
Inventory router for managing stock levels and inventory operations.

This router provides endpoints for:
- Viewing inventory stock levels with filters
- Adjusting inventory (add/remove items)
- Transferring items between locations
- Viewing transaction history
- Managing stock reservations
"""

from typing import Optional
from math import ceil
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.database import get_db
from app.models.item import Item
from app.models.location import Location
from app.models.item_stock import ItemStock
from app.models.item_history import ItemHistory, TRANSACTION_TYPES
from app.models.organization_member import OrganizationMember
from app.models.ship import Ship
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.inventory import (
    InventoryStock,
    InventoryAdjust,
    InventoryTransfer,
    InventoryHistory,
    StockReservation,
)
from app.routers.locations import check_location_access
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/inventory", tags=["inventory"])


def check_location_access_for_inventory(
    location: Location,
    current_user: User,
    db: Session,
    require_minimum_role: str = "viewer",
) -> bool:
    """
    Check if current user has access to a location for inventory operations.

    Uses the same logic as locations router but also handles ship-owned locations.
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

        from app.core.rbac import has_minimum_role, ROLE_HIERARCHY

        user_level = ROLE_HIERARCHY.get(membership.role, -1)
        required_level = ROLE_HIERARCHY.get(require_minimum_role, 999)
        return user_level >= required_level

    # Ship-owned locations: check ship ownership
    if location.owner_type == "ship":
        ship = db.query(Ship).filter(Ship.cargo_location_id == location.id).first()
        if not ship:
            return False
        # Check if user owns the ship or is member of owning organization
        if ship.owner_type == "user":
            return ship.owner_id == current_user.id
        elif ship.owner_type == "organization":
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
            from app.core.rbac import has_minimum_role, ROLE_HIERARCHY

            user_level = ROLE_HIERARCHY.get(membership.role, -1)
            required_level = ROLE_HIERARCHY.get(require_minimum_role, 999)
            return user_level >= required_level

    return False


def log_item_history(
    db: Session,
    item_id: str,
    location_id: str,
    quantity_change: Decimal,
    transaction_type: str,
    performed_by: str,
    notes: Optional[str] = None,
    related_craft_id: Optional[str] = None,
) -> ItemHistory:
    """
    Create an item history record for an inventory transaction.

    Args:
        db: Database session
        item_id: Item UUID
        location_id: Location UUID
        quantity_change: Amount changed (positive/negative)
        transaction_type: Type of transaction (add, remove, transfer, craft, consume)
        performed_by: User UUID who performed the action
        notes: Optional notes about the transaction
        related_craft_id: Optional craft UUID (for future use)

    Returns:
        Created ItemHistory record
    """
    if transaction_type not in TRANSACTION_TYPES:
        raise ValueError(f"Invalid transaction_type: {transaction_type}")

    history_entry = ItemHistory(
        item_id=item_id,
        location_id=location_id,
        quantity_change=quantity_change,
        transaction_type=transaction_type,
        performed_by=performed_by,
        notes=notes,
        related_craft_id=related_craft_id,
    )
    db.add(history_entry)
    return history_entry


def get_or_create_item_stock(
    db: Session, item_id: str, location_id: str, updated_by: str
) -> ItemStock:
    """
    Get existing ItemStock or create a new one with zero quantities.

    Args:
        db: Database session
        item_id: Item UUID
        location_id: Location UUID
        updated_by: User UUID who is updating

    Returns:
        ItemStock record
    """
    stock = (
        db.query(ItemStock)
        .filter(ItemStock.item_id == item_id, ItemStock.location_id == location_id)
        .first()
    )

    if not stock:
        stock = ItemStock(
            item_id=item_id,
            location_id=location_id,
            quantity=Decimal("0"),
            reserved_quantity=Decimal("0"),
            updated_by=updated_by,
        )
        db.add(stock)

    return stock


@router.get("", response_model=dict)
async def list_inventory(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    item_id: Optional[str] = Query(None, description="Filter by item UUID"),
    location_id: Optional[str] = Query(None, description="Filter by location UUID"),
    search: Optional[str] = Query(None, description="Search term for item name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List inventory stock levels with filters.

    Only returns stock at locations accessible to the current user.
    Can filter by item_id, location_id, or search by item name.
    """
    query = (
        db.query(ItemStock, Item, Location)
        .join(Item, ItemStock.item_id == Item.id)
        .join(Location, ItemStock.location_id == Location.id)
    )

    # Apply filters
    if item_id:
        query = query.filter(ItemStock.item_id == item_id)
    if location_id:
        query = query.filter(ItemStock.location_id == location_id)
    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))

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
    org_ids = [str(m[0]) for m in org_memberships]
    org_owned = Location.owner_type == "organization"
    if org_ids:
        org_owned = org_owned & Location.owner_id.in_(org_ids)
    else:
        from sqlalchemy import literal

        org_owned = literal(False)

    # Ship-owned locations (check via Ship relationship)
    ship_locations = Location.owner_type == "ship"
    # Get accessible ship cargo location IDs
    user_ships_query = db.query(Ship.cargo_location_id).filter(
        Ship.owner_type == "user", Ship.owner_id == current_user.id
    )
    user_ship_ids = [str(row[0]) for row in user_ships_query.all() if row[0]]

    org_ship_ids = []
    if org_ids:
        org_ships_query = db.query(Ship.cargo_location_id).filter(
            Ship.owner_type == "organization", Ship.owner_id.in_(org_ids)
        )
        org_ship_ids = [str(row[0]) for row in org_ships_query.all() if row[0]]

    accessible_ship_ids = user_ship_ids + org_ship_ids

    if accessible_ship_ids:
        ship_owned = ship_locations & Location.id.in_(accessible_ship_ids)
    else:
        from sqlalchemy import literal

        ship_owned = literal(False)  # type: ignore[assignment]

    # Combine filters
    query = query.filter(
        or_(
            canonical_locations,
            user_owned,
            org_owned,
            ship_owned,
        )
    )

    try:
        # Get total count
        total = query.count()

        # Apply pagination and order by item name
        results = query.order_by(Item.name).offset(skip).limit(limit).all()

        # Filter in-memory for fine-grained access control and build response
        inventory_items = []
        for stock, item, location in results:
            if check_location_access_for_inventory(location, current_user, db, "viewer"):
                inventory_items.append(
                    InventoryStock(
                        item_id=stock.item_id,
                        location_id=stock.location_id,
                        quantity=stock.quantity,
                        reserved_quantity=stock.reserved_quantity,
                        available_quantity=stock.available_quantity,
                        item_name=item.name,
                        item_category=item.category,
                        location_name=location.name,
                        location_type=location.type,
                        last_updated=stock.last_updated,
                        updated_by_username=stock.updater.username if stock.updater else None,
                    )
                )

        return {
            "items": inventory_items,
            "total": len(inventory_items),
            "skip": skip,
            "limit": limit,
            "pages": ceil(len(inventory_items) / limit) if limit > 0 else 0,
        }
    except Exception as e:
        # Log error and return empty result instead of crashing
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error listing inventory: {str(e)}", exc_info=True)
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "pages": 0,
        }


@router.post("/adjust", response_model=InventoryStock, status_code=status.HTTP_200_OK)
async def adjust_inventory(
    adjustment: InventoryAdjust,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Adjust inventory quantity (add or remove items).

    Positive quantity_change adds items, negative removes items.
    Requires 'member' role or higher for organization-owned locations.
    """
    # Validate item exists
    item = db.query(Item).filter(Item.id == adjustment.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id '{adjustment.item_id}' not found",
        )

    # Validate location exists and check access
    location = db.query(Location).filter(Location.id == adjustment.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id '{adjustment.location_id}' not found",
        )

    # Check access - require 'member' role for write operations
    if not check_location_access_for_inventory(location, current_user, db, "member"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to adjust inventory at this location",
        )

    # Get or create stock record
    stock = get_or_create_item_stock(
        db, adjustment.item_id, adjustment.location_id, current_user.id
    )

    # Validate we're not removing more than available
    if adjustment.quantity_change < 0:
        available = stock.quantity - stock.reserved_quantity
        if abs(adjustment.quantity_change) > available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot remove {abs(adjustment.quantity_change)} items. Only {available} available (after reserved).",
            )

    # Update stock
    stock.quantity += adjustment.quantity_change
    stock.updated_by = current_user.id

    # Determine transaction type
    transaction_type = "add" if adjustment.quantity_change > 0 else "remove"

    # Log history
    log_item_history(
        db=db,
        item_id=adjustment.item_id,
        location_id=adjustment.location_id,
        quantity_change=adjustment.quantity_change,
        transaction_type=transaction_type,
        performed_by=current_user.id,
        notes=adjustment.notes,
    )

    db.commit()
    db.refresh(stock)

    # Reload item and location for response
    item = db.query(Item).filter(Item.id == stock.item_id).first()
    location = db.query(Location).filter(Location.id == stock.location_id).first()

    if not item or not location:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve item or location details",
        )

    return InventoryStock(
        item_id=stock.item_id,
        location_id=stock.location_id,
        quantity=stock.quantity,
        reserved_quantity=stock.reserved_quantity,
        available_quantity=stock.available_quantity,
        item_name=item.name,
        item_category=item.category,
        location_name=location.name,
        location_type=location.type,
        last_updated=stock.last_updated,
        updated_by_username=stock.updater.username if stock.updater else None,
    )


@router.post("/transfer", response_model=dict, status_code=status.HTTP_200_OK)
async def transfer_inventory(
    transfer: InventoryTransfer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Transfer items from one location to another.

    Requires 'member' role or higher for both source and destination locations.
    Validates sufficient available quantity at source before transferring.
    """
    # Validate item exists
    item = db.query(Item).filter(Item.id == transfer.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id '{transfer.item_id}' not found",
        )

    # Validate source location exists and check access
    from_location = db.query(Location).filter(Location.id == transfer.from_location_id).first()
    if not from_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source location with id '{transfer.from_location_id}' not found",
        )

    if not check_location_access_for_inventory(from_location, current_user, db, "member"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to transfer from this location",
        )

    # Validate destination location exists and check access
    to_location = db.query(Location).filter(Location.id == transfer.to_location_id).first()
    if not to_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination location with id '{transfer.to_location_id}' not found",
        )

    if not check_location_access_for_inventory(to_location, current_user, db, "member"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to transfer to this location",
        )

    # Get source stock
    from_stock = get_or_create_item_stock(
        db, transfer.item_id, transfer.from_location_id, current_user.id
    )

    # Validate sufficient available quantity
    available = from_stock.quantity - from_stock.reserved_quantity
    if transfer.quantity > available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient quantity. Available: {available}, requested: {transfer.quantity}",
        )

    # Get or create destination stock
    to_stock = get_or_create_item_stock(
        db, transfer.item_id, transfer.to_location_id, current_user.id
    )

    # Perform transfer
    from_stock.quantity -= transfer.quantity
    from_stock.updated_by = current_user.id
    to_stock.quantity += transfer.quantity
    to_stock.updated_by = current_user.id

    # Log history for both locations
    log_item_history(
        db=db,
        item_id=transfer.item_id,
        location_id=transfer.from_location_id,
        quantity_change=-transfer.quantity,
        transaction_type="transfer",
        performed_by=current_user.id,
        notes=f"Transferred to {to_location.name}. {transfer.notes or ''}",
    )
    log_item_history(
        db=db,
        item_id=transfer.item_id,
        location_id=transfer.to_location_id,
        quantity_change=transfer.quantity,
        transaction_type="transfer",
        performed_by=current_user.id,
        notes=f"Transferred from {from_location.name}. {transfer.notes or ''}",
    )

    db.commit()
    db.refresh(from_stock)
    db.refresh(to_stock)

    # Build response
    return {
        "message": f"Successfully transferred {transfer.quantity} items",
        "from_location": {
            "id": from_stock.location_id,
            "name": from_location.name,
            "quantity": from_stock.quantity,
            "available_quantity": from_stock.available_quantity,
        },
        "to_location": {
            "id": to_stock.location_id,
            "name": to_location.name,
            "quantity": to_stock.quantity,
            "available_quantity": to_stock.available_quantity,
        },
    }


@router.post("/reserve", response_model=InventoryStock, status_code=status.HTTP_200_OK)
async def reserve_stock(
    reservation: StockReservation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Reserve stock for operations (e.g., crafting).

    Reserves quantity from available stock. Reserved items cannot be transferred
    or removed until unreserved.
    """
    # Validate item exists
    item = db.query(Item).filter(Item.id == reservation.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id '{reservation.item_id}' not found",
        )

    # Validate location exists and check access
    location = db.query(Location).filter(Location.id == reservation.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id '{reservation.location_id}' not found",
        )

    if not check_location_access_for_inventory(location, current_user, db, "member"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to reserve stock at this location",
        )

    # Get stock
    stock = get_or_create_item_stock(
        db, reservation.item_id, reservation.location_id, current_user.id
    )

    # Validate sufficient available quantity
    available = stock.quantity - stock.reserved_quantity
    if reservation.quantity > available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient available quantity. Available: {available}, requested: {reservation.quantity}",
        )

    # Reserve quantity
    stock.reserved_quantity += reservation.quantity
    stock.updated_by = current_user.id

    db.commit()
    db.refresh(stock)

    # Reload item and location for response
    item = db.query(Item).filter(Item.id == stock.item_id).first()
    location = db.query(Location).filter(Location.id == stock.location_id).first()

    if not item or not location:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve item or location details",
        )

    return InventoryStock(
        item_id=stock.item_id,
        location_id=stock.location_id,
        quantity=stock.quantity,
        reserved_quantity=stock.reserved_quantity,
        available_quantity=stock.available_quantity,
        item_name=item.name,
        item_category=item.category,
        location_name=location.name,
        location_type=location.type,
        last_updated=stock.last_updated,
        updated_by_username=stock.updater.username if stock.updater else None,
    )


@router.post("/unreserve", response_model=InventoryStock, status_code=status.HTTP_200_OK)
async def unreserve_stock(
    reservation: StockReservation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Unreserve previously reserved stock.

    Releases reserved quantity back to available stock.
    """
    # Validate item exists
    item = db.query(Item).filter(Item.id == reservation.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id '{reservation.item_id}' not found",
        )

    # Validate location exists and check access
    location = db.query(Location).filter(Location.id == reservation.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id '{reservation.location_id}' not found",
        )

    if not check_location_access_for_inventory(location, current_user, db, "member"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to unreserve stock at this location",
        )

    # Get stock
    stock = (
        db.query(ItemStock)
        .filter(
            ItemStock.item_id == reservation.item_id,
            ItemStock.location_id == reservation.location_id,
        )
        .first()
    )

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stock record found at this location",
        )

    # Validate sufficient reserved quantity
    if reservation.quantity > stock.reserved_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot unreserve {reservation.quantity}. Only {stock.reserved_quantity} reserved.",
        )

    # Unreserve quantity
    stock.reserved_quantity -= reservation.quantity
    stock.updated_by = current_user.id

    db.commit()
    db.refresh(stock)

    # Reload item and location for response
    item = db.query(Item).filter(Item.id == stock.item_id).first()
    location = db.query(Location).filter(Location.id == stock.location_id).first()

    if not item or not location:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve item or location details",
        )

    return InventoryStock(
        item_id=stock.item_id,
        location_id=stock.location_id,
        quantity=stock.quantity,
        reserved_quantity=stock.reserved_quantity,
        available_quantity=stock.available_quantity,
        item_name=item.name,
        item_category=item.category,
        location_name=location.name,
        location_type=location.type,
        last_updated=stock.last_updated,
        updated_by_username=stock.updater.username if stock.updater else None,
    )


@router.get("/history", response_model=dict)
async def get_inventory_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    item_id: Optional[str] = Query(None, description="Filter by item UUID"),
    location_id: Optional[str] = Query(None, description="Filter by location UUID"),
    transaction_type: Optional[str] = Query(
        None, description="Filter by transaction type: add, remove, transfer, craft, consume"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get inventory transaction history.

    Only returns history for locations accessible to the current user.
    Can filter by item_id, location_id, or transaction_type.
    """
    query = (
        db.query(ItemHistory, Item, Location, User)
        .join(Item, ItemHistory.item_id == Item.id)
        .join(Location, ItemHistory.location_id == Location.id)
        .join(User, ItemHistory.performed_by == User.id)
    )

    # Apply filters
    if item_id:
        query = query.filter(ItemHistory.item_id == item_id)
    if location_id:
        query = query.filter(ItemHistory.location_id == location_id)
    if transaction_type:
        if transaction_type not in TRANSACTION_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid transaction_type. Must be one of: {', '.join(TRANSACTION_TYPES)}",
            )
        query = query.filter(ItemHistory.transaction_type == transaction_type)

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
    org_ids = [str(m[0]) for m in org_memberships]
    org_owned = Location.owner_type == "organization"
    if org_ids:
        org_owned = org_owned & Location.owner_id.in_(org_ids)
    else:
        from sqlalchemy import literal

        org_owned = literal(False)

    # Ship-owned locations (similar to list_inventory)
    ship_locations = Location.owner_type == "ship"
    # Get accessible ship cargo location IDs
    user_ships_query = db.query(Ship.cargo_location_id).filter(
        Ship.owner_type == "user", Ship.owner_id == current_user.id
    )
    user_ship_ids = [str(row[0]) for row in user_ships_query.all() if row[0]]

    org_ship_ids = []
    if org_ids:
        org_ships_query = db.query(Ship.cargo_location_id).filter(
            Ship.owner_type == "organization", Ship.owner_id.in_(org_ids)
        )
        org_ship_ids = [str(row[0]) for row in org_ships_query.all() if row[0]]

    accessible_ship_ids = user_ship_ids + org_ship_ids

    if accessible_ship_ids:
        ship_owned = ship_locations & Location.id.in_(accessible_ship_ids)
    else:
        from sqlalchemy import literal

        ship_owned = literal(False)  # type: ignore[assignment]

    # Combine filters
    query = query.filter(or_(canonical_locations, user_owned, org_owned, ship_owned))

    # Get total count
    total = query.count()

    # Apply pagination and order by timestamp (newest first)
    results = query.order_by(ItemHistory.timestamp.desc()).offset(skip).limit(limit).all()

    # Filter in-memory and build response
    history_items = []
    for history, item, location, performer in results:
        if check_location_access_for_inventory(location, current_user, db, "viewer"):
            history_items.append(
                InventoryHistory(
                    id=history.id,
                    item_id=history.item_id,
                    item_name=item.name,
                    location_id=history.location_id,
                    location_name=location.name,
                    quantity_change=history.quantity_change,
                    transaction_type=history.transaction_type,
                    performed_by_username=performer.username,
                    timestamp=history.timestamp,
                    notes=history.notes,
                )
            )

    return {
        "history": history_items,
        "total": len(history_items),
        "skip": skip,
        "limit": limit,
        "pages": ceil(len(history_items) / limit) if limit > 0 else 0,
    }
