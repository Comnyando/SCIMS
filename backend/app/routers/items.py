"""
Items router for item catalog management.

This router provides endpoints for managing the item catalog (master data):
- List items with search and pagination
- Create new items
- Get item details
- Update items
- Delete items
"""

from typing import Optional
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.item import Item
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.config import settings


router = APIRouter(prefix=f"{settings.api_v1_prefix}/items", tags=["items"])


@router.get("", response_model=dict)
async def list_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    rarity: Optional[str] = Query(None, description="Filter by rarity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List items with optional search and filtering.

    Supports pagination, search by name/description, and filtering by
    category, subcategory, and rarity.
    """
    query = db.query(Item)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Item.name.ilike(search_pattern),
                Item.description.ilike(search_pattern),
            )
        )

    # Apply filters
    if category:
        query = query.filter(Item.category == category)
    if subcategory:
        query = query.filter(Item.subcategory == subcategory)
    if rarity:
        query = query.filter(Item.rarity == rarity)

    try:
        # Get total count for pagination
        total = query.count()

        # Apply pagination and order by name
        items = query.order_by(Item.name).offset(skip).limit(limit).all()

        return {
            "items": [ItemResponse.model_validate(item) for item in items],
            "total": total,
            "skip": skip,
            "limit": limit,
            "pages": ceil(total / limit) if limit > 0 else 0,
        }
    except Exception as e:
        # Log error and return empty result instead of crashing
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error listing items: {str(e)}", exc_info=True)
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "pages": 0,
        }


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new item in the catalog.

    Items are global master data entries that can be used across all
    organizations and users.
    """
    # Check if item with same name already exists (optional uniqueness check)
    existing_item = db.query(Item).filter(Item.name == item_data.name).first()
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item with name '{item_data.name}' already exists",
        )

    new_item = Item(
        name=item_data.name,
        description=item_data.description,
        category=item_data.category,
        subcategory=item_data.subcategory,
        rarity=item_data.rarity,
        meta=item_data.metadata,
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return ItemResponse.model_validate(new_item)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get item details by ID.
    """
    item = db.query(Item).filter(Item.id == item_id).first()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id '{item_id}' not found",
        )

    return ItemResponse.model_validate(item)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    item_data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an item by ID.

    Only provided fields will be updated (partial update).
    """
    item = db.query(Item).filter(Item.id == item_id).first()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id '{item_id}' not found",
        )

    # Check name uniqueness if name is being updated
    if item_data.name and item_data.name != item.name:
        existing_item = db.query(Item).filter(Item.name == item_data.name).first()
        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item with name '{item_data.name}' already exists",
            )

    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["meta"] = update_data.pop("metadata")

    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    return ItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete an item by ID.

    This will cascade delete all related stock records and history entries.
    Use with caution.
    """
    item = db.query(Item).filter(Item.id == item_id).first()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id '{item_id}' not found",
        )

    db.delete(item)
    db.commit()

    return None
