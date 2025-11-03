"""
CommonsEntity model for published entities in the public commons.
"""

from __future__ import annotations

from typing import Optional, Any, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Index, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.commons_entity_tag import CommonsEntityTag


class CommonsEntity(Base, UUIDPrimaryKeyMixin):
    """
    CommonsEntity model for published entities in the public commons.

    Represents versioned, immutable snapshots of published entities (items,
    blueprints, locations, etc.) that are available to the public.
    """

    __tablename__ = "commons_entities"
    __table_args__ = (
        Index("ix_commons_entities_entity_type", "entity_type"),
        Index("ix_commons_entities_is_public", "is_public"),
        Index("ix_commons_entities_canonical_id", "canonical_id"),
        Index(
            "ix_commons_entities_entity_type_is_public_version",
            "entity_type",
            "is_public",
            "version",
        ),
        {"comment": "Published entities in the public commons"},
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of entity (item, blueprint, location, ingredient, taxonomy)",
    )

    canonical_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        comment="Reference to items.id/blueprints.id/locations.id when applicable",
    )

    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Denormalized public representation (immutable snapshot per version)",
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
        comment="Version number of this entity",
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        comment="Whether this entity is publicly visible",
    )

    created_by: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="User who created this entity",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the entity was created",
    )

    superseded_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("commons_entities.id", ondelete="SET NULL"),
        nullable=True,
        comment="Reference to the entity that superseded this one",
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )
    tags: Mapped[list["CommonsEntityTag"]] = relationship(
        "CommonsEntityTag",
        back_populates="commons_entity",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<CommonsEntity(id={self.id!r}, entity_type={self.entity_type!r}, "
            f"version={self.version!r}, is_public={self.is_public!r})>"
        )
