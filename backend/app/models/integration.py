"""
Integration model for external integrations.

Tracks webhooks, API integrations, and other external service connections.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization
    from app.models.integration_log import IntegrationLog


class Integration(Base, UUIDPrimaryKeyMixin):
    """
    Integration model for external service connections.

    Supports:
    - Webhook integrations (for receiving events)
    - API integrations (for sending/receiving data)
    - Custom integrations (via config_data)

    Security:
    - API keys and secrets are encrypted at rest
    - Only the integration owner can view/update credentials
    """

    __tablename__ = "integrations"
    __table_args__ = (
        Index("ix_integrations_user_id", "user_id"),
        Index("ix_integrations_organization_id", "organization_id"),
        Index("ix_integrations_type", "type"),
        Index("ix_integrations_status", "status"),
        {"comment": "External integrations configuration (webhooks, APIs, etc.)"},
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Integration name",
    )

    type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Integration type (webhook, api, etc.)",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="active",
        comment="Integration status (active, inactive, error)",
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who created this integration",
    )

    organization_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        comment="Organization this integration belongs to (nullable)",
    )

    webhook_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Webhook URL for receiving events",
    )

    api_key_encrypted: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Encrypted API key (if applicable)",
    )

    api_secret_encrypted: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Encrypted API secret (if applicable)",
    )

    config_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional configuration data (JSON)",
    )

    last_tested_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last successful test timestamp",
    )

    last_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Last error message (if status is error)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the record was created",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the record was last updated",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
    )

    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    logs: Mapped[list["IntegrationLog"]] = relationship(
        "IntegrationLog",
        back_populates="integration",
        cascade="all, delete-orphan",
        order_by="IntegrationLog.timestamp.desc()",
    )

    def __repr__(self) -> str:
        return (
            f"<Integration(id={self.id!r}, name={self.name!r}, "
            f"type={self.type!r}, status={self.status!r})>"
        )
