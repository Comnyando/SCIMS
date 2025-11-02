"""
Celery tasks for analytics data aggregation.

These tasks aggregate usage events into pre-calculated statistics
for improved query performance.
"""

from datetime import date, timedelta, datetime
from app.celery_app import celery_app
from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import SessionLocal
from app.models.usage_event import UsageEvent
from app.models.recipe_usage_stats import RecipeUsageStats
from app.models.blueprint import Blueprint
from app.models.user import User
from app.models.craft import Craft, CRAFT_STATUS_COMPLETED, CRAFT_STATUS_CANCELLED


@shared_task(name="analytics.aggregate_recipe_stats")
def aggregate_recipe_stats(period_type: str = "daily") -> dict:
    """
    Aggregate recipe/blueprint usage statistics.

    Calculates statistics from usage_events and crafts tables,
    then stores them in recipe_usage_stats for fast queries.

    Args:
        period_type: Type of period to aggregate ("daily", "weekly", "monthly")

    Returns:
        dict with aggregation results
    """
    db = SessionLocal()
    try:
        # Determine period boundaries
        today = date.today()
        if period_type == "daily":
            period_start = today
            period_end = today
        elif period_type == "weekly":
            period_start = today - timedelta(days=7)
            period_end = today
        elif period_type == "monthly":
            period_start = today - timedelta(days=30)
            period_end = today
        else:
            return {"error": f"Invalid period_type: {period_type}"}

        # Get all blueprints
        blueprints = db.query(Blueprint).all()

        aggregated = 0
        for blueprint in blueprints:
            # Only count events from users who have consented
            consented_events = (
                db.query(UsageEvent)
                .join(User, UsageEvent.user_id == User.id)
                .filter(
                    and_(
                        User.analytics_consent == True,  # noqa: E712
                        UsageEvent.event_type == "blueprint_used",
                        UsageEvent.entity_id == blueprint.id,
                        UsageEvent.created_at
                        >= datetime.combine(period_start, datetime.min.time()),
                        UsageEvent.created_at <= datetime.combine(period_end, datetime.max.time()),
                    )
                )
            )

            total_uses = consented_events.count()
            unique_users = consented_events.with_entities(UsageEvent.user_id).distinct().count()

            # Get completion data from crafts
            completed_count = (
                db.query(Craft)
                .filter(
                    and_(
                        Craft.blueprint_id == blueprint.id,
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
                        Craft.blueprint_id == blueprint.id,
                        Craft.status == CRAFT_STATUS_CANCELLED,
                        Craft.created_at >= datetime.combine(period_start, datetime.min.time()),
                        Craft.created_at <= datetime.combine(period_end, datetime.max.time()),
                    )
                )
                .count()
            )

            # Update or create stats record
            existing = (
                db.query(RecipeUsageStats)
                .filter(
                    and_(
                        RecipeUsageStats.blueprint_id == blueprint.id,
                        RecipeUsageStats.period_start == period_start,
                        RecipeUsageStats.period_end == period_end,
                        RecipeUsageStats.period_type == period_type,
                    )
                )
                .first()
            )

            if existing:
                existing.total_uses = total_uses
                existing.unique_users = unique_users
                existing.completed_count = completed_count
                existing.cancelled_count = cancelled_count
            else:
                stats = RecipeUsageStats(
                    blueprint_id=blueprint.id,
                    period_start=period_start,
                    period_end=period_end,
                    period_type=period_type,
                    total_uses=total_uses,
                    unique_users=unique_users,
                    completed_count=completed_count,
                    cancelled_count=cancelled_count,
                )
                db.add(stats)

            aggregated += 1

        db.commit()

        return {
            "status": "success",
            "period_type": period_type,
            "period_start": str(period_start),
            "period_end": str(period_end),
            "blueprints_aggregated": aggregated,
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


@shared_task(name="analytics.cleanup_old_events")
def cleanup_old_events(days_to_keep: int = 365) -> dict:
    """
    Clean up old usage events to prevent database bloat.

    Deletes usage events older than the specified number of days.
    Aggregated statistics are preserved.

    Args:
        days_to_keep: Number of days of events to keep

    Returns:
        dict with cleanup results
    """
    db = SessionLocal()
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        deleted_count = db.query(UsageEvent).filter(UsageEvent.created_at < cutoff_date).delete()

        db.commit()

        return {
            "status": "success",
            "cutoff_date": cutoff_date.isoformat(),
            "events_deleted": deleted_count,
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
