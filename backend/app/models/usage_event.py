"""
Usage Event model for analytics tracking.

Tracks user actions and events for analytics purposes.
Requires explicit user consent before logging events.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING, Any
from sqlalchemy import String, Index, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class UsageEvent(Base, UUIDPrimaryKeyMixin):
    """
    Usage Event model for tracking user actions.

    Events are only logged if the user has given explicit consent (analytics_consent = true).
    This model stores:
    - Event type and entity information
    - Optional user ID (nullable for anonymous events)
    - Event-specific data as JSONB
    - Request metadata (IP, user agent) for analysis

    Privacy considerations:
    - IP addresses may be anonymized
    - User agent strings are truncated
    - Events can be aggregated for statistics
    """

    __tablename__ = "usage_events"
    __table_args__ = (
        Index("ix_usage_events_user_id", "user_id"),
        Index("ix_usage_events_event_type", "event_type"),
        Index("ix_usage_events_entity_type", "entity_type"),
        Index("ix_usage_events_entity_id", "entity_id"),
        Index("ix_usage_events_created_at", "created_at"),
        Index("ix_usage_events_user_event", "user_id", "event_type"),
        {"comment": "Usage events for analytics (requires user consent)"},
    )

    user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who triggered the event (nullable for anonymous events)",
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of event (e.g., blueprint_used, goal_created, item_stock_updated)",
    )

    entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Type of entity involved (e.g., blueprint, goal, item)",
    )

    entity_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
        comment="ID of the entity involved",
    )

    event_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional event-specific data (JSON)",
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
        comment="IP address (anonymized if required)",
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="User agent string (truncated)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when the event occurred",
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[user_id],
    )

    def __repr__(self) -> str:
        return (
            f"<UsageEvent(id={self.id!r}, event_type={self.event_type!r}, "
            f"entity_type={self.entity_type!r}, created_at={self.created_at!r})>"
        )
