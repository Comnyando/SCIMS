"""
Pydantic schemas for Canonical Location management.

Canonical locations are public locations that many players reference,
such as game stations, planets, or major landmarks.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class CanonicalLocationBase(BaseModel):
    """Base canonical location schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Canonical location name")
    type: str = Field(
        ..., max_length=50, description="Location type: station, ship, player_inventory, warehouse"
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate location type."""
        valid_types = {"station", "ship", "player_inventory", "warehouse"}
        if v not in valid_types:
            raise ValueError(f"Location type must be one of: {', '.join(valid_types)}")
        return v


class CanonicalLocationCreate(CanonicalLocationBase):
    """Schema for creating a new canonical location."""

    parent_location_id: Optional[str] = Field(
        None, description="Parent canonical location UUID for nested locations"
    )
    metadata: Optional[dict[str, Any]] = Field(
        None,
        description="Flexible location-specific data (JSON). Can include description, planet, system, etc.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "New Babbage Landing Zone",
                "type": "station",
                "parent_location_id": None,
                "metadata": {
                    "description": "Main landing zone on microTech",
                    "planet": "microTech",
                    "system": "Stanton",
                    "landing_pads": 8,
                },
            }
        }
    )


class CanonicalLocationUpdate(BaseModel):
    """Schema for updating canonical location information."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Canonical location name"
    )
    parent_location_id: Optional[str] = Field(None, description="Parent canonical location UUID")
    metadata: Optional[dict[str, Any]] = Field(
        None, description="Flexible location-specific data (JSON)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metadata": {"description": "Updated description", "updated": True},
            }
        }
    )


class CanonicalLocationResponse(CanonicalLocationBase):
    """Schema for canonical location API responses."""

    id: str = Field(..., description="Canonical location UUID")
    parent_location_id: Optional[str] = Field(None, description="Parent canonical location UUID")
    is_canonical: bool = Field(
        True, description="Whether this is a canonical location (always True)"
    )
    metadata: Optional[dict[str, Any]] = Field(
        None,
        alias="meta",
        description="Flexible location-specific data (JSON)",
        serialization_alias="metadata",
    )
    created_by: Optional[str] = Field(
        None, description="User UUID who created this canonical location"
    )
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "New Babbage Landing Zone",
                "type": "station",
                "parent_location_id": None,
                "metadata": {
                    "description": "Main landing zone on microTech",
                    "planet": "microTech",
                    "system": "Stanton",
                },
                "created_by": "550e8400-e29b-41d4-a716-446655440001",
                "created_at": "2024-01-01T00:00:00Z",
            }
        },
    )
