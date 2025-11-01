"""
Pydantic schemas for Ship model validation.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ShipBase(BaseModel):
    """Base ship schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Ship name")
    ship_type: Optional[str] = Field(
        None, max_length=100, description="Ship type/model (e.g., Constellation, Freelancer)"
    )
    owner_type: str = Field(..., max_length=50, description="Owner type: user, organization")
    owner_id: str = Field(..., description="Reference to the owner (user or organization UUID)")
    current_location_id: Optional[str] = Field(
        None, description="Current location where the ship is parked (nullable when in transit)"
    )

    @field_validator("owner_type")
    @classmethod
    def validate_owner_type(cls, v: str) -> str:
        """Validate owner type."""
        valid_owner_types = {"user", "organization"}
        if v not in valid_owner_types:
            raise ValueError(f"Owner type must be one of: {', '.join(valid_owner_types)}")
        return v


class ShipCreate(ShipBase):
    """Schema for creating a new ship."""

    metadata: Optional[dict[str, Any]] = Field(
        None, description="Ship-specific data (JSON: cargo capacity, modules, etc.)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "My Constellation",
                "ship_type": "Constellation Andromeda",
                "owner_type": "user",
                "owner_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_location_id": "550e8400-e29b-41d4-a716-446655440001",
                "metadata": {"cargo_capacity": 96.0, "crew_size": 4},
            }
        }
    )


class ShipUpdate(BaseModel):
    """Schema for updating ship information."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Ship name")
    ship_type: Optional[str] = Field(None, max_length=100, description="Ship type/model")
    current_location_id: Optional[str] = Field(
        None, description="Current location where the ship is parked (nullable when in transit)"
    )
    metadata: Optional[dict[str, Any]] = Field(None, description="Ship-specific data (JSON)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Ship Name",
                "current_location_id": "550e8400-e29b-41d4-a716-446655440002",
                "metadata": {"status": "docked"},
            }
        }
    )


class ShipResponse(ShipBase):
    """Schema for ship API responses."""

    id: str = Field(..., description="Ship UUID")
    cargo_location_id: str = Field(
        ..., description="Location UUID representing the ship cargo grid"
    )
    metadata: Optional[dict[str, Any]] = Field(
        None,
        alias="meta",
        description="Ship-specific data (JSON)",
        serialization_alias="metadata",
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "My Constellation",
                "ship_type": "Constellation Andromeda",
                "owner_type": "user",
                "owner_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_location_id": "550e8400-e29b-41d4-a716-446655440001",
                "cargo_location_id": "550e8400-e29b-41d4-a716-446655440003",
                "metadata": {"cargo_capacity": 96.0, "crew_size": 4},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        },
    )
