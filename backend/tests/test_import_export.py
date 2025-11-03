"""
Backend tests for Import/Export API endpoints.
"""

import pytest
import csv
import json
import io
from fastapi import status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.item import Item
from app.models.location import Location
from app.models.item_stock import ItemStock
from app.models.blueprint import Blueprint
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
def test_location(client, db_session, test_user):
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
def test_item(client, db_session):
    """Create a test item."""
    item = Item(
        name="Test Item",
        description="A test item",
        category="Materials",
        metadata={"volume": 1.0},
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def test_blueprint(client, db_session, test_user, test_item):
    """Create a test blueprint."""
    blueprint = Blueprint(
        name="Test Blueprint",
        description="A test blueprint",
        category="Crafting",
        crafting_time_minutes=10,
        output_item_id=test_item.id,
        output_quantity=Decimal("1.0"),
        blueprint_data={"ingredients": []},
        is_public=False,
        created_by=test_user.id,
    )
    db_session.add(blueprint)
    db_session.commit()
    db_session.refresh(blueprint)
    return blueprint


class TestExportItems:
    def test_export_items_csv(self, client, auth_headers, test_item):
        """Test exporting items to CSV."""
        response = client.get("/api/v1/import-export/items.csv", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

        # Parse CSV
        csv_content = response.content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)

        assert len(rows) >= 1
        # Check that our test item is in the export
        item_ids = [row["id"] for row in rows]
        assert str(test_item.id) in item_ids

    def test_export_items_csv_filter_category(self, client, auth_headers, test_item):
        """Test exporting items filtered by category."""
        response = client.get(
            "/api/v1/import-export/items.csv?category=Materials", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

        csv_content = response.content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)

        # All items should be in Materials category
        for row in rows:
            assert row["category"] == "Materials"

    def test_export_items_json(self, client, auth_headers, test_item):
        """Test exporting items to JSON."""
        response = client.get("/api/v1/import-export/items.json", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Check that our test item is in the export
        item_ids = [item["id"] for item in data]
        assert str(test_item.id) in item_ids

        # Verify structure
        test_item_data = next(item for item in data if item["id"] == str(test_item.id))
        assert test_item_data["name"] == test_item.name
        assert test_item_data["category"] == test_item.category


class TestExportInventory:
    def test_export_inventory_csv(
        self, client, auth_headers, test_user, test_item, test_location, db_session
    ):
        """Test exporting inventory to CSV."""
        # Create inventory stock
        stock = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("100.0"),
            reserved_quantity=Decimal("10.0"),
            updated_by=test_user.id,
        )
        db_session.add(stock)
        db_session.commit()

        response = client.get("/api/v1/import-export/inventory.csv", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

        csv_content = response.content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)

        assert len(rows) >= 1
        # Check that our stock is in the export
        stock_rows = [row for row in rows if row["item_id"] == str(test_item.id)]
        assert len(stock_rows) > 0

    def test_export_inventory_json(
        self, client, auth_headers, test_user, test_item, test_location, db_session
    ):
        """Test exporting inventory to JSON."""
        stock = ItemStock(
            item_id=test_item.id,
            location_id=test_location.id,
            quantity=Decimal("50.0"),
            reserved_quantity=Decimal("5.0"),
            updated_by=test_user.id,
        )
        db_session.add(stock)
        db_session.commit()

        response = client.get("/api/v1/import-export/inventory.json", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Find our stock
        stock_data = next((s for s in data if s["item_id"] == str(test_item.id)), None)
        assert stock_data is not None
        assert float(stock_data["quantity"]) == 50.0


class TestExportBlueprints:
    def test_export_blueprints_csv(self, client, auth_headers, test_blueprint):
        """Test exporting blueprints to CSV."""
        response = client.get("/api/v1/import-export/blueprints.csv", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        csv_content = response.content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)

        # Should include user's own blueprint
        blueprint_ids = [row["id"] for row in rows]
        assert str(test_blueprint.id) in blueprint_ids

    def test_export_blueprints_json(self, client, auth_headers, test_blueprint):
        """Test exporting blueprints to JSON."""
        response = client.get("/api/v1/import-export/blueprints.json", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)

        blueprint_ids = [bp["id"] for bp in data]
        assert str(test_blueprint.id) in blueprint_ids


class TestImportItems:
    def test_import_items_csv_valid(self, client, auth_headers, db_session):
        """Test importing valid items from CSV."""
        csv_content = """id,name,description,category,subcategory,rarity,metadata
550e8400-e29b-41d4-a716-446655440000,Imported Item,An imported item,Materials,Metals,common,"{""volume"": 2.0}"
"""
        files = {"file": ("items.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

        response = client.post(
            "/api/v1/import-export/items/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert data["imported_count"] == 1
        assert data["failed_count"] == 0

        # Verify item was created
        imported_item = db_session.query(Item).filter(Item.name == "Imported Item").first()
        assert imported_item is not None
        assert imported_item.category == "Materials"

    def test_import_items_csv_invalid_uuid(self, client, auth_headers):
        """Test importing items with invalid UUID."""
        csv_content = """id,name,description,category
invalid-uuid,Test Item,Description,Materials
"""
        files = {"file": ("items.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

        response = client.post(
            "/api/v1/import-export/items/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is False
        assert data["failed_count"] >= 1
        assert len(data["errors"]) > 0
        assert "Invalid UUID" in data["errors"][0]["message"]

    def test_import_items_csv_missing_name(self, client, auth_headers):
        """Test importing items with missing required field."""
        csv_content = """id,description,category
550e8400-e29b-41d4-a716-446655440000,Description,Materials
"""
        files = {"file": ("items.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

        response = client.post(
            "/api/v1/import-export/items/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["failed_count"] >= 1
        assert any("name is required" in error["message"] for error in data["errors"])

    def test_import_items_json_valid(self, client, auth_headers, db_session):
        """Test importing valid items from JSON."""
        json_data = [
            {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "name": "JSON Imported Item",
                "description": "Imported via JSON",
                "category": "Consumables",
                "metadata": {"weight": 0.5},
            }
        ]

        files = {
            "file": (
                "items.json",
                io.BytesIO(json.dumps(json_data).encode("utf-8")),
                "application/json",
            )
        }

        response = client.post(
            "/api/v1/import-export/items/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert data["imported_count"] == 1

        # Verify item was created
        imported_item = db_session.query(Item).filter(Item.name == "JSON Imported Item").first()
        assert imported_item is not None

    def test_import_items_update_existing(self, client, auth_headers, test_item, db_session):
        """Test importing updates existing item."""
        csv_content = f"""id,name,description,category
{test_item.id},{test_item.name},Updated description,Updated Category
"""
        files = {"file": ("items.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

        response = client.post(
            "/api/v1/import-export/items/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["imported_count"] == 1

        # Verify item was updated
        db_session.refresh(test_item)
        assert test_item.description == "Updated description"
        assert test_item.category == "Updated Category"


class TestImportInventory:
    def test_import_inventory_csv_valid(
        self, client, auth_headers, test_user, test_item, test_location, db_session
    ):
        """Test importing valid inventory from CSV."""
        csv_content = f"""item_id,location_id,quantity,reserved_quantity
{test_item.id},{test_location.id},100.0,10.0
"""
        files = {"file": ("inventory.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

        response = client.post(
            "/api/v1/import-export/inventory/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert data["imported_count"] == 1

        # Verify stock was created/updated
        stock = (
            db_session.query(ItemStock)
            .filter(
                ItemStock.item_id == test_item.id,
                ItemStock.location_id == test_location.id,
            )
            .first()
        )
        assert stock is not None
        assert stock.quantity == Decimal("100.0")
        assert stock.reserved_quantity == Decimal("10.0")

    def test_import_inventory_invalid_item_id(self, client, auth_headers, test_location):
        """Test importing inventory with invalid item ID."""
        csv_content = f"""item_id,location_id,quantity,reserved_quantity
00000000-0000-0000-0000-000000000000,{test_location.id},100.0,10.0
"""
        files = {"file": ("inventory.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

        response = client.post(
            "/api/v1/import-export/inventory/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["failed_count"] >= 1
        assert any("not found" in error["message"].lower() for error in data["errors"])

    def test_import_inventory_reserved_exceeds_quantity(
        self, client, auth_headers, test_item, test_location
    ):
        """Test importing inventory where reserved exceeds quantity."""
        csv_content = f"""item_id,location_id,quantity,reserved_quantity
{test_item.id},{test_location.id},10.0,20.0
"""
        files = {"file": ("inventory.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

        response = client.post(
            "/api/v1/import-export/inventory/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["failed_count"] >= 1
        assert any("cannot exceed" in error["message"] for error in data["errors"])


class TestImportBlueprints:
    def test_import_blueprints_csv_valid(
        self, client, auth_headers, test_user, test_item, db_session
    ):
        """Test importing valid blueprint from CSV."""
        # blueprint_data needs to be a JSON object with 'ingredients' array, not just an array
        blueprint_data_obj = {
            "ingredients": [{"item_id": str(test_item.id), "quantity": 2.0, "optional": False}]
        }
        ingredients_json = json.dumps(blueprint_data_obj)
        # Escape quotes for CSV
        escaped_json = ingredients_json.replace('"', '""')
        csv_content = f"""id,name,description,category,crafting_time_minutes,output_item_id,output_quantity,is_public,blueprint_data
770e8400-e29b-41d4-a716-446655440000,Imported Blueprint,Description,Crafting,15,{test_item.id},1.0,false,"{escaped_json}"
"""
        files = {"file": ("blueprints.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

        response = client.post(
            "/api/v1/import-export/blueprints/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True, f"Import failed: {data.get('errors', [])}"
        assert data["imported_count"] == 1

        # Verify blueprint was created
        imported_bp = (
            db_session.query(Blueprint).filter(Blueprint.name == "Imported Blueprint").first()
        )
        assert imported_bp is not None
        assert imported_bp.crafting_time_minutes == 15

    def test_import_blueprints_json_valid(
        self, client, auth_headers, test_user, test_item, db_session
    ):
        """Test importing valid blueprint from JSON."""
        json_data = [
            {
                "id": "880e8400-e29b-41d4-a716-446655440000",
                "name": "JSON Imported Blueprint",
                "description": "Imported via JSON",
                "category": "Crafting",
                "crafting_time_minutes": 20,
                "output_item_id": str(test_item.id),
                "output_quantity": "2.0",
                "is_public": False,
                "blueprint_data": {
                    "ingredients": [
                        {"item_id": str(test_item.id), "quantity": 3.0, "optional": False}
                    ]
                },
            }
        ]

        files = {
            "file": (
                "blueprints.json",
                io.BytesIO(json.dumps(json_data).encode("utf-8")),
                "application/json",
            )
        }

        response = client.post(
            "/api/v1/import-export/blueprints/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["success"] is True
        assert data["imported_count"] == 1

        # Verify blueprint and ingredients were created
        imported_bp = (
            db_session.query(Blueprint).filter(Blueprint.name == "JSON Imported Blueprint").first()
        )
        assert imported_bp is not None
        assert imported_bp.blueprint_data is not None
        assert "ingredients" in imported_bp.blueprint_data
        assert len(imported_bp.blueprint_data["ingredients"]) == 1

    def test_import_blueprints_missing_ingredients(self, client, auth_headers, test_item):
        """Test importing blueprint with missing ingredients."""
        json_data = [
            {
                "name": "Invalid Blueprint",
                "output_item_id": str(test_item.id),
                "output_quantity": "1.0",
                "blueprint_data": {},  # Missing ingredients
            }
        ]

        files = {
            "file": (
                "blueprints.json",
                io.BytesIO(json.dumps(json_data).encode("utf-8")),
                "application/json",
            )
        }

        response = client.post(
            "/api/v1/import-export/blueprints/import", headers=auth_headers, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["failed_count"] >= 1, f"Expected failures but got: {data}"
        # Should fail because blueprint_data is missing 'ingredients' array
        assert any(
            "ingredients" in error["message"].lower()
            or "blueprint_data is required" in error["message"].lower()
            for error in data["errors"]
        ), f"Expected 'ingredients' or 'blueprint_data is required' error but got: {data['errors']}"
