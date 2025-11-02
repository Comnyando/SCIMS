"""
Tests for Crafts API endpoints.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from app.models.craft import Craft, CRAFT_STATUS_PLANNED, CRAFT_STATUS_IN_PROGRESS, CRAFT_STATUS_COMPLETED, CRAFT_STATUS_CANCELLED
from app.models.craft_ingredient import CraftIngredient, INGREDIENT_STATUS_PENDING, INGREDIENT_STATUS_RESERVED, INGREDIENT_STATUS_FULFILLED, SOURCE_TYPE_STOCK
from app.models.blueprint import Blueprint
from app.models.item import Item
from app.models.location import Location
from app.models.item_stock import ItemStock
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.core.security import create_access_token, hash_password


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
def other_auth_headers(other_user):
    """Return auth headers for other user."""
    token = create_access_token(data={"sub": str(other_user.id), "email": other_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_item(client, db_session):
    """Create a test item."""
    item = Item(
        name="Test Item",
        description="A test item",
        category="Components",
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
def test_blueprint(client, db_session, test_user, test_item, test_ingredient_items):
    """Create a test blueprint."""
    blueprint = Blueprint(
        name="Test Blueprint",
        description="A test blueprint",
        category="Components",
        crafting_time_minutes=60,
        output_item_id=test_item.id,
        output_quantity=Decimal("1.0"),
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
def test_item_stocks(client, db_session, test_ingredient_items, test_location, test_user):
    """Create test item stocks with sufficient quantities."""
    stock1 = ItemStock(
        item_id=test_ingredient_items[0].id,
        location_id=test_location.id,
        quantity=Decimal("100.0"),
        reserved_quantity=Decimal("0.0"),
        updated_by=test_user.id,
    )
    stock2 = ItemStock(
        item_id=test_ingredient_items[1].id,
        location_id=test_location.id,
        quantity=Decimal("100.0"),
        reserved_quantity=Decimal("0.0"),
        updated_by=test_user.id,
    )
    db_session.add_all([stock1, stock2])
    db_session.commit()
    db_session.refresh(stock1)
    db_session.refresh(stock2)
    return [stock1, stock2]


@pytest.fixture
def test_org(test_user, db_session):
    """Create a test organization with test_user as owner."""
    org = Organization(name="Test Org", slug="test-org")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    membership = OrganizationMember(
        organization_id=org.id,
        user_id=test_user.id,
        role="owner",
    )
    db_session.add(membership)
    db_session.commit()
    return org


@pytest.fixture
def test_craft(client, db_session, test_user, test_blueprint, test_location):
    """Create a test craft."""
    craft = Craft(
        blueprint_id=test_blueprint.id,
        requested_by=test_user.id,
        status=CRAFT_STATUS_PLANNED,
        priority=5,
        output_location_id=test_location.id,
    )
    db_session.add(craft)
    db_session.flush()  # Get craft ID

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


class TestListCrafts:
    """Test list crafts endpoint."""

    def test_list_crafts_empty(self, client, auth_headers):
        """Test listing crafts when none exist."""
        response = client.get("/api/v1/crafts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["crafts"] == []

    def test_list_crafts_own(self, client, auth_headers, test_craft):
        """Test listing own crafts."""
        response = client.get("/api/v1/crafts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["crafts"][0]["id"] == test_craft.id
        assert data["crafts"][0]["status"] == CRAFT_STATUS_PLANNED

    def test_list_crafts_filter_status(self, client, auth_headers, db_session, test_user, test_blueprint, test_location):
        """Test filtering crafts by status."""
        craft1 = Craft(
            blueprint_id=test_blueprint.id,
            requested_by=test_user.id,
            status=CRAFT_STATUS_PLANNED,
            output_location_id=test_location.id,
        )
        craft2 = Craft(
            blueprint_id=test_blueprint.id,
            requested_by=test_user.id,
            status=CRAFT_STATUS_IN_PROGRESS,
            output_location_id=test_location.id,
        )
        db_session.add_all([craft1, craft2])
        db_session.commit()

        response = client.get("/api/v1/crafts?status_filter=planned", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(c["status"] == CRAFT_STATUS_PLANNED for c in data["crafts"])

    def test_list_crafts_filter_organization(self, client, auth_headers, db_session, test_user, test_blueprint, test_location, test_org):
        """Test filtering crafts by organization."""
        craft1 = Craft(
            blueprint_id=test_blueprint.id,
            requested_by=test_user.id,
            organization_id=test_org.id,
            status=CRAFT_STATUS_PLANNED,
            output_location_id=test_location.id,
        )
        craft2 = Craft(
            blueprint_id=test_blueprint.id,
            requested_by=test_user.id,
            status=CRAFT_STATUS_PLANNED,
            output_location_id=test_location.id,
        )
        db_session.add_all([craft1, craft2])
        db_session.commit()

        response = client.get(f"/api/v1/crafts?organization_id={test_org.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["crafts"][0]["organization_id"] == test_org.id

    def test_list_crafts_not_visible_other_user(self, client, other_auth_headers, test_craft):
        """Test that crafts from other users are not visible."""
        response = client.get("/api/v1/crafts", headers=other_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_list_crafts_pagination(self, client, auth_headers, db_session, test_user, test_blueprint, test_location):
        """Test pagination."""
        # Create 5 crafts
        crafts = []
        for i in range(5):
            craft = Craft(
                blueprint_id=test_blueprint.id,
                requested_by=test_user.id,
                status=CRAFT_STATUS_PLANNED,
                output_location_id=test_location.id,
            )
            crafts.append(craft)
        db_session.add_all(crafts)
        db_session.commit()

        # First page
        response = client.get("/api/v1/crafts?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["crafts"]) == 2


class TestCreateCraft:
    """Test create craft endpoint."""

    def test_create_craft_success(self, client, auth_headers, test_blueprint, test_location):
        """Test successful craft creation."""
        response = client.post(
            "/api/v1/crafts",
            headers=auth_headers,
            json={
                "blueprint_id": test_blueprint.id,
                "output_location_id": test_location.id,
                "priority": 5,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["blueprint_id"] == test_blueprint.id
        assert data["output_location_id"] == test_location.id
        assert data["status"] == CRAFT_STATUS_PLANNED
        assert data["priority"] == 5
        assert "id" in data
        assert "requested_by" in data

    def test_create_craft_with_reservation(self, client, auth_headers, test_blueprint, test_location, test_item_stocks):
        """Test creating craft with ingredient reservation."""
        response = client.post(
            "/api/v1/crafts?reserve_ingredients=true",
            headers=auth_headers,
            json={
                "blueprint_id": test_blueprint.id,
                "output_location_id": test_location.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == CRAFT_STATUS_PLANNED

        # Check ingredients were reserved
        craft_id = data["id"]
        craft_response = client.get(f"/api/v1/crafts/{craft_id}?include_ingredients=true", headers=auth_headers)
        assert craft_response.status_code == 200
        craft_data = craft_response.json()
        assert craft_data["ingredients"] is not None
        # Ingredients should be reserved
        for ingredient in craft_data["ingredients"]:
            if ingredient["source_type"] == SOURCE_TYPE_STOCK:
                assert ingredient["status"] == INGREDIENT_STATUS_RESERVED

    def test_create_craft_invalid_blueprint(self, client, auth_headers, test_location):
        """Test creating craft with invalid blueprint_id."""
        response = client.post(
            "/api/v1/crafts",
            headers=auth_headers,
            json={
                "blueprint_id": "00000000-0000-0000-0000-000000000000",
                "output_location_id": test_location.id,
            },
        )
        assert response.status_code == 404

    def test_create_craft_invalid_location(self, client, auth_headers, test_blueprint):
        """Test creating craft with invalid output_location_id."""
        response = client.post(
            "/api/v1/crafts",
            headers=auth_headers,
            json={
                "blueprint_id": test_blueprint.id,
                "output_location_id": "00000000-0000-0000-0000-000000000000",
            },
        )
        assert response.status_code == 404

    def test_create_craft_insufficient_stock(self, client, auth_headers, db_session, test_blueprint, test_location, test_ingredient_items, test_user):
        """Test creating craft with reservation when insufficient stock."""
        # Create stock with insufficient quantity
        stock = ItemStock(
            item_id=test_ingredient_items[0].id,
            location_id=test_location.id,
            quantity=Decimal("1.0"),  # Less than required (5.0)
            reserved_quantity=Decimal("0.0"),
            updated_by=test_user.id,
        )
        db_session.add(stock)
        db_session.commit()

        response = client.post(
            "/api/v1/crafts?reserve_ingredients=true",
            headers=auth_headers,
            json={
                "blueprint_id": test_blueprint.id,
                "output_location_id": test_location.id,
            },
        )
        assert response.status_code == 400
        assert "insufficient" in response.json()["detail"].lower()


class TestGetCraft:
    """Test get craft endpoint."""

    def test_get_craft_success(self, client, auth_headers, test_craft):
        """Test getting an existing craft."""
        response = client.get(f"/api/v1/crafts/{test_craft.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_craft.id
        assert data["status"] == CRAFT_STATUS_PLANNED

    def test_get_craft_with_ingredients(self, client, auth_headers, test_craft):
        """Test getting craft with ingredients."""
        response = client.get(f"/api/v1/crafts/{test_craft.id}?include_ingredients=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ingredients"] is not None
        assert len(data["ingredients"]) == 2

    def test_get_craft_not_found(self, client, auth_headers):
        """Test getting non-existent craft."""
        response = client.get("/api/v1/crafts/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404

    def test_get_craft_not_owner(self, client, other_auth_headers, test_craft):
        """Test that other users cannot access crafts they don't own."""
        response = client.get(f"/api/v1/crafts/{test_craft.id}", headers=other_auth_headers)
        assert response.status_code == 403


