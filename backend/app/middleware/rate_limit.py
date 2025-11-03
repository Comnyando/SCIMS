"""
Rate limiting middleware for FastAPI.

Provides per-user and per-IP rate limiting using Redis.
"""

import time
from typing import Optional, Callable, Any
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis

from app.config import settings


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get a Redis client instance.

    Uses fast-fail connection settings to avoid blocking in tests.
    """
    try:
        redis_url = getattr(settings, "redis_url", None)
        # Return None if redis_url is empty string, None, or not set
        if not redis_url or redis_url.strip() == "":
            return None

        # Use connection pool with timeout to fail fast
        # socket_connect_timeout: fail fast if can't connect (lower for tests)
        # socket_timeout: fail fast on operations
        # health_check_interval: check connection health
        return redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=0.1,  # 100ms timeout for connection (fast fail in tests)
            socket_timeout=0.1,  # 100ms timeout for operations
            health_check_interval=30,  # Check connection every 30s
            retry_on_timeout=False,  # Don't retry on timeout
        )
    except Exception:
        return None


def get_client_identifier(request: Request) -> str:
    """
    Get a unique identifier for rate limiting.

    Prefers authenticated user ID, falls back to IP address.
    """
    # Check if user is authenticated (would need to be set by auth middleware)
    # For now, use IP address
    client_ip = request.client.host if request.client else "unknown"

    # If we have a user ID from the request state (set by auth middleware), use it
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"

    return f"ip:{client_ip}"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.

    Configurable rate limits per endpoint pattern.
    """

    def __init__(
        self,
        app,
        default_requests_per_minute: int = 60,
        submission_requests_per_minute: int = 10,
        public_requests_per_minute: int = 120,
    ):
        super().__init__(app)
        self.default_requests_per_minute = default_requests_per_minute
        self.submission_requests_per_minute = submission_requests_per_minute
        self.public_requests_per_minute = public_requests_per_minute
        # Use property-based lazy initialization so test mocking works correctly
        # Each call to redis_client will call get_redis_client(), allowing monkeypatching

    @property
    def redis_client(self) -> Optional[redis.Redis]:
        """Lazy initialization of Redis client."""
        # Always call get_redis_client() to allow test mocking via monkeypatch
        return get_redis_client()

    def get_rate_limit(self, path: str) -> int:
        """Determine rate limit based on path."""
        # Submission endpoints have stricter limits
        if "/commons/submit" in path or "/commons/submissions" in path:
            return self.submission_requests_per_minute

        # Public endpoints have more lenient limits
        if path.startswith("/public"):
            return self.public_requests_per_minute

        # Default limit
        return self.default_requests_per_minute

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        """
        Process request with rate limiting.

        Skips rate limiting if Redis is unavailable.
        """
        # Skip rate limiting if Redis is not available
        if not self.redis_client:
            return await call_next(request)

        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        client_id = get_client_identifier(request)
        rate_limit = self.get_rate_limit(request.url.path)

        # Create rate limit key
        minute = int(time.time() / 60)
        rate_limit_key = f"rate_limit:{client_id}:{request.url.path}:{minute}"

        try:
            # Get current count
            current_count = self.redis_client.get(rate_limit_key)

            if current_count is None:
                # First request in this minute, set counter with 60 second expiry
                self.redis_client.setex(rate_limit_key, 60, 1)
                current_count = 1
            else:
                current_count = int(current_count)
                if current_count >= rate_limit:
                    # Rate limit exceeded
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded: {rate_limit} requests per minute. Please try again later.",
                        headers={"Retry-After": "60"},
                    )
                # Increment counter
                self.redis_client.incr(rate_limit_key)

            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, rate_limit - current_count))
            response.headers["X-RateLimit-Reset"] = str((minute + 1) * 60)

            return response

        except HTTPException:
            raise
        except Exception:
            # If rate limiting fails, allow the request to proceed
            # (fail open to avoid breaking the service)
            return await call_next(request)
