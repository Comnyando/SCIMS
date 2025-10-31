"""
Pydantic schemas for Organization model validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class OrganizationBase(BaseModel):
    """Base organization schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    slug: Optional[str] = Field(None, max_length=100, description="URL-friendly identifier")
    description: Optional[str] = Field(None, description="Organization description")


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "My Organization",
                "slug": "my-org",
                "description": "A great organization for inventory management",
            }
        }
    )


class OrganizationUpdate(BaseModel):
    """Schema for updating organization information."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Organization name")
    slug: Optional[str] = Field(None, max_length=100, description="URL-friendly identifier")
    description: Optional[str] = Field(None, description="Organization description")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Organization Name",
                "description": "Updated description",
            }
        }
    )


class OrganizationResponse(OrganizationBase):
    """Schema for organization API responses."""

    id: str = Field(..., description="Organization UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "My Organization",
                "slug": "my-org",
                "description": "A great organization",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        },
    )
