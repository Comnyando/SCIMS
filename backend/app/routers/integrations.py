"""
Integrations router for managing external service integrations.

This router provides endpoints for:
- Creating and managing integrations
- Testing integration connections
- Viewing integration logs
- Webhook management
"""

from typing import Optional
from math import ceil
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.integration import Integration
from app.models.integration_log import IntegrationLog
from app.models.organization_member import OrganizationMember
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationResponse,
    IntegrationTestResponse,
    IntegrationLogResponse,
    IntegrationLogsResponse,
    IntegrationsListResponse,
)
from app.utils.encryption import encrypt_value, decrypt_value
from app.services.integration_base import BaseIntegration
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/integrations", tags=["integrations"])


def validate_integration_access(integration: Integration, current_user: User, db: Session) -> None:
    """
    Validate that the current user has access to an integration.

    Users can access:
    - Their own integrations
    - Organization integrations (if they're a member)

    Raises HTTPException if access is denied.
    """
    # Check if user owns the integration
    if integration.user_id == current_user.id:
        return

    # Check if integration belongs to an organization the user is a member of
    if integration.organization_id:
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == integration.organization_id,
                OrganizationMember.user_id == current_user.id,
            )
            .first()
        )
        if membership:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to this integration",
    )


def build_integration_response(integration: Integration) -> dict:
    """Build an integration response dictionary."""
    return {
        "id": str(integration.id),
        "name": integration.name,
        "type": integration.type,
        "status": integration.status,
        "user_id": integration.user_id,
        "organization_id": integration.organization_id,
        "webhook_url": integration.webhook_url,
        "config_data": integration.config_data if integration.config_data is not None else {},
        "last_tested_at": integration.last_tested_at,
        "last_error": integration.last_error,
        "created_at": integration.created_at,
        "updated_at": integration.updated_at,
    }


@router.get("", response_model=IntegrationsListResponse)
async def list_integrations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    type_filter: Optional[str] = Query(None, description="Filter by type"),
    organization_id: Optional[str] = Query(None, description="Filter by organization UUID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List integrations accessible to the current user."""
    query = db.query(Integration)

    # Build access control filter
    user_org_ids = [
        str(row[0])
        for row in db.query(OrganizationMember.organization_id)
        .filter(OrganizationMember.user_id == current_user.id)
        .all()
        if row[0]
    ]

    if user_org_ids:
        query = query.filter(
            or_(
                Integration.user_id == current_user.id,
                Integration.organization_id.in_(user_org_ids),
            )
        )
    else:
        query = query.filter(Integration.user_id == current_user.id)

    # Apply filters
    if status_filter:
        query = query.filter(Integration.status == status_filter)
    if type_filter:
        query = query.filter(Integration.type == type_filter)
    if organization_id:
        query = query.filter(Integration.organization_id == organization_id)

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    integrations = query.order_by(Integration.created_at.desc()).offset(skip).limit(limit).all()

    # Build response
    integration_responses = [
        build_integration_response(integration) for integration in integrations
    ]

    return {
        "integrations": integration_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }


@router.post("", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new integration."""
    # Validate organization access if specified
    if integration_data.organization_id:
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == integration_data.organization_id,
                OrganizationMember.user_id == current_user.id,
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of the organization to create integrations for it",
            )

    # Encrypt API key and secret if provided
    api_key_encrypted = None
    api_secret_encrypted = None
    if integration_data.api_key:
        api_key_encrypted = encrypt_value(integration_data.api_key)
    if integration_data.api_secret:
        api_secret_encrypted = encrypt_value(integration_data.api_secret)

    # Create integration
    new_integration = Integration(
        name=integration_data.name,
        type=integration_data.type,
        status="active",
        user_id=current_user.id,
        organization_id=integration_data.organization_id,
        webhook_url=integration_data.webhook_url,
        api_key_encrypted=api_key_encrypted,
        api_secret_encrypted=api_secret_encrypted,
        config_data=integration_data.config_data,
    )

    db.add(new_integration)
    db.commit()
    db.refresh(new_integration)

    # Build response
    response_dict = build_integration_response(new_integration)
    return IntegrationResponse.model_validate(response_dict)


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get integration details by ID."""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id '{integration_id}' not found",
        )

    # Check access
    validate_integration_access(integration, current_user, db)

    # Build response
    response_dict = build_integration_response(integration)
    return IntegrationResponse.model_validate(response_dict)


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: str,
    integration_data: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing integration."""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id '{integration_id}' not found",
        )

    # Check access
    validate_integration_access(integration, current_user, db)

    # Update fields
    if integration_data.name is not None:
        integration.name = integration_data.name
    if integration_data.status is not None:
        integration.status = integration_data.status
    if integration_data.webhook_url is not None:
        integration.webhook_url = integration_data.webhook_url
    if integration_data.config_data is not None:
        integration.config_data = integration_data.config_data

    # Handle API key/secret updates
    if integration_data.api_key is not None:
        if integration_data.api_key:  # Not empty string
            integration.api_key_encrypted = encrypt_value(integration_data.api_key)
        else:  # Empty string means clear it
            integration.api_key_encrypted = None

    if integration_data.api_secret is not None:
        if integration_data.api_secret:  # Not empty string
            integration.api_secret_encrypted = encrypt_value(integration_data.api_secret)
        else:  # Empty string means clear it
            integration.api_secret_encrypted = None

    db.commit()
    db.refresh(integration)

    # Build response
    response_dict = build_integration_response(integration)
    return IntegrationResponse.model_validate(response_dict)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an integration."""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id '{integration_id}' not found",
        )

    # Check access
    validate_integration_access(integration, current_user, db)

    db.delete(integration)
    db.commit()

    return None


