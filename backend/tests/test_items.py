"""
Tests for Items API endpoints.
"""

import pytest
from app.models.item import Item
from app.core.security import create_access_token


@pytest.fixture
def auth_headers(client, db_session):
    """Create a test user and return auth headers."""
    from app.models.user import User
    from app.core.security import hash_password

    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("testpass123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {"Authorization": f"Bearer {token}"}


class TestListItems:
    """Test list items endpoint."""

    def test_list_items_empty(self, client, auth_headers):
        """Test listing items when none exist."""
        response = client.get("/api/v1/items", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_items_with_data(self, client, auth_headers, db_session):
        """Test listing items with data."""
        # Create test items
        item1 = Item(name="Item 1", category="Test", description="First item")
        item2 = Item(name="Item 2", category="Test", description="Second item")
        db_session.add_all([item1, item2])
        db_session.commit()

        response = client.get("/api/v1/items", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_items_search(self, client, auth_headers, db_session):
        """Test searching items by name."""
        item1 = Item(name="Quantum Fuel", description="Fuel for quantum drives")
        item2 = Item(name="Hydration Pack", description="Water for survival")
        db_session.add_all([item1, item2])
        db_session.commit()

        response = client.get("/api/v1/items?search=quantum", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Quantum Fuel"

    def test_list_items_filter_category(self, client, auth_headers, db_session):
        """Test filtering items by category."""
        item1 = Item(name="Item 1", category="Weapons")
        item2 = Item(name="Item 2", category="Consumables")
        db_session.add_all([item1, item2])
        db_session.commit()

        response = client.get("/api/v1/items?category=Weapons", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "Weapons"

    def test_list_items_pagination(self, client, auth_headers, db_session):
        """Test pagination."""
        # Create 5 items
        for i in range(5):
            item = Item(name=f"Item {i}")
            db_session.add(item)
        db_session.commit()

        # First page
        response = client.get("/api/v1/items?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["skip"] == 0
        assert data["limit"] == 2

        # Second page
        response = client.get("/api/v1/items?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2


class TestCreateItem:
    """Test create item endpoint."""

    def test_create_item_success(self, client, auth_headers):
        """Test successful item creation."""
        response = client.post(
            "/api/v1/items",
            headers=auth_headers,
            json={
                "name": "Test Item",
                "description": "A test item",
                "category": "Test",
                "rarity": "common",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["description"] == "A test item"
        assert "id" in data

    def test_create_item_duplicate_name(self, client, auth_headers, db_session):
        """Test that duplicate item names are rejected."""
        item = Item(name="Unique Item")
        db_session.add(item)
        db_session.commit()

        response = client.post(
            "/api/v1/items",
            headers=auth_headers,
            json={"name": "Unique Item"},
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_item_with_metadata(self, client, auth_headers):
        """Test creating item with metadata."""
        response = client.post(
            "/api/v1/items",
            headers=auth_headers,
            json={
                "name": "Item with Meta",
                "metadata": {"volume": 1.0, "weight": 0.5},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["metadata"]["volume"] == 1.0


class TestGetItem:
    """Test get item endpoint."""

    def test_get_item_success(self, client, auth_headers, db_session):
        """Test getting an existing item."""
        item = Item(name="Test Item", description="A test")
        db_session.add(item)
        db_session.commit()

        response = client.get(f"/api/v1/items/{item.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["id"] == item.id

    def test_get_item_not_found(self, client, auth_headers):
        """Test getting non-existent item."""
        response = client.get("/api/v1/items/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateItem:
    """Test update item endpoint."""

    def test_update_item_success(self, client, auth_headers, db_session):
        """Test successful item update."""
        item = Item(name="Original Name")
        db_session.add(item)
        db_session.commit()

        response = client.patch(
            f"/api/v1/items/{item.id}",
            headers=auth_headers,
            json={"name": "Updated Name", "description": "New description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "New description"

    def test_update_item_not_found(self, client, auth_headers):
        """Test updating non-existent item."""
        response = client.patch(
            "/api/v1/items/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
            json={"name": "New Name"},
        )
        assert response.status_code == 404


class TestDeleteItem:
    """Test delete item endpoint."""

    def test_delete_item_success(self, client, auth_headers, db_session):
        """Test successful item deletion."""
        item = Item(name="Item to Delete")
        db_session.add(item)
        db_session.commit()
        item_id = item.id

        response = client.delete(f"/api/v1/items/{item_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/v1/items/{item_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_item_not_found(self, client, auth_headers):
        """Test deleting non-existent item."""
        response = client.delete("/api/v1/items/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404

