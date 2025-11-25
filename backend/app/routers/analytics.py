"""
Analytics router for usage tracking and statistics.

This router provides endpoints for:
- Managing analytics consent
- Viewing usage statistics (if consented)
- Viewing recipe/blueprint statistics
"""

from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.database import get_db
from app.models.user import User
from app.models.usage_event import UsageEvent
from app.models.recipe_usage_stats import RecipeUsageStats
from app.models.blueprint import Blueprint
from app.core.dependencies import get_current_active_user
from app.schemas.analytics import (
    ConsentUpdate,
    ConsentResponse,
    UsageStatsResponse,
    RecipeStatsResponse,
)
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/analytics", tags=["analytics"])


@router.get("/consent", response_model=ConsentResponse)
async def get_consent(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's analytics consent status.
    """
    db.refresh(current_user)
    return ConsentResponse(
        analytics_consent=current_user.analytics_consent,
        updated_at=current_user.updated_at,
    )


@router.put("/consent", response_model=ConsentResponse)
async def update_consent(
    consent_data: ConsentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update analytics consent status.

    When consent is revoked (set to False), existing usage events for the user
    are not deleted, but no new events will be logged.
    """
    current_user.analytics_consent = consent_data.analytics_consent
    db.commit()
    db.refresh(current_user)

    return ConsentResponse(
        analytics_consent=current_user.analytics_consent,
        updated_at=current_user.updated_at,
    )


@router.get("/usage-stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    period_days: int = Query(
        30, ge=1, le=365, description="Number of days to include in statistics"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get aggregated usage statistics.

    Requires user consent. Returns statistics for consented users only.
    Statistics are aggregated from usage_events for the specified period.
    """
    # Check consent
    if not current_user.analytics_consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analytics consent required. Please enable analytics in your settings.",
        )

    # Calculate period
    from datetime import timezone

    period_end = datetime.now(timezone.utc).date()
    period_start = period_end - timedelta(days=period_days)

    # Only count events from users who have consented
    # Convert dates to datetimes for proper comparison with timezone-aware datetimes
    period_start_dt = datetime.combine(period_start, datetime.min.time()).replace(
        tzinfo=timezone.utc
    )
    period_end_dt = datetime.combine(period_end, datetime.max.time()).replace(tzinfo=timezone.utc)
    consented_events = (
        db.query(UsageEvent)
        .join(User, UsageEvent.user_id == User.id)
        .filter(
            and_(
                User.analytics_consent == True,  # noqa: E712
                UsageEvent.created_at >= period_start_dt,
                UsageEvent.created_at <= period_end_dt,
            )
        )
    )

    # Total events
    total_events = consented_events.count()

    # Events by type
    events_by_type_query = (
        consented_events.with_entities(
            UsageEvent.event_type, func.count(UsageEvent.id).label("count")
        )
        .group_by(UsageEvent.event_type)
        .all()
    )
    events_by_type = {event_type: count for event_type, count in events_by_type_query}

    # Top blueprints (from blueprint_used events)
    blueprint_events = consented_events.filter(UsageEvent.event_type == "blueprint_used")
    top_blueprints_query = (
        blueprint_events.with_entities(
            UsageEvent.entity_id, func.count(UsageEvent.id).label("uses")
        )
        .filter(UsageEvent.entity_id.isnot(None))
        .group_by(UsageEvent.entity_id)
        .order_by(desc("uses"))
        .limit(10)
        .all()
    )

    top_blueprints = []
    for blueprint_id, uses in top_blueprints_query:
        blueprint = db.query(Blueprint).filter(Blueprint.id == blueprint_id).first()
        if blueprint:
            top_blueprints.append(
                {
                    "blueprint_id": blueprint_id,
                    "name": blueprint.name,
                    "uses": uses,
                }
            )

    # Top goals (from goal_created events)
    goal_events = consented_events.filter(UsageEvent.event_type == "goal_created")
    top_goals_query = (
        goal_events.with_entities(
            UsageEvent.entity_id, func.count(UsageEvent.id).label("created_count")
        )
        .filter(UsageEvent.entity_id.isnot(None))
        .group_by(UsageEvent.entity_id)
        .order_by(desc("created_count"))
        .limit(10)
        .all()
    )

    # Note: We don't have goal names in the query, but we include the counts
    top_goals = [
        {
            "goal_id": goal_id,
            "created_count": created_count,
        }
        for goal_id, created_count in top_goals_query
    ]

    return UsageStatsResponse(
        total_events=total_events,
        events_by_type=events_by_type,
        top_blueprints=top_blueprints,
        top_goals=top_goals,
        period_start=period_start,
        period_end=period_end,
    )


@router.get("/recipe-stats/{blueprint_id}", response_model=RecipeStatsResponse)
async def get_recipe_stats(
    blueprint_id: str,
    period_type: str = Query("monthly", description="Period type: daily, weekly, monthly"),
    period_days: Optional[int] = Query(
        None, description="Override period - number of days to look back"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get usage statistics for a specific blueprint/recipe.

    Uses pre-aggregated statistics from recipe_usage_stats table.
    Falls back to calculating from usage_events if no aggregated stats exist.
    """
    # Validate blueprint exists
    blueprint = db.query(Blueprint).filter(Blueprint.id == blueprint_id).first()
    if not blueprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint with id '{blueprint_id}' not found",
        )

    # Validate period_type
    valid_periods = ["daily", "weekly", "monthly"]
    if period_type not in valid_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period_type. Must be one of: {', '.join(valid_periods)}",
        )

    # Determine period
    if period_days:
        period_end = date.today()
        period_start = period_end - timedelta(days=period_days)
    else:
        # Use default period based on period_type
        period_end = date.today()
        if period_type == "daily":
            period_start = period_end
        elif period_type == "weekly":
            period_start = period_end - timedelta(days=7)
        else:  # monthly
            period_start = period_end - timedelta(days=30)

    # Try to get aggregated stats first
    stats = (
        db.query(RecipeUsageStats)
        .filter(
            and_(
                RecipeUsageStats.blueprint_id == blueprint_id,
                RecipeUsageStats.period_type == period_type,
                RecipeUsageStats.period_start >= period_start,
                RecipeUsageStats.period_end <= period_end,
            )
        )
        .order_by(desc(RecipeUsageStats.period_start))
        .first()
    )

    if stats:
        # Use aggregated stats
        completion_rate = stats.completed_count / stats.total_uses if stats.total_uses > 0 else 0.0
        return RecipeStatsResponse(
            blueprint_id=blueprint_id,
            blueprint_name=blueprint.name,
            period_start=stats.period_start,
            period_end=stats.period_end,
            period_type=stats.period_type,
            total_uses=stats.total_uses,
            unique_users=stats.unique_users,
            completed_count=stats.completed_count,
            cancelled_count=stats.cancelled_count,
            completion_rate=completion_rate,
        )

    # Fallback: Calculate from usage_events (only for consented users)
    # Only count events from users who have consented
    consented_events = (
        db.query(UsageEvent)
        .join(User, UsageEvent.user_id == User.id)
        .filter(
            and_(
                User.analytics_consent == True,  # noqa: E712
                UsageEvent.event_type == "blueprint_used",
                UsageEvent.entity_id == blueprint_id,
                UsageEvent.created_at >= datetime.combine(period_start, datetime.min.time()),
                UsageEvent.created_at <= datetime.combine(period_end, datetime.max.time()),
            )
        )
    )

    total_uses = consented_events.count()
    unique_users = consented_events.with_entities(UsageEvent.user_id).distinct().count()

    # Get completion data from crafts (if available)
    from app.models.craft import Craft, CRAFT_STATUS_COMPLETED, CRAFT_STATUS_CANCELLED

    completed_count = (
        db.query(Craft)
        .filter(
            and_(
                Craft.blueprint_id == blueprint_id,
                Craft.status == CRAFT_STATUS_COMPLETED,
                Craft.created_at >= datetime.combine(period_start, datetime.min.time()),
                Craft.created_at <= datetime.combine(period_end, datetime.max.time()),
            )
        )
        .count()
    )
    cancelled_count = (
        db.query(Craft)
        .filter(
            and_(
                Craft.blueprint_id == blueprint_id,
                Craft.status == CRAFT_STATUS_CANCELLED,
                Craft.created_at >= datetime.combine(period_start, datetime.min.time()),
                Craft.created_at <= datetime.combine(period_end, datetime.max.time()),
            )
        )
        .count()
    )

    completion_rate = completed_count / total_uses if total_uses > 0 else 0.0

    return RecipeStatsResponse(
        blueprint_id=blueprint_id,
        blueprint_name=blueprint.name,
        period_start=period_start,
        period_end=period_end,
        period_type=period_type,
        total_uses=total_uses,
        unique_users=unique_users,
        completed_count=completed_count,
        cancelled_count=cancelled_count,
        completion_rate=completion_rate,
    )
