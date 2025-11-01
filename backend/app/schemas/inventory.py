"""
Pydantic schemas for inventory management operations.
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator


class InventoryStockBase(BaseModel):
    """Base schema for inventory stock information."""

    item_id: str = Field(..., description="Item UUID")
    location_id: str = Field(..., description="Location UUID")
    quantity: Decimal = Field(..., description="Total quantity available")
    reserved_quantity: Decimal = Field(..., description="Quantity reserved for operations")
    available_quantity: Decimal = Field(..., description="Available quantity (total - reserved)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "location_id": "550e8400-e29b-41d4-a716-446655440001",
                "quantity": "100.5",
                "reserved_quantity": "10.0",
                "available_quantity": "90.5",
            }
        }
    )


class InventoryStock(InventoryStockBase):
    """Schema for inventory stock with item and location details."""

    item_name: str = Field(..., description="Item name")
    item_category: Optional[str] = Field(None, description="Item category")
    location_name: str = Field(..., description="Location name")
    location_type: str = Field(..., description="Location type")
    last_updated: datetime = Field(..., description="Timestamp when stock was last updated")
    updated_by_username: Optional[str] = Field(
        None, description="Username of user who last updated"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "item_name": "Quantum Fuel",
                "item_category": "Consumables",
                "location_id": "550e8400-e29b-41d4-a716-446655440001",
                "location_name": "New Babbage Landing Zone",
                "location_type": "station",
                "quantity": "100.5",
                "reserved_quantity": "10.0",
                "available_quantity": "90.5",
                "last_updated": "2024-01-01T12:00:00Z",
                "updated_by_username": "testuser",
            }
        }
    )


class InventoryAdjust(BaseModel):
    """Schema for adjusting inventory quantities."""

    item_id: str = Field(..., description="Item UUID to adjust")
    location_id: str = Field(..., description="Location UUID where adjustment occurs")
    quantity_change: Decimal = Field(
        ...,
        description="Quantity change (positive to add, negative to remove)",
        ge=-1000000,
        le=1000000,
    )
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about the adjustment"
    )

    @field_validator("quantity_change")
    @classmethod
    def validate_quantity_change(cls, v: Decimal) -> Decimal:
        """Ensure quantity change is not zero."""
        if v == 0:
            raise ValueError(
                "Quantity change cannot be zero. Use positive to add, negative to remove."
            )
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "location_id": "550e8400-e29b-41d4-a716-446655440001",
                "quantity_change": "25.5",
                "notes": "Purchased from store",
            }
        }
    )


class InventoryTransfer(BaseModel):
    """Schema for transferring items between locations."""

    item_id: str = Field(..., description="Item UUID to transfer")
    from_location_id: str = Field(..., description="Source location UUID")
    to_location_id: str = Field(..., description="Destination location UUID")
    quantity: Decimal = Field(..., description="Quantity to transfer", gt=0, le=1000000)
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about the transfer"
    )

    @field_validator("to_location_id")
    @classmethod
    def validate_locations_different(cls, v: str, info) -> str:
        """Ensure source and destination are different."""
        if hasattr(info, "data") and "from_location_id" in info.data:
            if v == info.data["from_location_id"]:
                raise ValueError("Source and destination locations must be different")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "from_location_id": "550e8400-e29b-41d4-a716-446655440001",
                "to_location_id": "550e8400-e29b-41d4-a716-446655440002",
                "quantity": "50.0",
                "notes": "Moving to ship cargo",
            }
        }
    )


class InventoryHistory(BaseModel):
    """Schema for inventory transaction history."""

    id: str = Field(..., description="Transaction UUID")
    item_id: str = Field(..., description="Item UUID")
    item_name: str = Field(..., description="Item name")
    location_id: str = Field(..., description="Location UUID")
    location_name: str = Field(..., description="Location name")
    quantity_change: Decimal = Field(..., description="Quantity change (positive/negative)")
    transaction_type: str = Field(
        ..., description="Transaction type: add, remove, transfer, craft, consume"
    )
    performed_by_username: str = Field(..., description="Username of user who performed the action")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    notes: Optional[str] = Field(None, description="Optional transaction notes")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "item_name": "Quantum Fuel",
                "location_id": "550e8400-e29b-41d4-a716-446655440001",
                "location_name": "New Babbage Landing Zone",
                "quantity_change": "25.5",
                "transaction_type": "add",
                "performed_by_username": "testuser",
                "timestamp": "2024-01-01T12:00:00Z",
                "notes": "Purchased from store",
            }
        }
    )


class StockReservation(BaseModel):
    """Schema for reserving/unreserving stock."""

    item_id: str = Field(..., description="Item UUID to reserve")
    location_id: str = Field(..., description="Location UUID where reservation occurs")
    quantity: Decimal = Field(..., description="Quantity to reserve/unreserve", gt=0, le=1000000)
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about the reservation"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "location_id": "550e8400-e29b-41d4-a716-446655440001",
                "quantity": "10.0",
                "notes": "Reserved for craft operation",
            }
        }
    )
