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
from app.models.user import User
from app.core.security import hash_password, create_access_token

# Import all models to ensure they're registered with Base.metadata
from app.models import (  # noqa: F401
    user,
    organization,
    organization_member,
    location,
    item,
    item_stock,
    item_history,
    ship,
    blueprint,
    craft,
    craft_ingredient,
    resource_source,
    source_verification_log,
    goal,
    goal_item,
    usage_event,
    recipe_usage_stats,
    integration,
    integration_log,
    commons_submission,
    commons_moderation_action,
    commons_entity,
    commons_entity_tag,
    tag,
    entity_alias,
    duplicate_group,
)

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

# Replace PostgreSQL-specific types with SQLite-compatible types
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import JSON

for table in Base.metadata.tables.values():
    for column in table.columns.values():
        if isinstance(column.type, UUID):
            column.type = String(36)
        elif isinstance(column.type, JSONB):
            # Convert JSONB to JSON for SQLite compatibility
            # Preserve nullable and other column properties
            jsonb_type = column.type
            column.type = JSON(none_as_null=jsonb_type.astext_type is not None)

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
def client(db_session, monkeypatch):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Disable Redis in tests to avoid connection attempts and timeouts
    # This significantly speeds up tests by skipping Redis operations
    import app.utils.commons_cache
    import app.middleware.rate_limit
    
    def mock_get_redis_client():
        """Return None to disable Redis in tests."""
        return None
    
    # Override Redis client functions to return None immediately
    # This bypasses any connection attempts and prevents timeouts
    # Since RateLimitMiddleware.redis_client is a property that calls get_redis_client(),
    # mocking the function will work correctly for all middleware instances
    monkeypatch.setattr(app.utils.commons_cache, "get_redis_client", mock_get_redis_client)
    monkeypatch.setattr(app.middleware.rate_limit, "get_redis_client", mock_get_redis_client)
    
    # Use the app instance from app.main (FastAPI instance)
    from app.main import app as fastapi_app
    fastapi_app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(fastapi_app) as test_client:
        yield test_client
    
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("testpass123"),
        is_active=True,
        analytics_consent=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(db_session):
    """Create another test user."""
    user = User(
        email="otheruser@example.com",
        username="otheruser",
        hashed_password=hash_password("testpass123"),
        is_active=True,
        analytics_consent=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Return auth headers for test user."""
    token = create_access_token({"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_organization(test_user, db_session):
    """Create a test organization with test_user as owner."""
    from app.models.organization import Organization
    from app.models.organization_member import OrganizationMember
    
    org = Organization(
        name="Test Organization",
        slug="test-org",
        description="A test organization",
    )
    db_session.add(org)
    db_session.flush()
    
    membership = OrganizationMember(
        organization_id=org.id,
        user_id=test_user.id,
        role="owner",
    )
    db_session.add(membership)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def test_items(db_session):
    """Create a set of test items."""
    from app.models.item import Item
    
    items = [
        Item(name="Iron Ore", description="Raw iron ore", category="Materials"),
        Item(name="Steel Ingot", description="Refined steel", category="Components"),
        Item(name="Component A", description="Component A", category="Components"),
        Item(name="Component B", description="Component B", category="Components"),
    ]
    db_session.add_all(items)
    db_session.commit()
    for item in items:
        db_session.refresh(item)
    return items


@pytest.fixture
def test_location(test_user, db_session):
    """Create a test location owned by test_user."""
    from app.models.location import Location
    
    location = Location(
        name="Test Station",
        type="station",
        owner_type="user",
        owner_id=test_user.id,
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def test_org_location(test_organization, test_user, db_session):
    """Create a test location owned by test_organization."""
    from app.models.location import Location
    
    location = Location(
        name="Org Station",
        type="station",
        owner_type="organization",
        owner_id=test_organization.id,
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def test_item_stocks(test_items, test_location, test_user, db_session):
    """Create test item stocks with sufficient quantities."""
    from app.models.item_stock import ItemStock
    from decimal import Decimal
    
    stocks = []
    for item in test_items:
        stock = ItemStock(
            item_id=item.id,
            location_id=test_location.id,
            quantity=Decimal("100.0"),
            reserved_quantity=Decimal("0.0"),
            updated_by=test_user.id,
        )
        stocks.append(stock)
    
    db_session.add_all(stocks)
    db_session.commit()
    for stock in stocks:
        db_session.refresh(stock)
    return stocks


@pytest.fixture
def test_blueprint(test_user, test_items, db_session):
    """Create a test blueprint."""
    from app.models.blueprint import Blueprint
    from decimal import Decimal
    
    blueprint = Blueprint(
        name="Test Blueprint",
        description="A test blueprint",
        category="Crafting",
        crafting_time_minutes=60,
        output_item_id=test_items[1].id,  # Steel Ingot
        output_quantity=Decimal("1.0"),
        blueprint_data={
            "ingredients": [
                {"item_id": test_items[0].id, "quantity": 10.0, "optional": False}
            ]
        },
        created_by=test_user.id,
        is_public=False,
        usage_count=0,
    )
    db_session.add(blueprint)
    db_session.commit()
    db_session.refresh(blueprint)
    return blueprint


@pytest.fixture
def test_public_blueprint(test_user, test_items, db_session):
    """Create a public test blueprint."""
    from app.models.blueprint import Blueprint
    from decimal import Decimal
    
    blueprint = Blueprint(
        name="Public Blueprint",
        description="A publicly shared blueprint",
        category="Crafting",
        crafting_time_minutes=30,
        output_item_id=test_items[1].id,
        output_quantity=Decimal("1.0"),
        blueprint_data={
            "ingredients": [
                {"item_id": test_items[0].id, "quantity": 5.0, "optional": False}
            ]
        },
        created_by=test_user.id,
        is_public=True,
        usage_count=0,
    )
    db_session.add(blueprint)
    db_session.commit()
    db_session.refresh(blueprint)
    return blueprint


@pytest.fixture
def test_craft(test_user, test_blueprint, test_location, db_session):
    """Create a test craft."""
    from app.models.craft import Craft, CRAFT_STATUS_PLANNED
    from app.models.craft_ingredient import CraftIngredient, INGREDIENT_STATUS_PENDING, SOURCE_TYPE_STOCK
    from decimal import Decimal
    
    craft = Craft(
        blueprint_id=test_blueprint.id,
        requested_by=test_user.id,
        status=CRAFT_STATUS_PLANNED,
        priority=5,
        output_location_id=test_location.id,
    )
    db_session.add(craft)
    db_session.flush()
    
    # Create craft ingredients
    ingredients_data = test_blueprint.blueprint_data["ingredients"]
    for ingredient_data in ingredients_data:
        craft_ingredient = CraftIngredient(
            craft_id=craft.id,
            item_id=ingredient_data["item_id"],
            required_quantity=Decimal(str(ingredient_data["quantity"])),
            source_location_id=test_location.id,
            source_type=SOURCE_TYPE_STOCK,
            status=INGREDIENT_STATUS_PENDING,
        )
        db_session.add(craft_ingredient)
    
    db_session.commit()
    db_session.refresh(craft)
    return craft


@pytest.fixture
def test_integration(test_user, db_session):
    """Create a test integration."""
    from app.models.integration import Integration
    
    integration = Integration(
        name="Test Integration",
        type="webhook",
        status="active",
        webhook_url="https://example.com/webhook",
        config={"auto_sync": True},
        user_id=test_user.id,
    )
    db_session.add(integration)
    db_session.commit()
    db_session.refresh(integration)
    return integration