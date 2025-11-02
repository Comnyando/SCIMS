"""
Blueprint model representing crafting blueprints.

Blueprints define how to craft items by specifying:
- Output item and quantity
- Required ingredients (items and quantities)
- Crafting time
- Blueprint metadata (name, description, category)
- Sharing settings (public/private)
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING, Any
from decimal import Decimal
from sqlalchemy import String, Text, Integer, Numeric, Boolean, Index, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.user import User


class Blueprint(Base, UUIDPrimaryKeyMixin):
    """
    Blueprint model for crafting blueprints.

    Blueprints specify how to craft items:
    - Output: what item is produced and in what quantity
    - Ingredients: what items are needed and in what quantities (stored as JSONB)
    - Metadata: name, description, category for organization
    - Sharing: public blueprints are visible to all users, private blueprints are creator-only
    - Popularity: usage_count tracks how many times the blueprint has been used

    The blueprint_data JSONB field stores ingredients in this format:
    {
        "ingredients": [
            {"item_id": "uuid", "quantity": 5.0, "optional": false},
            ...
        ]
    }
    """

    __tablename__ = "blueprints"
    __table_args__ = (
        Index("ix_blueprints_name", "name"),
        Index("ix_blueprints_category", "category"),
        Index("ix_blueprints_output_item_id", "output_item_id"),
        Index("ix_blueprints_created_by", "created_by"),
        Index("ix_blueprints_is_public", "is_public"),
        Index("ix_blueprints_usage_count", "usage_count"),
        {"comment": "Crafting blueprints defining item production"},
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Blueprint name",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Blueprint description",
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Blueprint category (e.g., Weapons, Components, Food)",
    )

    crafting_time_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Crafting time in minutes (0 = instant)",
    )

    output_item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Item produced by this blueprint",
    )

    output_quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=False,
        comment="Quantity of output item produced",
    )

    blueprint_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Blueprint ingredients and metadata (JSON)",
    )

    created_by: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who created this blueprint",
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether blueprint is publicly visible",
    )

    usage_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of times this blueprint has been used (for popularity tracking)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the record was created",
    )

    # Relationships
    output_item: Mapped["Item"] = relationship(
        "Item",
        foreign_keys=[output_item_id],
    )

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )

    def __repr__(self) -> str:
        return (
            f"<Blueprint(id={self.id!r}, name={self.name!r}, "
            f"category={self.category!r}, output_item_id={self.output_item_id!r})>"
        )
