"""
IntegrationLog model for tracking integration events.

Logs webhook calls, API interactions, test results, and errors.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.integration import Integration


class IntegrationLog(Base, UUIDPrimaryKeyMixin):
    """
    IntegrationLog model for tracking integration events.

    Logs include:
    - Webhook calls (incoming and outgoing)
    - API test results
    - Error messages and stack traces
    - Execution metrics (timing, response codes, etc.)
    """

    __tablename__ = "integration_logs"
    __table_args__ = (
        Index("ix_integration_logs_integration_id", "integration_id"),
        Index("ix_integration_logs_event_type", "event_type"),
        Index("ix_integration_logs_status", "status"),
        Index("ix_integration_logs_timestamp", "timestamp"),
        {"comment": "Logs of integration events and webhook calls"},
    )

    integration_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("integrations.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the integration",
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Type of event (test, webhook_received, webhook_sent, error, etc.)",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Log status (success, error, pending)",
    )

    request_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Request data (JSON)",
    )

    response_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Response data (JSON)",
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message (if status is error)",
    )

    execution_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Execution time in milliseconds",
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp of the log entry",
    )

    # Relationships
    integration: Mapped["Integration"] = relationship(
        "Integration",
        foreign_keys=[integration_id],
        back_populates="logs",
    )

    def __repr__(self) -> str:
        return (
            f"<IntegrationLog(id={self.id!r}, integration_id={self.integration_id!r}, "
            f"event_type={self.event_type!r}, status={self.status!r}, "
            f"timestamp={self.timestamp!r})>"
        )
