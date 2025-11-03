"""
Webhooks router for receiving incoming webhook events.

This router handles incoming webhook calls from external services.
"""

from typing import Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.integration import Integration
from app.models.integration_log import IntegrationLog
from app.config import settings

router = APIRouter(prefix=f"{settings.api_v1_prefix}/webhooks", tags=["webhooks"])


@router.post("/receive/{integration_id}", status_code=status.HTTP_200_OK)
async def receive_webhook(
    integration_id: str,
    request: Request,
    db: Session = Depends(get_db),
    x_webhook_signature: str | None = Header(None, alias="X-Webhook-Signature"),
):
    """
    Receive an incoming webhook event for an integration.

    This endpoint is publicly accessible and accepts webhook calls from external services.
    The integration_id identifies which integration this webhook belongs to.
    """
    # Find the integration
    integration = db.query(Integration).filter(Integration.id == integration_id).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration with id '{integration_id}' not found",
        )

    # Check if integration is active
    if integration.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integration is not active (status: {integration.status})",
        )

    # Parse request body
    try:
        body_data = await request.json()
    except Exception:
        body_data = None

    # Get headers
    headers = dict(request.headers)

    start_time = datetime.now(timezone.utc)

    try:
        # TODO: Validate webhook signature if configured
        # For now, we just log the event

        # Create log entry
        log = IntegrationLog(
            integration_id=integration.id,
            event_type="webhook_received",
            status="success",
            request_data={
                "headers": headers,
                "body": body_data,
                "method": request.method,
                "path": request.url.path,
            },
            response_data={"message": "Webhook received successfully"},
            execution_time_ms=int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000),
            timestamp=datetime.now(timezone.utc),
        )
        db.add(log)
        db.commit()

        # TODO: Process webhook event based on integration type
        # This would trigger appropriate handlers based on the integration configuration

        return {"status": "ok", "message": "Webhook received"}

    except Exception as e:
        error_message = str(e)
        execution_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        # Log the error
        log = IntegrationLog(
            integration_id=integration.id,
            event_type="webhook_received",
            status="error",
            request_data={
                "headers": headers,
                "body": body_data,
                "method": request.method,
                "path": request.url.path,
            },
            error_message=error_message,
            execution_time_ms=execution_time,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(log)
        db.commit()

        # Update integration status on error
        integration.status = "error"
        integration.last_error = error_message
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {error_message}",
        )
