"""
Public Commons router for read-only public access to commons entities.
"""

from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, String

from app.database import get_db
from app.models.commons_entity import CommonsEntity
from app.models.commons_entity_tag import CommonsEntityTag
from app.models.tag import Tag
from app.schemas.commons import (
    CommonsEntityResponse,
    CommonsEntitiesListResponse,
    TagResponse,
    TagsListResponse,
)
from app.config import settings
from app.utils.commons_cache import (
    get_cached_public_data,
    set_cached_public_data,
    cache_key_public_items,
    cache_key_public_recipes,
    cache_key_public_locations,
    cache_key_public_entity,
    cache_key_tags,
)

router = APIRouter(prefix="/public", tags=["public", "commons"])


def build_entity_response(entity: CommonsEntity, db: Session) -> dict:
    """Build an entity response dictionary with tags."""
    # Fetch tags for this entity
    tag_relationships = (
        db.query(CommonsEntityTag)
        .join(Tag)
        .filter(CommonsEntityTag.commons_entity_id == entity.id)
        .all()
    )
    tag_names = [rel.tag.name for rel in tag_relationships]

    return {
        "id": str(entity.id),
        "entity_type": entity.entity_type,
        "canonical_id": entity.canonical_id,
        "data": entity.data,
        "version": entity.version,
        "is_public": entity.is_public,
        "created_by": entity.created_by,
        "created_at": entity.created_at,
        "tags": tag_names if tag_names else None,
    }


@router.get("/items", response_model=CommonsEntitiesListResponse)
async def list_public_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    db: Session = Depends(get_db),
):
    """
    List public items from the commons.

    No authentication required - this is a public read-only endpoint.
    Results are cached for 1 hour.
    """
    # Check cache first
    cache_key = cache_key_public_items(tag=tag, search=search, skip=skip, limit=limit)
    cached_data = get_cached_public_data(cache_key)
    if cached_data:
        return cached_data

    query = db.query(CommonsEntity).filter(
        and_(
            CommonsEntity.entity_type == "item",
            CommonsEntity.is_public == True,  # noqa: E712
        )
    )

    # Filter by tag if provided
    if tag:
        tag_obj = db.query(Tag).filter(Tag.name == tag).first()
        if tag_obj:
            query = query.join(CommonsEntityTag).filter(CommonsEntityTag.tag_id == tag_obj.id)
        else:
            # Tag doesn't exist, return empty result
            from sqlalchemy import false

            query = query.filter(false())

    # Search functionality (search in entity data JSONB)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                CommonsEntity.data["name"].astext.ilike(search_pattern),
                CommonsEntity.data["description"].astext.ilike(search_pattern),
            )
        )

    total = query.count()
    entities = query.order_by(desc(CommonsEntity.created_at)).offset(skip).limit(limit).all()

    entity_responses = [build_entity_response(entity, db) for entity in entities]

    result = {
        "entities": entity_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }

    # Cache the result (1 hour TTL)
    set_cached_public_data(cache_key, result, ttl_seconds=3600)

    return result


@router.get("/recipes", response_model=CommonsEntitiesListResponse)
async def list_public_recipes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    db: Session = Depends(get_db),
):
    """
    List public recipes (blueprints) from the commons.

    No authentication required - this is a public read-only endpoint.
    Results are cached for 1 hour.
    """
    # Check cache first
    cache_key = cache_key_public_recipes(tag=tag, search=search, skip=skip, limit=limit)
    cached_data = get_cached_public_data(cache_key)
    if cached_data:
        return cached_data

    query = db.query(CommonsEntity).filter(
        and_(
            CommonsEntity.entity_type == "blueprint",
            CommonsEntity.is_public == True,  # noqa: E712
        )
    )

    if tag:
        tag_obj = db.query(Tag).filter(Tag.name == tag).first()
        if tag_obj:
            query = query.join(CommonsEntityTag).filter(CommonsEntityTag.tag_id == tag_obj.id)
        else:
            from sqlalchemy import false

            query = query.filter(false())

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                CommonsEntity.data["name"].astext.ilike(search_pattern),
                CommonsEntity.data["description"].astext.ilike(search_pattern),
            )
        )

    try:
        total = query.count()
        entities = query.order_by(desc(CommonsEntity.created_at)).offset(skip).limit(limit).all()

        entity_responses = [build_entity_response(entity, db) for entity in entities]

        result = {
            "entities": entity_responses,
            "total": total,
            "skip": skip,
            "limit": limit,
            "pages": ceil(total / limit) if limit > 0 else 0,
        }

        # Cache the result (1 hour TTL)
        set_cached_public_data(cache_key, result, ttl_seconds=3600)

        return result
    except Exception as e:
        # Log error and return empty result instead of crashing
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error listing public recipes: {str(e)}", exc_info=True)
        # Return cached data if available, otherwise empty result
        return {
            "entities": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "pages": 0,
        }


