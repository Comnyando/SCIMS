"""
Tests for Optimization API endpoints and service.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.location import Location
from app.models.item_stock import ItemStock
from app.models.user import User
from app.models.blueprint import Blueprint
from app.models.craft import Craft, CRAFT_STATUS_PLANNED
from app.models.craft_ingredient import CraftIngredient, SOURCE_TYPE_STOCK
from app.models.resource_source import (
    ResourceSource,
    SOURCE_TYPE_PLAYER_STOCK,
    SOURCE_TYPE_UNIVERSE_LOCATION,
    SOURCE_TYPE_TRADING_POST,
)
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.core.security import create_access_token, hash_password
from app.services.optimization import OptimizationService
from app.schemas.optimization import FindSourcesRequest, SuggestCraftsRequest


@pytest.fixture
def test_user(client, db_session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("testpass123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(client, db_session):
    """Create another test user."""
    user = User(
        email="otheruser@example.com",
        username="otheruser",
        hashed_password=hash_password("testpass123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Return auth headers for test user."""
    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_item(client, db_session):
    """Create a test item."""
    item = Item(
        name="Test Item",
        description="A test item",
        category="Materials",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def test_ingredient_items(client, db_session):
    """Create test ingredient items."""
    item1 = Item(name="Ingredient 1", category="Materials")
    item2 = Item(name="Ingredient 2", category="Materials")
    db_session.add_all([item1, item2])
    db_session.commit()
    db_session.refresh(item1)
    db_session.refresh(item2)
    return [item1, item2]


@pytest.fixture
def test_location(test_user, db_session):
    """Create a test location."""
    location = Location(
        name="Test Location",
        type="station",
        owner_type="user",
        owner_id=test_user.id,
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def test_location_with_stock(test_location, test_item, test_user, db_session):
    """Create a location with stock."""
    stock = ItemStock(
        item_id=test_item.id,
        location_id=test_location.id,
        quantity=Decimal("100.0"),
        reserved_quantity=Decimal("0"),
        updated_by=test_user.id,
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)
    return test_location


@pytest.fixture
def test_resource_source(test_item, test_location, db_session):
    """Create a test resource source."""
    source = ResourceSource(
        item_id=test_item.id,
        source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
        source_identifier="Crusader Mining Outpost",
        available_quantity=Decimal("50.0"),
        cost_per_unit=Decimal("5.0"),
        reliability_score=Decimal("0.75"),
        location_id=test_location.id,
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    return source


@pytest.fixture
def test_blueprint(test_user, test_item, test_ingredient_items, db_session):
    """Create a test blueprint."""
    blueprint = Blueprint(
        name="Test Blueprint",
        description="A test blueprint",
        category="Components",
        crafting_time_minutes=60,
        output_item_id=test_item.id,
        output_quantity=Decimal("10.0"),
        blueprint_data={
            "ingredients": [
                {"item_id": test_ingredient_items[0].id, "quantity": 5.0, "optional": False},
                {"item_id": test_ingredient_items[1].id, "quantity": 2.0, "optional": False},
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
def test_craft(test_user, test_blueprint, test_location, db_session):
    """Create a test craft."""
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
        )
        db_session.add(craft_ingredient)

    db_session.commit()
    db_session.refresh(craft)
    return craft


class TestFindSources:
    """Test find sources endpoint and service."""

    def test_find_sources_from_stock(
        self, client: TestClient, auth_headers: dict, test_item: Item, test_location_with_stock: Location
    ):
        """Test finding sources from own stock."""
        response = client.post(
            "/api/v1/optimization/find-sources",
            json={
                "item_id": test_item.id,
                "required_quantity": 50.0,
                "max_sources": 10,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == test_item.id
        assert data["required_quantity"] == 50.0
        assert len(data["sources"]) > 0
        # First source should be from stock (cost = 0)
        stock_source = next((s for s in data["sources"] if s["source_type"] == "stock"), None)
        assert stock_source is not None
        assert stock_source["cost_per_unit"] == 0.0
        assert stock_source["total_cost"] == 0.0

    def test_find_sources_from_universe(
        self, client: TestClient, auth_headers: dict, test_item: Item, test_resource_source: ResourceSource
    ):
        """Test finding sources from universe locations."""
        response = client.post(
            "/api/v1/optimization/find-sources",
            json={
                "item_id": test_item.id,
                "required_quantity": 50.0,
                "max_sources": 10,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["sources"]) > 0
        # Should include universe source
        universe_source = next(
            (s for s in data["sources"] if s["source_type"] == SOURCE_TYPE_UNIVERSE_LOCATION),
            None,
        )
        assert universe_source is not None
        assert universe_source["reliability_score"] is not None

    def test_find_sources_with_min_reliability(
        self, client: TestClient, auth_headers: dict, test_item: Item, test_resource_source: ResourceSource, db_session: Session
    ):
        """Test finding sources with minimum reliability filter."""
        # Create a low-reliability source
        low_rel_source = ResourceSource(
            item_id=test_item.id,
            source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
            source_identifier="Unreliable Source",
            available_quantity=Decimal("100.0"),
            cost_per_unit=Decimal("1.0"),
            reliability_score=Decimal("0.2"),
        )
        db_session.add(low_rel_source)
        db_session.commit()

        response = client.post(
            "/api/v1/optimization/find-sources",
            json={
                "item_id": test_item.id,
                "required_quantity": 50.0,
                "max_sources": 10,
                "min_reliability": 0.5,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # Should not include low-reliability source
        for source in data["sources"]:
            if source.get("reliability_score") is not None:
                assert source["reliability_score"] >= 0.5

    def test_find_sources_prioritizes_stock(
        self, client: TestClient, auth_headers: dict, test_item: Item, test_location_with_stock: Location, test_resource_source: ResourceSource
    ):
        """Test that own stock is prioritized over universe sources."""
        response = client.post(
            "/api/v1/optimization/find-sources",
            json={
                "item_id": test_item.id,
                "required_quantity": 50.0,
                "max_sources": 10,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["sources"]) > 0
        # First source should be stock (cost = 0)
        assert data["sources"][0]["cost_per_unit"] == 0.0
        assert data["sources"][0]["source_type"] == "stock"

    def test_find_sources_item_not_found(self, client: TestClient, auth_headers: dict):
        """Test finding sources for non-existent item."""
        response = client.post(
            "/api/v1/optimization/find-sources",
            json={
                "item_id": "00000000-0000-0000-0000-000000000000",
                "required_quantity": 50.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_find_sources_service(self, db_session: Session, test_user: User, test_item: Item, test_location_with_stock: Location):
        """Test OptimizationService.find_sources_for_item directly."""
        service = OptimizationService(db_session, test_user.id)
        request = FindSourcesRequest(
            item_id=test_item.id,
            required_quantity=Decimal("50.0"),
            max_sources=10,
        )
        response = service.find_sources_for_item(request)
        assert response.item_id == test_item.id
        assert response.required_quantity == Decimal("50.0")
        assert len(response.sources) > 0
        assert response.total_available > 0
        assert response.has_sufficient


class TestSuggestCrafts:
    """Test suggest crafts endpoint and service."""

    def test_suggest_crafts(
        self, client: TestClient, auth_headers: dict, test_item: Item, test_blueprint: Blueprint
    ):
        """Test suggesting crafts for a target item."""
        response = client.post(
            "/api/v1/optimization/suggest-crafts",
            json={
                "target_item_id": test_item.id,
                "target_quantity": 100.0,
                "max_suggestions": 10,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["target_item_id"] == test_item.id
        assert data["target_quantity"] == 100.0
        assert len(data["suggestions"]) > 0
        suggestion = data["suggestions"][0]
        assert suggestion["blueprint_id"] == test_blueprint.id
        assert suggestion["output_item_id"] == test_item.id
        assert suggestion["suggested_count"] > 0

    def test_suggest_crafts_no_blueprints(
        self, client: TestClient, auth_headers: dict, test_item: Item, db_session: Session
    ):
        """Test suggesting crafts when no blueprints exist."""
        # Create item with no blueprints
        item2 = Item(name="No Blueprint Item", category="Materials")
        db_session.add(item2)
        db_session.commit()
        db_session.refresh(item2)

        response = client.post(
            "/api/v1/optimization/suggest-crafts",
            json={
                "target_item_id": item2.id,
                "target_quantity": 100.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) == 0

    def test_suggest_crafts_item_not_found(self, client: TestClient, auth_headers: dict):
        """Test suggesting crafts for non-existent item."""
        response = client.post(
            "/api/v1/optimization/suggest-crafts",
            json={
                "target_item_id": "00000000-0000-0000-0000-000000000000",
                "target_quantity": 100.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_suggest_crafts_service(
        self, db_session: Session, test_user: User, test_item: Item, test_blueprint: Blueprint
    ):
        """Test OptimizationService.suggest_crafts directly."""
        service = OptimizationService(db_session, test_user.id)
        request = SuggestCraftsRequest(
            target_item_id=test_item.id,
            target_quantity=Decimal("100.0"),
            max_suggestions=10,
        )
        response = service.suggest_crafts(request)
        assert response.target_item_id == test_item.id
        assert response.target_quantity == Decimal("100.0")
        assert len(response.suggestions) > 0
        assert response.suggestions[0].blueprint_id == test_blueprint.id


class TestResourceGap:
    """Test resource gap endpoint and service."""

    def test_get_resource_gap(
        self, client: TestClient, auth_headers: dict, test_craft: Craft, test_ingredient_items: list[Item], test_location: Location, test_user: User, db_session: Session
    ):
        """Test getting resource gap for a craft."""
        # Add stock for one ingredient but not the other
        stock1 = ItemStock(
            item_id=test_ingredient_items[0].id,
            location_id=test_location.id,
            quantity=Decimal("10.0"),  # More than needed (5.0)
            reserved_quantity=Decimal("0"),
            updated_by=test_user.id,
        )
        # No stock for item2 (needs 2.0)
        db_session.add(stock1)
        db_session.commit()

        response = client.get(
            f"/api/v1/optimization/resource-gap/{test_craft.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["craft_id"] == test_craft.id
        assert len(data["gaps"]) == 2  # Two ingredients
        # First gap should be item2 (no stock)
        assert data["gaps"][0]["gap_quantity"] > 0

    def test_get_resource_gap_all_available(
        self, client: TestClient, auth_headers: dict, test_craft: Craft, test_ingredient_items: list[Item], test_location: Location, test_user: User, db_session: Session
    ):
        """Test resource gap when all ingredients are available."""
        # Add sufficient stock for both ingredients
        stock1 = ItemStock(
            item_id=test_ingredient_items[0].id,
            location_id=test_location.id,
            quantity=Decimal("10.0"),
            reserved_quantity=Decimal("0"),
            updated_by=test_user.id,
        )
        stock2 = ItemStock(
            item_id=test_ingredient_items[1].id,
            location_id=test_location.id,
            quantity=Decimal("10.0"),
            reserved_quantity=Decimal("0"),
            updated_by=test_user.id,
        )
        db_session.add_all([stock1, stock2])
        db_session.commit()

        response = client.get(
            f"/api/v1/optimization/resource-gap/{test_craft.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["can_proceed"] is True
        # All gaps should be 0 or negative
        for gap in data["gaps"]:
            assert gap["gap_quantity"] <= 0

    def test_get_resource_gap_craft_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting resource gap for non-existent craft."""
        response = client.get(
            "/api/v1/optimization/resource-gap/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_get_resource_gap_service(
        self, db_session: Session, test_user: User, test_craft: Craft, test_ingredient_items: list[Item], test_location: Location
    ):
        """Test OptimizationService.get_resource_gap directly."""
        service = OptimizationService(db_session, test_user.id)
        response = service.get_resource_gap(test_craft.id)
        assert response.craft_id == test_craft.id
        assert len(response.gaps) == 2  # Two ingredients
        assert response.total_gaps >= 0


class TestOptimizationServiceOrganization:
    """Test optimization service with organizations."""

    def test_find_sources_with_org(
        self, db_session: Session, test_user: User, test_item: Item, test_location: Location
    ):
        """Test finding sources with organization context."""
        # Create organization
        org = Organization(
            name="Test Org",
            description="A test organization",
        )
        db_session.add(org)
        db_session.flush()

        # Add user as member
        membership = OrganizationMember(
            organization_id=org.id,
            user_id=test_user.id,
            role="admin",
        )
        db_session.add(membership)
        db_session.flush()

        # Create org location with stock
        org_location = Location(
            name="Org Warehouse",
            type="warehouse",
            owner_type="organization",
            owner_id=org.id,
        )
        db_session.add(org_location)
        db_session.flush()

        stock = ItemStock(
            item_id=test_item.id,
            location_id=org_location.id,
            quantity=Decimal("200.0"),
            reserved_quantity=Decimal("0"),
            updated_by=test_user.id,
        )
        db_session.add(stock)
        db_session.commit()

        service = OptimizationService(db_session, test_user.id)
        request = FindSourcesRequest(
            item_id=test_item.id,
            required_quantity=Decimal("50.0"),
            organization_id=org.id,
        )
        response = service.find_sources_for_item(request)
        assert response.total_available >= 50.0
        # Should find stock from org location
        org_stock_source = next(
            (s for s in response.sources if s.location_id == org_location.id),
            None,
        )
        assert org_stock_source is not None

