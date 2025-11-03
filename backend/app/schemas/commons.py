"""
Commons-related Pydantic schemas for API validation and serialization.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


# ==================== Submission Schemas ====================


class CommonsSubmissionBase(BaseModel):
    """Base schema for commons submission."""

    entity_type: str = Field(
        ..., description="Type of entity (item, blueprint, location, ingredient, taxonomy)"
    )
    entity_payload: Dict[str, Any] = Field(
        ..., description="Normalized shape for proposed entity or update (JSON)"
    )
    source_reference: Optional[str] = Field(
        None, max_length=500, description="URL or notes about the source"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entity_type": "item",
                "entity_payload": {
                    "name": "Quantum Drive",
                    "description": "Q5 Quantum Drive",
                    "category": "Components",
                },
                "source_reference": "https://starcitizen.fandom.com/wiki/Quantum_Drive",
            }
        }
    )


class CommonsSubmissionCreate(CommonsSubmissionBase):
    """Schema for creating a new commons submission."""

    pass


class CommonsSubmissionUpdate(BaseModel):
    """Schema for updating a commons submission."""

    entity_payload: Optional[Dict[str, Any]] = Field(None, description="Updated entity payload")
    source_reference: Optional[str] = Field(
        None, max_length=500, description="Updated source reference"
    )


class CommonsSubmissionResponse(CommonsSubmissionBase):
    """Schema for commons submission API response."""

    id: str = Field(..., description="Submission UUID")
    submitter_id: str = Field(..., description="User UUID who submitted")
    status: str = Field(..., description="Submission status")
    review_notes: Optional[str] = Field(None, description="Notes from moderator review")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class CommonsSubmissionsListResponse(BaseModel):
    """Schema for submissions list response."""

    submissions: List[CommonsSubmissionResponse] = Field(..., description="List of submissions")
    total: int = Field(..., description="Total number of submissions")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
    pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "submissions": [],
                "total": 0,
                "skip": 0,
                "limit": 50,
                "pages": 0,
            }
        }
    )


# ==================== Moderation Action Schemas ====================


class CommonsModerationActionCreate(BaseModel):
    """Schema for creating a moderation action."""

    action: str = Field(
        ..., description="Type of action (approve, reject, request_changes, merge, edit)"
    )
    action_payload: Optional[Dict[str, Any]] = Field(
        None, description="Action-specific data (diffs/merge mapping)"
    )
    notes: Optional[str] = Field(None, description="Notes about the action")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action": "approve",
                "notes": "Looks good, approved for publication",
            }
        }
    )


class CommonsModerationActionResponse(BaseModel):
    """Schema for moderation action API response."""

    id: str = Field(..., description="Action UUID")
    submission_id: str = Field(..., description="Submission UUID")
    moderator_id: str = Field(..., description="Moderator user UUID")
    action: str = Field(..., description="Type of action")
    action_payload: Optional[Dict[str, Any]] = Field(None, description="Action payload")
    notes: Optional[str] = Field(None, description="Notes")
    created_at: datetime = Field(..., description="Action timestamp")

    model_config = ConfigDict(from_attributes=True)


# ==================== Commons Entity Schemas ====================


class CommonsEntityResponse(BaseModel):
    """Schema for commons entity API response."""

    id: str = Field(..., description="Entity UUID")
    entity_type: str = Field(..., description="Type of entity")
    canonical_id: Optional[str] = Field(None, description="Reference to canonical entity")
    data: Dict[str, Any] = Field(..., description="Entity data (denormalized)")
    version: int = Field(..., description="Version number")
    is_public: bool = Field(..., description="Whether publicly visible")
    created_by: str = Field(..., description="Creator user UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    tags: Optional[List[str]] = Field(None, description="List of tag names")

    model_config = ConfigDict(from_attributes=True)


class CommonsEntitiesListResponse(BaseModel):
    """Schema for commons entities list response."""

    entities: List[CommonsEntityResponse] = Field(..., description="List of entities")
    total: int = Field(..., description="Total number of entities")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
    pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entities": [],
                "total": 0,
                "skip": 0,
                "limit": 50,
                "pages": 0,
            }
        }
    )


# ==================== Tag Schemas ====================


class TagCreate(BaseModel):
    """Schema for creating a tag."""

    name: str = Field(..., min_length=1, max_length=255, description="Tag name")
    description: Optional[str] = Field(None, description="Tag description")

    model_config = ConfigDict(
        json_schema_extra={"example": {"name": "weapons", "description": "Weapon items"}}
    )


class TagResponse(BaseModel):
    """Schema for tag API response."""

    id: str = Field(..., description="Tag UUID")
    name: str = Field(..., description="Tag name")
    description: Optional[str] = Field(None, description="Tag description")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class TagsListResponse(BaseModel):
    """Schema for tags list response."""

    tags: List[TagResponse] = Field(..., description="List of tags")
    total: int = Field(..., description="Total number of tags")

    model_config = ConfigDict(json_schema_extra={"example": {"tags": [], "total": 0}})
