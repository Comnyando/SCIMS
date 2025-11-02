"""
ItemHistory model representing audit trail of inventory transactions.

Tracks all changes to inventory including adds, removes, transfers, crafts,
and consumption. Provides complete history for auditing and reporting.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Numeric, ForeignKey, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.location import Location
    from app.models.user import User


# Transaction types for item history
TRANSACTION_TYPES = [
    "add",  # Items added to inventory
    "remove",  # Items removed from inventory
    "transfer",  # Items transferred between locations
    "craft",  # Items produced by crafting
    "consume",  # Items consumed in crafting or other operations
]


class ItemHistory(Base, UUIDPrimaryKeyMixin):
    """
    ItemHistory model for inventory transaction audit trail.

    Records every change to inventory with:
    - quantity_change: Amount changed (positive for additions, negative for removals)
    - transaction_type: Type of transaction (add, remove, transfer, craft, consume)
    - related_craft_id: Link to craft if this change was part of a craft (nullable)
    - performed_by: User who performed the action
    - notes: Optional notes about the transaction

    This table provides complete auditability and can be used for:
    - Transaction history per item/location
    - Reporting and analytics
    - Debugging inventory discrepancies
    - User activity tracking

    **Data Retention:**
    By default, records older than 30 days are automatically cleaned up to prevent
    unbounded table growth. Use the `cleanup_old_item_history()` database function
    or the `scripts/cleanup_item_history.py` script to manually clean up old records.

    **Future Enhancement:**
    Plans exist to aggregate old data into compressed statistics/trends before deletion,
    preserving analytical value while reducing storage requirements. This will be
    implemented after the current scope is complete.

    Note: related_craft_id foreign key will be added in Phase 3 when crafts table exists.
    """

    __tablename__ = "item_history"
    __table_args__ = (
        Index("ix_item_history_item_id", "item_id"),
        Index("ix_item_history_location_id", "location_id"),
        Index("ix_item_history_transaction_type", "transaction_type"),
        Index("ix_item_history_performed_by", "performed_by"),
        Index("ix_item_history_timestamp", "timestamp"),
        {"comment": "Audit trail of all inventory transactions and changes"},
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

    quantity_change: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=False,
        comment="Quantity change (positive for additions, negative for removals)",
    )

    transaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Transaction type: add, remove, transfer, craft, consume",
    )

    related_craft_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        comment="Reference to related craft (if applicable, nullable) - FK to be added in Phase 3",
    )

    performed_by: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the user who performed the transaction",
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the transaction occurred",
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional notes about the transaction",
    )

    # Relationships
    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="history",
    )

    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="history",
    )

    performer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[performed_by],
    )

    def __repr__(self) -> str:
        return (
            f"<ItemHistory(id={self.id!r}, item_id={self.item_id!r}, "
            f"location_id={self.location_id!r}, transaction_type={self.transaction_type!r}, "
            f"quantity_change={self.quantity_change!r})>"
        )