@router.post("/{integration_id}/test", response_model=IntegrationTestResponse)
async def test_integration(
    integration_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Test an integration connection/configuration."""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id '{integration_id}' not found",
        )

    # Check access
    validate_integration_access(integration, current_user, db)

    # Create a basic integration instance for testing
    # For now, we'll do a basic connectivity test
    # Real integrations should implement BaseIntegration
    start_time = datetime.now(timezone.utc)

    try:
        # Basic validation test
        if integration.type == "webhook" and not integration.webhook_url:
            raise ValueError("Webhook URL is required for webhook integrations")

        # For now, just mark as tested if basic validation passes
        # In a real implementation, this would call the actual integration's test_connection method
        integration.last_tested_at = datetime.now(timezone.utc)
        integration.status = "active"
        integration.last_error = None

        execution_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        # Log the test
        log = IntegrationLog(
            integration_id=integration.id,
            event_type="test",
            status="success",
            response_data={"message": "Basic validation passed"},
            execution_time_ms=execution_time,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(log)

        db.commit()

        return IntegrationTestResponse(
            success=True,
            message="Integration test successful",
            data={"execution_time_ms": execution_time},
        )

    except Exception as e:
        execution_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        error_message = str(e)

        integration.status = "error"
        integration.last_error = error_message

        # Log the error
        log = IntegrationLog(
            integration_id=integration.id,
            event_type="test",
            status="error",
            error_message=error_message,
            execution_time_ms=execution_time,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(log)

        db.commit()

        return IntegrationTestResponse(
            success=False,
            message=f"Integration test failed: {error_message}",
            data=None,
        )


@router.get("/{integration_id}/logs", response_model=IntegrationLogsResponse)
async def get_integration_logs(
    integration_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get logs for an integration."""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id '{integration_id}' not found",
        )

    # Check access
    validate_integration_access(integration, current_user, db)

    # Build query
    query = db.query(IntegrationLog).filter(IntegrationLog.integration_id == integration_id)

    # Apply filters
    if event_type:
        query = query.filter(IntegrationLog.event_type == event_type)
    if status_filter:
        query = query.filter(IntegrationLog.status == status_filter)

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    logs = query.order_by(IntegrationLog.timestamp.desc()).offset(skip).limit(limit).all()

    # Build response
    log_responses = [
        IntegrationLogResponse.model_validate(
            {
                "id": str(log.id),
                "integration_id": log.integration_id,
                "event_type": log.event_type,
                "status": log.status,
                "request_data": log.request_data,
                "response_data": log.response_data,
                "error_message": log.error_message,
                "execution_time_ms": log.execution_time_ms,
                "timestamp": log.timestamp,
            }
        )
        for log in logs
    ]

    return {
        "logs": log_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": ceil(total / limit) if limit > 0 else 0,
    }
