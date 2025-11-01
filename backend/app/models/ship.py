"""
Ship model representing ships owned by users or organizations.

Ships can be moved between locations and contain their own cargo grid
location for inventory storage. This enables tracking items stored in
ship cargo as well as ship positioning in the universe.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Any
from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.location import Location


class Ship(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Ship model for ship tracking.

    Ships represent player/organization owned vessels:
    - Can be owned by users or organizations
    - Have a current location (where they're parked/stationed)
    - Contain a cargo grid location for storing items
    - Can be moved between locations (current_location_id is updatable)

    Features:
    - current_location_id: Nullable to support ships in transit
    - cargo_location_id: Required location representing the ship's cargo grid
    - metadata: JSONB for ship-specific data (cargo capacity, modules, etc.)
    - Automatic updated_at tracking for movement/changes

    Design:
    - The cargo_location is a Location with owner_type='ship' and owner_id=ships.id
    - When a ship is created, the cargo location should be created first
    - Ships can be moved by updating current_location_id
    - The cargo_location_id is immutable (use RESTRICT to prevent accidental deletion)

    Future considerations:
    - Ship status (in_flight, docked, damaged, etc.)
    - Ship modules/components tracking
    - Ship-to-ship transfers
    - Ship insurance/replacement tracking
    """

    __tablename__ = "ships"
    __table_args__ = (
        Index("ix_ships_name", "name"),
        Index("ix_ships_ship_type", "ship_type"),
        Index("ix_ships_owner", "owner_type", "owner_id"),
        Index("ix_ships_current_location", "current_location_id"),
        Index("ix_ships_cargo_location", "cargo_location_id", unique=True),
        {"comment": "Ships owned by users or organizations, movable between locations"},
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Ship name",
    )

    ship_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Ship type/model (e.g., Constellation, Freelancer)",
    )

    owner_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Owner type: user, organization",
    )

    owner_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        comment="Reference to the owner (user or organization)",
    )

    current_location_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        comment="Current location where the ship is parked/stationed (nullable when ship is in transit)",
    )

    cargo_location_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Location representing the ship cargo grid",
    )

    meta: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Ship-specific data (JSON: cargo capacity, modules, etc.)",
    )

    # Relationships
    current_location: Mapped[Optional["Location"]] = relationship(
        "Location",
        foreign_keys=[current_location_id],
        back_populates="ships_at_location",
    )

    cargo_location: Mapped["Location"] = relationship(
        "Location",
        foreign_keys=[cargo_location_id],
        back_populates="ship",
    )

    def __repr__(self) -> str:
        return (
            f"<Ship(id={self.id!r}, name={self.name!r}, "
            f"ship_type={self.ship_type!r}, owner_type={self.owner_type!r})>"
        )
