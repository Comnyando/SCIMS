"""
Pydantic schemas for Location model validation.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class LocationBase(BaseModel):
    """Base location schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Location name")
    type: str = Field(
        ...,
        max_length=50,
        description="Location type: station, ship, player_inventory, warehouse, structure",
    )
    owner_type: str = Field(
        ..., max_length=50, description="Owner type: user, organization, ship, world, system"
    )
    owner_id: Optional[str] = Field(
        None,
        description="Reference to the owner (user, organization, or ship UUID). Optional for world-owned locations.",
    )
    parent_location_id: Optional[str] = Field(
        None, description="Parent location UUID for nested locations"
    )
    canonical_location_id: Optional[str] = Field(
        None,
        description="Reference to canonical location (for player locations at a canonical location)",
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate location type."""
        valid_types = {"station", "ship", "player_inventory", "warehouse", "structure"}
        if v not in valid_types:
            raise ValueError(f"Location type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("owner_type")
    @classmethod
    def validate_owner_type(cls, v: str) -> str:
        """Validate owner type."""
        valid_owner_types = {"user", "organization", "ship", "world", "system"}
        if v not in valid_owner_types:
            raise ValueError(f"Owner type must be one of: {', '.join(valid_owner_types)}")
        return v

    @model_validator(mode="after")
    def validate_owner_id(self) -> "LocationBase":
        """Validate owner_id is provided for non-world and non-system owner types."""
        if self.owner_type not in ("world", "system") and not self.owner_id:
            raise ValueError(f"owner_id is required when owner_type is '{self.owner_type}'")
        return self


class LocationCreate(LocationBase):
    """Schema for creating a new location."""

    metadata: Optional[dict[str, Any]] = Field(
        None, description="Flexible location-specific data (JSON)"
    )

    @field_validator("parent_location_id", "canonical_location_id")
    @classmethod
    def validate_optional_ids(cls, v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None for optional ID fields."""
        if v is not None and (not v or not v.strip()):
            return None
        return v.strip() if v else None

    @model_validator(mode="after")
    def validate_metadata(self):
        """Ensure metadata is None if empty dict."""
        if self.metadata is not None and not isinstance(self.metadata, dict):
            raise ValueError("Metadata must be a dictionary or null")
        if self.metadata is not None and len(self.metadata) == 0:
            self.metadata = None
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "New Babbage Landing Zone",
                "type": "station",
                "owner_type": "organization",
                "owner_id": "550e8400-e29b-41d4-a716-446655440000",
                "parent_location_id": None,
                "metadata": {"planet": "microTech", "system": "Stanton"},
            }
        }
    )


class LocationUpdate(BaseModel):
    """Schema for updating location information."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Location name")
    type: Optional[str] = Field(None, max_length=50, description="Location type")
    parent_location_id: Optional[str] = Field(None, description="Parent location UUID")
    canonical_location_id: Optional[str] = Field(
        None, description="Reference to canonical location"
    )
    metadata: Optional[dict[str, Any]] = Field(
        None, description="Flexible location-specific data (JSON)"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize name if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Name cannot be empty or whitespace only")
            return v.strip()
        return v

    @field_validator("parent_location_id", "canonical_location_id")
    @classmethod
    def validate_optional_ids(cls, v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None for optional ID fields."""
        if v is not None and (not v or not v.strip()):
            return None
        return v.strip() if v else None

    @model_validator(mode="after")
    def validate_metadata(self):
        """Ensure metadata is None if empty dict."""
        if self.metadata is not None and not isinstance(self.metadata, dict):
            raise ValueError("Metadata must be a dictionary or null")
        if self.metadata is not None and len(self.metadata) == 0:
            self.metadata = None
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Location Name",
                "metadata": {"updated": True},
            }
        }
    )


class ChildLocationInfo(BaseModel):
    """Schema for child location information."""

    id: str = Field(..., description="Child location UUID")
    name: str = Field(..., description="Child location name")


class LocationResponse(LocationBase):
    """Schema for location API responses."""

    id: str = Field(..., description="Location UUID")
    is_canonical: bool = Field(..., description="Whether this is a canonical/public location")
    parent_location_name: Optional[str] = Field(
        None, description="Name of the parent location (if any)"
    )
    child_locations: list[ChildLocationInfo] = Field(
        default_factory=list, description="List of child locations"
    )
    metadata: Optional[dict[str, Any]] = Field(
        None,
        alias="meta",
        description="Flexible location-specific data (JSON)",
        serialization_alias="metadata",
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
                "owner_type": "organization",
                "owner_id": "550e8400-e29b-41d4-a716-446655440000",
                "parent_location_id": None,
                "metadata": {"planet": "microTech", "system": "Stanton"},
                "created_at": "2024-01-01T00:00:00Z",
            }
        },
    )
