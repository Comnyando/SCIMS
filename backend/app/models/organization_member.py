"""
OrganizationMember model representing the many-to-many relationship
between Users and Organizations.

This junction table stores membership information including roles and
timestamps. Designed to support flexible role hierarchies and permissions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization


# Valid roles for organization members
# This can be extended in the future without migration if we use an enum
# For now, using a string allows flexibility
VALID_ROLES = ["owner", "admin", "member", "viewer"]


class OrganizationMember(Base, UUIDPrimaryKeyMixin):
    """
    Organization membership junction table.

    Links users to organizations with role-based access:
    - organization_id: Foreign key to organizations table
    - user_id: Foreign key to users table
    - role: User's role in the organization (owner, admin, member, viewer)
    - joined_at: When the user joined the organization

    Constraints:
    - Unique constraint on (organization_id, user_id) prevents duplicate memberships
    - Foreign keys ensure referential integrity

    Future considerations:
    - Role hierarchy system
    - Custom permissions per role
    - Invitation system (pending status)
    - Member metadata (notes, tags)
    """

    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member_user_org"),
        Index("ix_organization_members_org_id", "organization_id"),
        Index("ix_organization_members_user_id", "user_id"),
        Index("ix_organization_members_role", "role"),
        {"comment": "Many-to-many relationship between users and organizations"},
    )

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the organization",
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the user",
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="member",
        comment="User role in the organization (owner, admin, member, viewer)",
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the user joined the organization",
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="members",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="organizations",
    )

    def __repr__(self) -> str:
        return (
            f"<OrganizationMember(id={self.id!r}, "
            f"organization_id={self.organization_id!r}, "
            f"user_id={self.user_id!r}, role={self.role!r})>"
        )
