"""
Location model representing storage locations.

Locations can be stations, ships (as cargo grids), player inventories, warehouses,
or other storage locations. They support hierarchical nesting (parent locations)
and flexible ownership (user, organization, or ship).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING, Any
from sqlalchemy import String, ForeignKey, Index, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.item_stock import ItemStock
    from app.models.item_history import ItemHistory
    from app.models.ship import Ship
    from app.models.user import User


class Location(Base, UUIDPrimaryKeyMixin):
    """
    Location model for storage locations.

    Locations can represent:
    - Stations (fixed locations in the universe)
    - Ship cargo grids (owned by ships)
    - Player inventories (owned by users)
    - Warehouses (owned by organizations)
    - Other storage types

    Features:
    - Hierarchical nesting via parent_location_id
    - Flexible ownership (user, organization, or ship)
    - JSONB metadata for location-specific data

    Future considerations:
    - Location capacity limits
    - Access control per location
    - Location visibility (public/private)
    """

    __tablename__ = "locations"
    __table_args__ = (
        Index("ix_locations_name", "name"),
        Index("ix_locations_type", "type"),
        Index("ix_locations_owner", "owner_type", "owner_id"),
        Index("ix_locations_parent", "parent_location_id"),
        Index("ix_locations_is_canonical", "is_canonical"),
        Index("ix_locations_canonical_location_id", "canonical_location_id"),
        Index("ix_locations_created_by", "created_by"),
        {"comment": "Storage locations (stations, ships, player inventories, warehouses)"},
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Location name",
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Location type: station, ship, player_inventory, warehouse",
    )

    owner_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Owner type: user, organization, ship",
    )

    owner_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        comment="Reference to the owner (user, organization, or ship)",
    )

    parent_location_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        comment="Parent location for nested locations (optional)",
    )

    is_canonical: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="Whether this is a canonical/public location that many players reference",
    )

    canonical_location_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        comment="Reference to canonical location (for player locations that are at a canonical location)",
    )

    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created this canonical location (nullable for user-owned locations)",
    )

    meta: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Flexible location-specific data (JSON)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the record was created",
    )

    # Relationships
    parent_location: Mapped[Optional["Location"]] = relationship(
        "Location",
        remote_side="Location.id",
        back_populates="child_locations",
        foreign_keys=[parent_location_id],
    )

    child_locations: Mapped[list["Location"]] = relationship(
        "Location",
        remote_side="Location.parent_location_id",
        back_populates="parent_location",
        foreign_keys="Location.parent_location_id",
    )

    stocks: Mapped[list["ItemStock"]] = relationship(
        "ItemStock",
        back_populates="location",
        cascade="all, delete-orphan",
    )

    history: Mapped[list["ItemHistory"]] = relationship(
        "ItemHistory",
        back_populates="location",
        cascade="all, delete-orphan",
    )

    # Ship relationship (if this location is a ship's cargo grid)
    ship: Mapped[Optional["Ship"]] = relationship(
        "Ship",
        back_populates="cargo_location",
        foreign_keys="Ship.cargo_location_id",
        uselist=False,
    )

    # Ships that are currently at this location
    ships_at_location: Mapped[list["Ship"]] = relationship(
        "Ship",
        back_populates="current_location",
        foreign_keys="Ship.current_location_id",
    )

    # Canonical location relationship (for player locations)
    canonical_location: Mapped[Optional["Location"]] = relationship(
        "Location",
        remote_side="Location.id",
        foreign_keys=[canonical_location_id],
        post_update=True,
    )

    # Locations that reference this as canonical (reverse relationship)
    locations_at_canonical: Mapped[list["Location"]] = relationship(
        "Location",
        foreign_keys="Location.canonical_location_id",
        post_update=True,
        overlaps="canonical_location",
    )

    # Creator relationship (for canonical locations)
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
    )

    def __repr__(self) -> str:
        return (
            f"<Location(id={self.id!r}, name={self.name!r}, "
            f"type={self.type!r}, owner_type={self.owner_type!r})>"
        )
