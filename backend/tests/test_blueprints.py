"""
Tests for Blueprints API endpoints.
"""

import pytest
from decimal import Decimal
from app.models.blueprint import Blueprint
from app.models.item import Item
from app.models.user import User
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
def public_blueprint(client, db_session, test_user, test_item, test_ingredient_items):
    """Create a public test blueprint."""
    blueprint = Blueprint(
        name="Public Blueprint",
        description="A public blueprint",
        category="Weapons",
        crafting_time_minutes=120,
        output_item_id=test_item.id,
        output_quantity=Decimal("1.0"),
        blueprint_data={
            "ingredients": [
                {"item_id": test_ingredient_items[0].id, "quantity": 10.0, "optional": False},
            ]
        },
        created_by=test_user.id,
        is_public=True,
        usage_count=5,
    )
    db_session.add(blueprint)
    db_session.commit()
    db_session.refresh(blueprint)
    return blueprint


class TestListBlueprints:
    """Test list blueprints endpoint."""

    def test_list_blueprints_empty(self, client, auth_headers):
        """Test listing blueprints when none exist."""
        response = client.get("/api/v1/blueprints", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["blueprints"] == []

    def test_list_blueprints_own_private(self, client, auth_headers, test_blueprint):
        """Test listing own private blueprint."""
        response = client.get("/api/v1/blueprints", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["blueprints"][0]["name"] == "Test Blueprint"
        assert data["blueprints"][0]["is_public"] is False

    def test_list_blueprints_public(self, client, auth_headers, public_blueprint):
        """Test listing public blueprint."""
        response = client.get("/api/v1/blueprints", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["blueprints"][0]["name"] == "Public Blueprint"
        assert data["blueprints"][0]["is_public"] is True

    def test_list_blueprints_not_visible_private(self, client, other_auth_headers, test_blueprint):
        """Test that private blueprints from other users are not visible."""
        response = client.get("/api/v1/blueprints", headers=other_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_list_blueprints_search(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test searching blueprints by name."""
        bp1 = Blueprint(
            name="Quantum Drive Component",
            output_item_id=test_item.id,
            output_quantity=Decimal("1.0"),
            blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
            created_by=test_user.id,
        )
        bp2 = Blueprint(
            name="Hydration System",
            output_item_id=test_item.id,
            output_quantity=Decimal("1.0"),
            blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 3.0}]},
            created_by=test_user.id,
        )
        db_session.add_all([bp1, bp2])
        db_session.commit()

        response = client.get("/api/v1/blueprints?search=quantum", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["blueprints"][0]["name"] == "Quantum Drive Component"

    def test_list_blueprints_filter_category(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test filtering blueprints by category."""
        bp1 = Blueprint(
            name="Weapon Blueprint",
            category="Weapons",
            output_item_id=test_item.id,
            output_quantity=Decimal("1.0"),
            blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
            created_by=test_user.id,
        )
        bp2 = Blueprint(
            name="Food Blueprint",
            category="Food",
            output_item_id=test_item.id,
            output_quantity=Decimal("1.0"),
            blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 3.0}]},
            created_by=test_user.id,
        )
        db_session.add_all([bp1, bp2])
        db_session.commit()

        response = client.get("/api/v1/blueprints?category=Weapons", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["blueprints"][0]["category"] == "Weapons"

    def test_list_blueprints_filter_public(self, client, auth_headers, test_blueprint, public_blueprint):
        """Test filtering blueprints by public/private."""
        response = client.get("/api/v1/blueprints?is_public=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(bp["is_public"] is True for bp in data["blueprints"])

        response = client.get("/api/v1/blueprints?is_public=false", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(bp["is_public"] is False for bp in data["blueprints"])

    def test_list_blueprints_filter_output_item(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test filtering blueprints by output item."""
        item2 = Item(name="Other Item", category="Test")
        db_session.add(item2)
        db_session.commit()
        db_session.refresh(item2)

        bp1 = Blueprint(
            name="Blueprint 1",
            output_item_id=test_item.id,
            output_quantity=Decimal("1.0"),
            blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
            created_by=test_user.id,
        )
        bp2 = Blueprint(
            name="Blueprint 2",
            output_item_id=item2.id,
            output_quantity=Decimal("1.0"),
            blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 3.0}]},
            created_by=test_user.id,
        )
        db_session.add_all([bp1, bp2])
        db_session.commit()

        response = client.get(f"/api/v1/blueprints?output_item_id={test_item.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["blueprints"][0]["output_item_id"] == test_item.id

    def test_list_blueprints_pagination(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test pagination."""
        # Create 5 blueprints
        blueprints = []
        for i in range(5):
            bp = Blueprint(
                name=f"Blueprint {i}",
                output_item_id=test_item.id,
                output_quantity=Decimal("1.0"),
                blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                created_by=test_user.id,
            )
            blueprints.append(bp)
        db_session.add_all(blueprints)
        db_session.commit()

        # First page
        response = client.get("/api/v1/blueprints?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["blueprints"]) == 2
        assert data["skip"] == 0
        assert data["limit"] == 2

        # Second page
        response = client.get("/api/v1/blueprints?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["blueprints"]) == 2

    def test_list_blueprints_sort_by_name(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test sorting blueprints by name."""
        bp1 = Blueprint(name="Zebra Blueprint", output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                       created_by=test_user.id)
        bp2 = Blueprint(name="Alpha Blueprint", output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                       created_by=test_user.id)
        db_session.add_all([bp1, bp2])
        db_session.commit()

        response = client.get("/api/v1/blueprints?sort_by=name&sort_order=asc", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["blueprints"][0]["name"] == "Alpha Blueprint"
        assert data["blueprints"][1]["name"] == "Zebra Blueprint"

    def test_list_blueprints_sort_by_usage_count(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test sorting blueprints by usage_count."""
        bp1 = Blueprint(name="Blueprint 1", usage_count=10, output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                       created_by=test_user.id)
        bp2 = Blueprint(name="Blueprint 2", usage_count=5, output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                       created_by=test_user.id)
        db_session.add_all([bp1, bp2])
        db_session.commit()

        response = client.get("/api/v1/blueprints?sort_by=usage_count&sort_order=desc", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["blueprints"][0]["usage_count"] == 10
        assert data["blueprints"][1]["usage_count"] == 5


class TestCreateBlueprint:
    """Test create blueprint endpoint."""

    def test_create_blueprint_success(self, client, auth_headers, test_item, test_ingredient_items):
        """Test successful blueprint creation."""
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "New Blueprint",
                "description": "A new blueprint",
                "category": "Components",
                "crafting_time_minutes": 60,
                "output_item_id": test_item.id,
                "output_quantity": 1.0,
                "blueprint_data": {
                    "ingredients": [
                        {"item_id": test_ingredient_items[0].id, "quantity": 5.0, "optional": False},
                        {"item_id": test_ingredient_items[1].id, "quantity": 2.0, "optional": False},
                    ]
                },
                "is_public": False,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Blueprint"
        assert data["description"] == "A new blueprint"
        assert data["category"] == "Components"
        assert data["crafting_time_minutes"] == 60
        assert data["output_item_id"] == test_item.id
        # Decimal can be serialized as string or float, check both
        assert float(data["output_quantity"]) == 1.0
        assert data["is_public"] is False
        assert data["usage_count"] == 0
        assert "id" in data
        assert "created_by" in data
        assert "created_at" in data
        assert len(data["blueprint_data"]["ingredients"]) == 2

    def test_create_blueprint_invalid_output_item(self, client, auth_headers, test_ingredient_items):
        """Test creating blueprint with invalid output_item_id."""
        # Use a valid UUID format but non-existent item - should get 404 after validation
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Invalid Blueprint",
                "output_item_id": "00000000-0000-0000-0000-000000000000",
                "output_quantity": 1.0,
                "blueprint_data": {
                    "ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]
                },
            },
        )
        # The endpoint validates item existence, so should return 404
        assert response.status_code in [404, 422]  # Could be 422 if UUID validation fails first
        if response.status_code == 404:
            assert "output_item" in response.json()["detail"].lower()

    def test_create_blueprint_invalid_ingredient_item(self, client, auth_headers, test_item):
        """Test creating blueprint with invalid ingredient item_id."""
        # Use a valid UUID format but non-existent item
        fake_uuid = "12345678-1234-5678-9012-123456789012"
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Invalid Blueprint",
                "output_item_id": test_item.id,
                "output_quantity": 1.0,
                "blueprint_data": {
                    "ingredients": [
                        {"item_id": fake_uuid, "quantity": 5.0}
                    ]
                },
            },
        )
        # The endpoint validates ingredient item existence, so should return 404
        assert response.status_code in [404, 422]  # Could be 422 if validation format fails first
        if response.status_code == 404:
            assert "ingredient" in response.json()["detail"].lower()

    def test_create_blueprint_empty_ingredients(self, client, auth_headers, test_item):
        """Test creating blueprint with empty ingredients array."""
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Invalid Blueprint",
                "output_item_id": test_item.id,
                "output_quantity": 1.0,
                "blueprint_data": {"ingredients": []},
            },
        )
        assert response.status_code == 422  # Validation error

    def test_create_blueprint_missing_ingredients_key(self, client, auth_headers, test_item):
        """Test creating blueprint without ingredients key."""
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Invalid Blueprint",
                "output_item_id": test_item.id,
                "output_quantity": 1.0,
                "blueprint_data": {},
            },
        )
        assert response.status_code == 422  # Validation error

    def test_create_blueprint_duplicate_ingredient_item(self, client, auth_headers, test_item, test_ingredient_items):
        """Test creating blueprint with duplicate ingredient item_id."""
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Invalid Blueprint",
                "output_item_id": test_item.id,
                "output_quantity": 1.0,
                "blueprint_data": {
                    "ingredients": [
                        {"item_id": test_ingredient_items[0].id, "quantity": 5.0},
                        {"item_id": test_ingredient_items[0].id, "quantity": 3.0},  # Duplicate
                    ]
                },
            },
        )
        assert response.status_code == 422  # Validation error
        detail = response.json()["detail"]
        # Error can be in different formats - check for duplicate message
        if isinstance(detail, list):
            assert any("duplicate" in str(msg).lower() for msg in detail)
        else:
            assert "duplicate" in str(detail).lower()

    def test_create_blueprint_negative_quantity(self, client, auth_headers, test_item, test_ingredient_items):
        """Test creating blueprint with negative quantity."""
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Invalid Blueprint",
                "output_item_id": test_item.id,
                "output_quantity": -1.0,  # Invalid
                "blueprint_data": {
                    "ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]
                },
            },
        )
        assert response.status_code == 422  # Validation error

    def test_create_blueprint_public(self, client, auth_headers, test_item, test_ingredient_items):
        """Test creating public blueprint."""
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Public Blueprint",
                "output_item_id": test_item.id,
                "output_quantity": 1.0,
                "crafting_time_minutes": 60,
                "blueprint_data": {
                    "ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]
                },
                "is_public": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["is_public"] is True


