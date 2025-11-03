"""
Tag model for categorizing commons entities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Text, Index, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.commons_entity_tag import CommonsEntityTag


class Tag(Base, UUIDPrimaryKeyMixin):
    """
    Tag model for categorizing commons entities.

    Tags are used to organize and search commons entities.
    """

    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("name", name="uq_tags_name"),
        Index("ix_tags_name", "name"),
        {"comment": "Tags for categorizing commons entities"},
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Tag name (unique)",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Tag description",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the tag was created",
    )

    # Relationships
    commons_entity_tags: Mapped[list["CommonsEntityTag"]] = relationship(
        "CommonsEntityTag",
        back_populates="tag",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id!r}, name={self.name!r})>"
