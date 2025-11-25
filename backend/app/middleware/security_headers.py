"""
Security headers middleware for FastAPI.

Adds security headers to all responses to protect against common vulnerabilities.
"""

from typing import Callable, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Implements OWASP recommended security headers:
    - Content-Security-Policy (CSP)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Strict-Transport-Security (HSTS)
    - Referrer-Policy
    - Permissions-Policy
    """

    def __init__(self, app, hsts_max_age: int = 31536000):
        """
        Initialize security headers middleware.

        Args:
            app: FastAPI application
            hsts_max_age: HSTS max-age in seconds (default: 1 year)
        """
        super().__init__(app)
        self.hsts_max_age = hsts_max_age

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response: Response = await call_next(request)

        # Content Security Policy
        # Allow same-origin, API endpoints, and common CDNs
        # Adjust based on your frontend needs
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # unsafe-inline/eval for Swagger UI
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # XSS Protection (legacy, but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HSTS (only in production with HTTPS)
        # In development, this header should not be set or should have a short max-age
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains; preload"
            )

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature-Policy)
        permissions_policy = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        response.headers["Permissions-Policy"] = permissions_policy

        # Remove server header (if present)
        # MutableHeaders doesn't have pop() in newer Starlette versions
        if "server" in response.headers:
            del response.headers["server"]

        return response
