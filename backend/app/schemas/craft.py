"""
Craft-related Pydantic schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.craft import CRAFT_STATUSES
from app.models.craft_ingredient import (
    SOURCE_TYPES,
    INGREDIENT_STATUSES,
)


class CraftIngredientBase(BaseModel):
    """Base schema for craft ingredient."""

    item_id: str = Field(..., description="Item UUID for this ingredient")
    required_quantity: Decimal = Field(
        ..., gt=0, description="Required quantity (must be positive)"
    )
    source_location_id: Optional[str] = Field(
        None, description="Location UUID where ingredient will be sourced from"
    )
    source_type: str = Field(
        default="stock",
        description="Source type: stock, player, universe",
    )
    status: str = Field(
        default="pending",
        description="Ingredient status: pending, reserved, fulfilled",
    )

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        """Validate source_type is one of the allowed values."""
        if v not in SOURCE_TYPES:
            raise ValueError(f"source_type must be one of: {', '.join(SOURCE_TYPES)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of the allowed values."""
        if v not in INGREDIENT_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(INGREDIENT_STATUSES)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "required_quantity": 5.0,
                "source_location_id": "660e8400-e29b-41d4-a716-446655440000",
                "source_type": "stock",
                "status": "pending",
            }
        }
    )


class CraftBase(BaseModel):
    """Base craft schema with common fields."""

    blueprint_id: str = Field(..., description="UUID of blueprint to execute")
    organization_id: Optional[str] = Field(None, description="Organization UUID (optional)")
    output_location_id: str = Field(
        ..., description="Location UUID where output items will be placed"
    )
    priority: int = Field(default=0, description="Craft priority (higher = more important)")
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time (optional)")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional craft metadata (JSON)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "blueprint_id": "880e8400-e29b-41d4-a716-446655440000",
                "organization_id": "990e8400-e29b-41d4-a716-446655440000",
                "output_location_id": "aa0e8400-e29b-41d4-a716-446655440000",
                "priority": 5,
                "scheduled_start": "2024-01-01T12:00:00Z",
            }
        }
    )


class CraftCreate(CraftBase):
    """Schema for creating a new craft."""

    pass


class CraftUpdate(BaseModel):
    """Schema for updating craft information."""

    organization_id: Optional[str] = Field(None, description="Organization UUID")
    output_location_id: Optional[str] = Field(
        None, description="Location UUID where output items will be placed"
    )
    priority: Optional[int] = Field(None, description="Craft priority")
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional craft metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "priority": 10,
                "scheduled_start": "2024-01-02T12:00:00Z",
            }
        }
    )


class CraftIngredientResponse(CraftIngredientBase):
    """Schema for craft ingredient API responses."""

    id: str = Field(..., description="Craft ingredient UUID")
    craft_id: str = Field(..., description="Craft UUID")

    # Optional nested objects
    item: Optional[dict[str, Any]] = Field(default=None, description="Item details")
    source_location: Optional[dict[str, Any]] = Field(
        default=None, description="Source location details"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "bb0e8400-e29b-41d4-a716-446655440000",
                "craft_id": "cc0e8400-e29b-41d4-a716-446655440000",
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "required_quantity": 5.0,
                "source_location_id": "660e8400-e29b-41d4-a716-446655440000",
                "source_type": "stock",
                "status": "reserved",
            }
        },
    )


class CraftResponse(CraftBase):
    """Schema for craft API responses."""

    id: str = Field(..., description="Craft UUID")
    requested_by: str = Field(..., description="User UUID who requested this craft")
    status: str = Field(..., description="Craft status: planned, in_progress, completed, cancelled")
    started_at: Optional[datetime] = Field(None, description="Actual start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")

    # Optional nested objects
    blueprint: Optional[dict[str, Any]] = Field(default=None, description="Blueprint details")
    organization: Optional[dict[str, Any]] = Field(default=None, description="Organization details")
    requester: Optional[dict[str, Any]] = Field(default=None, description="Requester user details")
    output_location: Optional[dict[str, Any]] = Field(
        default=None, description="Output location details"
    )
    ingredients: Optional[list[CraftIngredientResponse]] = Field(
        default=None, description="Craft ingredients"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "cc0e8400-e29b-41d4-a716-446655440000",
                "blueprint_id": "880e8400-e29b-41d4-a716-446655440000",
                "organization_id": "990e8400-e29b-41d4-a716-446655440000",
                "requested_by": "dd0e8400-e29b-41d4-a716-446655440000",
                "status": "planned",
                "priority": 5,
                "output_location_id": "aa0e8400-e29b-41d4-a716-446655440000",
                "scheduled_start": "2024-01-01T12:00:00Z",
            }
        },
    )


class CraftProgressResponse(BaseModel):
    """Schema for craft progress information."""

    craft_id: str = Field(..., description="Craft UUID")
    status: str = Field(..., description="Current craft status")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time")
    elapsed_minutes: Optional[int] = Field(
        None, description="Elapsed time in minutes (if in progress)"
    )
    estimated_completion_minutes: Optional[int] = Field(
        None, description="Estimated minutes until completion (if in progress)"
    )
    ingredients_status: dict[str, Any] = Field(
        ..., description="Summary of ingredient fulfillment status"
    )
    blueprint_crafting_time_minutes: int = Field(
        ..., description="Blueprint crafting time in minutes"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "craft_id": "cc0e8400-e29b-41d4-a716-446655440000",
                "status": "in_progress",
                "started_at": "2024-01-01T12:00:00Z",
                "elapsed_minutes": 30,
                "estimated_completion_minutes": 90,
                "ingredients_status": {
                    "total": 5,
                    "pending": 0,
                    "reserved": 5,
                    "fulfilled": 5,
                },
                "blueprint_crafting_time_minutes": 120,
            }
        }
    )
