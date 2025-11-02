"""
Source Verification Log model.

Logs verification attempts for resource sources to track reliability.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.resource_source import ResourceSource
    from app.models.user import User


class SourceVerificationLog(Base, UUIDPrimaryKeyMixin):
    """
    Source verification log model.

    Tracks when users verify resource sources and whether the information was accurate.
    """

    __tablename__ = "source_verification_log"

    source_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("resource_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the resource source",
    )

    verified_by: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who performed the verification",
    )

    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Timestamp when verification was performed",
    )

    was_accurate: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        index=True,
        comment="Whether the source information was accurate",
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional notes about the verification",
    )

    # Relationships
    source: Mapped["ResourceSource"] = relationship(
        "ResourceSource", back_populates="verification_logs"
    )
    verifier: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<SourceVerificationLog(id={self.id!r}, source_id={self.source_id!r}, "
            f"was_accurate={self.was_accurate})>"
        )
