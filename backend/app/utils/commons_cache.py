"""
Commons caching utilities using Redis.

Provides functions for caching public commons data and cache invalidation.
"""

import json
from typing import Optional, Dict, Any, List, cast
from datetime import timedelta
import redis
from app.config import settings


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get a Redis client instance.

    Returns None if Redis is not configured or unavailable.
    Uses fast-fail connection settings to avoid blocking.
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
        # Redis not available or misconfigured
        return None


def cache_key_public_items(
    tag: Optional[str] = None, search: Optional[str] = None, skip: int = 0, limit: int = 50
) -> str:
    """Generate cache key for public items list."""
    parts = ["commons:public:items"]
    if tag:
        parts.append(f"tag:{tag}")
    if search:
        parts.append(f"search:{search}")
    parts.append(f"skip:{skip}")
    parts.append(f"limit:{limit}")
    return ":".join(parts)


def cache_key_public_recipes(
    tag: Optional[str] = None, search: Optional[str] = None, skip: int = 0, limit: int = 50
) -> str:
    """Generate cache key for public recipes list."""
    parts = ["commons:public:recipes"]
    if tag:
        parts.append(f"tag:{tag}")
    if search:
        parts.append(f"search:{search}")
    parts.append(f"skip:{skip}")
    parts.append(f"limit:{limit}")
    return ":".join(parts)


def cache_key_public_locations(
    tag: Optional[str] = None, search: Optional[str] = None, skip: int = 0, limit: int = 50
) -> str:
    """Generate cache key for public locations list."""
    parts = ["commons:public:locations"]
    if tag:
        parts.append(f"tag:{tag}")
    if search:
        parts.append(f"search:{search}")
    parts.append(f"skip:{skip}")
    parts.append(f"limit:{limit}")
    return ":".join(parts)


def cache_key_public_entity(entity_type: str, entity_id: str) -> str:
    """Generate cache key for a specific public entity."""
    return f"commons:public:{entity_type}:{entity_id}"


def cache_key_tags() -> str:
    """Generate cache key for tags list."""
    return "commons:public:tags"


def get_cached_public_data(key: str) -> Optional[Dict[str, Any]]:
    """
    Get cached public data from Redis.

    Returns None if cache miss or Redis unavailable.
    """
    client = get_redis_client()
    if not client:
        return None

    try:
        cached = client.get(key)
        if cached:
            parsed: Any = json.loads(cached)
            if isinstance(parsed, dict):
                return cast(Dict[str, Any], parsed)
    except Exception:
        pass

    return None


def set_cached_public_data(key: str, data: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
    """
    Cache public data in Redis.

    Returns True if successful, False otherwise.
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        client.setex(key, ttl_seconds, json.dumps(data))
        return True
    except Exception:
        return False


def invalidate_public_cache(entity_type: Optional[str] = None) -> bool:
    """
    Invalidate public commons cache.

    If entity_type is provided, only invalidate that type's cache.
    Otherwise, invalidate all public commons caches.

    Returns True if successful, False otherwise.
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        if entity_type:
            pattern = f"commons:public:{entity_type}:*"
        else:
            pattern = "commons:public:*"

        # Find all matching keys
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)

        # Also invalidate general lists
        if entity_type:
            list_patterns = [
                f"commons:public:{entity_type}*",
                "commons:public:tags",  # Tags might have changed
            ]
        else:
            list_patterns = ["commons:public:*"]

        for pattern in list_patterns:
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)

        return True
    except Exception:
        return False
