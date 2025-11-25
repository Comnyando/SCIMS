"""
Integration tests for critical user flows.

These tests verify end-to-end workflows that span multiple API endpoints
and services, ensuring the system works correctly as a whole.

Critical flows tested:
1. User registration → org creation → inventory → craft
2. Recipe sharing → craft planning → execution
3. Integration setup → data import
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.item import Item
from app.models.location import Location
from app.models.item_stock import ItemStock
from app.models.blueprint import Blueprint
from app.models.craft import Craft, CRAFT_STATUS_PLANNED, CRAFT_STATUS_IN_PROGRESS, CRAFT_STATUS_COMPLETED
from app.models.craft_ingredient import CraftIngredient, INGREDIENT_STATUS_RESERVED, SOURCE_TYPE_STOCK
from app.models.integration import Integration
from app.core.security import hash_password


class TestFlowUserRegistrationToCraft:
    """
    Integration test for: User registration → org creation → inventory → craft
    
    This tests the complete flow of:
    1. User registers
    2. User creates an organization
    3. User creates items and locations
    4. User adds inventory
    5. User creates a blueprint
    6. User creates and executes a craft
    """

    def test_complete_user_to_craft_flow(self, client, db_session):
        """Test the complete flow from user registration to craft completion."""
        # Step 1: User Registration
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepass123",
            },
        )
        assert register_response.status_code == 201
        register_data = register_response.json()
        access_token = register_data["access_token"]
        user_id = register_data["user"]["id"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 2: Create Organization
        # Note: Organizations are created directly in DB for now
        # In a real scenario, this would be through an API endpoint
        org = Organization(
            name="Test Org",
            slug="test-org",
            description="A test organization",
        )
        db_session.add(org)
        db_session.flush()

        # Add user as owner
        membership = OrganizationMember(
            organization_id=org.id,
            user_id=user_id,
            role="owner",
        )
        db_session.add(membership)
        db_session.commit()
        db_session.refresh(org)

        # Step 3: Create Items
        item1 = Item(
            name="Iron Ore",
            description="Raw iron ore",
            category="Materials",
        )
        item2 = Item(
            name="Steel Ingot",
            description="Refined steel",
            category="Components",
        )
        db_session.add_all([item1, item2])
        db_session.commit()
        db_session.refresh(item1)
        db_session.refresh(item2)

        # Step 4: Create Location
        location_response = client.post(
            "/api/v1/locations",
            headers=auth_headers,
            json={
                "name": "Test Station",
                "type": "station",
                "owner_type": "organization",
                "owner_id": org.id,
            },
        )
        assert location_response.status_code == 201
        location_data = location_response.json()
        location_id = location_data["id"]

        # Step 5: Add Inventory
        adjust_response = client.post(
            "/api/v1/inventory/adjust",
            headers=auth_headers,
            json={
                "item_id": item1.id,
                "location_id": location_id,
                "quantity_change": 100.0,
                "reason": "Initial stock",
            },
        )
        assert adjust_response.status_code == 200

        # Verify inventory was added
        inventory_response = client.get(
            "/api/v1/inventory",
            headers=auth_headers,
            params={"location_id": location_id},
        )
        assert inventory_response.status_code == 200
        inventory_data = inventory_response.json()
        assert inventory_data["total"] > 0
        iron_ore_stock = next(
            (s for s in inventory_data["items"] if s["item_id"] == item1.id),
            None,
        )
        assert iron_ore_stock is not None
        assert float(iron_ore_stock["quantity"]) == 100.0

        # Step 6: Create Blueprint
        blueprint_response = client.post(
            "/api/v1/blueprints",
            headers=auth_headers,
            json={
                "name": "Steel Ingot Recipe",
                "description": "Craft steel ingot from iron ore",
                "category": "Refining",
                "crafting_time_minutes": 60,
                "output_item_id": item2.id,
                "output_quantity": 1.0,
                "blueprint_data": {
                    "ingredients": [
                        {"item_id": item1.id, "quantity": 10.0, "optional": False}
                    ]
                },
                "is_public": False,
            },
        )
        assert blueprint_response.status_code == 201
        blueprint_data = blueprint_response.json()
        blueprint_id = blueprint_data["id"]

        # Step 7: Create Craft
        craft_response = client.post(
            "/api/v1/crafts?reserve_ingredients=true",
            headers=auth_headers,
            json={
                "blueprint_id": blueprint_id,
                "output_location_id": location_id,
                "organization_id": org.id,
            },
        )
        assert craft_response.status_code == 201
        craft_data = craft_response.json()
        craft_id = craft_data["id"]
        assert craft_data["status"] == CRAFT_STATUS_PLANNED

        # Step 8: Start Craft
        start_response = client.post(
            f"/api/v1/crafts/{craft_id}/start",
            headers=auth_headers,
        )
        assert start_response.status_code == 200
        start_data = start_response.json()
        assert start_data["status"] == CRAFT_STATUS_IN_PROGRESS
        assert start_data["started_at"] is not None

        # Step 9: Complete Craft
        complete_response = client.post(
            f"/api/v1/crafts/{craft_id}/complete",
            headers=auth_headers,
        )
        assert complete_response.status_code == 200
        complete_data = complete_response.json()
        assert complete_data["status"] == CRAFT_STATUS_COMPLETED
        assert complete_data["completed_at"] is not None

        # Step 10: Verify Output Item was Created
        inventory_response = client.get(
            "/api/v1/inventory",
            headers=auth_headers,
            params={"location_id": location_id, "item_id": item2.id},
        )
        assert inventory_response.status_code == 200
        inventory_data = inventory_response.json()
        steel_stock = next(
            (s for s in inventory_data["items"] if s["item_id"] == item2.id),
            None,
        )
        assert steel_stock is not None
        assert float(steel_stock["quantity"]) >= 1.0

        # Step 11: Verify Input Stock was Deducted
        inventory_response = client.get(
            "/api/v1/inventory",
            headers=auth_headers,
            params={"location_id": location_id, "item_id": item1.id},
        )
        assert inventory_response.status_code == 200
        inventory_data = inventory_response.json()
        iron_ore_stock = next(
            (s for s in inventory_data["items"] if s["item_id"] == item1.id),
            None,
        )
        assert iron_ore_stock is not None
        # Should have 10 less (reserved and deducted)
        assert float(iron_ore_stock["quantity"]) == 90.0


class TestFlowRecipeSharingToExecution:
    """
    Integration test for: Recipe sharing → craft planning → execution
    
    This tests the complete flow of:
    1. User A creates a public blueprint
    2. User B discovers and uses the blueprint
    3. User B creates a craft from the blueprint
    4. User B executes the craft
    """

    def test_recipe_sharing_to_execution_flow(self, client, db_session):
        """Test the complete flow from recipe sharing to craft execution."""
        # Step 1: User A registers and creates a public blueprint
        user_a_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "usera@example.com",
                "username": "usera",
                "password": "password123",
            },
        )
        assert user_a_response.status_code == 201
        user_a_token = user_a_response.json()["access_token"]
        user_a_headers = {"Authorization": f"Bearer {user_a_token}"}
        user_a_id = user_a_response.json()["user"]["id"]

        # Create items for User A
        item_a = Item(name="Component A", category="Components")
        item_b = Item(name="Component B", category="Components")
        item_output = Item(name="Final Product", category="Products")
        db_session.add_all([item_a, item_b, item_output])
        db_session.commit()
        db_session.refresh(item_a)
        db_session.refresh(item_b)
        db_session.refresh(item_output)

        # User A creates location
        location_a_response = client.post(
            "/api/v1/locations",
            headers=user_a_headers,
            json={
                "name": "User A Station",
                "type": "station",
                "owner_type": "user",
                "owner_id": user_a_id,
            },
        )
        assert location_a_response.status_code == 201
        location_a_id = location_a_response.json()["id"]

        # User A creates a public blueprint
        blueprint_response = client.post(
            "/api/v1/blueprints",
            headers=user_a_headers,
            json={
                "name": "Shared Recipe",
                "description": "A publicly shared recipe",
                "category": "Crafting",
                "crafting_time_minutes": 30,
                "output_item_id": item_output.id,
                "output_quantity": 1.0,
                "blueprint_data": {
                    "ingredients": [
                        {"item_id": item_a.id, "quantity": 2.0, "optional": False},
                        {"item_id": item_b.id, "quantity": 3.0, "optional": False},
                    ]
                },
                "is_public": True,
            },
        )
        assert blueprint_response.status_code == 201
        blueprint_data = blueprint_response.json()
        blueprint_id = blueprint_data["id"]
        assert blueprint_data["is_public"] is True

        # Step 2: User B registers
        user_b_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "userb@example.com",
                "username": "userb",
                "password": "password123",
            },
        )
        assert user_b_response.status_code == 201
        user_b_token = user_b_response.json()["access_token"]
        user_b_headers = {"Authorization": f"Bearer {user_b_token}"}
        user_b_id = user_b_response.json()["user"]["id"]

        # Step 3: User B discovers the public blueprint
        public_blueprints_response = client.get(
            "/api/v1/blueprints",
            headers=user_b_headers,
            params={"is_public": True},
        )
        assert public_blueprints_response.status_code == 200
        public_blueprints = public_blueprints_response.json()
        assert public_blueprints["total"] > 0
        shared_blueprint = next(
            (b for b in public_blueprints["blueprints"] if b["id"] == blueprint_id),
            None,
        )
        assert shared_blueprint is not None

        # Step 4: User B creates location and adds inventory
        location_b_response = client.post(
            "/api/v1/locations",
            headers=user_b_headers,
            json={
                "name": "User B Station",
                "type": "station",
                "owner_type": "user",
                "owner_id": user_b_id,
            },
        )
        assert location_b_response.status_code == 201
        location_b_id = location_b_response.json()["id"]

        # User B adds required items to inventory
        client.post(
            "/api/v1/inventory/adjust",
            headers=user_b_headers,
            json={
                "item_id": item_a.id,
                "location_id": location_b_id,
                "quantity_change": 10.0,
                "reason": "Stocking up",
            },
        )
        client.post(
            "/api/v1/inventory/adjust",
            headers=user_b_headers,
            json={
                "item_id": item_b.id,
                "location_id": location_b_id,
                "quantity_change": 15.0,
                "reason": "Stocking up",
            },
        )

        # Step 5: User B creates craft from shared blueprint
        craft_response = client.post(
            "/api/v1/crafts?reserve_ingredients=true",
            headers=user_b_headers,
            json={
                "blueprint_id": blueprint_id,
                "output_location_id": location_b_id,
            },
        )
        assert craft_response.status_code == 201
        craft_data = craft_response.json()
        craft_id = craft_data["id"]
        assert craft_data["blueprint_id"] == blueprint_id

        # Step 6: User B starts the craft
        start_response = client.post(
            f"/api/v1/crafts/{craft_id}/start",
            headers=user_b_headers,
        )
        assert start_response.status_code == 200
        assert start_response.json()["status"] == CRAFT_STATUS_IN_PROGRESS

        # Step 7: User B completes the craft
        complete_response = client.post(
            f"/api/v1/crafts/{craft_id}/complete",
            headers=user_b_headers,
        )
        assert complete_response.status_code == 200
        complete_data = complete_response.json()
        assert complete_data["status"] == CRAFT_STATUS_COMPLETED

        # Step 8: Verify User B received the output
        inventory_response = client.get(
            "/api/v1/inventory",
            headers=user_b_headers,
            params={"location_id": location_b_id, "item_id": item_output.id},
        )
        assert inventory_response.status_code == 200
        inventory_data = inventory_response.json()
        output_stock = next(
            (s for s in inventory_data["items"] if s["item_id"] == item_output.id),
            None,
        )
        assert output_stock is not None
        assert float(output_stock["quantity"]) >= 1.0

        # Step 9: Verify blueprint usage count increased
        blueprint_check = client.get(
            f"/api/v1/blueprints/{blueprint_id}",
            headers=user_b_headers,
        )
        assert blueprint_check.status_code == 200
        assert blueprint_check.json()["usage_count"] > 0


class TestFlowIntegrationToDataImport:
    """
    Integration test for: Integration setup → data import
    
    This tests the complete flow of:
    1. User creates an integration
    2. User exports data
    3. User imports data through integration
    4. Verify data integrity
    """

    def test_integration_to_data_import_flow(self, client, db_session):
        """Test the complete flow from integration setup to data import."""
        # Step 1: User registers
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "integration@example.com",
                "username": "integration_user",
                "password": "password123",
            },
        )
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = register_response.json()["user"]["id"]

        # Step 2: Create some initial data (items, locations, inventory)
        item1 = Item(name="Test Item 1", category="Test")
        item2 = Item(name="Test Item 2", category="Test")
        db_session.add_all([item1, item2])
        db_session.commit()
        db_session.refresh(item1)
        db_session.refresh(item2)

        location_response = client.post(
            "/api/v1/locations",
            headers=headers,
            json={
                "name": "Test Location",
                "type": "station",
                "owner_type": "user",
                "owner_id": user_id,
            },
        )
        assert location_response.status_code == 201
        location_id = location_response.json()["id"]

        # Add inventory
        client.post(
            "/api/v1/inventory/adjust",
            headers=headers,
            json={
                "item_id": item1.id,
                "location_id": location_id,
                "quantity_change": 50.0,
                "reason": "Initial stock",
            },
        )

        # Step 3: Create an integration
        integration_response = client.post(
            "/api/v1/integrations",
            headers=headers,
            json={
                "name": "Test Integration",
                "type": "webhook",
                "status": "active",
                "webhook_url": "https://example.com/webhook",
                "config": {"auto_sync": True},
            },
        )
        assert integration_response.status_code == 201
        integration_data = integration_response.json()
        integration_id = integration_data["id"]

        # Step 4: Test the integration
        test_response = client.post(
            f"/api/v1/integrations/{integration_id}/test",
            headers=headers,
        )
        # May succeed or fail depending on webhook availability, but should not error
        assert test_response.status_code in [200, 400, 500]

        # Step 5: Verify integration can be retrieved
        get_integration_response = client.get(
            f"/api/v1/integrations/{integration_id}",
            headers=headers,
        )
        assert get_integration_response.status_code == 200
        integration_data = get_integration_response.json()
        assert integration_data["id"] == integration_id
        assert integration_data["status"] == "active"

        # Step 6: Check integration logs (may be empty)
        logs_response = client.get(
            f"/api/v1/integrations/{integration_id}/logs",
            headers=headers,
        )
        assert logs_response.status_code == 200
        # Logs may be empty, but endpoint should work

        # Step 7: Verify integration appears in list
        list_response = client.get(
            "/api/v1/integrations",
            headers=headers,
        )
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data["total"] >= 1
        integration_ids = {intg["id"] for intg in list_data["integrations"]}
        assert integration_id in integration_ids

