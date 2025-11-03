"""
DuplicateGroup model for grouping entities identified as potential duplicates.
"""

from __future__ import annotations

from typing import Any
from datetime import datetime
from sqlalchemy import String, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin


class DuplicateGroup(Base, UUIDPrimaryKeyMixin):
    """
    DuplicateGroup model for grouping potential duplicates.

    Used by duplicate detection algorithms to group entities that may
    be duplicates of each other for review and merging.
    """

    __tablename__ = "duplicate_groups"
    __table_args__ = (
        Index("ix_duplicate_groups_entity_type", "entity_type"),
        Index("ix_duplicate_groups_group_key", "group_key"),
        {"comment": "Groups of entities identified as potential duplicates"},
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of entity (item, blueprint, location)",
    )

    group_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Heuristic key for grouping duplicates",
    )

    members: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        comment="List of IDs considered duplicates (JSON array)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the group was created",
    )

    def __repr__(self) -> str:
        return (
            f"<DuplicateGroup(id={self.id!r}, entity_type={self.entity_type!r}, "
            f"group_key={self.group_key!r})>"
        )
