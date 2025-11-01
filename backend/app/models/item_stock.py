"""
ItemStock model representing stock levels for items at locations.

Tracks available and reserved quantities for each item at each location.
Reserved quantities are used for in-progress crafts or planned operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Numeric, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.location import Location
    from app.models.user import User


class ItemStock(Base, UUIDPrimaryKeyMixin):
    """
    ItemStock model for tracking stock levels.

    Represents the quantity of a specific item at a specific location:
    - quantity: Available quantity (can be used/transferred)
    - reserved_quantity: Reserved for in-progress operations (crafts, transfers)
    - updated_by: User who last modified this stock level
    - last_updated: Timestamp of last update

    Constraints:
    - Unique constraint on (item_id, location_id) ensures one stock record per item/location
    - Supports fractional quantities (DECIMAL type)

    Usage:
    - When reserving items for crafts, increase reserved_quantity
    - When fulfilling crafts, decrease reserved_quantity and quantity
    - Available quantity = quantity - reserved_quantity
    """

    __tablename__ = "item_stocks"
    __table_args__ = (
        UniqueConstraint("item_id", "location_id", name="uq_item_stock_item_location"),
        Index("ix_item_stocks_item_id", "item_id"),
        Index("ix_item_stocks_location_id", "location_id"),
        Index("ix_item_stocks_updated_by", "updated_by"),
        {"comment": "Stock levels for items at specific locations"},
    )

    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the item",
    )

    location_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the location",
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=False,
        server_default="0",
        comment="Available quantity (supports fractional quantities)",
    )

    reserved_quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=False,
        server_default="0",
        comment="Quantity reserved for in-progress crafts",
    )

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when stock was last updated",
    )

    updated_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Reference to the user who last updated this stock",
    )

    # Relationships
    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="stocks",
    )

    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="stocks",
    )

    updater: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by],
    )

    @property
    def available_quantity(self) -> Decimal:
        """
        Calculate available quantity (total - reserved).

        This represents the quantity that can actually be used or transferred.
        """
        return self.quantity - self.reserved_quantity

    def __repr__(self) -> str:
        return (
            f"<ItemStock(id={self.id!r}, item_id={self.item_id!r}, "
            f"location_id={self.location_id!r}, quantity={self.quantity!r}, "
            f"reserved_quantity={self.reserved_quantity!r})>"
        )
