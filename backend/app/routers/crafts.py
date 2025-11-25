"""
Crafts router for managing crafting operations.

This router provides endpoints for:
- Creating crafts from blueprints
- Tracking craft status and progress
- Managing ingredient reservations
- Completing crafts and producing output items
"""

from typing import Optional, Any
from math import ceil
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc

from app.database import get_db
from app.models.craft import (
    Craft,
    CRAFT_STATUS_PLANNED,
    CRAFT_STATUS_IN_PROGRESS,
    CRAFT_STATUS_COMPLETED,
    CRAFT_STATUS_CANCELLED,
)
from app.models.craft_ingredient import (
    CraftIngredient,
    INGREDIENT_STATUS_PENDING,
    INGREDIENT_STATUS_RESERVED,
    INGREDIENT_STATUS_FULFILLED,
    SOURCE_TYPE_STOCK,
)
from app.models.blueprint import Blueprint
from app.models.item import Item
from app.models.location import Location
from app.models.item_stock import ItemStock
from app.models.item_history import ItemHistory
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.craft import (
    CraftCreate,
    CraftUpdate,
    CraftResponse,
    CraftProgressResponse,
    CraftIngredientResponse,
)
from app.routers.inventory import (
    get_or_create_item_stock,
    log_item_history,
    check_location_access_for_inventory,
)
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/crafts", tags=["crafts"])


def validate_blueprint_exists(db: Session, blueprint_id: str) -> Blueprint:
    """Validate that a blueprint exists, raise 404 if not."""
    blueprint = db.query(Blueprint).filter(Blueprint.id == blueprint_id).first()
    if not blueprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint with id '{blueprint_id}' not found",
        )
    return blueprint


def validate_location_exists(db: Session, location_id: str) -> Location:
    """Validate that a location exists, raise 404 if not."""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id '{location_id}' not found",
        )
    return location


def validate_craft_access(craft: Craft, current_user: User, db: Session) -> None:
    """
    Validate that the current user has access to the craft.

    User can access craft if:
    - They requested it (requested_by == current_user.id)
    - They are a member of the organization (if organization_id is set)
    """
    if craft.requested_by == current_user.id:
        return

    # If craft belongs to organization, check membership
    if craft.organization_id:
        from app.models.organization_member import OrganizationMember

        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == craft.organization_id,
                OrganizationMember.user_id == current_user.id,
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this craft",
            )
    else:
        # Craft doesn't belong to organization and user didn't request it
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this craft",
        )


def reserve_ingredient_stock(
    db: Session,
    ingredient: CraftIngredient,
    current_user: User,
) -> None:
    """
    Reserve stock for a craft ingredient if source_type is 'stock' and source_location is set.

    Args:
        db: Database session
        ingredient: CraftIngredient to reserve stock for
        current_user: User performing the reservation
    """
    if ingredient.source_type != SOURCE_TYPE_STOCK or not ingredient.source_location_id:
        # Only reserve for stock sources with a location
        return

    # Get or create stock
    stock = get_or_create_item_stock(
        db, ingredient.item_id, ingredient.source_location_id, current_user.id
    )

    # Check available quantity
    available = stock.quantity - stock.reserved_quantity
    if ingredient.required_quantity > available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Insufficient stock for ingredient {ingredient.item_id}. "
                f"Required: {ingredient.required_quantity}, Available: {available}"
            ),
        )

    # Reserve quantity
    stock.reserved_quantity += ingredient.required_quantity
    stock.updated_by = current_user.id

    # Mark ingredient as reserved
    ingredient.status = INGREDIENT_STATUS_RESERVED


def unreserve_ingredient_stock(
    db: Session,
    ingredient: CraftIngredient,
    current_user: User,
) -> None:
    """
    Unreserve stock for a craft ingredient.

    Args:
        db: Database session
        ingredient: CraftIngredient to unreserve stock for
        current_user: User performing the unreservation
    """
    if (
        ingredient.source_type != SOURCE_TYPE_STOCK
        or not ingredient.source_location_id
        or ingredient.status != INGREDIENT_STATUS_RESERVED
    ):
        # Only unreserve if it was actually reserved
        return

    # Get stock
    stock = (
        db.query(ItemStock)
        .filter(
            ItemStock.item_id == ingredient.item_id,
            ItemStock.location_id == ingredient.source_location_id,
        )
        .first()
    )

    if stock and stock.reserved_quantity >= ingredient.required_quantity:
        # Unreserve quantity
        stock.reserved_quantity -= ingredient.required_quantity
        stock.updated_by = current_user.id

    # Mark ingredient as pending
    ingredient.status = INGREDIENT_STATUS_PENDING


