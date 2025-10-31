"""
Organization model representing groups of users.

Organizations allow multiple users to collaborate on inventory management.
This model is designed to support future features like billing, plans, and
organizational settings.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization_member import OrganizationMember


class Organization(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Organization model for user groups/teams.

    Organizations enable collaborative inventory management:
    - name: Required organization name
    - description: Optional description
    - slug: Optional URL-friendly identifier (for future public pages)

    Future considerations:
    - Billing and subscription plans
    - Organization settings (theme, branding)
    - Limits (max users, storage, etc.)
    - Public/private organization visibility
    - Organization-level integrations
    """

    __tablename__ = "organizations"
    __table_args__ = (
        Index("ix_organizations_name", "name"),
        Index("ix_organizations_slug", "slug", unique=True),
        {"comment": "Organizations (teams/groups) for collaborative inventory management"},
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Organization name",
    )

    slug: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
        comment="URL-friendly identifier (optional, for future public pages)",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Organization description",
    )

    # Relationships
    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id!r}, name={self.name!r}, slug={self.slug!r})>"
