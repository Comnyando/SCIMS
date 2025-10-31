"""
Pydantic schemas for OrganizationMember model validation.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.user import UserResponse
from app.schemas.organization import OrganizationResponse


class OrganizationMemberBase(BaseModel):
    """Base organization member schema."""

    role: Literal["owner", "admin", "member", "viewer"] = Field(
        default="member",
        description="User role in the organization",
    )


class OrganizationMemberCreate(OrganizationMemberBase):
    """Schema for creating a new organization membership."""

    user_id: str = Field(..., description="User UUID to add to the organization")
    organization_id: str = Field(..., description="Organization UUID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "organization_id": "660e8400-e29b-41d4-a716-446655440000",
                "role": "admin",
            }
        }
    )


class OrganizationMemberResponse(OrganizationMemberBase):
    """Schema for organization member API responses."""

    id: str = Field(..., description="Membership UUID")
    user_id: str = Field(..., description="User UUID")
    organization_id: str = Field(..., description="Organization UUID")
    joined_at: datetime = Field(..., description="Timestamp when user joined")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "organization_id": "660e8400-e29b-41d4-a716-446655440000",
                "role": "admin",
                "joined_at": "2024-01-01T00:00:00Z",
            }
        },
    )


class OrganizationMemberWithDetails(OrganizationMemberResponse):
    """Schema for organization member with nested user and organization details."""

    user: UserResponse = Field(..., description="User details")
    organization: OrganizationResponse = Field(..., description="Organization details")

    model_config = ConfigDict(
        from_attributes=True,
    )
