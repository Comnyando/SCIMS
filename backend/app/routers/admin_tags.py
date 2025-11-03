"""
Admin Tags router for managing tags.
"""

from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.tag import Tag
from app.models.commons_entity_tag import CommonsEntityTag
from app.models.user import User
from app.core.dependencies import get_current_active_user
from app.core.commons_dependencies import require_moderator
from app.schemas.commons import TagCreate, TagResponse, TagsListResponse
from app.config import settings

router = APIRouter(
    prefix=f"{settings.api_v1_prefix}/admin/commons/tags", tags=["admin", "commons", "tags"]
)


@router.get("", response_model=TagsListResponse)
async def list_tags(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    moderator: User = Depends(require_moderator),
):
    """List all tags (admin only)."""
    query = db.query(Tag)
    total = query.count()
    tags = query.order_by(Tag.name).offset(skip).limit(limit).all()

    tag_responses = [
        {
            "id": str(tag.id),
            "name": tag.name,
            "description": tag.description,
            "created_at": tag.created_at,
        }
        for tag in tags
    ]

    return {"tags": tag_responses, "total": total}


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    moderator: User = Depends(require_moderator),
):
    """Create a new tag (admin only)."""
    # Check if tag with same name already exists
    existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag_data.name}' already exists",
        )

    tag = Tag(
        name=tag_data.name,
        description=tag_data.description,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return {
        "id": str(tag.id),
        "name": tag.name,
        "description": tag.description,
        "created_at": tag.created_at,
    }


@router.patch("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    moderator: User = Depends(require_moderator),
):
    """Update a tag (admin only)."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    # Check if name change would conflict with existing tag
    if tag_data.name != tag.name:
        existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name '{tag_data.name}' already exists",
            )

    tag.name = tag_data.name
    tag.description = tag_data.description
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return {
        "id": str(tag.id),
        "name": tag.name,
        "description": tag.description,
        "created_at": tag.created_at,
    }


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: str,
    db: Session = Depends(get_db),
    moderator: User = Depends(require_moderator),
):
    """Delete a tag (admin only)."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    # Check if tag is in use
    usage_count = db.query(CommonsEntityTag).filter(CommonsEntityTag.tag_id == tag_id).count()

    if usage_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete tag '{tag.name}' - it is in use by {usage_count} entities. Remove tag associations first.",
        )

    db.delete(tag)
    db.commit()

    return None
