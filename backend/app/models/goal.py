"""
Goal model representing user and organization goals.

Tracks goals for inventory management, such as target quantities of items.
Goals can be personal or organization-wide.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING, Any
from decimal import Decimal
from sqlalchemy import String, Index, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.item import Item
    from app.models.goal_item import GoalItem


# Goal statuses
GOAL_STATUS_ACTIVE = "active"
GOAL_STATUS_COMPLETED = "completed"
GOAL_STATUS_CANCELLED = "cancelled"

GOAL_STATUSES = [
    GOAL_STATUS_ACTIVE,
    GOAL_STATUS_COMPLETED,
    GOAL_STATUS_CANCELLED,
]


class Goal(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Goal model for tracking inventory goals.

    Represents a goal to achieve a certain quantity of an item:
    - Can be personal (created_by user) or organization-wide (organization_id)
    - Tracks target item and quantity
    - Optional target date for completion
    - Progress tracked via progress_data JSONB field
    - Status: active, completed, cancelled

    Progress Calculation:
    - For item-based goals: Calculates current stock across accessible locations
    - Progress_data stores calculated progress, current_quantity, and percentage
    - Completion is detected when current_quantity >= target_quantity
    """

    __tablename__ = "goals"
    __table_args__ = (
        Index("ix_goals_organization_id", "organization_id"),
        Index("ix_goals_created_by", "created_by"),
        Index("ix_goals_status", "status"),
        Index("ix_goals_status_organization", "status", "organization_id"),
        Index("ix_goals_target_date", "target_date"),
        {"comment": "Goals tracking for inventory management"},
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Goal name",
    )

    description: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="Goal description",
    )

    organization_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        comment="Organization this goal belongs to (nullable)",
    )

    created_by: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who created this goal",
    )

    target_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Target completion date (nullable)",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=GOAL_STATUS_ACTIVE,
        server_default=GOAL_STATUS_ACTIVE,
        comment="Goal status: active, completed, cancelled",
    )

    progress_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Progress tracking data (JSON)",
    )

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )

    goal_items: Mapped[list["GoalItem"]] = relationship(
        "GoalItem",
        back_populates="goal",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Goal(id={self.id!r}, name={self.name!r}, status={self.status!r})>"
