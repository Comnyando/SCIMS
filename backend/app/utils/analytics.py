"""
Analytics utility functions for logging usage events.

These functions provide a convenient way to log usage events from route handlers
with full context (entity IDs, event data, etc.).
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.usage_event import UsageEvent
from app.models.user import User
from app.middleware.analytics import anonymize_ip, truncate_user_agent


def log_event(
    db: Session,
    user_id: Optional[str],
    event_type: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    event_data: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    Log a usage event if user has consented.

    This is a convenience function that route handlers can use to log events
    with full context. Only logs if the user has analytics_consent = true.

    Args:
        db: Database session
        user_id: User ID (optional, for anonymous events)
        event_type: Type of event (e.g., "blueprint_used", "goal_created")
        entity_type: Type of entity (e.g., "blueprint", "goal")
        entity_id: ID of the entity
        event_data: Additional event-specific data (dict)
        ip_address: IP address (will be anonymized)
        user_agent: User agent string (will be truncated)
    """
    # If user_id is provided, check consent
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.analytics_consent:
            return  # Don't log if user hasn't consented

    # Anonymize and truncate sensitive data
    anonymized_ip = anonymize_ip(ip_address) if ip_address else None
    truncated_ua = truncate_user_agent(user_agent)

    # Create event
    event = UsageEvent(
        user_id=user_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        event_data=event_data,
        ip_address=anonymized_ip,
        user_agent=truncated_ua,
    )

    db.add(event)
    # Don't commit here - let the route handler commit the transaction
