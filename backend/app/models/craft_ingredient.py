"""
CraftIngredient model representing individual ingredients for a craft operation.

Tracks ingredient requirements, sourcing, and fulfillment status for each craft.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.craft import Craft
    from app.models.item import Item
    from app.models.location import Location


# Ingredient source types
SOURCE_TYPE_STOCK = "stock"
SOURCE_TYPE_PLAYER = "player"
SOURCE_TYPE_UNIVERSE = "universe"

SOURCE_TYPES = [SOURCE_TYPE_STOCK, SOURCE_TYPE_PLAYER, SOURCE_TYPE_UNIVERSE]

# Ingredient statuses
INGREDIENT_STATUS_PENDING = "pending"
INGREDIENT_STATUS_RESERVED = "reserved"
INGREDIENT_STATUS_FULFILLED = "fulfilled"

INGREDIENT_STATUSES = [
    INGREDIENT_STATUS_PENDING,
    INGREDIENT_STATUS_RESERVED,
    INGREDIENT_STATUS_FULFILLED,
]


class CraftIngredient(Base, UUIDPrimaryKeyMixin):
    """
    CraftIngredient model for tracking individual ingredients in a craft.

    Each craft has multiple ingredients, each tracked separately:
    - Links to a craft and an item
    - Tracks required quantity
    - Identifies source location and source type
    - Tracks fulfillment status

    Status Flow:
    - pending: Ingredient requirement identified but not yet reserved
    - reserved: Quantity reserved in stock (for stock sources)
    - fulfilled: Ingredient requirement met, ready for craft

    Source Types:
    - stock: Ingredient comes from existing inventory stock
    - player: Ingredient will be provided by a player
    - universe: Ingredient needs to be acquired from in-game universe

    Unique constraint ensures each item appears only once per craft.
    """

    __tablename__ = "craft_ingredients"
    __table_args__ = (
        UniqueConstraint("craft_id", "item_id", name="uq_craft_ingredient_craft_item"),
        Index("ix_craft_ingredients_craft_id", "craft_id"),
        Index("ix_craft_ingredients_item_id", "item_id"),
        Index("ix_craft_ingredients_status", "status"),
        {"comment": "Individual ingredients for each craft operation"},
    )

    craft_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("crafts.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the craft",
    )

    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Reference to the ingredient item",
    )

    required_quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=False,
        comment="Required quantity of this ingredient",
    )

    source_location_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        comment="Location where ingredient will be sourced from (nullable)",
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=SOURCE_TYPE_STOCK,
        server_default=SOURCE_TYPE_STOCK,
        comment="Source type: stock, player, universe",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=INGREDIENT_STATUS_PENDING,
        server_default=INGREDIENT_STATUS_PENDING,
        comment="Ingredient status: pending, reserved, fulfilled",
    )

    # Relationships
    craft: Mapped["Craft"] = relationship(
        "Craft",
        foreign_keys=[craft_id],
        back_populates="ingredients",
    )

    item: Mapped["Item"] = relationship(
        "Item",
        foreign_keys=[item_id],
    )

    source_location: Mapped[Optional["Location"]] = relationship(
        "Location",
        foreign_keys=[source_location_id],
    )

    def __repr__(self) -> str:
        return (
            f"<CraftIngredient(id={self.id!r}, craft_id={self.craft_id!r}, "
            f"item_id={self.item_id!r}, status={self.status!r}, "
            f"required_quantity={self.required_quantity!r})>"
        )
