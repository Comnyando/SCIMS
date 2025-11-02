"""
Analytics-related Pydantic schemas for API requests and responses.
"""

from datetime import datetime, date
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class ConsentUpdate(BaseModel):
    """Schema for updating analytics consent."""

    analytics_consent: bool = Field(
        ..., description="Whether to consent to analytics data collection"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "analytics_consent": True,
            }
        }
    )


class ConsentResponse(BaseModel):
    """Schema for analytics consent status response."""

    analytics_consent: bool = Field(..., description="Current consent status")
    updated_at: datetime = Field(..., description="When consent was last updated")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "analytics_consent": True,
                "updated_at": "2024-01-01T00:00:00Z",
            }
        },
    )


class UsageStatsResponse(BaseModel):
    """Schema for usage statistics response."""

    total_events: int = Field(..., description="Total number of events")
    events_by_type: dict[str, int] = Field(..., description="Event counts by type")
    top_blueprints: list[dict[str, Any]] = Field(
        default_factory=list, description="Most used blueprints"
    )
    top_goals: list[dict[str, Any]] = Field(default_factory=list, description="Most common goals")
    period_start: Optional[date] = Field(None, description="Start of statistics period")
    period_end: Optional[date] = Field(None, description="End of statistics period")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_events": 1500,
                "events_by_type": {
                    "blueprint_used": 500,
                    "goal_created": 200,
                    "item_stock_updated": 800,
                },
                "top_blueprints": [
                    {"blueprint_id": "uuid", "name": "Item X", "uses": 150},
                ],
                "top_goals": [
                    {"goal_id": "uuid", "name": "Stockpile Resources", "created_count": 25},
                ],
                "period_start": "2024-01-01",
                "period_end": "2024-01-31",
            }
        }
    )


class RecipeStatsResponse(BaseModel):
    """Schema for recipe/blueprint statistics response."""

    blueprint_id: str = Field(..., description="Blueprint UUID")
    blueprint_name: Optional[str] = Field(None, description="Blueprint name")
    period_start: date = Field(..., description="Start of the period")
    period_end: date = Field(..., description="End of the period")
    period_type: str = Field(..., description="Type of period: daily, weekly, monthly")
    total_uses: int = Field(..., description="Total number of uses")
    unique_users: int = Field(..., description="Number of unique users")
    completed_count: int = Field(..., description="Number of completed crafts")
    cancelled_count: int = Field(..., description="Number of cancelled crafts")
    completion_rate: float = Field(..., description="Completion rate (0-1)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "blueprint_id": "550e8400-e29b-41d4-a716-446655440000",
                "blueprint_name": "Weapon Component X",
                "period_start": "2024-01-01",
                "period_end": "2024-01-31",
                "period_type": "monthly",
                "total_uses": 150,
                "unique_users": 25,
                "completed_count": 140,
                "cancelled_count": 10,
                "completion_rate": 0.933,
            }
        },
    )
