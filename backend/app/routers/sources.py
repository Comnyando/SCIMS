"""
Resource Sources router for managing resource sources.

This router provides endpoints for:
- Creating and managing resource sources (where items can be obtained)
- Tracking source reliability through verification
- Verifying sources and updating reliability scores
"""

from typing import Optional, Any
from math import ceil
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc

from app.database import get_db
from app.models.resource_source import (
    ResourceSource,
    SOURCE_TYPE_PLAYER_STOCK,
    SOURCE_TYPE_UNIVERSE_LOCATION,
    SOURCE_TYPE_TRADING_POST,
)
from app.models.source_verification_log import SourceVerificationLog
from app.models.item import Item
from app.models.location import Location
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.resource_source import (
    ResourceSourceCreate,
    ResourceSourceUpdate,
    ResourceSourceResponse,
    SourceVerificationLogCreate,
    SourceVerificationLogResponse,
)
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/sources", tags=["sources"])


def validate_item_exists(db: Session, item_id: str) -> Item:
    """Validate that an item exists, raise 404 if not."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id '{item_id}' not found",
        )
    return item


def validate_location_exists(db: Session, location_id: str) -> Location:
    """Validate that a location exists, raise 404 if not."""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id '{location_id}' not found",
        )
    return location


def validate_source_exists(db: Session, source_id: str) -> ResourceSource:
    """Validate that a resource source exists, raise 404 if not."""
    source = (
        db.query(ResourceSource)
        .options(joinedload(ResourceSource.item), joinedload(ResourceSource.location))
        .filter(ResourceSource.id == source_id)
        .first()
    )
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource source with id '{source_id}' not found",
        )
    return source


def calculate_reliability_score(db: Session, source_id: str) -> Decimal:
    """
    Calculate reliability score based on verification history.

    Algorithm:
    - Start with default score of 0.5
    - For each verification:
      - If accurate: add 0.1 to score (capped at 1.0)
      - If inaccurate: subtract 0.15 from score (capped at 0.0)
    - Apply exponential decay based on time since last verification
      - Score decays by 10% per 30 days of staleness
    - Recent verifications are weighted more heavily

    Returns a score between 0.0 and 1.0.
    """
    verifications = (
        db.query(SourceVerificationLog)
        .filter(SourceVerificationLog.source_id == source_id)
        .order_by(SourceVerificationLog.verified_at.desc())
        .all()
    )

    if not verifications:
        return Decimal("0.5")  # Default score for unverified sources

    # Calculate base score from verification history
    score = Decimal("0.5")
    total_verifications = len(verifications)
    accurate_count = sum(1 for v in verifications if v.was_accurate)

    if total_verifications > 0:
        # Apply recency weighting (more recent verifications matter more)
        now = datetime.now(timezone.utc)
        weighted_sum = Decimal("0")
        total_weight = Decimal("0")

        for verification in verifications:
            # Ensure verification.verified_at is timezone-aware
            verified_at = verification.verified_at
            if verified_at.tzinfo is None:
                verified_at = verified_at.replace(tzinfo=timezone.utc)

            days_ago = (now - verified_at).days
            # Weight decreases exponentially: 1.0 for today, 0.5 for 7 days, 0.25 for 14 days, etc.
            weight = Decimal("1.0") / (Decimal("1") + Decimal(str(days_ago)) / Decimal("7"))
            value = Decimal("1.0") if verification.was_accurate else Decimal("0.0")
            weighted_sum += weight * value
            total_weight += weight

        if total_weight > 0:
            # Use recency-weighted accuracy as the primary score
            score = weighted_sum / total_weight
        else:
            # Fallback to simple accuracy rate if no weights
            accuracy_rate = Decimal(accurate_count) / Decimal(total_verifications)
            score = accuracy_rate

    # Apply staleness penalty (if last verification is old)
    source = db.query(ResourceSource).filter(ResourceSource.id == source_id).first()
    if source and source.last_verified:
        # Ensure last_verified is timezone-aware
        last_verified = source.last_verified
        if last_verified.tzinfo is None:
            last_verified = last_verified.replace(tzinfo=timezone.utc)

        days_since_verification = (datetime.now(timezone.utc) - last_verified).days
        if days_since_verification > 30:
            # Apply exponential decay: 10% penalty per 30 days
            staleness_penalty = min(
                Decimal("0.5"),
                Decimal(str(days_since_verification - 30)) / Decimal("60") * Decimal("0.1"),
            )
            score = max(Decimal("0"), score - staleness_penalty)

    # Ensure score is in valid range
    return max(Decimal("0"), min(Decimal("1"), score))


@router.get("", response_model=dict)
async def list_sources(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    item_id: Optional[str] = Query(None, description="Filter by item ID"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    min_reliability: Optional[float] = Query(
        None, ge=0, le=1, description="Minimum reliability score"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List resource sources with optional filtering.

    Supports pagination, filtering by item, source type, and minimum reliability score.
    """
    query = db.query(ResourceSource).options(
        joinedload(ResourceSource.item), joinedload(ResourceSource.location)
    )

    # Apply filters
    if item_id:
        query = query.filter(ResourceSource.item_id == item_id)
    if source_type:
        query = query.filter(ResourceSource.source_type == source_type)
    if min_reliability is not None:
        query = query.filter(ResourceSource.reliability_score >= Decimal(str(min_reliability)))

    # Get total count for pagination
    total = query.count()

    # Apply pagination and order by reliability score (desc) and item_id
    sources = (
        query.order_by(desc(ResourceSource.reliability_score), ResourceSource.item_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Convert to response format
    source_responses = []
    for source in sources:
        source_dict = {
            "id": str(source.id),
            "item_id": str(source.item_id),
            "source_type": source.source_type,
            "source_identifier": source.source_identifier,
            "available_quantity": float(source.available_quantity),
            "cost_per_unit": float(source.cost_per_unit) if source.cost_per_unit else None,
            "last_verified": source.last_verified,
            "reliability_score": (
                float(source.reliability_score) if source.reliability_score else None
            ),
            "metadata": source.source_metadata if source.source_metadata else {},
            "created_at": source.created_at,
            "updated_at": source.updated_at,
            "location_id": str(source.location_id) if source.location_id else None,
            "item": (
                {
                    "id": source.item.id,
                    "name": source.item.name,
                    "category": source.item.category,
                }
                if source.item
                else None
            ),
            "location": (
                {
                    "id": source.location.id,
                    "name": source.location.name,
                    "type": source.location.type,
                }
                if source.location
                else None
            ),
        }
        source_responses.append(ResourceSourceResponse.model_validate(source_dict))

    return {
        "items": source_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }


@router.post("", response_model=ResourceSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source_data: ResourceSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new resource source.

    Validates that the item exists, then creates a new resource source entry.
    """
    # Validate item exists
    validate_item_exists(db, source_data.item_id)

    # Validate location if provided
    if source_data.location_id:
        validate_location_exists(db, source_data.location_id)

    # Create new source
    new_source = ResourceSource(
        item_id=source_data.item_id,
        source_type=source_data.source_type,
        source_identifier=source_data.source_identifier,
        available_quantity=source_data.available_quantity,
        cost_per_unit=source_data.cost_per_unit,
        reliability_score=source_data.reliability_score,
        source_metadata=source_data.metadata,
        location_id=source_data.location_id,
    )

    db.add(new_source)
    db.commit()
    db.refresh(new_source)

    # Load relationships
    db.refresh(new_source)
    source = (
        db.query(ResourceSource)
        .options(joinedload(ResourceSource.item), joinedload(ResourceSource.location))
        .filter(ResourceSource.id == new_source.id)
        .first()
    )

    if not source:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created source",
        )

    # Build response
    source_dict = {
        "id": str(source.id),
        "item_id": str(source.item_id),
        "source_type": source.source_type,
        "source_identifier": source.source_identifier,
        "available_quantity": float(source.available_quantity),
        "cost_per_unit": float(source.cost_per_unit) if source.cost_per_unit else None,
        "last_verified": source.last_verified,
        "reliability_score": float(source.reliability_score) if source.reliability_score else None,
        "metadata": source.source_metadata if source.source_metadata else {},
        "created_at": source.created_at,
        "updated_at": source.updated_at,
        "location_id": str(source.location_id) if source.location_id else None,
        "item": (
            {
                "id": source.item.id,
                "name": source.item.name,
                "category": source.item.category,
            }
            if source.item
            else None
        ),
        "location": (
            {
                "id": source.location.id,
                "name": source.location.name,
                "type": source.location.type,
            }
            if source.location
            else None
        ),
    }

    return ResourceSourceResponse.model_validate(source_dict)


@router.get("/{source_id}", response_model=ResourceSourceResponse)
async def get_source(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific resource source by ID.
    """
    source = validate_source_exists(db, source_id)

    # Build response
    source_dict = {
        "id": str(source.id),
        "item_id": str(source.item_id),
        "source_type": source.source_type,
        "source_identifier": source.source_identifier,
        "available_quantity": float(source.available_quantity),
        "cost_per_unit": float(source.cost_per_unit) if source.cost_per_unit else None,
        "last_verified": source.last_verified,
        "reliability_score": float(source.reliability_score) if source.reliability_score else None,
        "metadata": source.source_metadata if source.source_metadata else {},
        "created_at": source.created_at,
        "updated_at": source.updated_at,
        "location_id": str(source.location_id) if source.location_id else None,
        "item": (
            {
                "id": source.item.id,
                "name": source.item.name,
                "category": source.item.category,
            }
            if source.item
            else None
        ),
        "location": (
            {
                "id": source.location.id,
                "name": source.location.name,
                "type": source.location.type,
            }
            if source.location
            else None
        ),
    }

    return ResourceSourceResponse.model_validate(source_dict)


@router.patch("/{source_id}", response_model=ResourceSourceResponse)
async def update_source(
    source_id: str,
    source_data: ResourceSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a resource source.

    Only updates fields that are provided in the request.
    """
    source = validate_source_exists(db, source_id)

    # Validate location if provided in update
    if source_data.location_id is not None:
        validate_location_exists(db, source_data.location_id)

    # Update fields
    update_dict = source_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        # Map metadata to source_metadata for model
        if field == "metadata":
            setattr(source, "source_metadata", value)
        else:
            setattr(source, field, value)

    db.commit()
    db.refresh(source)

    # Reload with relationships
    updated_source = (
        db.query(ResourceSource)
        .options(joinedload(ResourceSource.item), joinedload(ResourceSource.location))
        .filter(ResourceSource.id == source_id)
        .first()
    )

    if not updated_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource source with id '{source_id}' not found",
        )

    # Build response
    source_dict = {
        "id": str(updated_source.id),
        "item_id": str(updated_source.item_id),
        "source_type": updated_source.source_type,
        "source_identifier": updated_source.source_identifier,
        "available_quantity": float(updated_source.available_quantity),
        "cost_per_unit": (
            float(updated_source.cost_per_unit) if updated_source.cost_per_unit else None
        ),
        "last_verified": updated_source.last_verified,
        "reliability_score": (
            float(updated_source.reliability_score) if updated_source.reliability_score else None
        ),
        "metadata": updated_source.source_metadata if updated_source.source_metadata else {},
        "created_at": updated_source.created_at,
        "updated_at": updated_source.updated_at,
        "location_id": str(updated_source.location_id) if updated_source.location_id else None,
        "item": (
            {
                "id": updated_source.item.id,
                "name": updated_source.item.name,
                "category": updated_source.item.category,
            }
            if updated_source.item
            else None
        ),
        "location": (
            {
                "id": updated_source.location.id,
                "name": updated_source.location.name,
                "type": updated_source.location.type,
            }
            if updated_source.location
            else None
        ),
    }

    return ResourceSourceResponse.model_validate(source_dict)


@router.post(
    "/{source_id}/verify",
    response_model=SourceVerificationLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def verify_source(
    source_id: str,
    verification_data: SourceVerificationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Verify a resource source and update its reliability score.

    Creates a verification log entry and recalculates the source's reliability score
    based on all verification history.
    """
    # Validate source exists
    source = validate_source_exists(db, source_id)

    # Ensure source_id in request matches URL parameter
    if verification_data.source_id != source_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source ID in request body must match URL parameter",
        )

    # Create verification log entry
    verification = SourceVerificationLog(
        source_id=source_id,
        verified_by=current_user.id,
        was_accurate=verification_data.was_accurate,
        notes=verification_data.notes,
    )

    db.add(verification)
    db.commit()
    db.refresh(verification)

    # Update source's last_verified timestamp
    source.last_verified = datetime.now(timezone.utc)

    # Recalculate reliability score
    source.reliability_score = calculate_reliability_score(db, source_id)

    db.commit()
    db.refresh(source)
    db.refresh(verification)

    # Build response
    verification_dict = {
        "id": str(verification.id),
        "source_id": str(verification.source_id),
        "verified_by": str(verification.verified_by),
        "verified_at": verification.verified_at,
        "was_accurate": verification.was_accurate,
        "notes": verification.notes,
        "verifier": {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
        },
        "source": None,  # Could include source details if needed
    }

    return SourceVerificationLogResponse.model_validate(verification_dict)
