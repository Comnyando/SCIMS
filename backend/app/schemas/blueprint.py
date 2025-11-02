"""
Pydantic schemas for Blueprint model validation.
"""

from datetime import datetime
from typing import Optional, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class BlueprintIngredient(BaseModel):
    """Schema for a blueprint ingredient."""

    item_id: str = Field(..., description="Item UUID")
    quantity: Decimal = Field(..., gt=0, description="Required quantity (must be positive)")
    optional: bool = Field(default=False, description="Whether this ingredient is optional")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "quantity": 5.0,
                "optional": False,
            }
        }
    )


class BlueprintBase(BaseModel):
    """Base blueprint schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Blueprint name")
    description: Optional[str] = Field(None, description="Blueprint description")
    category: Optional[str] = Field(None, max_length=100, description="Blueprint category")
    crafting_time_minutes: int = Field(
        ..., ge=0, description="Crafting time in minutes (0 = instant)"
    )
    output_item_id: str = Field(..., description="UUID of item produced by this blueprint")
    output_quantity: Decimal = Field(..., gt=0, description="Quantity of output item produced")
    blueprint_data: dict[str, Any] = Field(
        ..., description="Blueprint data including ingredients array"
    )
    is_public: bool = Field(default=False, description="Whether blueprint is publicly visible")

    @field_validator("blueprint_data")
    @classmethod
    def validate_blueprint_data(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate blueprint_data structure and ingredients."""
        if not isinstance(v, dict):
            raise ValueError("blueprint_data must be a dictionary")

        if "ingredients" not in v:
            raise ValueError("blueprint_data must contain 'ingredients' key")

        ingredients = v["ingredients"]
        if not isinstance(ingredients, list):
            raise ValueError("ingredients must be an array")

        if len(ingredients) == 0:
            raise ValueError("ingredients array cannot be empty")

        # Validate each ingredient
        item_ids = set()
        for idx, ingredient in enumerate(ingredients):
            if not isinstance(ingredient, dict):
                raise ValueError(f"ingredient at index {idx} must be an object")

            if "item_id" not in ingredient:
                raise ValueError(f"ingredient at index {idx} must have 'item_id' field")

            if "quantity" not in ingredient:
                raise ValueError(f"ingredient at index {idx} must have 'quantity' field")

            item_id = ingredient["item_id"]
            if not isinstance(item_id, str):
                raise ValueError(f"ingredient at index {idx} 'item_id' must be a string (UUID)")

            # Check for duplicate item_ids
            if item_id in item_ids:
                raise ValueError(f"Duplicate item_id '{item_id}' in ingredients (at index {idx})")

            item_ids.add(item_id)

            quantity = ingredient["quantity"]
            try:
                quantity_decimal = Decimal(str(quantity))
                if quantity_decimal <= 0:
                    raise ValueError(f"ingredient at index {idx} 'quantity' must be positive")
            except (ValueError, TypeError):
                raise ValueError(f"ingredient at index {idx} 'quantity' must be a positive number")

            # Optional field validation
            if "optional" in ingredient and not isinstance(ingredient["optional"], bool):
                raise ValueError(f"ingredient at index {idx} 'optional' must be a boolean")

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Quantum Drive Component",
                "description": "Advanced quantum drive component for ship upgrades",
                "category": "Components",
                "crafting_time_minutes": 120,
                "output_item_id": "550e8400-e29b-41d4-a716-446655440000",
                "output_quantity": 1.0,
                "blueprint_data": {
                    "ingredients": [
                        {
                            "item_id": "660e8400-e29b-41d4-a716-446655440000",
                            "quantity": 5.0,
                            "optional": False,
                        },
                        {
                            "item_id": "770e8400-e29b-41d4-a716-446655440000",
                            "quantity": 2.0,
                            "optional": False,
                        },
                    ]
                },
                "is_public": False,
            }
        }
    )


class BlueprintCreate(BlueprintBase):
    """Schema for creating a new blueprint."""

    pass


class BlueprintUpdate(BaseModel):
    """Schema for updating blueprint information."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Blueprint name")
    description: Optional[str] = Field(None, description="Blueprint description")
    category: Optional[str] = Field(None, max_length=100, description="Blueprint category")
    crafting_time_minutes: Optional[int] = Field(None, ge=0, description="Crafting time in minutes")
    output_item_id: Optional[str] = Field(
        None, description="UUID of item produced by this blueprint"
    )
    output_quantity: Optional[Decimal] = Field(
        None, gt=0, description="Quantity of output item produced"
    )
    blueprint_data: Optional[dict[str, Any]] = Field(
        None, description="Blueprint data including ingredients array"
    )
    is_public: Optional[bool] = Field(None, description="Whether blueprint is publicly visible")

    @field_validator("blueprint_data")
    @classmethod
    def validate_blueprint_data(cls, v: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        """Validate blueprint_data structure if provided."""
        if v is None:
            return v
        # Reuse validation from BlueprintBase
        return BlueprintBase.validate_blueprint_data(v)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Blueprint Name",
                "crafting_time_minutes": 90,
                "is_public": True,
            }
        }
    )


class BlueprintResponse(BlueprintBase):
    """Schema for blueprint API responses."""

    id: str = Field(..., description="Blueprint UUID")
    created_by: str = Field(..., description="User UUID who created this blueprint")
    usage_count: int = Field(..., description="Number of times this blueprint has been used")
    created_at: datetime = Field(..., description="Timestamp when the blueprint was created")

    # Optional nested objects (can be included via query params)
    # Note: These are set to None by default. When relationships are loaded,
    # they will be Item/User objects, so we exclude them and handle separately in the router
    output_item: Optional[dict[str, Any]] = Field(default=None, description="Output item details")
    creator: Optional[dict[str, Any]] = Field(default=None, description="Creator user details")

    @model_validator(mode="before")
    @classmethod
    def handle_relationships(cls, data: Any) -> Any:
        """Handle SQLAlchemy relationship objects by converting to None."""
        if isinstance(data, dict):
            # Already a dict, pass through
            return data
        # If it's a model instance, exclude relationships - they'll be set manually
        return data

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440000",
                "name": "Quantum Drive Component",
                "description": "Advanced quantum drive component",
                "category": "Components",
                "crafting_time_minutes": 120,
                "output_item_id": "550e8400-e29b-41d4-a716-446655440000",
                "output_quantity": 1.0,
                "blueprint_data": {
                    "ingredients": [
                        {
                            "item_id": "660e8400-e29b-41d4-a716-446655440000",
                            "quantity": 5.0,
                            "optional": False,
                        },
                    ]
                },
                "created_by": "990e8400-e29b-41d4-a716-446655440000",
                "is_public": False,
                "usage_count": 5,
                "created_at": "2024-01-01T12:00:00Z",
            }
        },
    )
