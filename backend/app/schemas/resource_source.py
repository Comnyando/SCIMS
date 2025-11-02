"""
Resource Source-related Pydantic schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.resource_source import (
    SOURCE_TYPE_PLAYER_STOCK,
    SOURCE_TYPE_UNIVERSE_LOCATION,
    SOURCE_TYPE_TRADING_POST,
    SOURCE_TYPES,
)


class ResourceSourceBase(BaseModel):
    """Base schema for resource source."""

    item_id: str = Field(..., description="Item UUID this source provides")
    source_type: str = Field(
        ...,
        description="Source type: player_stock, universe_location, trading_post",
    )
    source_identifier: str = Field(
        ...,
        description="Identifier for the source (player_id, location_name, etc.)",
    )
    available_quantity: float = Field(
        default=0,
        ge=0,
        description="Available quantity at this source (must be >= 0)",
    )
    cost_per_unit: Optional[float] = Field(
        None,
        ge=0,
        description="Cost per unit (nullable, must be >= 0 if provided)",
    )
    reliability_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Reliability score (0-1), defaults to None (will be calculated if not provided)",
    )
    metadata: Optional[dict[str, Any]] = Field(
        None, description="Additional source metadata (JSON)"
    )
    location_id: Optional[str] = Field(
        None,
        description="Optional location UUID where this source can be found (for universe locations, trading posts, etc.)",
    )

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        """Validate source_type is one of the allowed values."""
        if v not in SOURCE_TYPES:
            raise ValueError(f"source_type must be one of: {', '.join(SOURCE_TYPES)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "source_type": "universe_location",
                "source_identifier": "MicroTech Mining Outpost Alpha",
                "available_quantity": 1000.0,
                "cost_per_unit": None,
                "reliability_score": 0.75,
                "location_id": None,
            }
        }
    )


class ResourceSourceCreate(ResourceSourceBase):
    """Schema for creating a new resource source."""

    pass


class ResourceSourceUpdate(BaseModel):
    """Schema for updating a resource source."""

    source_type: Optional[str] = Field(
        None,
        description="Source type: player_stock, universe_location, trading_post",
    )
    source_identifier: Optional[str] = Field(
        None,
        description="Identifier for the source (player_id, location_name, etc.)",
    )
    available_quantity: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Available quantity at this source (must be >= 0)",
    )
    cost_per_unit: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Cost per unit (nullable, must be >= 0 if provided)",
    )
    reliability_score: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1,
        description="Reliability score (0-1)",
    )
    metadata: Optional[dict[str, Any]] = Field(
        None, description="Additional source metadata (JSON)"
    )
    location_id: Optional[str] = Field(
        None,
        description="Optional location UUID where this source can be found",
    )

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate source_type is one of the allowed values if provided."""
        if v is not None and v not in SOURCE_TYPES:
            raise ValueError(f"source_type must be one of: {', '.join(SOURCE_TYPES)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "available_quantity": 1500.0,
                "cost_per_unit": 10.5,
                "reliability_score": 0.8,
            }
        }
    )


class ResourceSourceResponse(ResourceSourceBase):
    """Schema for resource source response."""

    id: str = Field(..., description="Resource source UUID")
    last_verified: Optional[datetime] = Field(
        None, description="Last time this source was verified"
    )
    reliability_score: Optional[float] = Field(
        None, ge=0, le=1, description="Reliability score (0-1), may be None"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    item: Optional[dict[str, Any]] = Field(
        None, description="Item details (if included in response)"
    )
    location: Optional[dict[str, Any]] = Field(
        None, description="Location details (if included in response)"
    )

    model_config = ConfigDict(from_attributes=True)


class SourceVerificationLogBase(BaseModel):
    """Base schema for source verification log."""

    source_id: str = Field(..., description="Resource source UUID")
    was_accurate: bool = Field(..., description="Whether the source information was accurate")
    notes: Optional[str] = Field(None, description="Optional notes about the verification")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_id": "660e8400-e29b-41d4-a716-446655440000",
                "was_accurate": True,
                "notes": "Verified in-game, stock levels accurate",
            }
        }
    )


class SourceVerificationLogCreate(SourceVerificationLogBase):
    """Schema for creating a new verification log entry."""

    pass


class SourceVerificationLogResponse(SourceVerificationLogBase):
    """Schema for verification log response."""

    id: str = Field(..., description="Verification log UUID")
    verified_by: str = Field(..., description="User UUID who performed verification")
    verified_at: datetime = Field(..., description="Verification timestamp")
    verifier: Optional[dict[str, Any]] = Field(
        None, description="Verifier user details (if included in response)"
    )
    source: Optional[dict[str, Any]] = Field(
        None, description="Source details (if included in response)"
    )

    model_config = ConfigDict(from_attributes=True)
