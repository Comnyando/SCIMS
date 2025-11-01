"""
Pydantic schemas for Item model validation.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class ItemBase(BaseModel):
    """Base item schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    category: Optional[str] = Field(None, max_length=100, description="Item category")
    subcategory: Optional[str] = Field(None, max_length=100, description="Item subcategory")
    rarity: Optional[str] = Field(None, max_length=50, description="Item rarity level")


class ItemCreate(ItemBase):
    """Schema for creating a new item."""

    metadata: Optional[dict[str, Any]] = Field(None, description="Game-specific attributes (JSON)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Quantum Fuel",
                "description": "Refined quantum fuel for FTL travel",
                "category": "Consumables",
                "subcategory": "Fuel",
                "rarity": "common",
                "metadata": {"volume": 1.0, "weight": 0.5},
            }
        }
    )


class ItemUpdate(BaseModel):
    """Schema for updating item information."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    category: Optional[str] = Field(None, max_length=100, description="Item category")
    subcategory: Optional[str] = Field(None, max_length=100, description="Item subcategory")
    rarity: Optional[str] = Field(None, max_length=50, description="Item rarity level")
    metadata: Optional[dict[str, Any]] = Field(None, description="Game-specific attributes (JSON)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Updated description",
                "rarity": "rare",
            }
        }
    )


class ItemResponse(ItemBase):
    """Schema for item API responses."""

    id: str = Field(..., description="Item UUID")
    metadata: Optional[dict[str, Any]] = Field(
        None,
        alias="meta",
        description="Game-specific attributes (JSON)",
        serialization_alias="metadata",
    )
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Quantum Fuel",
                "description": "Refined quantum fuel for FTL travel",
                "category": "Consumables",
                "subcategory": "Fuel",
                "rarity": "common",
                "metadata": {"volume": 1.0, "weight": 0.5},
                "created_at": "2024-01-01T00:00:00Z",
            }
        },
    )
