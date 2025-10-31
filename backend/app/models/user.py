"""
User model representing system users.

This model stores user account information including authentication details
and profile data. Designed to be flexible for future authentication providers
and additional profile fields.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization_member import OrganizationMember


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User model for system accounts.

    Fields are designed to be flexible and extensible:
    - email: Used for authentication and communication
    - username: Optional display name (can be added later)
    - hashed_password: Bcrypt/Argon2 hashed password (nullable for OAuth users)
    - is_active: Soft delete flag
    - is_verified: Email verification status

    Future considerations:
    - OAuth provider integration (google_id, discord_id, etc.)
    - Profile fields (avatar_url, bio, etc.)
    - Preferences (theme, notifications, etc.)
    - Last login tracking
    """

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        {"comment": "User accounts and authentication data"},
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address (unique, used for login)",
    )

    username: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
        comment="Optional username for display",
    )

    hashed_password: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Bcrypt/Argon2 hashed password (nullable for OAuth users)",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the user account is active",
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user email has been verified",
    )

    # Relationships
    organizations: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id!r}, email={self.email!r}, username={self.username!r})>"
