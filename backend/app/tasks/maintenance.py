"""
Celery tasks for maintenance operations.

Handles periodic cleanup and maintenance tasks.
"""

from celery import Task
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal


@celery_app.task(name="app.tasks.maintenance.cleanup_old_item_history", bind=True)
def cleanup_old_item_history(self: Task, retention_days: int = 30) -> dict:
    """
    Celery task to clean up old item_history records.

    This task runs daily to remove item_history records older than the retention period.
    Uses the database function for efficient deletion.

    Args:
        retention_days: Number of days to retain (default 30)

    Returns:
        dict: Summary of cleanup operation
    """
    db: Session = SessionLocal()

    try:
        # Call the database function to clean up old records
        result = db.execute(
            text("SELECT cleanup_old_item_history(:retention_days)"),
            {"retention_days": retention_days},
        )
        deleted_count = result.scalar()

        db.commit()

        return {
            "status": "success",
            "deleted_records": deleted_count,
            "retention_days": retention_days,
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e),
        }
    finally:
        db.close()
