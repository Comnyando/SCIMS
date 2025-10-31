"""
Base model class with common fields and functionality.

This module provides a base class for all database models, ensuring
consistent patterns for timestamps, UUIDs, and other common fields.
This makes future schema changes easier to manage.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base class for all database models.

    Provides common fields and functionality that all models share:
    - UUID primary keys
    - Timestamps (created_at, updated_at)
    - Flexible structure for future additions
    """

    pass


class TimestampMixin:
    """
    Mixin class providing created_at and updated_at timestamp fields.

    These fields are automatically managed:
    - created_at: Set when the record is first created
    - updated_at: Automatically updated on each save (via database trigger or ORM)
    """

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


class UUIDPrimaryKeyMixin:
    """
    Mixin class providing a UUID primary key field.

    Uses PostgreSQL's UUID type for efficient storage and indexing.
    """

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),  # Store as string for JSON serialization compatibility
        primary_key=True,
        default=lambda: str(uuid4()),
        nullable=False,
        comment="Unique identifier (UUID)",
    )
