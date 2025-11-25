"""
Database connection and session management.

This module provides the SQLAlchemy engine and session factory with
proper connection pooling for production use. The configuration is
flexible and can be adjusted via environment variables.
"""

from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings


# Configure connection pool
# These settings balance performance and resource usage
# Increased for better concurrent request handling
pool_config = {
    "pool_size": 20,  # Number of connections to maintain in the pool (increased from 5)
    "max_overflow": 30,  # Max connections beyond pool_size (increased from 10)
    "pool_timeout": 30,  # Seconds to wait for a connection from the pool
    "pool_recycle": 3600,  # Recycle connections after 1 hour (prevents stale connections)
    "pool_pre_ping": True,  # Verify connections before using them (handles DB restarts)
    "echo": False,  # Set to True for SQL query logging (useful for debugging)
}

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    future=True,
    **pool_config,
)

# Session factory for creating database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,  # Don't auto-flush (call session.flush() explicitly)
    autocommit=False,  # Use explicit transactions
    expire_on_commit=False,  # Keep objects accessible after commit
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get a database session.

    Usage in FastAPI routes:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            # Use db session here
            pass

    The session is automatically closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
