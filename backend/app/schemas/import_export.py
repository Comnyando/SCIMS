"""
Pydantic schemas for import/export operations.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ExportFilters(BaseModel):
    """Schema for export filters."""

    category: Optional[str] = Field(None, description="Filter by category")
    location_id: Optional[str] = Field(None, description="Filter by location ID (for inventory)")
    item_id: Optional[str] = Field(None, description="Filter by item ID (for inventory)")
    is_public: Optional[bool] = Field(None, description="Filter by public status (for blueprints)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "Materials",
                "location_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    )


class ImportResponse(BaseModel):
    """Schema for import operation response."""

    success: bool = Field(..., description="Whether the import was successful")
    imported_count: int = Field(..., description="Number of items successfully imported")
    failed_count: int = Field(..., description="Number of items that failed to import")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="List of import errors")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "imported_count": 10,
                "failed_count": 0,
                "errors": [],
            }
        }
    )
