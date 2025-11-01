"""
Tests for Inventory API endpoints.
"""

import pytest
from decimal import Decimal
from app.models.item import Item
from app.models.location import Location
from app.models.item_stock import ItemStock
from app.models.item_history import ItemHistory
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.ship import Ship
from app.models.user import User
from app.core.security import create_access_token, hash_password


@pytest.fixture
def test_user(db_session):
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
def test_user2(db_session):
    """Create a second test user."""
    user = User(
        email="testuser2@example.com",
        username="testuser2",
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
def test_item(db_session):
    """Create a test item."""
    item = Item(name="Quantum Fuel", category="Consumables", description="Fuel for quantum travel")
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def test_item2(db_session):
    """Create a second test item."""
    item = Item(name="Steel Ingot", category="Materials", description="Refined steel")
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def test_location(test_user, db_session):
    """Create a test location."""
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
def test_location2(test_user, db_session):
    """Create a second test location."""
    location = Location(
        name="Test Warehouse",
        type="warehouse",
        owner_type="user",
        owner_id=test_user.id,
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def test_location_other_user(test_user2, db_session):
    """Create a location owned by another user."""
    location = Location(
        name="Other User Station",
        type="station",
        owner_type="user",
        owner_id=test_user2.id,
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def test_org(test_user, db_session):
    """Create a test organization with test_user as owner."""
    org = Organization(name="Test Org", slug="test-org")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    # Add user as owner
    membership = OrganizationMember(
        organization_id=org.id,
        user_id=test_user.id,
        role="owner",
    )
    db_session.add(membership)
    db_session.commit()
    return org


@pytest.fixture
def test_org_location(test_org, db_session):
    """Create an organization-owned location."""
    location = Location(
        name="Org Warehouse",
        type="warehouse",
        owner_type="organization",
        owner_id=test_org.id,
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def test_item_stock(test_item, test_location, test_user, db_session):
    """Create a test item stock."""
    stock = ItemStock(
        item_id=test_item.id,
        location_id=test_location.id,
        quantity=Decimal("100.0"),
        reserved_quantity=Decimal("10.0"),
        updated_by=test_user.id,
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)
    return stock


class TestListInventory:
    """Test list inventory endpoint."""

    def test_list_inventory_empty(self, client, auth_headers):
        """Test listing inventory when none exists."""
        response = client.get("/api/v1/inventory", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_inventory_with_stock(self, client, auth_headers, test_item_stock):
        """Test listing inventory with stock data."""
        response = client.get("/api/v1/inventory", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["item_id"] == test_item_stock.item_id
        assert Decimal(data["items"][0]["quantity"]) == Decimal("100.0")

    def test_list_inventory_filter_by_item(self, client, auth_headers, test_item, test_item2, test_location, test_user, db_session):
        """Test filtering inventory by item_id."""
        # Create stock for both items
        stock1 = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("50.0"),
            updated_by=test_user.id,
        )
        stock2 = ItemStock(
            item_id=test_item2.id,
            location_id=test_location.id,
            quantity=Decimal("25.0"),
            updated_by=test_user.id,
        )
        db_session.add_all([stock1, stock2])
        db_session.commit()

        response = client.get(f"/api/v1/inventory?item_id={test_item.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["item_id"] == test_item.id

    def test_list_inventory_filter_by_location(self, client, auth_headers, test_item, test_location, test_location2, test_user, db_session):
        """Test filtering inventory by location_id."""
        # Create stock at both locations
        stock1 = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("50.0"),
            updated_by=test_user.id,
        )
        stock2 = ItemStock(
            item_id=test_item.id,
            location_id=test_location2.id,
            quantity=Decimal("25.0"),
            updated_by=test_user.id,
        )
        db_session.add_all([stock1, stock2])
        db_session.commit()

        response = client.get(f"/api/v1/inventory?location_id={test_location.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["location_id"] == test_location.id

    def test_list_inventory_search(self, client, auth_headers, test_item, test_item2, test_location, test_user, db_session):
        """Test searching inventory by item name."""
        # Create stock for both items
        stock1 = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("50.0"),
            updated_by=test_user.id,
        )
        stock2 = ItemStock(
            item_id=test_item2.id,
            location_id=test_location.id,
            quantity=Decimal("25.0"),
            updated_by=test_user.id,
        )
        db_session.add_all([stock1, stock2])
        db_session.commit()

        response = client.get("/api/v1/inventory?search=Quantum", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "Quantum" in data["items"][0]["item_name"]

    def test_list_inventory_only_accessible_locations(self, client, auth_headers, test_item, test_location, test_location_other_user, test_user, test_user2, db_session):
        """Test that inventory only shows accessible locations."""
        # Create stock at both locations
        stock1 = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("50.0"),
            updated_by=test_user.id,
        )
        stock2 = ItemStock(
            item_id=test_item.id,
            location_id=test_location_other_user.id,
            quantity=Decimal("25.0"),
            updated_by=test_user2.id,
        )
        db_session.add_all([stock1, stock2])
        db_session.commit()

        response = client.get("/api/v1/inventory", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should only see own location
        assert data["total"] == 1
        assert data["items"][0]["location_id"] == test_location.id


class TestAdjustInventory:
    """Test adjust inventory endpoint."""

    def test_adjust_inventory_add_items(self, client, auth_headers, test_item, test_location):
        """Test adding items to inventory."""
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_location.id,
                "quantity_change": "25.5",
                "notes": "Purchased from store",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["quantity"]) == Decimal("25.5")
        assert Decimal(data["reserved_quantity"]) == Decimal("0.0")
        assert Decimal(data["available_quantity"]) == Decimal("25.5")
        assert data["item_name"] == test_item.name
        assert data["location_name"] == test_location.name

    def test_adjust_inventory_remove_items(self, client, auth_headers, test_item_stock):
        """Test removing items from inventory."""
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item_stock.item_id,
                "location_id": test_item_stock.location_id,
                "quantity_change": "-20.0",
                "notes": "Used in operation",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["quantity"]) == Decimal("80.0")  # 100 - 20
        assert Decimal(data["available_quantity"]) == Decimal("70.0")  # 80 - 10 reserved

    def test_adjust_inventory_item_not_found(self, client, auth_headers, test_location):
        """Test adjusting inventory with non-existent item."""
        import uuid
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": str(uuid.uuid4()),
                "location_id": test_location.id,
                "quantity_change": "10.0",
            },
        )
        assert response.status_code == 404

    def test_adjust_inventory_location_not_found(self, client, auth_headers, test_item):
        """Test adjusting inventory with non-existent location."""
        import uuid
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": str(uuid.uuid4()),
                "quantity_change": "10.0",
            },
        )
        assert response.status_code == 404

    def test_adjust_inventory_access_denied(self, client, auth_headers, test_item, test_location_other_user):
        """Test adjusting inventory at inaccessible location."""
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_location_other_user.id,
                "quantity_change": "10.0",
            },
        )
        assert response.status_code == 403

    def test_adjust_inventory_insufficient_quantity(self, client, auth_headers, test_item_stock):
        """Test removing more items than available."""
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item_stock.item_id,
                "location_id": test_item_stock.location_id,
                "quantity_change": "-95.0",  # Only 90 available (100 - 10 reserved)
            },
        )
        assert response.status_code == 400
        assert "insufficient" in response.json()["detail"].lower() or "only" in response.json()["detail"].lower()

    def test_adjust_inventory_zero_quantity_change(self, client, auth_headers, test_item, test_location):
        """Test adjusting with zero quantity change."""
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_location.id,
                "quantity_change": "0.0",
            },
        )
        assert response.status_code == 422  # Validation error

    def test_adjust_inventory_creates_history(self, client, auth_headers, test_item, test_location, test_user, db_session):
        """Test that adjusting inventory creates history record."""
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_location.id,
                "quantity_change": "25.0",
                "notes": "Test adjustment",
            },
        )
        assert response.status_code == 200

        # Check history was created
        history = (
            db_session.query(ItemHistory)
            .filter(
                ItemHistory.item_id == test_item.id,
                ItemHistory.location_id == test_location.id,
                ItemHistory.transaction_type == "add",
            )
            .first()
        )
        assert history is not None
        assert history.quantity_change == Decimal("25.0")
        assert history.notes == "Test adjustment"
        assert history.performed_by == test_user.id


