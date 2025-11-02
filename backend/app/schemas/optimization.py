"""
Optimization-related Pydantic schemas for API requests and responses.
"""

from typing import Optional, List, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class SourceOption(BaseModel):
    """A single source option for obtaining an item."""

    source_type: str = Field(
        ...,
        description="Type of source: stock, player_stock, universe_location, trading_post",
    )
    location_id: Optional[str] = Field(
        None, description="Location UUID if applicable (for stock, player_stock)"
    )
    location_name: Optional[str] = Field(None, description="Location name if applicable")
    source_id: Optional[str] = Field(
        None, description="Resource source UUID if applicable (for universe sources)"
    )
    source_identifier: Optional[str] = Field(
        None, description="Source identifier (player_id, location_name, etc.)"
    )
    available_quantity: float = Field(..., description="Available quantity at this source")
    cost_per_unit: float = Field(default=0, description="Cost per unit (0 for owned stock)")
    total_cost: float = Field(..., description="Total cost for required quantity")
    reliability_score: Optional[float] = Field(
        None, ge=0, le=1, description="Reliability score (0-1) for universe sources"
    )
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional source metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_type": "stock",
                "location_id": "550e8400-e29b-41d4-a716-446655440000",
                "location_name": "Warehouse Alpha",
                "available_quantity": 100.0,
                "cost_per_unit": 0.0,
                "total_cost": 0.0,
                "reliability_score": None,
            }
        }
    )


class FindSourcesRequest(BaseModel):
    """Request schema for finding sources for items."""

    item_id: str = Field(..., description="Item UUID to find sources for")
    required_quantity: Decimal = Field(..., gt=0, description="Required quantity (must be > 0)")
    max_sources: int = Field(
        default=10, ge=1, le=50, description="Maximum number of source options to return"
    )
    include_player_stocks: bool = Field(
        default=True, description="Include other players' stocks (if permissions allow)"
    )
    min_reliability: Optional[Decimal] = Field(
        None, ge=0, le=1, description="Minimum reliability score for universe sources"
    )
    organization_id: Optional[str] = Field(
        None, description="Organization ID to check stock for (optional)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "required_quantity": 50.0,
                "max_sources": 10,
                "include_player_stocks": True,
                "min_reliability": 0.5,
            }
        }
    )


class FindSourcesResponse(BaseModel):
    """Response schema for finding sources."""

    item_id: str = Field(..., description="Item UUID")
    item_name: Optional[str] = Field(None, description="Item name")
    required_quantity: float = Field(..., description="Required quantity")
    sources: List[SourceOption] = Field(
        ..., description="List of source options, sorted by priority"
    )
    total_available: float = Field(..., description="Total available quantity across all sources")
    has_sufficient: bool = Field(
        ...,
        description="Whether there are sufficient sources to meet the requirement",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "item_name": "Iron Ore",
                "required_quantity": 50.0,
                "sources": [],
                "total_available": 100.0,
                "has_sufficient": True,
            }
        }
    )


class CraftSuggestion(BaseModel):
    """A suggested craft operation."""

    blueprint_id: str = Field(..., description="Blueprint UUID")
    blueprint_name: str = Field(..., description="Blueprint name")
    output_item_id: str = Field(..., description="Output item UUID")
    output_item_name: Optional[str] = Field(None, description="Output item name")
    output_quantity: float = Field(..., description="Quantity produced per craft")
    crafting_time_minutes: int = Field(..., description="Crafting time in minutes")
    suggested_count: int = Field(
        ..., ge=1, description="Suggested number of times to craft this blueprint"
    )
    total_output: float = Field(..., description="Total output if crafted suggested_count times")
    ingredients: List[dict[str, Any]] = Field(..., description="Required ingredients for one craft")
    all_ingredients_available: bool = Field(
        ..., description="Whether all ingredients are available in stock"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "blueprint_id": "660e8400-e29b-41d4-a716-446655440000",
                "blueprint_name": "Basic Component Blueprint",
                "output_item_id": "770e8400-e29b-41d4-a716-446655440000",
                "output_item_name": "Basic Component",
                "output_quantity": 10.0,
                "crafting_time_minutes": 60,
                "suggested_count": 5,
                "total_output": 50.0,
                "ingredients": [{"item_id": "xxx", "quantity": 5}],
                "all_ingredients_available": True,
            }
        }
    )


class SuggestCraftsRequest(BaseModel):
    """Request schema for suggesting crafts."""

    target_item_id: str = Field(..., description="Target item UUID to craft")
    target_quantity: Decimal = Field(
        ..., gt=0, description="Target quantity to produce (must be > 0)"
    )
    organization_id: Optional[str] = Field(
        None, description="Organization ID to check stock for (optional)"
    )
    max_suggestions: int = Field(
        default=10, ge=1, le=50, description="Maximum number of craft suggestions to return"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "target_item_id": "550e8400-e29b-41d4-a716-446655440000",
                "target_quantity": 100.0,
                "max_suggestions": 10,
            }
        }
    )


class SuggestCraftsResponse(BaseModel):
    """Response schema for craft suggestions."""

    target_item_id: str = Field(..., description="Target item UUID")
    target_item_name: Optional[str] = Field(None, description="Target item name")
    target_quantity: float = Field(..., description="Target quantity")
    suggestions: List[CraftSuggestion] = Field(
        ..., description="List of craft suggestions, sorted by feasibility"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "target_item_id": "550e8400-e29b-41d4-a716-446655440000",
                "target_item_name": "Advanced Component",
                "target_quantity": 100.0,
                "suggestions": [],
            }
        }
    )


class ResourceGapItem(BaseModel):
    """A resource gap item showing what's missing."""

    item_id: str = Field(..., description="Item UUID")
    item_name: Optional[str] = Field(None, description="Item name")
    required_quantity: float = Field(..., description="Total required quantity")
    available_quantity: float = Field(..., description="Available quantity in stock")
    gap_quantity: float = Field(..., description="Missing quantity (required - available)")
    sources: List[SourceOption] = Field(
        ...,
        description="Available sources to fill the gap, sorted by priority",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "item_name": "Iron Ore",
                "required_quantity": 100.0,
                "available_quantity": 30.0,
                "gap_quantity": 70.0,
                "sources": [],
            }
        }
    )


class ResourceGapResponse(BaseModel):
    """Response schema for resource gap analysis."""

    craft_id: str = Field(..., description="Craft UUID")
    craft_status: str = Field(..., description="Current craft status")
    blueprint_name: Optional[str] = Field(None, description="Blueprint name")
    gaps: List[ResourceGapItem] = Field(
        ..., description="List of resource gaps, sorted by severity"
    )
    total_gaps: int = Field(..., description="Total number of items with gaps")
    can_proceed: bool = Field(
        ...,
        description="Whether the craft can proceed (all gaps have available sources)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "craft_id": "880e8400-e29b-41d4-a716-446655440000",
                "craft_status": "planned",
                "blueprint_name": "Advanced Component Blueprint",
                "gaps": [],
                "total_gaps": 2,
                "can_proceed": True,
            }
        }
    )
