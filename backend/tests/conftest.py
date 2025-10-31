"""
Pytest configuration and fixtures for test suite.
"""

import os
import pytest
from sqlalchemy import create_engine, event, String, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import OperationalError
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.models.base import Base

# Import all models to ensure they're registered with Base.metadata
from app.models import user, organization, organization_member  # noqa: F401

# Use an in-memory SQLite database for tests
TEST_DB_PATH = "sqlite:///:memory:"

# Enable foreign keys for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign keys for SQLite."""
    if dbapi_conn.__class__.__module__ == "sqlite3":
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Replace UUID types with String for SQLite compatibility
from sqlalchemy.dialects.postgresql import UUID

for table in Base.metadata.tables.values():
    for column in table.columns.values():
        if isinstance(column.type, UUID):
            column.type = String(36)

# Create test engine with StaticPool to ensure same connection for :memory: database
test_engine = create_engine(
    TEST_DB_PATH,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _drop_all_indexes(conn_or_engine):
    """Drop all indexes manually for SQLite compatibility."""
    # Handle both connection and engine
    if hasattr(conn_or_engine, 'execute'):
        conn = conn_or_engine
        close_after = False
    else:
        conn = conn_or_engine.connect()
        close_after = True
    
    try:
        # Query sqlite_master directly to find all indexes
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        ))
        indexes = [row[0] for row in result]
        for index_name in indexes:
            try:
                conn.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
            except OperationalError:
                pass  # Index might not exist or already dropped
        if close_after:
            conn.commit()
    finally:
        if close_after:
            conn.close()


def _create_all_with_index_handling(engine):
    """Create all tables and indexes, handling existing index errors for SQLite."""
    # Use a single connection/transaction to ensure consistency
    with engine.begin() as conn:
        # Drop all existing indexes and tables first (using same connection)
        _drop_all_indexes(conn)
        Base.metadata.drop_all(bind=conn, checkfirst=True)
        
        # Create tables (this may also create indexes, which we'll handle)
        for table in Base.metadata.tables.values():
            try:
                table.create(bind=conn, checkfirst=True)
            except OperationalError as e:
                # If it's an index error, the table was created but index failed
                # Continue and we'll handle indexes separately
                if "already exists" in str(e) and "index" in str(e).lower():
                    pass  # Table exists, index will be handled below
                else:
                    raise
        
        # Ensure all indexes exist, ignoring "already exists" errors
        for table in Base.metadata.tables.values():
            for index in table.indexes:
                try:
                    index.create(bind=conn)
                except OperationalError as e:
                    if "already exists" not in str(e):
                        raise  # Re-raise if it's a different error


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables and indexes with special handling (includes cleanup)
    _create_all_with_index_handling(test_engine)
    
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Clean up: drop all indexes and tables
        _drop_all_indexes(test_engine)
        Base.metadata.drop_all(bind=test_engine, checkfirst=True)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