@router.get("", response_model=dict)
async def list_crafts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    organization_id: Optional[str] = Query(None, description="Filter by organization UUID"),
    blueprint_id: Optional[str] = Query(None, description="Filter by blueprint UUID"),
    sort_by: Optional[str] = Query("priority", description="Sort field (priority, created_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List crafts with optional filtering and pagination.

    Access Control:
    - Users can only see crafts they requested or crafts in organizations they belong to
    """
    query = db.query(Craft)

    # Apply access control: only crafts user requested or organization crafts they're in
    from app.models.organization_member import OrganizationMember

    user_org_ids = [
        str(m.organization_id)
        for m in db.query(OrganizationMember)
        .filter(OrganizationMember.user_id == current_user.id)
        .all()
    ]

    # Build access control filter
    if user_org_ids:
        query = query.filter(
            or_(
                Craft.requested_by == current_user.id,
                Craft.organization_id.in_(user_org_ids),
            )
        )
    else:
        query = query.filter(Craft.requested_by == current_user.id)

    # Apply filters
    if status_filter:
        query = query.filter(Craft.status == status_filter)
    if organization_id:
        query = query.filter(Craft.organization_id == organization_id)
    if blueprint_id:
        query = query.filter(Craft.blueprint_id == blueprint_id)

    # Apply sorting
    if sort_by:
        sort_column = getattr(Craft, sort_by, None)
        if sort_column is None:
            sort_column = Craft.priority
    else:
        sort_column = Craft.priority

    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    try:
        # Get total count
        total = query.count()

        # Apply pagination
        crafts = query.offset(skip).limit(limit).all()

        # Build response - manually construct dicts to avoid relationship validation issues
        craft_responses = []
        for craft in crafts:
            craft_dict = {
                "id": str(craft.id),
                "blueprint_id": craft.blueprint_id,
                "organization_id": craft.organization_id,
                "requested_by": craft.requested_by,
                "status": craft.status,
                "priority": craft.priority,
                "scheduled_start": craft.scheduled_start,
                "started_at": craft.started_at,
                "completed_at": craft.completed_at,
                "output_location_id": craft.output_location_id,
                "metadata": craft.craft_metadata if craft.craft_metadata is not None else {},
                "blueprint": None,
                "organization": None,
                "requester": None,
                "output_location": None,
                "ingredients": None,
            }
            craft_responses.append(craft_dict)

        return {
            "crafts": craft_responses,
            "total": total,
            "skip": skip,
            "limit": limit,
            "pages": ceil(total / limit) if limit > 0 else 0,
        }
    except Exception as e:
        # Log error and return empty result instead of crashing
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error listing crafts: {str(e)}", exc_info=True)
        return {
            "crafts": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "pages": 0,
        }


@router.post("", response_model=CraftResponse, status_code=status.HTTP_201_CREATED)
async def create_craft(
    craft_data: CraftCreate,
    reserve_ingredients: bool = Query(
        False, description="Automatically reserve ingredients on creation"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new craft from a blueprint.

    This will:
    1. Validate blueprint exists
    2. Validate output location exists and user has access
    3. Create craft with status 'planned'
    4. Create craft_ingredients from blueprint ingredients
    5. Optionally reserve stock for ingredients if reserve_ingredients=True

    Ingredient reservation:
    - Only ingredients with source_type='stock' and source_location_id set will be reserved
    - If reservation fails for any ingredient, the entire craft creation fails
    """
    # Validate blueprint exists
    blueprint = validate_blueprint_exists(db, craft_data.blueprint_id)

    # Validate output location exists and check access
    output_location = validate_location_exists(db, craft_data.output_location_id)
    if not check_location_access_for_inventory(output_location, current_user, db, "member"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to output location",
        )

    # Validate organization if provided
    if craft_data.organization_id:
        from app.models.organization import Organization
        from app.models.organization_member import OrganizationMember

        org = db.query(Organization).filter(Organization.id == craft_data.organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with id '{craft_data.organization_id}' not found",
            )
        # Check user is member of organization
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == craft_data.organization_id,
                OrganizationMember.user_id == current_user.id,
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this organization",
            )

    # Create craft
    new_craft = Craft(
        blueprint_id=craft_data.blueprint_id,
        organization_id=craft_data.organization_id,
        requested_by=current_user.id,
        status=CRAFT_STATUS_PLANNED,
        priority=craft_data.priority,
        scheduled_start=craft_data.scheduled_start,
        output_location_id=craft_data.output_location_id,
        craft_metadata=craft_data.metadata,
    )
    db.add(new_craft)
    db.flush()  # Flush to get the craft ID

    # Create craft ingredients from blueprint
    blueprint_ingredients = blueprint.blueprint_data.get("ingredients", [])
    craft_ingredients = []

    for bp_ingredient in blueprint_ingredients:
        # Determine source location - use provided source_location_id or default to output_location
        source_location_id = craft_data.output_location_id  # Default to output location
        source_type = SOURCE_TYPE_STOCK  # Default to stock

        # Create craft ingredient
        craft_ingredient = CraftIngredient(
            craft_id=new_craft.id,
            item_id=bp_ingredient["item_id"],
            required_quantity=Decimal(str(bp_ingredient["quantity"])),
            source_location_id=source_location_id,
            source_type=source_type,
            status=INGREDIENT_STATUS_PENDING,
        )
        db.add(craft_ingredient)
        craft_ingredients.append(craft_ingredient)

    # If reserve_ingredients is True, reserve stock for all stock-type ingredients
    if reserve_ingredients:
        for ingredient in craft_ingredients:
            try:
                reserve_ingredient_stock(db, ingredient, current_user)
            except HTTPException:
                # Rollback on reservation failure
                db.rollback()
                raise

    db.commit()
    db.refresh(new_craft)

    # Log blueprint usage event (if user has consented)
    from app.utils.analytics import log_event

    # Note: IP and user agent are logged by middleware; this provides blueprint_id context
    try:
        log_event(
            db=db,
            user_id=current_user.id,
            event_type="blueprint_used",
            entity_type="blueprint",
            entity_id=blueprint.id,
            event_data={"craft_id": new_craft.id},
        )
        db.commit()  # Commit the event
    except Exception:
        pass  # Don't fail craft creation if logging fails

    # Build response
    response_dict = {
        "id": str(new_craft.id),
        "blueprint_id": new_craft.blueprint_id,
        "organization_id": new_craft.organization_id,
        "requested_by": new_craft.requested_by,
        "status": new_craft.status,
        "priority": new_craft.priority,
        "scheduled_start": new_craft.scheduled_start,
        "started_at": new_craft.started_at,
        "completed_at": new_craft.completed_at,
        "output_location_id": new_craft.output_location_id,
        "metadata": new_craft.craft_metadata if new_craft.craft_metadata is not None else {},
        "blueprint": None,
        "organization": None,
        "requester": None,
        "output_location": None,
        "ingredients": None,
    }
    return CraftResponse.model_validate(response_dict)


