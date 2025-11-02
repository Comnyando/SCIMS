"""
Celery application configuration and setup.

Provides Celery instance for background task processing.
"""

from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "scims",
    broker=settings.celery_broker_url,
    backend=settings.celery_broker_url,  # Using Redis as both broker and result backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic task configuration (for scheduled tasks)
celery_app.conf.beat_schedule = {
    "complete-ready-crafts": {
        "task": "app.tasks.crafts.complete_ready_crafts",
        "schedule": 60.0,  # Run every 60 seconds
    },
    "cleanup-old-item-history": {
        "task": "app.tasks.maintenance.cleanup_old_item_history",
        "schedule": 86400.0,  # Run daily (24 hours in seconds)
    },
    "aggregate-recipe-stats-daily": {
        "task": "analytics.aggregate_recipe_stats",
        "schedule": 86400.0,  # Run daily
        "kwargs": {"period_type": "daily"},
    },
    "aggregate-recipe-stats-weekly": {
        "task": "analytics.aggregate_recipe_stats",
        "schedule": 604800.0,  # Run weekly (7 days in seconds)
        "kwargs": {"period_type": "weekly"},
    },
    "aggregate-recipe-stats-monthly": {
        "task": "analytics.aggregate_recipe_stats",
        "schedule": 2592000.0,  # Run monthly (30 days in seconds)
        "kwargs": {"period_type": "monthly"},
    },
    "cleanup-old-analytics-events": {
        "task": "analytics.cleanup_old_events",
        "schedule": 86400.0,  # Run daily
        "kwargs": {"days_to_keep": 365},
    },
}
