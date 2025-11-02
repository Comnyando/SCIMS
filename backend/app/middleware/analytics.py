"""
Analytics middleware for logging usage events.

Only logs events if the user has given explicit consent (analytics_consent = true).
"""

from typing import Callable, Optional, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.usage_event import UsageEvent
from app.models.user import User
from app.core.security import decode_token


def anonymize_ip(ip_address: str) -> str:
    """
    Anonymize IP address by removing last octet (IPv4) or last 64 bits (IPv6).

    Privacy safeguard: Only store anonymized IP addresses.
    """
    if not ip_address:
        return ip_address

    # IPv4: Remove last octet (e.g., 192.168.1.123 -> 192.168.1.0)
    if "." in ip_address:
        parts = ip_address.split(".")
        if len(parts) == 4:
            return ".".join(parts[:3]) + ".0"

    # IPv6: Remove last 64 bits (heuristic: truncate after last colon group)
    if ":" in ip_address:
        # Simple approach: truncate to first 3 groups
        parts = ip_address.split(":")
        if len(parts) > 3:
            return ":".join(parts[:3]) + ":0:0:0:0"

    return ip_address


def truncate_user_agent(user_agent: Optional[str], max_length: int = 500) -> str:
    """
    Truncate user agent string to max_length.

    Privacy safeguard: Limit stored user agent data.
    """
    if not user_agent:
        return ""
    return user_agent[:max_length] if len(user_agent) > max_length else user_agent


def log_usage_event(
    db: Session,
    user_id: Optional[str],
    event_type: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    event_data: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    Log a usage event if user has consented.

    Only logs events for users who have analytics_consent = true.
    """
    # If user_id is provided, check consent
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.analytics_consent:
            return  # Don't log if user hasn't consented

    # Anonymize and truncate sensitive data
    anonymized_ip = anonymize_ip(ip_address) if ip_address else None
    truncated_ua = truncate_user_agent(user_agent)

    # Create event
    event = UsageEvent(
        user_id=user_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        event_data=event_data,
        ip_address=anonymized_ip,
        user_agent=truncated_ua,
    )

    db.add(event)
    db.commit()


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log API usage events.

    Logs events for:
    - Blueprint usage (craft creation)
    - Goal creation/updates
    - Item stock updates
    - Other key actions

    Only logs if user has analytics_consent = true.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process request and log events as needed.
        """
        # Extract user_id from Authorization header if present
        user_id = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_token(token, token_type="access")
            if payload:
                user_id = payload.get("sub")

        # Process request
        response = await call_next(request)

        # Only log successful requests (2xx status)
        if 200 <= response.status_code < 300:
            # Determine event type based on path and method
            event_type = None
            entity_type = None
            entity_id = None
            event_data = None

            path = request.url.path
            method = request.method

            # Extract entity ID from path if present
            path_parts = path.strip("/").split("/")
            if len(path_parts) >= 3:
                entity_id = path_parts[-1] if path_parts[-1] not in ["new", "edit"] else None

            # Blueprint usage (craft creation)
            # Note: Detailed logging (including blueprint_id) should be done in route handler
            if path.startswith("/api/v1/crafts") and method == "POST":
                event_type = "blueprint_used"
                entity_type = "craft"

            # Goal creation
            elif path.startswith("/api/v1/goals") and method == "POST":
                event_type = "goal_created"
                entity_type = "goal"

            # Goal update
            elif path.startswith("/api/v1/goals") and method == "PATCH" and entity_id:
                event_type = "goal_updated"
                entity_type = "goal"

            # Item stock update
            elif path.startswith("/api/v1/inventory") and method in ["POST", "PATCH", "PUT"]:
                event_type = "item_stock_updated"
                entity_type = "item_stock"

            # Blueprint creation
            elif path.startswith("/api/v1/blueprints") and method == "POST":
                event_type = "blueprint_created"
                entity_type = "blueprint"

            # Log the event if we identified one
            if event_type:
                # Get IP and user agent
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")

                # Use a separate DB session for logging to avoid transaction issues
                db = SessionLocal()
                try:
                    log_usage_event(
                        db=db,
                        user_id=user_id,
                        event_type=event_type,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        event_data=event_data,
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                except Exception:
                    # Don't fail the request if logging fails
                    db.rollback()
                finally:
                    db.close()

        return response