@router.get("/{craft_id}", response_model=CraftResponse)
async def get_craft(
    craft_id: str,
    include_ingredients: bool = Query(True, description="Include ingredients in response"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get craft details by ID."""
    craft = (
        db.query(Craft).options(joinedload(Craft.ingredients)).filter(Craft.id == craft_id).first()
    )

    if not craft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Craft with id '{craft_id}' not found",
        )

    # Check access
    validate_craft_access(craft, current_user, db)

    # Build ingredients if requested
    ingredients = None
    if include_ingredients:
        ingredients = []
        for ingredient in craft.ingredients:
            ing_dict = {
                "id": str(ingredient.id),
                "craft_id": ingredient.craft_id,
                "item_id": ingredient.item_id,
                "required_quantity": float(ingredient.required_quantity),
                "source_location_id": ingredient.source_location_id,
                "source_type": ingredient.source_type,
                "status": ingredient.status,
                "item": None,
                "source_location": None,
            }
            ingredients.append(CraftIngredientResponse.model_validate(ing_dict))

    # Build response
    response_dict = {
        "id": str(craft.id),
        "blueprint_id": craft.blueprint_id,
        "organization_id": craft.organization_id,
        "requested_by": craft.requested_by,
        "status": craft.status,
        "priority": craft.priority,
        "scheduled_start": craft.scheduled_start,
        "started_at": craft.started_at,
        "completed_at": craft.completed_at,
        "output_location_id": craft.output_location_id,
        "metadata": craft.craft_metadata if craft.craft_metadata is not None else {},
        "blueprint": None,
        "organization": None,
        "requester": None,
        "output_location": None,
        "ingredients": ingredients,
    }
    return CraftResponse.model_validate(response_dict)


@router.patch("/{craft_id}", response_model=CraftResponse)
async def update_craft(
    craft_id: str,
    craft_data: CraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a craft by ID. Only allowed for planned crafts."""
    craft = db.query(Craft).filter(Craft.id == craft_id).first()

    if not craft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Craft with id '{craft_id}' not found",
        )

    # Check access
    validate_craft_access(craft, current_user, db)

    # Only allow updates for planned crafts
    if craft.status != CRAFT_STATUS_PLANNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update craft with status '{craft.status}'. Only 'planned' crafts can be updated.",
        )

    # Validate output location if being updated
    if craft_data.output_location_id:
        output_location = validate_location_exists(db, craft_data.output_location_id)
        if not check_location_access_for_inventory(output_location, current_user, db, "member"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to output location",
            )

    # Update fields
    update_dict = craft_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        # Map metadata to craft_metadata for model
        if field == "metadata":
            setattr(craft, "craft_metadata", value)
        else:
            setattr(craft, field, value)

    db.commit()
    db.refresh(craft)

    # Build response
    response_dict = {
        "id": str(craft.id),
        "blueprint_id": craft.blueprint_id,
        "organization_id": craft.organization_id,
        "requested_by": craft.requested_by,
        "status": craft.status,
        "priority": craft.priority,
        "scheduled_start": craft.scheduled_start,
        "started_at": craft.started_at,
        "completed_at": craft.completed_at,
        "output_location_id": craft.output_location_id,
        "metadata": craft.craft_metadata if craft.craft_metadata is not None else {},
        "blueprint": None,
        "organization": None,
        "requester": None,
        "output_location": None,
        "ingredients": None,
    }
    return CraftResponse.model_validate(response_dict)


