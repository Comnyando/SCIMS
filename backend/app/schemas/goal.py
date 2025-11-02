"""
Goal-related Pydantic schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional, Any, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

from app.models.goal import GOAL_STATUSES


class GoalItemCreate(BaseModel):
    """Schema for a single goal item when creating a goal."""

    item_id: str = Field(..., description="Target item UUID")
    target_quantity: Decimal = Field(
        ..., gt=0, description="Target quantity for this item (must be positive)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "target_quantity": 1000.0,
            }
        }
    )


class GoalItemResponse(BaseModel):
    """Schema for goal item in API responses."""

    id: str = Field(..., description="GoalItem UUID")
    item_id: str = Field(..., description="Target item UUID")
    target_quantity: Decimal = Field(..., description="Target quantity")
    item: Optional[dict[str, Any]] = Field(default=None, description="Item details")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "bb0e8400-e29b-41d4-a716-446655440000",
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "target_quantity": 1000.0,
            }
        },
    )


class GoalItemProgress(BaseModel):
    """Schema for progress on a single goal item."""

    item_id: str = Field(..., description="Item UUID")
    current_quantity: Decimal = Field(..., description="Current quantity achieved")
    target_quantity: Decimal = Field(..., description="Target quantity")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage (0-100)")
    is_completed: bool = Field(..., description="Whether this item's goal is completed")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_quantity": 750.0,
                "target_quantity": 1000.0,
                "progress_percentage": 75.0,
                "is_completed": False,
            }
        }
    )


class GoalBase(BaseModel):
    """Base schema for goal with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Goal name")
    description: Optional[str] = Field(None, description="Goal description")
    organization_id: Optional[str] = Field(None, description="Organization UUID (optional)")
    goal_items: List[GoalItemCreate] = Field(
        ..., min_length=1, description="List of target items and quantities"
    )
    target_date: Optional[datetime] = Field(None, description="Target completion date (optional)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Stockpile Resources",
                "description": "Build up reserves for upcoming crafting projects",
                "organization_id": "990e8400-e29b-41d4-a716-446655440000",
                "goal_items": [
                    {"item_id": "550e8400-e29b-41d4-a716-446655440000", "target_quantity": 1000.0},
                    {"item_id": "660e8400-e29b-41d4-a716-446655440000", "target_quantity": 500.0},
                ],
                "target_date": "2024-12-31T23:59:59Z",
            }
        }
    )


class GoalCreate(GoalBase):
    """Schema for creating a new goal."""

    pass


class GoalUpdate(BaseModel):
    """Schema for updating goal information."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Goal name")
    description: Optional[str] = Field(None, description="Goal description")
    organization_id: Optional[str] = Field(None, description="Organization UUID")
    goal_items: Optional[List[GoalItemCreate]] = Field(
        None, min_length=1, description="List of target items and quantities (replaces existing)"
    )
    target_date: Optional[datetime] = Field(None, description="Target completion date")
    status: Optional[str] = Field(None, description="Goal status: active, completed, cancelled")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status is one of the allowed values."""
        if v is not None and v not in GOAL_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(GOAL_STATUSES)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Goal Name",
                "target_quantity": 1500.0,
            }
        }
    )


class GoalProgress(BaseModel):
    """Schema for goal progress information."""

    current_quantity: Decimal = Field(
        ..., description="Current total quantity achieved (sum of all items)"
    )
    target_quantity: Decimal = Field(..., description="Target total quantity (sum of all items)")
    progress_percentage: float = Field(
        ..., ge=0, le=100, description="Overall progress percentage (0-100)"
    )
    is_completed: bool = Field(
        ..., description="Whether goal is completed (all items at or above target)"
    )
    days_remaining: Optional[int] = Field(None, description="Days until target_date (if set)")
    item_progress: Optional[List[GoalItemProgress]] = Field(
        None, description="Progress for each individual item"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_quantity": 1500.0,
                "target_quantity": 2000.0,
                "progress_percentage": 75.0,
                "is_completed": False,
                "days_remaining": 45,
                "item_progress": [
                    {
                        "item_id": "550e8400-e29b-41d4-a716-446655440000",
                        "current_quantity": 1000.0,
                        "target_quantity": 1000.0,
                        "progress_percentage": 100.0,
                        "is_completed": True,
                    },
                    {
                        "item_id": "660e8400-e29b-41d4-a716-446655440000",
                        "current_quantity": 500.0,
                        "target_quantity": 1000.0,
                        "progress_percentage": 50.0,
                        "is_completed": False,
                    },
                ],
            }
        }
    )


class GoalResponse(BaseModel):
    """Schema for goal API responses."""

    id: str = Field(..., description="Goal UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Goal name")
    description: Optional[str] = Field(None, description="Goal description")
    organization_id: Optional[str] = Field(None, description="Organization UUID (optional)")
    created_by: str = Field(..., description="User UUID who created this goal")
    status: str = Field(..., description="Goal status: active, completed, cancelled")
    goal_items: List[GoalItemResponse] = Field(..., description="List of goal items")
    target_date: Optional[datetime] = Field(None, description="Target completion date (optional)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    progress_data: Optional[dict[str, Any]] = Field(None, description="Progress tracking data")

    # Optional nested objects
    organization: Optional[dict[str, Any]] = Field(default=None, description="Organization details")
    creator: Optional[dict[str, Any]] = Field(default=None, description="Creator user details")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "aa0e8400-e29b-41d4-a716-446655440000",
                "name": "Stockpile 1000 units of Iron",
                "description": "Build up iron reserves",
                "organization_id": "990e8400-e29b-41d4-a716-446655440000",
                "target_item_id": "550e8400-e29b-41d4-a716-446655440000",
                "target_quantity": 1000.0,
                "target_date": "2024-12-31T23:59:59Z",
                "created_by": "dd0e8400-e29b-41d4-a716-446655440000",
                "status": "active",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "progress_data": {
                    "current_quantity": 750.0,
                    "progress_percentage": 75.0,
                },
            }
        },
    )


class GoalProgressResponse(BaseModel):
    """Schema for detailed goal progress response."""

    goal_id: str = Field(..., description="Goal UUID")
    status: str = Field(..., description="Current goal status")
    progress: GoalProgress = Field(..., description="Progress information")
    last_calculated_at: Optional[datetime] = Field(
        None, description="When progress was last calculated"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "goal_id": "aa0e8400-e29b-41d4-a716-446655440000",
                "status": "active",
                "progress": {
                    "current_quantity": 750.0,
                    "target_quantity": 1000.0,
                    "progress_percentage": 75.0,
                    "is_completed": False,
                    "days_remaining": 45,
                },
                "last_calculated_at": "2024-01-15T12:00:00Z",
            }
        }
    )
