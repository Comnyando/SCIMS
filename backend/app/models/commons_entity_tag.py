"""
CommonsEntityTag model for many-to-many relationship between commons entities and tags.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import Index, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.commons_entity import CommonsEntity
    from app.models.tag import Tag


class CommonsEntityTag(Base, UUIDPrimaryKeyMixin):
    """
    CommonsEntityTag model for tagging commons entities.

    Many-to-many relationship between commons entities and tags.
    """

    __tablename__ = "commons_entity_tags"
    __table_args__ = (
        UniqueConstraint("commons_entity_id", "tag_id", name="uq_commons_entity_tags_entity_tag"),
        Index("ix_commons_entity_tags_commons_entity_id", "commons_entity_id"),
        Index("ix_commons_entity_tags_tag_id", "tag_id"),
        {"comment": "Many-to-many relationship between commons entities and tags"},
    )

    commons_entity_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("commons_entities.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the commons entity",
    )

    tag_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the tag",
    )

    # Relationships
    commons_entity: Mapped["CommonsEntity"] = relationship(
        "CommonsEntity",
        foreign_keys=[commons_entity_id],
        back_populates="tags",
    )
    tag: Mapped["Tag"] = relationship(
        "Tag",
        foreign_keys=[tag_id],
        back_populates="commons_entity_tags",
    )

    def __repr__(self) -> str:
        return (
            f"<CommonsEntityTag(id={self.id!r}, commons_entity_id={self.commons_entity_id!r}, "
            f"tag_id={self.tag_id!r})>"
        )
