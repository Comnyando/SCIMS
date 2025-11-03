"""
Base integration framework for external service integrations.

Provides a base class that all integrations should inherit from,
defining the interface and common functionality.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.integration import Integration
from app.models.integration_log import IntegrationLog
from sqlalchemy.orm import Session


class BaseIntegration(ABC):
    """
    Base class for all integration implementations.

    Provides:
    - Standardized interface for integrations
    - Common helper methods
    - Logging functionality
    - Error handling
    """

    def __init__(self, integration: Integration, db: Session):
        """
        Initialize the integration with its configuration.

        Args:
            integration: Integration model instance
            db: Database session
        """
        self.integration = integration
        self.db = db

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the integration connection/configuration.

        Returns:
            Dictionary with test results:
            - success: bool
            - message: str (optional)
            - data: dict (optional, additional test data)
        """
        pass

    @abstractmethod
    async def send_webhook(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a webhook event to the integration endpoint.

        Args:
            event_type: Type of event (e.g., 'inventory_updated', 'craft_completed')
            data: Event data payload

        Returns:
            Dictionary with response:
            - success: bool
            - status_code: int (optional)
            - message: str (optional)
        """
        pass

    def log_event(
        self,
        event_type: str,
        status: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
    ) -> IntegrationLog:
        """
        Log an integration event.

        Args:
            event_type: Type of event (test, webhook_received, webhook_sent, error, etc.)
            status: Log status (success, error, pending)
            request_data: Request data (optional)
            response_data: Response data (optional)
            error_message: Error message if status is error (optional)
            execution_time_ms: Execution time in milliseconds (optional)

        Returns:
            Created IntegrationLog instance
        """
        log = IntegrationLog(
            integration_id=self.integration.id,
            event_type=event_type,
            status=status,
            request_data=request_data,
            response_data=response_data,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            timestamp=datetime.now(),
        )
        self.db.add(log)
        self.db.flush()
        return log

    def update_integration_status(self, status: str, error_message: Optional[str] = None) -> None:
        """
        Update the integration status and last error.

        Args:
            status: New status (active, inactive, error)
            error_message: Error message if status is error (optional)
        """
        self.integration.status = status
        if error_message:
            self.integration.last_error = error_message
        self.db.flush()

    def mark_tested(self) -> None:
        """Mark the integration as successfully tested."""
        self.integration.last_tested_at = datetime.now()
        self.integration.status = "active"
        self.integration.last_error = None
        self.db.flush()
