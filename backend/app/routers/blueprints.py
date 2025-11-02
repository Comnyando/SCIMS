"""
Blueprints router for crafting blueprint management.

This router provides endpoints for managing crafting blueprints:
- List blueprints with search and pagination
- Create new blueprints
- Get blueprint details
- Update blueprints
- Delete blueprints
- Get popular blueprints
- Get blueprints by output item
"""

from typing import Optional, Any
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc

from app.database import get_db
from app.models.blueprint import Blueprint
from app.models.item import Item
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.blueprint import (
    BlueprintCreate,
    BlueprintUpdate,
    BlueprintResponse,
)
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/blueprints", tags=["blueprints"])


def validate_item_exists(db: Session, item_id: str, field_name: str = "item") -> None:
    """Validate that an item exists, raise 404 if not."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{field_name.capitalize()} with id '{item_id}' not found",
        )


def validate_blueprint_access(
    blueprint: Blueprint, current_user: User, require_owner: bool = False
) -> None:
    """
    Validate that the current user has access to the blueprint.

    Args:
        blueprint: The blueprint to check access for
        current_user: The current authenticated user
        require_owner: If True, require that the user is the creator
    """
    # Public blueprints are visible to all authenticated users
    if blueprint.is_public and not require_owner:
        return

    # Private blueprints are only visible to creator
    if blueprint.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this blueprint",
        )


def validate_blueprint_ingredients(db: Session, blueprint_data: dict) -> None:
    """
    Validate that all ingredient item IDs exist.

    Args:
        db: Database session
        blueprint_data: Blueprint data dictionary containing ingredients array

    Raises:
        HTTPException: If any ingredient item_id doesn't exist
    """
    if "ingredients" not in blueprint_data:
        return

    ingredients = blueprint_data["ingredients"]
    if not isinstance(ingredients, list):
        return

    # Check each ingredient item_id exists
    for idx, ingredient in enumerate(ingredients):
        if not isinstance(ingredient, dict):
            continue
        if "item_id" not in ingredient:
            continue

        item_id = ingredient["item_id"]
        try:
            validate_item_exists(db, item_id, f"ingredient at index {idx}")
        except HTTPException:
            # Re-raise with more specific message
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredient at index {idx} with item_id '{item_id}' not found",
            )


@router.get("", response_model=dict)
async def list_blueprints(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    output_item_id: Optional[str] = Query(None, description="Filter by output item"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    created_by: Optional[str] = Query(None, description="Filter by creator user ID"),
    sort_by: Optional[str] = Query("name", description="Sort field: name, usage_count, created_at"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc, desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List blueprints with optional search and filtering.

    Supports pagination, search by name/description, and filtering by
    category, output item, public/private status, and creator.

    Access Control:
    - Public blueprints: visible to all authenticated users
    - Private blueprints: only visible to creator
    """
    query = db.query(Blueprint)

    # Apply access control: only public blueprints or user's own blueprints
    query = query.filter(
        or_(
            Blueprint.is_public == True,  # Public blueprints
            Blueprint.created_by == current_user.id,  # User's own blueprints
        )
    )

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Blueprint.name.ilike(search_pattern),
                Blueprint.description.ilike(search_pattern),
            )
        )

    # Apply filters
    if category:
        query = query.filter(Blueprint.category == category)
    if output_item_id:
        query = query.filter(Blueprint.output_item_id == output_item_id)
    if is_public is not None:
        query = query.filter(Blueprint.is_public == is_public)
    if created_by:
        query = query.filter(Blueprint.created_by == created_by)

    # Apply sorting
    sort_column: Any
    if sort_by == "name":
        sort_column = Blueprint.name
    elif sort_by == "usage_count":
        sort_column = Blueprint.usage_count
    elif sort_by == "created_at":
        sort_column = Blueprint.created_at
    else:
        sort_column = Blueprint.name

    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    # Get total count for pagination
    total = query.count()

    # Apply pagination
    blueprints = query.offset(skip).limit(limit).all()

    # Build response - manually construct dicts to avoid relationship validation issues
    blueprint_responses = []
    for blueprint in blueprints:
        bp_dict = {
            "id": str(blueprint.id),
            "name": blueprint.name,
            "description": blueprint.description,
            "category": blueprint.category,
            "crafting_time_minutes": blueprint.crafting_time_minutes,
            "output_item_id": blueprint.output_item_id,
            "output_quantity": float(blueprint.output_quantity),
            "blueprint_data": blueprint.blueprint_data,
            "created_by": blueprint.created_by,
            "is_public": blueprint.is_public,
            "usage_count": blueprint.usage_count,
            "created_at": blueprint.created_at,
            "output_item": None,
            "creator": None,
        }
        blueprint_responses.append(bp_dict)

    return {
        "blueprints": blueprint_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }


