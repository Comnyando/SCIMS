"""
Resource Source model.

Represents a source where items can be obtained (player stock, universe location, trading post).
"""

from decimal import Decimal
from typing import Optional, TYPE_CHECKING, Any
from datetime import datetime
from sqlalchemy import String, ForeignKey, Numeric, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.location import Location
    from app.models.source_verification_log import SourceVerificationLog


# Source type constants
SOURCE_TYPE_PLAYER_STOCK = "player_stock"
SOURCE_TYPE_UNIVERSE_LOCATION = "universe_location"
SOURCE_TYPE_TRADING_POST = "trading_post"

SOURCE_TYPES = [
    SOURCE_TYPE_PLAYER_STOCK,
    SOURCE_TYPE_UNIVERSE_LOCATION,
    SOURCE_TYPE_TRADING_POST,
]


class ResourceSource(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Resource source model.

    Tracks where items can be obtained, including availability, cost, and reliability.
    """

    __tablename__ = "resource_sources"

    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Reference to the item this source provides",
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Source type: player_stock, universe_location, trading_post",
    )

    source_identifier: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Identifier for the source (player_id, location_name, etc.)",
    )

    available_quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=False,
        server_default="0",
        comment="Available quantity at this source",
    )

    cost_per_unit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=True,
        comment="Cost per unit (nullable, for trading posts or player trades)",
    )

    last_verified: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Last time this source was verified",
    )

    reliability_score: Mapped[Decimal] = mapped_column(
        Numeric(precision=3, scale=2),
        nullable=False,
        server_default="0.5",
        index=True,
        comment="Reliability score (0-1) based on verification history",
    )

    source_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional source metadata (JSON)",
    )

    location_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Optional location where this source can be found (for universe locations, trading posts, etc.)",
    )

    # Relationships
    item: Mapped["Item"] = relationship("Item", back_populates="resource_sources")
    location: Mapped[Optional["Location"]] = relationship(
        "Location",
        foreign_keys=[location_id],
    )
    verification_logs: Mapped[list["SourceVerificationLog"]] = relationship(
        "SourceVerificationLog",
        back_populates="source",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ResourceSource(id={self.id!r}, item_id={self.item_id!r}, "
            f"source_type={self.source_type!r}, reliability={self.reliability_score})>"
        )