class TestTransferInventory:
    """Test transfer inventory endpoint."""

    def test_transfer_inventory_success(self, client, auth_headers, test_item, test_location, test_location2, test_user, db_session):
        """Test transferring items between locations."""
        # Create source stock
        source_stock = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("100.0"),
            updated_by=test_user.id,
        )
        db_session.add(source_stock)
        db_session.commit()

        response = client.post(
            "/api/v1/inventory/transfer",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "from_location_id": test_location.id,
                "to_location_id": test_location2.id,
                "quantity": "30.0",
                "notes": "Moving to warehouse",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "Successfully transferred" in data["message"]
        assert Decimal(data["from_location"]["quantity"]) == Decimal("70.0")
        assert Decimal(data["to_location"]["quantity"]) == Decimal("30.0")

    def test_transfer_inventory_insufficient_quantity(self, client, auth_headers, test_item, test_location, test_location2, test_user, db_session):
        """Test transferring more items than available."""
        # Create source stock with limited quantity
        source_stock = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("50.0"),
            reserved_quantity=Decimal("20.0"),  # Only 30 available
            updated_by=test_user.id,
        )
        db_session.add(source_stock)
        db_session.commit()

        response = client.post(
            "/api/v1/inventory/transfer",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "from_location_id": test_location.id,
                "to_location_id": test_location2.id,
                "quantity": "40.0",  # More than available
            },
        )
        assert response.status_code == 400
        assert "insufficient" in response.json()["detail"].lower()

    def test_transfer_inventory_same_location(self, client, auth_headers, test_item, test_location):
        """Test transferring to same location."""
        response = client.post(
            "/api/v1/inventory/transfer",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "from_location_id": test_location.id,
                "to_location_id": test_location.id,
                "quantity": "10.0",
            },
        )
        assert response.status_code == 422  # Validation error

    def test_transfer_inventory_access_denied_source(self, client, auth_headers, test_item, test_location_other_user, test_location):
        """Test transferring from inaccessible source location."""
        response = client.post(
            "/api/v1/inventory/transfer",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "from_location_id": test_location_other_user.id,
                "to_location_id": test_location.id,
                "quantity": "10.0",
            },
        )
        assert response.status_code == 403

    def test_transfer_inventory_access_denied_dest(self, client, auth_headers, test_item, test_location, test_location_other_user):
        """Test transferring to inaccessible destination location."""
        response = client.post(
            "/api/v1/inventory/transfer",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "from_location_id": test_location.id,
                "to_location_id": test_location_other_user.id,
                "quantity": "10.0",
            },
        )
        assert response.status_code == 403

    def test_transfer_inventory_creates_history(self, client, auth_headers, test_item, test_location, test_location2, test_user, db_session):
        """Test that transfer creates history records for both locations."""
        # Create source stock
        source_stock = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("100.0"),
            updated_by=test_user.id,
        )
        db_session.add(source_stock)
        db_session.commit()

        response = client.post(
            "/api/v1/inventory/transfer",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "from_location_id": test_location.id,
                "to_location_id": test_location2.id,
                "quantity": "25.0",
            },
        )
        assert response.status_code == 200

        # Check history was created for both locations
        from_history = (
            db_session.query(ItemHistory)
            .filter(
                ItemHistory.item_id == test_item.id,
                ItemHistory.location_id == test_location.id,
                ItemHistory.transaction_type == "transfer",
                ItemHistory.quantity_change < 0,
            )
            .first()
        )
        assert from_history is not None
        assert from_history.quantity_change == Decimal("-25.0")

        to_history = (
            db_session.query(ItemHistory)
            .filter(
                ItemHistory.item_id == test_item.id,
                ItemHistory.location_id == test_location2.id,
                ItemHistory.transaction_type == "transfer",
                ItemHistory.quantity_change > 0,
            )
            .first()
        )
        assert to_history is not None
        assert to_history.quantity_change == Decimal("25.0")