@router.post("", response_model=BlueprintResponse, status_code=status.HTTP_201_CREATED)
async def create_blueprint(
    blueprint_data: BlueprintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new blueprint.

    Requires authentication. The blueprint will be owned by the current user.
    Validates that output_item_id and all ingredient item_ids exist.
    """
    # Validate output item exists
    validate_item_exists(db, blueprint_data.output_item_id, "output_item")

    # Validate all ingredient items exist
    validate_blueprint_ingredients(db, blueprint_data.blueprint_data)

    new_blueprint = Blueprint(
        name=blueprint_data.name,
        description=blueprint_data.description,
        category=blueprint_data.category,
        crafting_time_minutes=blueprint_data.crafting_time_minutes,
        output_item_id=blueprint_data.output_item_id,
        output_quantity=blueprint_data.output_quantity,
        blueprint_data=blueprint_data.blueprint_data,
        created_by=current_user.id,
        is_public=blueprint_data.is_public,
        usage_count=0,
    )

    db.add(new_blueprint)
    db.commit()
    db.refresh(new_blueprint)

    # Manually construct response to avoid relationship validation
    response_dict = {
        "id": str(new_blueprint.id),
        "name": new_blueprint.name,
        "description": new_blueprint.description,
        "category": new_blueprint.category,
        "crafting_time_minutes": new_blueprint.crafting_time_minutes,
        "output_item_id": new_blueprint.output_item_id,
        "output_quantity": float(new_blueprint.output_quantity),
        "blueprint_data": new_blueprint.blueprint_data,
        "created_by": new_blueprint.created_by,
        "is_public": new_blueprint.is_public,
        "usage_count": new_blueprint.usage_count,
        "created_at": new_blueprint.created_at,
        "output_item": None,
        "creator": None,
    }
    return BlueprintResponse.model_validate(response_dict)


@router.get("/popular", response_model=dict)
async def get_popular_blueprints(
    limit: int = Query(10, ge=1, le=50, description="Number of blueprints to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get most popular blueprints (by usage_count).

    Returns public blueprints or user's own blueprints, sorted by usage_count descending.
    """
    query = db.query(Blueprint)

    # Apply access control: only public blueprints or user's own blueprints
    query = query.filter(
        or_(
            Blueprint.is_public == True,
            Blueprint.created_by == current_user.id,
        )
    )

    # Filter by category if provided
    if category:
        query = query.filter(Blueprint.category == category)

    # Sort by usage_count descending
    query = query.order_by(desc(Blueprint.usage_count))

    # Get top blueprints
    blueprints = query.limit(limit).all()

    # Build response - manually construct dicts to avoid relationship validation issues
    blueprint_responses = []
    for blueprint in blueprints:
        bp_dict = {
            "id": str(blueprint.id),
            "name": blueprint.name,
            "description": blueprint.description,
            "category": blueprint.category,
            "crafting_time_minutes": blueprint.crafting_time_minutes,
            "output_item_id": blueprint.output_item_id,
            "output_quantity": float(blueprint.output_quantity),
            "blueprint_data": blueprint.blueprint_data,
            "created_by": blueprint.created_by,
            "is_public": blueprint.is_public,
            "usage_count": blueprint.usage_count,
            "created_at": blueprint.created_at,
            "output_item": None,
            "creator": None,
        }
        blueprint_responses.append(bp_dict)

    return {
        "blueprints": blueprint_responses,
        "total": len(blueprint_responses),
    }


@router.get("/by-item/{item_id}", response_model=dict)
async def get_blueprints_by_item(
    item_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all blueprints that produce a specific item.

    Access Control:
    - Returns public blueprints + user's own blueprints
    """
    # Validate item exists
    validate_item_exists(db, item_id, "item")

    query = db.query(Blueprint).filter(Blueprint.output_item_id == item_id)

    # Apply access control
    query = query.filter(
        or_(
            Blueprint.is_public == True,
            Blueprint.created_by == current_user.id,
        )
    )

    # Filter by public/private if specified
    if is_public is not None:
        query = query.filter(Blueprint.is_public == is_public)

    # Sort by usage_count descending (most popular first)
    query = query.order_by(desc(Blueprint.usage_count))

    # Get total count
    total = query.count()

    # Apply pagination
    blueprints = query.offset(skip).limit(limit).all()

    # Build response - manually construct dicts to avoid relationship validation issues
    blueprint_responses = []
    for blueprint in blueprints:
        bp_dict = {
            "id": str(blueprint.id),
            "name": blueprint.name,
            "description": blueprint.description,
            "category": blueprint.category,
            "crafting_time_minutes": blueprint.crafting_time_minutes,
            "output_item_id": blueprint.output_item_id,
            "output_quantity": float(blueprint.output_quantity),
            "blueprint_data": blueprint.blueprint_data,
            "created_by": blueprint.created_by,
            "is_public": blueprint.is_public,
            "usage_count": blueprint.usage_count,
            "created_at": blueprint.created_at,
            "output_item": None,
            "creator": None,
        }
        blueprint_responses.append(bp_dict)

    return {
        "blueprints": blueprint_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }


@router.get("/{blueprint_id}", response_model=BlueprintResponse)
async def get_blueprint(
    blueprint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get blueprint details by ID.

    Access Control:
    - Public blueprints: visible to all authenticated users
    - Private blueprints: only visible to creator
    """
    blueprint = db.query(Blueprint).filter(Blueprint.id == blueprint_id).first()

    if blueprint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint with id '{blueprint_id}' not found",
        )

    # Check access
    validate_blueprint_access(blueprint, current_user)

    # Manually construct response to avoid relationship validation
    response_dict = {
        "id": str(blueprint.id),
        "name": blueprint.name,
        "description": blueprint.description,
        "category": blueprint.category,
        "crafting_time_minutes": blueprint.crafting_time_minutes,
        "output_item_id": blueprint.output_item_id,
        "output_quantity": float(blueprint.output_quantity),
        "blueprint_data": blueprint.blueprint_data,
        "created_by": blueprint.created_by,
        "is_public": blueprint.is_public,
        "usage_count": blueprint.usage_count,
        "created_at": blueprint.created_at,
        "output_item": None,
        "creator": None,
    }
    return BlueprintResponse.model_validate(response_dict)


@router.patch("/{blueprint_id}", response_model=BlueprintResponse)
async def update_blueprint(
    blueprint_id: str,
    blueprint_data: BlueprintUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a blueprint by ID.

    Only the creator can update their blueprint.
    Only provided fields will be updated (partial update).
    """
    blueprint = db.query(Blueprint).filter(Blueprint.id == blueprint_id).first()

    if blueprint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint with id '{blueprint_id}' not found",
        )

    # Check ownership
    validate_blueprint_access(blueprint, current_user, require_owner=True)

    # Validate output item if being updated
    if blueprint_data.output_item_id:
        validate_item_exists(db, blueprint_data.output_item_id, "output_item")

    # Validate ingredients if being updated
    if blueprint_data.blueprint_data:
        validate_blueprint_ingredients(db, blueprint_data.blueprint_data)

    # Update fields
    update_dict = blueprint_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(blueprint, field, value)

    db.commit()
    db.refresh(blueprint)

    # Manually construct response to avoid relationship validation
    response_dict = {
        "id": str(blueprint.id),
        "name": blueprint.name,
        "description": blueprint.description,
        "category": blueprint.category,
        "crafting_time_minutes": blueprint.crafting_time_minutes,
        "output_item_id": blueprint.output_item_id,
        "output_quantity": float(blueprint.output_quantity),
        "blueprint_data": blueprint.blueprint_data,
        "created_by": blueprint.created_by,
        "is_public": blueprint.is_public,
        "usage_count": blueprint.usage_count,
        "created_at": blueprint.created_at,
        "output_item": None,
        "creator": None,
    }
    return BlueprintResponse.model_validate(response_dict)


@router.delete("/{blueprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blueprint(
    blueprint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a blueprint by ID.

    Only the creator can delete their blueprint.

    Note: Future enhancement - consider soft delete or cascade handling
    for blueprints used in crafts (Phase 3.2).
    """
    blueprint = db.query(Blueprint).filter(Blueprint.id == blueprint_id).first()

    if blueprint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint with id '{blueprint_id}' not found",
        )

    # Check ownership
    validate_blueprint_access(blueprint, current_user, require_owner=True)

    db.delete(blueprint)
    db.commit()

    return None