@router.delete("/{craft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_craft(
    craft_id: str,
    unreserve_ingredients: bool = Query(True, description="Unreserve ingredients when deleting"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a craft by ID.

    Only allowed for planned or cancelled crafts.
    If unreserve_ingredients=True, will unreserve any reserved stock.
    """
    craft = (
        db.query(Craft).options(joinedload(Craft.ingredients)).filter(Craft.id == craft_id).first()
    )

    if not craft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Craft with id '{craft_id}' not found",
        )

    # Check access
    validate_craft_access(craft, current_user, db)

    # Only allow deletion for planned or cancelled crafts
    if craft.status not in [CRAFT_STATUS_PLANNED, CRAFT_STATUS_CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete craft with status '{craft.status}'. Only 'planned' or 'cancelled' crafts can be deleted.",
        )

    # Unreserve ingredients if requested
    if unreserve_ingredients:
        for ingredient in craft.ingredients:
            unreserve_ingredient_stock(db, ingredient, current_user)

    db.delete(craft)
    db.commit()

    return None


@router.post("/{craft_id}/start", response_model=CraftResponse)
async def start_craft(
    craft_id: str,
    reserve_missing_ingredients: bool = Query(False, description="Reserve any pending ingredients"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Start a craft (change status to 'in_progress').

    This will:
    1. Validate craft is in 'planned' status
    2. Optionally reserve any pending ingredients
    3. Mark all ingredients as 'fulfilled' if source_type is not 'stock'
    4. Set started_at timestamp
    5. Update craft status to 'in_progress'
    """
    craft = (
        db.query(Craft).options(joinedload(Craft.ingredients)).filter(Craft.id == craft_id).first()
    )

    if not craft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Craft with id '{craft_id}' not found",
        )

    # Check access
    validate_craft_access(craft, current_user, db)

    # Only allow starting planned crafts
    if craft.status != CRAFT_STATUS_PLANNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start craft with status '{craft.status}'. Only 'planned' crafts can be started.",
        )

    # Reserve missing ingredients if requested
    if reserve_missing_ingredients:
        for ingredient in craft.ingredients:
            if ingredient.status == INGREDIENT_STATUS_PENDING:
                try:
                    reserve_ingredient_stock(db, ingredient, current_user)
                except HTTPException:
                    db.rollback()
                    raise

    # Mark non-stock ingredients as fulfilled (they don't need reservation)
    for ingredient in craft.ingredients:
        if (
            ingredient.source_type != SOURCE_TYPE_STOCK
            and ingredient.status == INGREDIENT_STATUS_PENDING
        ):
            ingredient.status = INGREDIENT_STATUS_FULFILLED

    # Update craft
    craft.status = CRAFT_STATUS_IN_PROGRESS
    craft.started_at = datetime.now(timezone.utc)

    # Increment blueprint usage count
    blueprint = db.query(Blueprint).filter(Blueprint.id == craft.blueprint_id).first()
    if blueprint:
        blueprint.usage_count += 1

    db.commit()
    db.refresh(craft)

    # Build response
    response_dict = {
        "id": str(craft.id),
        "blueprint_id": craft.blueprint_id,
        "organization_id": craft.organization_id,
        "requested_by": craft.requested_by,
        "status": craft.status,
        "priority": craft.priority,
        "scheduled_start": craft.scheduled_start,
        "started_at": craft.started_at,
        "completed_at": craft.completed_at,
        "output_location_id": craft.output_location_id,
        "metadata": craft.craft_metadata if craft.craft_metadata is not None else {},
        "blueprint": None,
        "organization": None,
        "requester": None,
        "output_location": None,
        "ingredients": None,
    }
    return CraftResponse.model_validate(response_dict)