class TestReserveStock:
    """Test reserve stock endpoint."""

    def test_reserve_stock_success(self, client, auth_headers, test_item_stock):
        """Test reserving stock."""
        response = client.post(
            "/api/v1/inventory/reserve",
            headers=auth_headers,
            json={
                "item_id": test_item_stock.item_id,
                "location_id": test_item_stock.location_id,
                "quantity": "20.0",
                "notes": "Reserved for craft",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["reserved_quantity"]) == Decimal("30.0")  # 10 + 20
        assert Decimal(data["available_quantity"]) == Decimal("70.0")  # 100 - 30

    def test_reserve_stock_insufficient_quantity(self, client, auth_headers, test_item_stock):
        """Test reserving more than available."""
        response = client.post(
            "/api/v1/inventory/reserve",
            headers=auth_headers,
            json={
                "item_id": test_item_stock.item_id,
                "location_id": test_item_stock.location_id,
                "quantity": "95.0",  # Only 90 available
            },
        )
        assert response.status_code == 400
        assert "insufficient" in response.json()["detail"].lower()

    def test_reserve_stock_item_not_found(self, client, auth_headers, test_location):
        """Test reserving stock for non-existent item."""
        import uuid
        response = client.post(
            "/api/v1/inventory/reserve",
            headers=auth_headers,
            json={
                "item_id": str(uuid.uuid4()),
                "location_id": test_location.id,
                "quantity": "10.0",
            },
        )
        assert response.status_code == 404

    def test_reserve_stock_access_denied(self, client, auth_headers, test_item, test_location_other_user):
        """Test reserving stock at inaccessible location."""
        response = client.post(
            "/api/v1/inventory/reserve",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_location_other_user.id,
                "quantity": "10.0",
            },
        )
        assert response.status_code == 403


