"""
CommonsSubmission model for user submissions to the public commons.
"""

from __future__ import annotations

from typing import Optional, Any, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Text, Index, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.commons_moderation_action import CommonsModerationAction


class CommonsSubmission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    CommonsSubmission model for user submissions to the public commons.

    Users can submit items, blueprints, locations, etc. for inclusion in the
    public commons. Submissions go through a moderation workflow.
    """

    __tablename__ = "commons_submissions"
    __table_args__ = (
        Index("ix_commons_submissions_submitter_id", "submitter_id"),
        Index("ix_commons_submissions_entity_type", "entity_type"),
        Index("ix_commons_submissions_status", "status"),
        Index(
            "ix_commons_submissions_status_created_at",
            "status",
            "created_at",
        ),
        {"comment": "User submissions to the public commons"},
    )

    submitter_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who submitted this entry",
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of entity (item, blueprint, location, ingredient, taxonomy)",
    )

    entity_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Normalized shape for proposed entity or update (JSON)",
    )

    source_reference: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL or notes about the source",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="pending",
        comment="Submission status (pending, approved, rejected, needs_changes, merged)",
    )

    review_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Notes from moderator review",
    )

    # Relationships
    submitter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[submitter_id],
    )
    moderation_actions: Mapped[list["CommonsModerationAction"]] = relationship(
        "CommonsModerationAction",
        back_populates="submission",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<CommonsSubmission(id={self.id!r}, entity_type={self.entity_type!r}, "
            f"status={self.status!r}, submitter_id={self.submitter_id!r})>"
        )