@router.post("/{craft_id}/complete", response_model=CraftResponse)
async def complete_craft(
    craft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Complete a craft (change status to 'completed').

    This will:
    1. Validate craft is in 'in_progress' status
    2. Deduct reserved quantities from stock for all reserved ingredients
    3. Add output items to output location
    4. Set completed_at timestamp
    5. Update craft status to 'completed'
    """
    craft = (
        db.query(Craft).options(joinedload(Craft.ingredients)).filter(Craft.id == craft_id).first()
    )

    if not craft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Craft with id '{craft_id}' not found",
        )

    # Check access
    validate_craft_access(craft, current_user, db)

    # Only allow completing in_progress crafts
    if craft.status != CRAFT_STATUS_IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete craft with status '{craft.status}'. Only 'in_progress' crafts can be completed.",
        )

    # Get blueprint
    blueprint = db.query(Blueprint).filter(Blueprint.id == craft.blueprint_id).first()
    if not blueprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint with id '{craft.blueprint_id}' not found",
        )

    # Deduct reserved stock for all reserved ingredients
    for ingredient in craft.ingredients:
        if (
            ingredient.status == INGREDIENT_STATUS_RESERVED
            and ingredient.source_type == SOURCE_TYPE_STOCK
        ):
            # Get stock
            stock = (
                db.query(ItemStock)
                .filter(
                    ItemStock.item_id == ingredient.item_id,
                    ItemStock.location_id == ingredient.source_location_id,
                )
                .first()
            )

            if stock:
                # Validate we have enough reserved
                if stock.reserved_quantity < ingredient.required_quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Insufficient reserved quantity for ingredient {ingredient.item_id}. "
                            f"Required: {ingredient.required_quantity}, Reserved: {stock.reserved_quantity}"
                        ),
                    )

                # Deduct from quantity and reserved_quantity
                stock.quantity -= ingredient.required_quantity
                stock.reserved_quantity -= ingredient.required_quantity
                stock.updated_by = current_user.id

                # Log history (source_location_id should always be set for stock ingredients)
                if ingredient.source_location_id:
                    log_item_history(
                        db=db,
                        item_id=ingredient.item_id,
                        location_id=ingredient.source_location_id,
                        quantity_change=-ingredient.required_quantity,
                        transaction_type="consume",
                        performed_by=current_user.id,
                        notes=f"Consumed for craft {craft.id}",
                        related_craft_id=craft.id,
                    )

            # Mark ingredient as fulfilled
            ingredient.status = INGREDIENT_STATUS_FULFILLED

    # Add output items to output location
    output_stock = get_or_create_item_stock(
        db, blueprint.output_item_id, craft.output_location_id, current_user.id
    )
    output_stock.quantity += blueprint.output_quantity
    output_stock.updated_by = current_user.id

    # Log history for output
    log_item_history(
        db=db,
        item_id=blueprint.output_item_id,
        location_id=craft.output_location_id,
        quantity_change=blueprint.output_quantity,
        transaction_type="craft",
        performed_by=current_user.id,
        notes=f"Crafted from blueprint {blueprint.id}",
        related_craft_id=craft.id,
    )

    # Update craft
    craft.status = CRAFT_STATUS_COMPLETED
    craft.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(craft)

    # Build response
    response_dict = {
        "id": str(craft.id),
        "blueprint_id": craft.blueprint_id,
        "organization_id": craft.organization_id,
        "requested_by": craft.requested_by,
        "status": craft.status,
        "priority": craft.priority,
        "scheduled_start": craft.scheduled_start,
        "started_at": craft.started_at,
        "completed_at": craft.completed_at,
        "output_location_id": craft.output_location_id,
        "metadata": craft.craft_metadata if craft.craft_metadata is not None else {},
        "blueprint": None,
        "organization": None,
        "requester": None,
        "output_location": None,
        "ingredients": None,
    }
    return CraftResponse.model_validate(response_dict)


@router.get("/{craft_id}/progress", response_model=CraftProgressResponse)
async def get_craft_progress(
    craft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get craft progress information including timing and ingredient status."""
    craft = (
        db.query(Craft).options(joinedload(Craft.ingredients)).filter(Craft.id == craft_id).first()
    )

    if not craft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Craft with id '{craft_id}' not found",
        )

    # Check access
    validate_craft_access(craft, current_user, db)

    # Get blueprint
    blueprint = db.query(Blueprint).filter(Blueprint.id == craft.blueprint_id).first()
    if not blueprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint with id '{craft.blueprint_id}' not found",
        )

    # Calculate elapsed time and estimated completion
    elapsed_minutes = None
    estimated_completion_minutes = None

    if craft.started_at and craft.status == CRAFT_STATUS_IN_PROGRESS:
        # Ensure craft.started_at is timezone-aware (SQLite may return naive datetimes)
        started_at = craft.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        elapsed = datetime.now(timezone.utc) - started_at
        elapsed_minutes = int(elapsed.total_seconds() / 60)
        estimated_completion_minutes = max(0, blueprint.crafting_time_minutes - elapsed_minutes)

    # Calculate ingredient status summary
    ingredients_status = {
        "total": len(craft.ingredients),
        "pending": sum(1 for ing in craft.ingredients if ing.status == INGREDIENT_STATUS_PENDING),
        "reserved": sum(1 for ing in craft.ingredients if ing.status == INGREDIENT_STATUS_RESERVED),
        "fulfilled": sum(
            1 for ing in craft.ingredients if ing.status == INGREDIENT_STATUS_FULFILLED
        ),
    }

    return CraftProgressResponse(
        craft_id=str(craft.id),
        status=craft.status,
        started_at=craft.started_at,
        completed_at=craft.completed_at,
        scheduled_start=craft.scheduled_start,
        elapsed_minutes=elapsed_minutes,
        estimated_completion_minutes=estimated_completion_minutes,
        ingredients_status=ingredients_status,
        blueprint_crafting_time_minutes=blueprint.crafting_time_minutes,
    )