class TestUnreserveStock:
    """Test unreserve stock endpoint."""

    def test_unreserve_stock_success(self, client, auth_headers, test_item_stock):
        """Test unreserving stock."""
        response = client.post(
            "/api/v1/inventory/unreserve",
            headers=auth_headers,
            json={
                "item_id": test_item_stock.item_id,
                "location_id": test_item_stock.location_id,
                "quantity": "5.0",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["reserved_quantity"]) == Decimal("5.0")  # 10 - 5
        assert Decimal(data["available_quantity"]) == Decimal("95.0")  # 100 - 5

    def test_unreserve_stock_insufficient_reserved(self, client, auth_headers, test_item_stock):
        """Test unreserving more than reserved."""
        response = client.post(
            "/api/v1/inventory/unreserve",
            headers=auth_headers,
            json={
                "item_id": test_item_stock.item_id,
                "location_id": test_item_stock.location_id,
                "quantity": "15.0",  # Only 10 reserved
            },
        )
        assert response.status_code == 400

    def test_unreserve_stock_no_stock_record(self, client, auth_headers, test_item, test_location):
        """Test unreserving when no stock record exists."""
        response = client.post(
            "/api/v1/inventory/unreserve",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_location.id,
                "quantity": "10.0",
            },
        )
        assert response.status_code == 404


