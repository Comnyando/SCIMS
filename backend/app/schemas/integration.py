"""
Pydantic schemas for integrations API.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, HttpUrl


class IntegrationBase(BaseModel):
    """Base schema for integration with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Integration name")
    type: str = Field(
        ..., min_length=1, max_length=100, description="Integration type (webhook, api, etc.)"
    )
    organization_id: Optional[str] = Field(None, description="Organization UUID (optional)")
    webhook_url: Optional[str] = Field(
        None, max_length=500, description="Webhook URL for receiving events"
    )
    config_data: Optional[Dict[str, Any]] = Field(
        None, description="Additional configuration data (JSON)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Discord Webhook",
                "type": "webhook",
                "organization_id": "990e8400-e29b-41d4-a716-446655440000",
                "webhook_url": "https://discord.com/api/webhooks/...",
                "config_data": {"channel": "inventory-updates"},
            }
        }
    )


class IntegrationCreate(IntegrationBase):
    """Schema for creating a new integration."""

    api_key: Optional[str] = Field(None, description="API key (will be encrypted)")
    api_secret: Optional[str] = Field(None, description="API secret (will be encrypted)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "External API Integration",
                "type": "api",
                "api_key": "your-api-key-here",
                "api_secret": "your-api-secret-here",
                "config_data": {"base_url": "https://api.example.com"},
            }
        }
    )


class IntegrationUpdate(BaseModel):
    """Schema for updating an existing integration."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Integration name")
    status: Optional[str] = Field(None, description="Integration status (active, inactive, error)")
    webhook_url: Optional[str] = Field(None, max_length=500, description="Webhook URL")
    config_data: Optional[Dict[str, Any]] = Field(None, description="Configuration data")
    api_key: Optional[str] = Field(
        None, description="API key (will be encrypted, use null to clear)"
    )
    api_secret: Optional[str] = Field(
        None, description="API secret (will be encrypted, use null to clear)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Integration Name",
                "status": "active",
                "webhook_url": "https://discord.com/api/webhooks/...",
            }
        }
    )


class IntegrationResponse(IntegrationBase):
    """Schema for integration API responses."""

    id: str = Field(..., description="Integration UUID")
    user_id: str = Field(..., description="User UUID who created this integration")
    status: str = Field(..., description="Integration status (active, inactive, error)")
    last_tested_at: Optional[datetime] = Field(None, description="Last successful test timestamp")
    last_error: Optional[str] = Field(None, description="Last error message")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Note: api_key_encrypted and api_secret_encrypted are NOT included in responses
    # for security reasons

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "aa0e8400-e29b-41d4-a716-446655440000",
                "name": "Discord Webhook",
                "type": "webhook",
                "status": "active",
                "user_id": "bb0e8400-e29b-41d4-a716-446655440000",
                "organization_id": "990e8400-e29b-41d4-a716-446655440000",
                "webhook_url": "https://discord.com/api/webhooks/...",
                "last_tested_at": "2024-01-15T10:30:00Z",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        },
    )


class IntegrationTestResponse(BaseModel):
    """Schema for integration test response."""

    success: bool = Field(..., description="Whether the test was successful")
    message: str = Field(..., description="Test result message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional test data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Connection test successful",
                "data": {"response_time_ms": 150, "status_code": 200},
            }
        }
    )


class IntegrationLogResponse(BaseModel):
    """Schema for integration log entry response."""

    id: str = Field(..., description="Log entry UUID")
    integration_id: str = Field(..., description="Integration UUID")
    event_type: str = Field(..., description="Type of event")
    status: str = Field(..., description="Log status (success, error, pending)")
    request_data: Optional[Dict[str, Any]] = Field(None, description="Request data")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error_message: Optional[str] = Field(None, description="Error message")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    timestamp: datetime = Field(..., description="Log timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "cc0e8400-e29b-41d4-a716-446655440000",
                "integration_id": "aa0e8400-e29b-41d4-a716-446655440000",
                "event_type": "test",
                "status": "success",
                "execution_time_ms": 150,
                "timestamp": "2024-01-15T10:30:00Z",
            }
        },
    )


class IntegrationLogsResponse(BaseModel):
    """Schema for integration logs list response."""

    logs: List[IntegrationLogResponse] = Field(..., description="List of log entries")
    total: int = Field(..., description="Total number of logs")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
    pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "logs": [],
                "total": 0,
                "skip": 0,
                "limit": 50,
                "pages": 0,
            }
        }
    )


class IntegrationsListResponse(BaseModel):
    """Schema for integrations list response."""

    integrations: List[IntegrationResponse] = Field(..., description="List of integrations")
    total: int = Field(..., description="Total number of integrations")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
    pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "integrations": [],
                "total": 0,
                "skip": 0,
                "limit": 50,
                "pages": 0,
            }
        }
    )
