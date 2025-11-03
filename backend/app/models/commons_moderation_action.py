"""
CommonsModerationAction model for logging moderation actions on submissions.
"""

from __future__ import annotations

from typing import Optional, Any, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Text, Index, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.commons_submission import CommonsSubmission


class CommonsModerationAction(Base, UUIDPrimaryKeyMixin):
    """
    CommonsModerationAction model for logging moderation actions.

    Tracks all actions taken by moderators on submissions, including
    approvals, rejections, change requests, merges, and edits.
    """

    __tablename__ = "commons_moderation_actions"
    __table_args__ = (
        Index("ix_commons_moderation_actions_submission_id", "submission_id"),
        Index("ix_commons_moderation_actions_moderator_id", "moderator_id"),
        Index("ix_commons_moderation_actions_action", "action"),
        {"comment": "Log of moderation actions on submissions"},
    )

    submission_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("commons_submissions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the submission",
    )

    moderator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="User who performed the moderation action",
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of action (approve, reject, request_changes, merge, edit)",
    )

    action_payload: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Action-specific data (diffs/merge mapping)",
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Notes about the action",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the action was performed",
    )

    # Relationships
    submission: Mapped["CommonsSubmission"] = relationship(
        "CommonsSubmission",
        foreign_keys=[submission_id],
        back_populates="moderation_actions",
    )
    moderator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[moderator_id],
    )

    def __repr__(self) -> str:
        return (
            f"<CommonsModerationAction(id={self.id!r}, submission_id={self.submission_id!r}, "
            f"action={self.action!r}, moderator_id={self.moderator_id!r})>"
        )
