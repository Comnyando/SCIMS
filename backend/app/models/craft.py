"""
Craft model representing crafting operations.

Tracks the execution of blueprints, including status, timing, and ingredient fulfillment.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING, Any
from decimal import Decimal
from sqlalchemy import String, Integer, Boolean, Index, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.blueprint import Blueprint
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.location import Location
    from app.models.craft_ingredient import CraftIngredient


# Craft statuses
CRAFT_STATUS_PLANNED = "planned"
CRAFT_STATUS_IN_PROGRESS = "in_progress"
CRAFT_STATUS_COMPLETED = "completed"
CRAFT_STATUS_CANCELLED = "cancelled"

CRAFT_STATUSES = [
    CRAFT_STATUS_PLANNED,
    CRAFT_STATUS_IN_PROGRESS,
    CRAFT_STATUS_COMPLETED,
    CRAFT_STATUS_CANCELLED,
]


class Craft(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Craft model for tracking crafting operations.

    Represents the execution of a blueprint to produce items:
    - Links to a blueprint that defines what to craft
    - Tracks status through the crafting lifecycle
    - Manages timing (scheduled, started, completed)
    - Associates with organization and requester
    - Defines output location for produced items

    Status Flow:
    - planned: Craft created but not yet started
    - in_progress: Craft has started, ingredients reserved
    - completed: Craft finished, items produced
    - cancelled: Craft was cancelled before completion

    Ingredients are tracked separately in CraftIngredient model.
    """

    __tablename__ = "crafts"
    __table_args__ = (
        Index("ix_crafts_blueprint_id", "blueprint_id"),
        Index("ix_crafts_organization_id", "organization_id"),
        Index("ix_crafts_requested_by", "requested_by"),
        Index("ix_crafts_status", "status"),
        Index("ix_crafts_status_organization", "status", "organization_id"),
        {"comment": "Crafting operations tracking"},
    )

    blueprint_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("blueprints.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Reference to the blueprint",
    )

    organization_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        comment="Organization this craft belongs to (nullable)",
    )

    requested_by: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who requested this craft",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=CRAFT_STATUS_PLANNED,
        server_default=CRAFT_STATUS_PLANNED,
        comment="Craft status: planned, in_progress, completed, cancelled",
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Craft priority (higher = more important)",
    )

    scheduled_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scheduled start time (nullable)",
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Actual start time (nullable)",
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Completion time (nullable)",
    )

    output_location_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Location where output items will be placed",
    )

    craft_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional craft metadata (JSON)",
    )

    # Relationships
    blueprint: Mapped["Blueprint"] = relationship(
        "Blueprint",
        foreign_keys=[blueprint_id],
    )

    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    requester: Mapped["User"] = relationship(
        "User",
        foreign_keys=[requested_by],
    )

    output_location: Mapped["Location"] = relationship(
        "Location",
        foreign_keys=[output_location_id],
    )

    ingredients: Mapped[list["CraftIngredient"]] = relationship(
        "CraftIngredient",
        back_populates="craft",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Craft(id={self.id!r}, blueprint_id={self.blueprint_id!r}, "
            f"status={self.status!r}, requested_by={self.requested_by!r})>"
        )