class TestUpdateCraft:
    """Test update craft endpoint."""

    def test_update_craft_success(self, client, auth_headers, test_craft):
        """Test successful craft update."""
        response = client.patch(
            f"/api/v1/crafts/{test_craft.id}",
            headers=auth_headers,
            json={
                "priority": 10,
                "metadata": {"note": "Updated priority"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == 10

    def test_update_craft_not_found(self, client, auth_headers):
        """Test updating non-existent craft."""
        response = client.patch(
            "/api/v1/crafts/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
            json={"priority": 10},
        )
        assert response.status_code == 404

    def test_update_craft_not_owner(self, client, other_auth_headers, test_craft):
        """Test that only owner can update craft."""
        response = client.patch(
            f"/api/v1/crafts/{test_craft.id}",
            headers=other_auth_headers,
            json={"priority": 10},
        )
        assert response.status_code == 403

    def test_update_craft_in_progress_not_allowed(self, client, auth_headers, db_session, test_craft):
        """Test that in_progress crafts cannot be updated."""
        test_craft.status = CRAFT_STATUS_IN_PROGRESS
        db_session.commit()

        response = client.patch(
            f"/api/v1/crafts/{test_craft.id}",
            headers=auth_headers,
            json={"priority": 10},
        )
        assert response.status_code == 400
        assert "planned" in response.json()["detail"].lower()


class TestDeleteCraft:
    """Test delete craft endpoint."""

    def test_delete_craft_success(self, client, auth_headers, db_session, test_user, test_blueprint, test_location):
        """Test successful craft deletion."""
        craft = Craft(
            blueprint_id=test_blueprint.id,
            requested_by=test_user.id,
            status=CRAFT_STATUS_PLANNED,
            output_location_id=test_location.id,
        )
        db_session.add(craft)
        db_session.commit()
        db_session.refresh(craft)
        craft_id = craft.id

        response = client.delete(f"/api/v1/crafts/{craft_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/v1/crafts/{craft_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_craft_not_found(self, client, auth_headers):
        """Test deleting non-existent craft."""
        response = client.delete("/api/v1/crafts/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_craft_not_owner(self, client, other_auth_headers, test_craft):
        """Test that only owner can delete craft."""
        response = client.delete(f"/api/v1/crafts/{test_craft.id}", headers=other_auth_headers)
        assert response.status_code == 403

    def test_delete_craft_in_progress_not_allowed(self, client, auth_headers, db_session, test_craft):
        """Test that in_progress crafts cannot be deleted."""
        test_craft.status = CRAFT_STATUS_IN_PROGRESS
        db_session.commit()

        response = client.delete(f"/api/v1/crafts/{test_craft.id}", headers=auth_headers)
        assert response.status_code == 400
        assert "planned" in response.json()["detail"].lower() or "cancelled" in response.json()["detail"].lower()


class TestStartCraft:
    """Test start craft endpoint."""

    def test_start_craft_success(self, client, auth_headers, test_craft):
        """Test successfully starting a craft."""
        response = client.post(f"/api/v1/crafts/{test_craft.id}/start", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == CRAFT_STATUS_IN_PROGRESS
        assert data["started_at"] is not None

    def test_start_craft_with_reservation(self, client, auth_headers, test_craft, test_item_stocks):
        """Test starting craft and reserving missing ingredients."""
        response = client.post(
            f"/api/v1/crafts/{test_craft.id}/start?reserve_missing_ingredients=true",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == CRAFT_STATUS_IN_PROGRESS

    def test_start_craft_not_planned(self, client, auth_headers, db_session, test_craft):
        """Test that only planned crafts can be started."""
        test_craft.status = CRAFT_STATUS_IN_PROGRESS
        db_session.commit()

        response = client.post(f"/api/v1/crafts/{test_craft.id}/start", headers=auth_headers)
        assert response.status_code == 400
        assert "planned" in response.json()["detail"].lower()

    def test_start_craft_increments_usage_count(self, client, auth_headers, db_session, test_craft, test_blueprint):
        """Test that starting a craft increments blueprint usage count."""
        initial_count = test_blueprint.usage_count
        response = client.post(f"/api/v1/crafts/{test_craft.id}/start", headers=auth_headers)
        assert response.status_code == 200

        db_session.refresh(test_blueprint)
        assert test_blueprint.usage_count == initial_count + 1


class TestCompleteCraft:
    """Test complete craft endpoint."""

    def test_complete_craft_success(self, client, auth_headers, db_session, test_craft, test_blueprint, test_location, test_item_stocks):
        """Test successfully completing a craft."""
        # Start the craft first
        test_craft.status = CRAFT_STATUS_IN_PROGRESS
        test_craft.started_at = datetime.now(timezone.utc)
        
        # Reserve ingredients
        for ingredient in test_craft.ingredients:
            if ingredient.source_type == SOURCE_TYPE_STOCK:
                stock = db_session.query(ItemStock).filter(
                    ItemStock.item_id == ingredient.item_id,
                    ItemStock.location_id == ingredient.source_location_id,
                ).first()
                if stock:
                    stock.reserved_quantity += ingredient.required_quantity
                    ingredient.status = INGREDIENT_STATUS_RESERVED
        
        db_session.commit()

        response = client.post(f"/api/v1/crafts/{test_craft.id}/complete", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == CRAFT_STATUS_COMPLETED
        assert data["completed_at"] is not None

        # Verify stock was deducted
        db_session.refresh(test_item_stocks[0])
        assert test_item_stocks[0].reserved_quantity < Decimal("100.0")

        # Verify output items were added
        output_stock = db_session.query(ItemStock).filter(
            ItemStock.item_id == test_blueprint.output_item_id,
            ItemStock.location_id == test_location.id,
        ).first()
        assert output_stock is not None
        assert output_stock.quantity >= test_blueprint.output_quantity

    def test_complete_craft_not_in_progress(self, client, auth_headers, test_craft):
        """Test that only in_progress crafts can be completed."""
        response = client.post(f"/api/v1/crafts/{test_craft.id}/complete", headers=auth_headers)
        assert response.status_code == 400
        assert "in_progress" in response.json()["detail"].lower()

    def test_complete_craft_insufficient_reserved(self, client, auth_headers, db_session, test_user, test_blueprint, test_location, test_ingredient_items):
        """Test completing craft with insufficient reserved stock."""
        # Create a new craft for this test
        craft = Craft(
            blueprint_id=test_blueprint.id,
            requested_by=test_user.id,
            status=CRAFT_STATUS_IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
            output_location_id=test_location.id,
        )
        db_session.add(craft)
        db_session.flush()
        
        # Create ingredient with reserved status but stock doesn't have enough reserved
        ingredient = CraftIngredient(
            craft_id=craft.id,
            item_id=test_ingredient_items[0].id,
            required_quantity=Decimal("10.0"),
            source_location_id=test_location.id,
            source_type=SOURCE_TYPE_STOCK,
            status=INGREDIENT_STATUS_RESERVED,
        )
        db_session.add(ingredient)
        
        # Stock has less reserved than required
        stock = ItemStock(
            item_id=test_ingredient_items[0].id,
            location_id=test_location.id,
            quantity=Decimal("100.0"),
            reserved_quantity=Decimal("5.0"),  # Less than required 10.0
            updated_by=test_user.id,
        )
        db_session.add(stock)
        db_session.commit()

        response = client.post(f"/api/v1/crafts/{craft.id}/complete", headers=auth_headers)
        assert response.status_code == 400
        assert "insufficient" in response.json()["detail"].lower()


class TestGetCraftProgress:
    """Test get craft progress endpoint."""

    def test_get_progress_planned(self, client, auth_headers, test_craft):
        """Test getting progress for planned craft."""
        response = client.get(f"/api/v1/crafts/{test_craft.id}/progress", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == CRAFT_STATUS_PLANNED
        assert data["elapsed_minutes"] is None
        assert data["estimated_completion_minutes"] is None
        assert "ingredients_status" in data

    def test_get_progress_in_progress(self, client, auth_headers, db_session, test_craft):
        """Test getting progress for in_progress craft."""
        test_craft.status = CRAFT_STATUS_IN_PROGRESS
        test_craft.started_at = datetime.now(timezone.utc) - timedelta(minutes=30)
        db_session.commit()

        response = client.get(f"/api/v1/crafts/{test_craft.id}/progress", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == CRAFT_STATUS_IN_PROGRESS
        assert data["elapsed_minutes"] is not None
        assert data["estimated_completion_minutes"] is not None
        assert "ingredients_status" in data

    def test_get_progress_ingredients_summary(self, client, auth_headers, test_craft):
        """Test that progress includes ingredient status summary."""
        response = client.get(f"/api/v1/crafts/{test_craft.id}/progress", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "ingredients_status" in data
        status = data["ingredients_status"]
        assert "total" in status
        assert "pending" in status
        assert "reserved" in status
        assert "fulfilled" in status


class TestCraftAccessControl:
    """Test craft access control."""

    def test_list_crafts_organization_member(self, client, auth_headers, db_session, test_user, test_blueprint, test_location, test_org):
        """Test that organization members can see organization crafts."""
        craft = Craft(
            blueprint_id=test_blueprint.id,
            requested_by=test_user.id,
            organization_id=test_org.id,
            status=CRAFT_STATUS_PLANNED,
            output_location_id=test_location.id,
        )
        db_session.add(craft)
        db_session.commit()

        response = client.get("/api/v1/crafts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_list_crafts_non_member_cannot_see_org_craft(self, client, other_auth_headers, db_session, test_user, test_blueprint, test_location, test_org):
        """Test that non-members cannot see organization crafts."""
        craft = Craft(
            blueprint_id=test_blueprint.id,
            requested_by=test_user.id,
            organization_id=test_org.id,
            status=CRAFT_STATUS_PLANNED,
            output_location_id=test_location.id,
        )
        db_session.add(craft)
        db_session.commit()

        response = client.get("/api/v1/crafts", headers=other_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


class TestCraftReservation:
    """Test craft ingredient reservation."""

    def test_create_craft_with_reservation_deducts_stock(self, client, auth_headers, db_session, test_blueprint, test_location, test_item_stocks):
        """Test that creating craft with reservation deducts available stock."""
        initial_available = test_item_stocks[0].quantity - test_item_stocks[0].reserved_quantity
        initial_reserved = test_item_stocks[0].reserved_quantity

        response = client.post(
            "/api/v1/crafts?reserve_ingredients=true",
            headers=auth_headers,
            json={
                "blueprint_id": test_blueprint.id,
                "output_location_id": test_location.id,
            },
        )
        assert response.status_code == 201

        # Check reserved quantity increased using the same db_session
        db_session.refresh(test_item_stocks[0])
        assert test_item_stocks[0].reserved_quantity > initial_reserved
        # Available should decrease
        assert (test_item_stocks[0].quantity - test_item_stocks[0].reserved_quantity) < initial_available

    def test_delete_craft_unreserves_ingredients(self, client, auth_headers, db_session, test_blueprint, test_location, test_item_stocks, test_user):
        """Test that deleting craft unreserves ingredients."""
        # Create craft with reserved ingredients
        craft = Craft(
            blueprint_id=test_blueprint.id,
            requested_by=test_user.id,
            status=CRAFT_STATUS_PLANNED,
            output_location_id=test_location.id,
        )
        db_session.add(craft)
        db_session.flush()

        # Create and reserve ingredients
        for ingredient_data in test_blueprint.blueprint_data["ingredients"]:
            ingredient = CraftIngredient(
                craft_id=craft.id,
                item_id=ingredient_data["item_id"],
                required_quantity=Decimal(str(ingredient_data["quantity"])),
                source_location_id=test_location.id,
                source_type=SOURCE_TYPE_STOCK,
                status=INGREDIENT_STATUS_RESERVED,
            )
            db_session.add(ingredient)

            # Reserve in stock
            stock = db_session.query(ItemStock).filter(
                ItemStock.item_id == ingredient_data["item_id"],
                ItemStock.location_id == test_location.id,
            ).first()
            if stock:
                stock.reserved_quantity += Decimal(str(ingredient_data["quantity"]))

        db_session.commit()
        db_session.refresh(craft)
        initial_reserved = db_session.query(ItemStock).filter(ItemStock.id == test_item_stocks[0].id).first().reserved_quantity

        # Delete craft with unreserve
        response = client.delete(f"/api/v1/crafts/{craft.id}?unreserve_ingredients=true", headers=auth_headers)
        assert response.status_code == 204

        # Verify ingredients were unreserved
        stock = db_session.query(ItemStock).filter(ItemStock.id == test_item_stocks[0].id).first()
        assert stock.reserved_quantity < initial_reserved