@router.get("/locations", response_model=CommonsEntitiesListResponse)
async def list_public_locations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    db: Session = Depends(get_db),
):
    """
    List public locations from the commons.

    No authentication required - this is a public read-only endpoint.
    Results are cached for 1 hour.
    """
    # Check cache first
    cache_key = cache_key_public_locations(tag=tag, search=search, skip=skip, limit=limit)
    cached_data = get_cached_public_data(cache_key)
    if cached_data:
        return cached_data

    query = db.query(CommonsEntity).filter(
        and_(
            CommonsEntity.entity_type == "location",
            CommonsEntity.is_public == True,  # noqa: E712
        )
    )

    if tag:
        tag_obj = db.query(Tag).filter(Tag.name == tag).first()
        if tag_obj:
            query = query.join(CommonsEntityTag).filter(CommonsEntityTag.tag_id == tag_obj.id)
        else:
            from sqlalchemy import false

            query = query.filter(false())

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                CommonsEntity.data["name"].astext.ilike(search_pattern),
                CommonsEntity.data["description"].astext.ilike(search_pattern),
            )
        )

    total = query.count()
    entities = query.order_by(desc(CommonsEntity.created_at)).offset(skip).limit(limit).all()

    entity_responses = [build_entity_response(entity, db) for entity in entities]

    result = {
        "entities": entity_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }

    # Cache the result (1 hour TTL)
    set_cached_public_data(cache_key, result, ttl_seconds=3600)

    return result


@router.get("/tags", response_model=TagsListResponse)
async def list_tags(
    db: Session = Depends(get_db),
):
    """
    List all tags in the commons.

    No authentication required - this is a public read-only endpoint.
    Results are cached for 1 hour.
    """
    # Check cache first
    cache_key = cache_key_tags()
    cached_data = get_cached_public_data(cache_key)
    if cached_data:
        return cached_data

    tags = db.query(Tag).order_by(Tag.name).all()

    tag_responses = [
        {
            "id": str(tag.id),
            "name": tag.name,
            "description": tag.description,
            "created_at": tag.created_at,
        }
        for tag in tags
    ]

    result = {"tags": tag_responses, "total": len(tag_responses)}

    # Cache the result (1 hour TTL)
    set_cached_public_data(cache_key, result, ttl_seconds=3600)

    return result


@router.get("/search", response_model=CommonsEntitiesListResponse)
async def search_public_entities(
    q: str = Query(..., description="Search query"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """
    Full-text search across all public commons entities.

    No authentication required - this is a public read-only endpoint.
    """
    query = db.query(CommonsEntity).filter(CommonsEntity.is_public == True)  # noqa: E712

    if entity_type:
        query = query.filter(CommonsEntity.entity_type == entity_type)

    # Full-text search across entity data
    # Note: Searching entire JSONB as text is complex in SQLAlchemy 2.0
    # We search name and description fields which cover most use cases
    search_pattern = f"%{q}%"
    query = query.filter(
        or_(
            CommonsEntity.data["name"].astext.ilike(search_pattern),
            CommonsEntity.data["description"].astext.ilike(search_pattern),
        )
    )

    total = query.count()
    entities = query.order_by(desc(CommonsEntity.created_at)).offset(skip).limit(limit).all()

    entity_responses = [build_entity_response(entity, db) for entity in entities]

    return {
        "entities": entity_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }


@router.get("/items/{entity_id}", response_model=CommonsEntityResponse)
async def get_public_item(
    entity_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific public item by ID.

    Results are cached for 1 hour.
    """
    # Check cache first
    cache_key = cache_key_public_entity("item", entity_id)
    cached_data = get_cached_public_data(cache_key)
    if cached_data:
        return cached_data

    entity = (
        db.query(CommonsEntity)
        .filter(
            and_(
                CommonsEntity.id == entity_id,
                CommonsEntity.entity_type == "item",
                CommonsEntity.is_public == True,  # noqa: E712
            )
        )
        .first()
    )

    if not entity:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public item not found",
        )

    result = build_entity_response(entity, db)

    # Cache the result (1 hour TTL)
    set_cached_public_data(cache_key, result, ttl_seconds=3600)

    return result


@router.get("/recipes/{entity_id}", response_model=CommonsEntityResponse)
async def get_public_recipe(
    entity_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific public recipe (blueprint) by ID.

    Results are cached for 1 hour.
    """
    # Check cache first
    cache_key = cache_key_public_entity("blueprint", entity_id)
    cached_data = get_cached_public_data(cache_key)
    if cached_data:
        return cached_data

    entity = (
        db.query(CommonsEntity)
        .filter(
            and_(
                CommonsEntity.id == entity_id,
                CommonsEntity.entity_type == "blueprint",
                CommonsEntity.is_public == True,  # noqa: E712
            )
        )
        .first()
    )

    if not entity:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public recipe not found",
        )

    result = build_entity_response(entity, db)

    # Cache the result (1 hour TTL)
    set_cached_public_data(cache_key, result, ttl_seconds=3600)

    return result


@router.get("/locations/{entity_id}", response_model=CommonsEntityResponse)
async def get_public_location(
    entity_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific public location by ID.

    Results are cached for 1 hour.
    """
    # Check cache first
    cache_key = cache_key_public_entity("location", entity_id)
    cached_data = get_cached_public_data(cache_key)
    if cached_data:
        return cached_data

    entity = (
        db.query(CommonsEntity)
        .filter(
            and_(
                CommonsEntity.id == entity_id,
                CommonsEntity.entity_type == "location",
                CommonsEntity.is_public == True,  # noqa: E712
            )
        )
        .first()
    )

    if not entity:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public location not found",
        )

    result = build_entity_response(entity, db)

    # Cache the result (1 hour TTL)
    set_cached_public_data(cache_key, result, ttl_seconds=3600)

    return result
