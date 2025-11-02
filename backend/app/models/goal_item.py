"""
GoalItem model representing individual target items for a goal.

Tracks target items and their required quantities for each goal.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Numeric, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.goal import Goal
    from app.models.item import Item


class GoalItem(Base, UUIDPrimaryKeyMixin):
    """
    GoalItem model for tracking individual target items in a goal.

    Each goal can have multiple target items, each tracked separately:
    - Links to a goal and an item
    - Tracks target quantity for that item
    - Progress is calculated per item and aggregated for overall goal completion

    Unique constraint ensures each item appears only once per goal.
    """

    __tablename__ = "goal_items"
    __table_args__ = (
        UniqueConstraint("goal_id", "item_id", name="uq_goal_item_goal_item"),
        Index("ix_goal_items_goal_id", "goal_id"),
        Index("ix_goal_items_item_id", "item_id"),
        {"comment": "Individual target items for each goal"},
    )

    goal_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("goals.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the goal",
    )

    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Reference to the target item",
    )

    target_quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=False,
        comment="Target quantity for this item",
    )

    # Relationships
    goal: Mapped["Goal"] = relationship(
        "Goal",
        foreign_keys=[goal_id],
        back_populates="goal_items",
    )

    item: Mapped["Item"] = relationship(
        "Item",
        foreign_keys=[item_id],
    )

    def __repr__(self) -> str:
        return (
            f"<GoalItem(id={self.id!r}, goal_id={self.goal_id!r}, "
            f"item_id={self.item_id!r}, target_quantity={self.target_quantity!r})>"
        )