class TestInventoryHistory:
    """Test inventory history endpoint."""

    def test_get_inventory_history_empty(self, client, auth_headers):
        """Test getting history when none exists."""
        response = client.get("/api/v1/inventory/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["history"] == []

    def test_get_inventory_history_with_data(self, client, auth_headers, test_item, test_location, test_user, db_session):
        """Test getting history with records."""
        # Create some history records
        history1 = ItemHistory(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity_change=Decimal("25.0"),
            transaction_type="add",
            performed_by=test_user.id,
            notes="Initial stock",
        )
        history2 = ItemHistory(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity_change=Decimal("-5.0"),
            transaction_type="remove",
            performed_by=test_user.id,
        )
        db_session.add_all([history1, history2])
        db_session.commit()

        response = client.get("/api/v1/inventory/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["history"]) == 2
        # Should be ordered newest first
        assert data["history"][0]["transaction_type"] == "remove"

    def test_get_inventory_history_filter_by_item(self, client, auth_headers, test_item, test_item2, test_location, test_user, db_session):
        """Test filtering history by item_id."""
        # Create history for both items
        history1 = ItemHistory(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity_change=Decimal("25.0"),
            transaction_type="add",
            performed_by=test_user.id,
        )
        history2 = ItemHistory(
            item_id=test_item2.id,
            location_id=test_location.id,
            quantity_change=Decimal("10.0"),
            transaction_type="add",
            performed_by=test_user.id,
        )
        db_session.add_all([history1, history2])
        db_session.commit()

        response = client.get(f"/api/v1/inventory/history?item_id={test_item.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["history"][0]["item_id"] == test_item.id

    def test_get_inventory_history_filter_by_location(self, client, auth_headers, test_item, test_location, test_location2, test_user, db_session):
        """Test filtering history by location_id."""
        # Create history at both locations
        history1 = ItemHistory(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity_change=Decimal("25.0"),
            transaction_type="add",
            performed_by=test_user.id,
        )
        history2 = ItemHistory(
            item_id=test_item.id,
            location_id=test_location2.id,
            quantity_change=Decimal("10.0"),
            transaction_type="add",
            performed_by=test_user.id,
        )
        db_session.add_all([history1, history2])
        db_session.commit()

        response = client.get(f"/api/v1/inventory/history?location_id={test_location.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["history"][0]["location_id"] == test_location.id

    def test_get_inventory_history_filter_by_transaction_type(self, client, auth_headers, test_item, test_location, test_user, db_session):
        """Test filtering history by transaction_type."""
        # Create history with different types
        history1 = ItemHistory(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity_change=Decimal("25.0"),
            transaction_type="add",
            performed_by=test_user.id,
        )
        history2 = ItemHistory(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity_change=Decimal("-5.0"),
            transaction_type="remove",
            performed_by=test_user.id,
        )
        db_session.add_all([history1, history2])
        db_session.commit()

        response = client.get("/api/v1/inventory/history?transaction_type=add", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["history"][0]["transaction_type"] == "add"

    def test_get_inventory_history_invalid_transaction_type(self, client, auth_headers):
        """Test filtering history with invalid transaction_type."""
        response = client.get("/api/v1/inventory/history?transaction_type=invalid", headers=auth_headers)
        assert response.status_code == 400

    def test_get_inventory_history_only_accessible_locations(self, client, auth_headers, test_item, test_location, test_location_other_user, test_user, test_user2, db_session):
        """Test that history only shows accessible locations."""
        # Create history at both locations
        history1 = ItemHistory(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity_change=Decimal("25.0"),
            transaction_type="add",
            performed_by=test_user.id,
        )
        history2 = ItemHistory(
            item_id=test_item.id,
            location_id=test_location_other_user.id,
            quantity_change=Decimal("10.0"),
            transaction_type="add",
            performed_by=test_user2.id,
        )
        db_session.add_all([history1, history2])
        db_session.commit()

        response = client.get("/api/v1/inventory/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should only see own location history
        assert data["total"] == 1
        assert data["history"][0]["location_id"] == test_location.id


class TestInventoryOrganizationAccess:
    """Test inventory access control for organization-owned locations."""

    def test_adjust_inventory_org_location_as_member(self, client, auth_headers, test_item, test_org_location, test_user, test_org, db_session):
        """Test adjusting inventory at org location as member."""
        # Update user role to member (already owner from fixture)
        membership = (
            db_session.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == test_user.id,
                OrganizationMember.organization_id == test_org.id,
            )
            .first()
        )
        membership.role = "member"
        db_session.commit()

        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_org_location.id,
                "quantity_change": "25.0",
            },
        )
        assert response.status_code == 200

    def test_adjust_inventory_org_location_as_viewer(self, client, auth_headers, test_item, test_org_location, test_user, test_org, db_session):
        """Test adjusting inventory at org location as viewer (should fail)."""
        # Update user role to viewer (already owner from fixture)
        membership = (
            db_session.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == test_user.id,
                OrganizationMember.organization_id == test_org.id,
            )
            .first()
        )
        membership.role = "viewer"
        db_session.commit()

        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_org_location.id,
                "quantity_change": "25.0",
            },
        )
        assert response.status_code == 403

    def test_list_inventory_org_location(self, client, auth_headers, test_item, test_org_location, test_user, test_org, db_session):
        """Test listing inventory at org location."""
        # Create stock at org location (user is already owner from fixture)
        stock = ItemStock(
            item_id=test_item.id,
            location_id=test_org_location.id,
            quantity=Decimal("100.0"),
            updated_by=test_user.id,
        )
        db_session.add(stock)
        db_session.commit()

        response = client.get("/api/v1/inventory", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["location_id"] == test_org_location.id


@pytest.fixture
def test_ship(test_user, test_location, db_session):
    """Create a test ship with cargo location."""
    import uuid
    temp_owner_id = str(uuid.uuid4())
    
    # Create cargo location
    cargo_loc = Location(
        name="Ship Cargo",
        type="ship",
        owner_type="ship",
        owner_id=temp_owner_id,
    )
    db_session.add(cargo_loc)
    db_session.flush()

    ship = Ship(
        name="Test Ship",
        ship_type="Constellation",
        owner_type="user",
        owner_id=test_user.id,
        current_location_id=test_location.id,
        cargo_location_id=cargo_loc.id,
    )
    db_session.add(ship)
    db_session.flush()
    cargo_loc.owner_id = ship.id
    db_session.commit()
    return ship


class TestInventoryShipAccess:
    """Test inventory access control for ship-owned locations (cargo)."""

    def test_list_inventory_ship_cargo(self, client, auth_headers, test_item, test_ship, test_user, db_session):
        """Test listing inventory at ship cargo location."""
        cargo_location = db_session.query(Location).filter(Location.id == test_ship.cargo_location_id).first()
        
        # Create stock at ship cargo location
        stock = ItemStock(
            item_id=test_item.id,
            location_id=cargo_location.id,
            quantity=Decimal("50.0"),
            updated_by=test_user.id,
        )
        db_session.add(stock)
        db_session.commit()

        response = client.get("/api/v1/inventory", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["location_id"] == cargo_location.id

    def test_adjust_inventory_ship_cargo(self, client, auth_headers, test_item, test_ship, test_user, db_session):
        """Test adjusting inventory at ship cargo location."""
        cargo_location = db_session.query(Location).filter(Location.id == test_ship.cargo_location_id).first()
        
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": cargo_location.id,
                "quantity_change": "25.0",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["quantity"]) == Decimal("25.0")


class TestInventoryPagination:
    """Test pagination for inventory endpoints."""

    def test_list_inventory_pagination(self, client, auth_headers, test_item, test_item2, test_location, test_location2, test_user, db_session):
        """Test pagination in list inventory."""
        # Create multiple stock records with unique item/location combinations
        # Use a pattern to create 5 unique combinations
        stock_combinations = [
            (test_item.id, test_location.id),
            (test_item2.id, test_location.id),
            (test_item.id, test_location2.id),
            (test_item2.id, test_location2.id),
            (test_item.id, test_location.id),  # Duplicate combination - will update existing
        ]
        
        # Create initial stock for the first combination
        stock1 = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("10.0"),
            updated_by=test_user.id,
        )
        db_session.add(stock1)
        db_session.flush()
        
        # Create remaining unique combinations
        stocks = [
            ItemStock(
                item_id=item_id,
                location_id=loc_id,
                quantity=Decimal(f"{(i + 2) * 10}.0"),
                updated_by=test_user.id,
            )
            for i, (item_id, loc_id) in enumerate(stock_combinations[1:])
            if (item_id, loc_id) != (test_item.id, test_location.id)  # Skip duplicate
        ]
        db_session.add_all(stocks)
        db_session.commit()

        # First page
        response = client.get("/api/v1/inventory?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["skip"] == 0
        assert data["limit"] == 2
        assert data["pages"] >= 1

        # Second page
        response = client.get("/api/v1/inventory?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2


class TestInventoryEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_adjust_inventory_large_quantity(self, client, auth_headers, test_item, test_location):
        """Test adjusting inventory with large quantity."""
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_location.id,
                "quantity_change": "999999.999",
            },
        )
        assert response.status_code == 200

    def test_adjust_inventory_fractional_quantity(self, client, auth_headers, test_item, test_location):
        """Test adjusting inventory with fractional quantity."""
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_location.id,
                "quantity_change": "0.001",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["quantity"]) == Decimal("0.001")

    def test_transfer_entire_stock(self, client, auth_headers, test_item, test_location, test_location2, test_user, db_session):
        """Test transferring all available stock."""
        # Create source stock
        source_stock = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("100.0"),
            reserved_quantity=Decimal("10.0"),  # Only 90 available
            updated_by=test_user.id,
        )
        db_session.add(source_stock)
        db_session.commit()

        response = client.post(
            "/api/v1/inventory/transfer",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "from_location_id": test_location.id,
                "to_location_id": test_location2.id,
                "quantity": "90.0",  # All available
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["from_location"]["quantity"]) == Decimal("10.0")  # Only reserved left
        assert Decimal(data["to_location"]["quantity"]) == Decimal("90.0")

    def test_reserve_all_available(self, client, auth_headers, test_item_stock):
        """Test reserving all available stock."""
        response = client.post(
            "/api/v1/inventory/reserve",
            headers=auth_headers,
            json={
                "item_id": test_item_stock.item_id,
                "location_id": test_item_stock.location_id,
                "quantity": "90.0",  # All available (100 - 10 reserved)
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["reserved_quantity"]) == Decimal("100.0")  # 10 + 90
        assert Decimal(data["available_quantity"]) == Decimal("0.0")

    def test_unreserve_all_reserved(self, client, auth_headers, test_item_stock):
        """Test unreserving all reserved stock."""
        response = client.post(
            "/api/v1/inventory/unreserve",
            headers=auth_headers,
            json={
                "item_id": test_item_stock.item_id,
                "location_id": test_item_stock.location_id,
                "quantity": "10.0",  # All reserved
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["reserved_quantity"]) == Decimal("0.0")
        assert Decimal(data["available_quantity"]) == Decimal("100.0")

    def test_adjust_inventory_creates_stock_record(self, client, auth_headers, test_item, test_location, db_session):
        """Test that adjusting inventory creates stock record if it doesn't exist."""
        # Verify no stock record exists
        stock = (
            db_session.query(ItemStock)
            .filter(
                ItemStock.item_id == test_item.id,
                ItemStock.location_id == test_location.id,
            )
            .first()
        )
        assert stock is None

        # Adjust inventory - should create stock record
        response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": test_item.id,
                "location_id": test_location.id,
                "quantity_change": "10.0",
            },
        )
        assert response.status_code == 200

        # Verify stock record was created
        stock = (
            db_session.query(ItemStock)
            .filter(
                ItemStock.item_id == test_item.id,
                ItemStock.location_id == test_location.id,
            )
            .first()
        )
        assert stock is not None
        assert stock.quantity == Decimal("10.0")

    def test_get_inventory_history_pagination(self, client, auth_headers, test_item, test_location, test_user, db_session):
        """Test pagination in inventory history."""
        # Create multiple history records
        histories = [
            ItemHistory(
                item_id=test_item.id,
                location_id=test_location.id,
                quantity_change=Decimal(f"{i + 1}.0"),
                transaction_type="add",
                performed_by=test_user.id,
            )
            for i in range(5)
        ]
        db_session.add_all(histories)
        db_session.commit()

        # First page
        response = client.get("/api/v1/inventory/history?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) == 2
        assert data["skip"] == 0
        assert data["limit"] == 2

