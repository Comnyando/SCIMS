"""
Optimization router for resource optimization and source finding.

This router provides endpoints for:
- Finding sources for items (stocks, players, universe)
- Suggesting crafts to produce target items
- Analyzing resource gaps for crafts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.craft import Craft
from app.services.optimization import OptimizationService
from app.schemas.optimization import (
    FindSourcesRequest,
    FindSourcesResponse,
    SuggestCraftsRequest,
    SuggestCraftsResponse,
    ResourceGapResponse,
)
from app.routers.crafts import validate_craft_access
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/optimization", tags=["optimization"])


@router.post("/find-sources", response_model=FindSourcesResponse)
async def find_sources(
    request: FindSourcesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Find sources for obtaining a specific item.

    Searches for sources in priority order:
    1. Own stock (user and organization locations)
    2. Other players' stocks (if permissions allow)
    3. Universe sources (trading posts, locations)

    Returns sorted list of source options with cost and availability information.
    """
    service = OptimizationService(db, current_user.id)

    try:
        return service.find_sources_for_item(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding sources: {str(e)}",
        )


@router.post("/suggest-crafts", response_model=SuggestCraftsResponse)
async def suggest_crafts(
    request: SuggestCraftsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Suggest crafts to produce a target item.

    Finds blueprints that produce the target item and suggests how many times
    to craft each blueprint to reach the target quantity. Sorts suggestions by
    feasibility (all ingredients available first) and crafting time.
    """
    service = OptimizationService(db, current_user.id)

    try:
        return service.suggest_crafts(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error suggesting crafts: {str(e)}",
        )


@router.get("/resource-gap/{craft_id}", response_model=ResourceGapResponse)
async def get_resource_gap(
    craft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Analyze resource gaps for a craft.

    For each ingredient required by the craft, calculates:
    - Required quantity
    - Available quantity in stock
    - Gap quantity (missing)
    - Available sources to fill the gap

    Returns gap analysis sorted by severity (largest gaps first).
    """
    # Validate craft exists and user has access
    craft = db.query(Craft).filter(Craft.id == craft_id).first()
    if not craft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Craft with id '{craft_id}' not found",
        )

    validate_craft_access(craft, current_user, db)

    service = OptimizationService(db, current_user.id)

    try:
        return service.get_resource_gap(craft_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resource gap: {str(e)}",
        )
