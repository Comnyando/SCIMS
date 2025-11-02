"""
Recipe Usage Stats model for aggregated blueprint statistics.

Stores pre-aggregated statistics about blueprint usage for performance.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Date, Index, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.blueprint import Blueprint


class RecipeUsageStats(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Recipe Usage Stats model for aggregated blueprint statistics.

    Pre-aggregated statistics about blueprint usage to avoid querying
    large numbers of usage_events. Statistics are aggregated by time period
    (daily, weekly, monthly) and updated by Celery tasks.

    This model stores:
    - Blueprint reference
    - Time period (start, end, type)
    - Aggregated metrics (total uses, unique users, completion rates)
    """

    __tablename__ = "recipe_usage_stats"
    __table_args__ = (
        UniqueConstraint(
            "blueprint_id",
            "period_start",
            "period_end",
            "period_type",
            name="uq_recipe_stats_period",
        ),
        Index("ix_recipe_usage_stats_blueprint_id", "blueprint_id"),
        Index("ix_recipe_usage_stats_period", "period_start", "period_end"),
        Index("ix_recipe_usage_stats_period_type", "period_type"),
        {"comment": "Aggregated usage statistics for blueprints"},
    )

    blueprint_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("blueprints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Blueprint this stat is for",
    )

    period_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Start of the aggregation period",
    )

    period_end: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="End of the aggregation period",
    )

    period_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Type of period: daily, weekly, monthly",
    )

    total_uses: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of times blueprint was used",
    )

    unique_users: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of unique users who used this blueprint",
    )

    completed_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of completed crafts",
    )

    cancelled_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of cancelled crafts",
    )

    # Relationships
    blueprint: Mapped["Blueprint"] = relationship(
        "Blueprint",
        foreign_keys=[blueprint_id],
    )

    def __repr__(self) -> str:
        return (
            f"<RecipeUsageStats(id={self.id!r}, blueprint_id={self.blueprint_id!r}, "
            f"period_type={self.period_type!r}, total_uses={self.total_uses!r})>"
        )
