"""
Item model representing the item catalog/master data.

Items are the definitions/master data for inventory items. Actual stock
quantities are tracked in ItemStock, which links items to locations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING, Any
from sqlalchemy import String, Text, Index, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.item_stock import ItemStock
    from app.models.item_history import ItemHistory
    from app.models.resource_source import ResourceSource


class Item(Base, UUIDPrimaryKeyMixin):
    """
    Item model for the item catalog.

    Items represent master data/definitions for inventory items:
    - Name, description, category, subcategory, rarity
    - JSONB metadata for game-specific attributes
    - Links to stock levels (ItemStock) and history (ItemHistory)

    This is separate from stock levels to allow:
    - Multiple locations to have the same item
    - Item definitions to exist without stock
    - Efficient catalog browsing and search

    Future considerations:
    - Item images/icons
    - Item variants
    - Public/private items
    - Item templates for blueprints
    """

    __tablename__ = "items"
    __table_args__ = (
        Index("ix_items_name", "name"),
        Index("ix_items_category", "category"),
        Index("ix_items_subcategory", "subcategory"),
        Index("ix_items_rarity", "rarity"),
        {"comment": "Item catalog (definitions/master data)"},
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Item name",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Item description",
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Item category",
    )

    subcategory: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Item subcategory",
    )

    rarity: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Item rarity level",
    )

    meta: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Game-specific attributes (JSON)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the record was created",
    )

    # Relationships
    stocks: Mapped[list["ItemStock"]] = relationship(
        "ItemStock",
        back_populates="item",
        cascade="all, delete-orphan",
    )

    history: Mapped[list["ItemHistory"]] = relationship(
        "ItemHistory",
        back_populates="item",
        cascade="all, delete-orphan",
    )

    resource_sources: Mapped[list["ResourceSource"]] = relationship(
        "ResourceSource",
        back_populates="item",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Item(id={self.id!r}, name={self.name!r}, "
            f"category={self.category!r}, rarity={self.rarity!r})>"
        )
