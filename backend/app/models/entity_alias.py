"""
EntityAlias model for alternative names/aliases for entities.
"""

from __future__ import annotations

from sqlalchemy import String, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class EntityAlias(Base, UUIDPrimaryKeyMixin):
    """
    EntityAlias model for alternative names/aliases.

    Maps alternative names to canonical entity IDs (items, blueprints, locations).
    Used for search and duplicate detection.
    """

    __tablename__ = "entity_aliases"
    __table_args__ = (
        UniqueConstraint(
            "entity_type", "canonical_id", "alias", name="uq_entity_aliases_type_id_alias"
        ),
        Index("ix_entity_aliases_entity_type", "entity_type"),
        Index("ix_entity_aliases_canonical_id", "canonical_id"),
        Index("ix_entity_aliases_entity_type_alias", "entity_type", "alias"),
        {"comment": "Alternative names/aliases for entities"},
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of entity (item, blueprint, location)",
    )

    canonical_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        comment="Reference to items.id/blueprints.id/locations.id",
    )

    alias: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Alternative name or alias",
    )

    def __repr__(self) -> str:
        return (
            f"<EntityAlias(id={self.id!r}, entity_type={self.entity_type!r}, "
            f"canonical_id={self.canonical_id!r}, alias={self.alias!r})>"
        )