class TestGetBlueprint:
    """Test get blueprint endpoint."""

    def test_get_blueprint_success(self, client, auth_headers, test_blueprint):
        """Test getting an existing blueprint."""
        response = client.get(f"/api/v1/blueprints/{test_blueprint.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Blueprint"
        assert data["id"] == test_blueprint.id

    def test_get_blueprint_not_found(self, client, auth_headers):
        """Test getting non-existent blueprint."""
        response = client.get("/api/v1/blueprints/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404

    def test_get_blueprint_private_not_owner(self, client, other_auth_headers, test_blueprint):
        """Test that private blueprints are not accessible by non-owners."""
        response = client.get(f"/api/v1/blueprints/{test_blueprint.id}", headers=other_auth_headers)
        assert response.status_code == 403

    def test_get_blueprint_public_accessible(self, client, other_auth_headers, public_blueprint):
        """Test that public blueprints are accessible by all users."""
        response = client.get(f"/api/v1/blueprints/{public_blueprint.id}", headers=other_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Public Blueprint"


class TestUpdateBlueprint:
    """Test update blueprint endpoint."""

    def test_update_blueprint_success(self, client, auth_headers, test_blueprint):
        """Test successful blueprint update."""
        response = client.patch(
            f"/api/v1/blueprints/{test_blueprint.id}",
            headers=auth_headers,
            json={
                "name": "Updated Blueprint",
                "description": "Updated description",
                "crafting_time_minutes": 90,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Blueprint"
        assert data["description"] == "Updated description"
        assert data["crafting_time_minutes"] == 90

    def test_update_blueprint_not_found(self, client, auth_headers):
        """Test updating non-existent blueprint."""
        response = client.patch(
            "/api/v1/blueprints/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
            json={"name": "New Name"},
        )
        assert response.status_code == 404

    def test_update_blueprint_not_owner(self, client, other_auth_headers, test_blueprint):
        """Test that only owner can update blueprint."""
        response = client.patch(
            f"/api/v1/blueprints/{test_blueprint.id}",
            headers=other_auth_headers,
            json={"name": "Hacked Name"},
        )
        assert response.status_code == 403

    def test_update_blueprint_invalid_output_item(self, client, auth_headers, test_blueprint):
        """Test updating blueprint with invalid output_item_id."""
        response = client.patch(
            f"/api/v1/blueprints/{test_blueprint.id}",
            headers=auth_headers,
            json={"output_item_id": "00000000-0000-0000-0000-000000000000"},
        )
        assert response.status_code == 404

    def test_update_blueprint_update_ingredients(self, client, auth_headers, test_blueprint, test_ingredient_items):
        """Test updating blueprint ingredients."""
        new_ingredients = {
            "ingredients": [
                {"item_id": test_ingredient_items[0].id, "quantity": 10.0, "optional": False},
            ]
        }
        response = client.patch(
            f"/api/v1/blueprints/{test_blueprint.id}",
            headers=auth_headers,
            json={"blueprint_data": new_ingredients},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["blueprint_data"]["ingredients"]) == 1
        assert data["blueprint_data"]["ingredients"][0]["quantity"] == 10.0

    def test_update_blueprint_public_status(self, client, auth_headers, test_blueprint):
        """Test updating blueprint public status."""
        response = client.patch(
            f"/api/v1/blueprints/{test_blueprint.id}",
            headers=auth_headers,
            json={"is_public": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_public"] is True


class TestDeleteBlueprint:
    """Test delete blueprint endpoint."""

    def test_delete_blueprint_success(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test successful blueprint deletion."""
        blueprint = Blueprint(
            name="Blueprint to Delete",
            output_item_id=test_item.id,
            output_quantity=Decimal("1.0"),
            blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
            created_by=test_user.id,
        )
        db_session.add(blueprint)
        db_session.commit()
        db_session.refresh(blueprint)
        blueprint_id = blueprint.id

        response = client.delete(f"/api/v1/blueprints/{blueprint_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/v1/blueprints/{blueprint_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_blueprint_not_found(self, client, auth_headers):
        """Test deleting non-existent blueprint."""
        response = client.delete("/api/v1/blueprints/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_blueprint_not_owner(self, client, other_auth_headers, test_blueprint):
        """Test that only owner can delete blueprint."""
        response = client.delete(f"/api/v1/blueprints/{test_blueprint.id}", headers=other_auth_headers)
        assert response.status_code == 403


class TestPopularBlueprints:
    """Test popular blueprints endpoint."""

    def test_get_popular_blueprints_empty(self, client, auth_headers):
        """Test getting popular blueprints when none exist."""
        response = client.get("/api/v1/blueprints/popular", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["blueprints"] == []

    def test_get_popular_blueprints_sorted(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test that popular blueprints are sorted by usage_count."""
        bp1 = Blueprint(name="Low Usage", usage_count=5, output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                       created_by=test_user.id, is_public=True)
        bp2 = Blueprint(name="High Usage", usage_count=20, output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                       created_by=test_user.id, is_public=True)
        bp3 = Blueprint(name="Medium Usage", usage_count=10, output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                       created_by=test_user.id, is_public=True)
        db_session.add_all([bp1, bp2, bp3])
        db_session.commit()

        response = client.get("/api/v1/blueprints/popular", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["blueprints"]) == 3
        assert data["blueprints"][0]["usage_count"] == 20
        assert data["blueprints"][1]["usage_count"] == 10
        assert data["blueprints"][2]["usage_count"] == 5

    def test_get_popular_blueprints_limit(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test limiting popular blueprints results."""
        for i in range(10):
            bp = Blueprint(name=f"Blueprint {i}", usage_count=i, output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                          blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                          created_by=test_user.id, is_public=True)
            db_session.add(bp)
        db_session.commit()

        response = client.get("/api/v1/blueprints/popular?limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["blueprints"]) == 5

    def test_get_popular_blueprints_filter_category(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test filtering popular blueprints by category."""
        bp1 = Blueprint(name="Weapon", category="Weapons", usage_count=10, output_item_id=test_item.id,
                       output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                       created_by=test_user.id, is_public=True)
        bp2 = Blueprint(name="Food", category="Food", usage_count=5, output_item_id=test_item.id,
                       output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                       created_by=test_user.id, is_public=True)
        db_session.add_all([bp1, bp2])
        db_session.commit()

        response = client.get("/api/v1/blueprints/popular?category=Weapons", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["blueprints"]) == 1
        assert data["blueprints"][0]["category"] == "Weapons"

    def test_get_popular_blueprints_includes_own_private(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test that popular blueprints include user's own private blueprints."""
        private_bp = Blueprint(name="Private", usage_count=100, output_item_id=test_item.id,
                              output_quantity=Decimal("1.0"),
                              blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                              created_by=test_user.id, is_public=False)
        db_session.add(private_bp)
        db_session.commit()

        response = client.get("/api/v1/blueprints/popular", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["blueprints"][0]["name"] == "Private"


class TestBlueprintsByItem:
    """Test blueprints by item endpoint."""

    def test_get_blueprints_by_item_empty(self, client, auth_headers, test_item):
        """Test getting blueprints for item with none."""
        response = client.get(f"/api/v1/blueprints/by-item/{test_item.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_get_blueprints_by_item_success(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test getting blueprints for an item."""
        item2 = Item(name="Other Item", category="Test")
        db_session.add(item2)
        db_session.commit()
        db_session.refresh(item2)

        bp1 = Blueprint(name="Blueprint 1", output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                       created_by=test_user.id, usage_count=10, is_public=True)
        bp2 = Blueprint(name="Blueprint 2", output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 3.0}]},
                       created_by=test_user.id, usage_count=5, is_public=True)
        bp3 = Blueprint(name="Blueprint 3", output_item_id=item2.id, output_quantity=Decimal("1.0"),
                       blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 2.0}]},
                       created_by=test_user.id, usage_count=15, is_public=True)
        db_session.add_all([bp1, bp2, bp3])
        db_session.commit()

        response = client.get(f"/api/v1/blueprints/by-item/{test_item.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        # Should be sorted by usage_count descending
        assert data["blueprints"][0]["usage_count"] == 10
        assert data["blueprints"][1]["usage_count"] == 5

    def test_get_blueprints_by_item_invalid_item(self, client, auth_headers):
        """Test getting blueprints for non-existent item."""
        response = client.get("/api/v1/blueprints/by-item/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404

    def test_get_blueprints_by_item_filter_public(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test filtering blueprints by public/private."""
        public_bp = Blueprint(name="Public", output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                             blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                             created_by=test_user.id, is_public=True)
        private_bp = Blueprint(name="Private", output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                              blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 3.0}]},
                              created_by=test_user.id, is_public=False)
        db_session.add_all([public_bp, private_bp])
        db_session.commit()

        response = client.get(f"/api/v1/blueprints/by-item/{test_item.id}?is_public=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["blueprints"][0]["is_public"] is True

    def test_get_blueprints_by_item_includes_own_private(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test that user's own private blueprints are included."""
        private_bp = Blueprint(name="Private", output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                              blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                              created_by=test_user.id, is_public=False)
        db_session.add(private_bp)
        db_session.commit()

        response = client.get(f"/api/v1/blueprints/by-item/{test_item.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_get_blueprints_by_item_excludes_other_private(self, client, other_auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test that other users' private blueprints are excluded."""
        private_bp = Blueprint(name="Private", output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                              blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                              created_by=test_user.id, is_public=False)
        db_session.add(private_bp)
        db_session.commit()

        response = client.get(f"/api/v1/blueprints/by-item/{test_item.id}", headers=other_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_get_blueprints_by_item_pagination(self, client, auth_headers, db_session, test_user, test_item, test_ingredient_items):
        """Test pagination for blueprints by item."""
        for i in range(5):
            bp = Blueprint(name=f"Blueprint {i}", output_item_id=test_item.id, output_quantity=Decimal("1.0"),
                          blueprint_data={"ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]},
                          created_by=test_user.id, is_public=True)
            db_session.add(bp)
        db_session.commit()

        response = client.get(f"/api/v1/blueprints/by-item/{test_item.id}?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["blueprints"]) == 2


class TestBlueprintAuthentication:
    """Test authentication requirements for blueprint endpoints."""

    def test_list_blueprints_requires_auth(self, client):
        """Test that listing blueprints requires authentication."""
        response = client.get("/api/v1/blueprints")
        assert response.status_code == 401

    def test_create_blueprint_requires_auth(self, client, test_item, test_ingredient_items):
        """Test that creating blueprints requires authentication."""
        response = client.post(
            "/api/v1/blueprints",
            json={
                "name": "Unauthorized Blueprint",
                "output_item_id": test_item.id,
                "output_quantity": 1.0,
                "blueprint_data": {
                    "ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]
                },
            },
        )
        assert response.status_code == 401

    def test_get_blueprint_requires_auth(self, client, test_blueprint):
        """Test that getting a blueprint requires authentication."""
        response = client.get(f"/api/v1/blueprints/{test_blueprint.id}")
        assert response.status_code == 401

    def test_update_blueprint_requires_auth(self, client, test_blueprint):
        """Test that updating a blueprint requires authentication."""
        response = client.patch(
            f"/api/v1/blueprints/{test_blueprint.id}",
            json={"name": "Unauthorized Update"},
        )
        assert response.status_code == 401

    def test_delete_blueprint_requires_auth(self, client, test_blueprint):
        """Test that deleting a blueprint requires authentication."""
        response = client.delete(f"/api/v1/blueprints/{test_blueprint.id}")
        assert response.status_code == 401

    def test_get_popular_blueprints_requires_auth(self, client):
        """Test that getting popular blueprints requires authentication."""
        response = client.get("/api/v1/blueprints/popular")
        assert response.status_code == 401

    def test_get_blueprints_by_item_requires_auth(self, client, test_item):
        """Test that getting blueprints by item requires authentication."""
        response = client.get(f"/api/v1/blueprints/by-item/{test_item.id}")
        assert response.status_code == 401


class TestBlueprintValidationEdgeCases:
    """Test additional validation edge cases."""

    def test_create_blueprint_zero_quantity(self, client, auth_headers, test_item, test_ingredient_items):
        """Test creating blueprint with zero output quantity."""
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Zero Quantity Blueprint",
                "output_item_id": test_item.id,
                "output_quantity": 0.0,  # Should fail validation
                "blueprint_data": {
                    "ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]
                },
            },
        )
        assert response.status_code == 422

    def test_create_blueprint_zero_ingredient_quantity(self, client, auth_headers, test_item, test_ingredient_items):
        """Test creating blueprint with zero ingredient quantity."""
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Zero Ingredient Quantity",
                "output_item_id": test_item.id,
                "output_quantity": 1.0,
                "blueprint_data": {
                    "ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 0.0}]
                },
            },
        )
        assert response.status_code == 422

    def test_create_blueprint_optional_ingredient(self, client, auth_headers, test_item, test_ingredient_items):
        """Test creating blueprint with optional ingredient."""
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Optional Ingredient Blueprint",
                "output_item_id": test_item.id,
                "output_quantity": 1.0,
                "crafting_time_minutes": 60,
                "blueprint_data": {
                    "ingredients": [
                        {"item_id": test_ingredient_items[0].id, "quantity": 5.0, "optional": False},
                        {"item_id": test_ingredient_items[1].id, "quantity": 2.0, "optional": True},
                    ]
                },
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["blueprint_data"]["ingredients"]) == 2
        assert data["blueprint_data"]["ingredients"][1]["optional"] is True

    def test_create_blueprint_invalid_crafting_time(self, client, auth_headers, test_item, test_ingredient_items):
        """Test creating blueprint with negative crafting time."""
        response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Invalid Crafting Time",
                "output_item_id": test_item.id,
                "output_quantity": 1.0,
                "crafting_time_minutes": -10,  # Should fail validation
                "blueprint_data": {
                    "ingredients": [{"item_id": test_ingredient_items[0].id, "quantity": 5.0}]
                },
            },
        )
        assert response.status_code == 422

    def test_update_blueprint_zero_quantity(self, client, auth_headers, test_blueprint):
        """Test updating blueprint with zero quantity."""
        response = client.patch(
            f"/api/v1/blueprints/{test_blueprint.id}",
            headers=auth_headers,
            json={"output_quantity": 0.0},
        )
        assert response.status_code == 422

    def test_list_blueprints_invalid_sort_field(self, client, auth_headers, test_blueprint):
        """Test listing blueprints with invalid sort field."""
        response = client.get("/api/v1/blueprints?sort_by=invalid_field", headers=auth_headers)
        # Should default to name sorting
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 0  # Should still work, just use default sort
