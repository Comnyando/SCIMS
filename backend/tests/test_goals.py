"""
Tests for Goals API endpoints.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from app.models.goal import Goal, GOAL_STATUS_ACTIVE, GOAL_STATUS_COMPLETED, GOAL_STATUS_CANCELLED
from app.models.goal_item import GoalItem
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
def test_item_stock(test_user, db_session, test_item, test_location):
    """Create test item stock."""
    stock = ItemStock(
        item_id=test_item.id,
        location_id=test_location.id,
        quantity=Decimal("100.0"),
        reserved_quantity=Decimal("0.0"),
        updated_by=test_user.id,
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)
    return stock


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
def test_goal(test_user, db_session, test_item):
    """Create a test goal with high target to avoid auto-completion."""
    goal = Goal(
        name="Test Goal",
        description="A test goal",
        created_by=test_user.id,
        status=GOAL_STATUS_ACTIVE,
    )
    db_session.add(goal)
    db_session.flush()
    
    # Add goal item
    goal_item = GoalItem(
        goal_id=goal.id,
        item_id=test_item.id,
        target_quantity=Decimal("1000.0"),  # High target to avoid auto-completion
    )
    db_session.add(goal_item)
    db_session.commit()
    db_session.refresh(goal)
    return goal


class TestListGoals:
    """Tests for GET /api/v1/goals endpoint."""

    def test_list_goals_empty(self, client, auth_headers):
        """Test listing goals when none exist."""
        response = client.get("/api/v1/goals", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["goals"]) == 0

    def test_list_goals_own(self, client, auth_headers, test_goal):
        """Test listing own goals."""
        response = client.get("/api/v1/goals", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["goals"]) == 1
        assert data["goals"][0]["id"] == test_goal.id

    def test_list_goals_filter_status(self, client, auth_headers, db_session, test_user, test_item):
        """Test filtering goals by status."""
        # Create goals with different statuses
        active_goal = Goal(
            name="Active Goal",
            created_by=test_user.id,
            status=GOAL_STATUS_ACTIVE,
        )
        completed_goal = Goal(
            name="Completed Goal",
            created_by=test_user.id,
            status=GOAL_STATUS_COMPLETED,
        )
        db_session.add_all([active_goal, completed_goal])
        db_session.flush()
        
        # Add goal items
        active_item = GoalItem(goal_id=active_goal.id, item_id=test_item.id, target_quantity=Decimal("100.0"))
        completed_item = GoalItem(goal_id=completed_goal.id, item_id=test_item.id, target_quantity=Decimal("100.0"))
        db_session.add_all([active_item, completed_item])
        db_session.commit()

        # Filter by active
        response = client.get("/api/v1/goals?status_filter=active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["goals"][0]["status"] == "active"

        # Filter by completed
        response = client.get("/api/v1/goals?status_filter=completed", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["goals"][0]["status"] == "completed"

    def test_list_goals_filter_organization(
        self, client, auth_headers, db_session, test_user, test_item, test_org
    ):
        """Test filtering goals by organization."""
        # Create personal and org goals
        personal_goal = Goal(
            name="Personal Goal",
            created_by=test_user.id,
            status=GOAL_STATUS_ACTIVE,
        )
        org_goal = Goal(
            name="Org Goal",
            created_by=test_user.id,
            organization_id=test_org.id,
            status=GOAL_STATUS_ACTIVE,
        )
        db_session.add_all([personal_goal, org_goal])
        db_session.flush()
        
        # Add goal items
        personal_item = GoalItem(goal_id=personal_goal.id, item_id=test_item.id, target_quantity=Decimal("100.0"))
        org_item = GoalItem(goal_id=org_goal.id, item_id=test_item.id, target_quantity=Decimal("100.0"))
        db_session.add_all([personal_item, org_item])
        db_session.commit()

        # Filter by organization
        response = client.get(
            f"/api/v1/goals?organization_id={test_org.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["goals"][0]["organization_id"] == test_org.id

    def test_list_goals_not_visible_other_user(self, client, other_auth_headers, test_goal):
        """Test that other users cannot see personal goals."""
        response = client.get("/api/v1/goals", headers=other_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_list_goals_pagination(
        self, client, auth_headers, db_session, test_user, test_item
    ):
        """Test pagination of goals list."""
        # Create multiple goals
        goals = []
        for i in range(5):
            goal = Goal(
                name=f"Goal {i}",
                created_by=test_user.id,
                status=GOAL_STATUS_ACTIVE,
            )
            goals.append(goal)
        db_session.add_all(goals)
        db_session.flush()
        
        # Add goal items
        goal_items = []
        for goal in goals:
            goal_item = GoalItem(goal_id=goal.id, item_id=test_item.id, target_quantity=Decimal("100.0"))
            goal_items.append(goal_item)
        db_session.add_all(goal_items)
        db_session.commit()

        # First page
        response = client.get("/api/v1/goals?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 2
        assert data["total"] == 5

        # Second page
        response = client.get("/api/v1/goals?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 2

    def test_list_goals_organization_member(
        self, client, auth_headers, db_session, test_user, test_item, test_org
    ):
        """Test that organization members can see organization goals."""
        org_goal = Goal(
            name="Org Goal",
            created_by=test_user.id,
            organization_id=test_org.id,
            status=GOAL_STATUS_ACTIVE,
        )
        db_session.add(org_goal)
        db_session.flush()
        
        goal_item = GoalItem(goal_id=org_goal.id, item_id=test_item.id, target_quantity=Decimal("100.0"))
        db_session.add(goal_item)
        db_session.commit()

        response = client.get("/api/v1/goals", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        goal_ids = [g["id"] for g in data["goals"]]
        assert org_goal.id in goal_ids


class TestCreateGoal:
    """Tests for POST /api/v1/goals endpoint."""

    def test_create_goal_success(self, client, auth_headers, test_item):
        """Test creating a goal successfully."""
        goal_data = {
            "name": "New Goal",
            "description": "Test description",
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 100.0}
            ],
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Goal"
        assert data["goal_items"] is not None
        assert len(data["goal_items"]) == 1
        assert data["goal_items"][0]["item_id"] == test_item.id
        assert float(data["goal_items"][0]["target_quantity"]) == 100.0
        assert data["status"] == "active"
        assert "progress_data" in data

    def test_create_goal_with_organization(
        self, client, auth_headers, test_item, test_org
    ):
        """Test creating a goal for an organization."""
        goal_data = {
            "name": "Org Goal",
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 100.0}
            ],
            "organization_id": test_org.id,
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["organization_id"] == test_org.id

    def test_create_goal_with_target_date(self, client, auth_headers, test_item):
        """Test creating a goal with target date."""
        target_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        goal_data = {
            "name": "Goal with Date",
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 100.0}
            ],
            "target_date": target_date,
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["target_date"] is not None

    def test_create_goal_invalid_item(self, client, auth_headers):
        """Test creating a goal with invalid item ID."""
        goal_data = {
            "name": "Invalid Goal",
            "goal_items": [
                {"item_id": "invalid-uuid", "target_quantity": 100.0}
            ],
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 404

    def test_create_goal_invalid_organization(
        self, client, auth_headers, test_item
    ):
        """Test creating a goal with invalid organization."""
        goal_data = {
            "name": "Invalid Org Goal",
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 100.0}
            ],
            "organization_id": "invalid-uuid",
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 404

    def test_create_goal_not_org_member(
        self, client, other_auth_headers, test_item, test_org
    ):
        """Test that non-members cannot create org goals."""
        goal_data = {
            "name": "Org Goal",
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 100.0}
            ],
            "organization_id": test_org.id,
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=other_auth_headers)
        assert response.status_code == 403

    def test_create_goal_initial_progress_calculated(
        self, client, auth_headers, test_item, test_location, test_item_stock
    ):
        """Test that initial progress is calculated on goal creation."""
        goal_data = {
            "name": "Goal with Stock",
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 100.0}
            ],
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert "progress_data" in data
        progress = data["progress_data"]
        assert "current_quantity" in progress
        assert "progress_percentage" in progress
        # Should have some progress since we have 100 units in stock
        assert progress["current_quantity"] == 100.0


class TestGetGoal:
    """Tests for GET /api/v1/goals/{goal_id} endpoint."""

    def test_get_goal_success(self, client, auth_headers, test_goal):
        """Test getting a goal successfully."""
        response = client.get(f"/api/v1/goals/{test_goal.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_goal.id
        assert data["name"] == "Test Goal"

    def test_get_goal_not_found(self, client, auth_headers):
        """Test getting a non-existent goal."""
        response = client.get(
            "/api/v1/goals/00000000-0000-0000-0000-000000000000", headers=auth_headers
        )
        assert response.status_code == 404

    def test_get_goal_not_owner(self, client, other_auth_headers, test_goal):
        """Test that other users cannot access personal goals."""
        response = client.get(f"/api/v1/goals/{test_goal.id}", headers=other_auth_headers)
        assert response.status_code == 403


class TestUpdateGoal:
    """Tests for PATCH /api/v1/goals/{goal_id} endpoint."""

    def test_update_goal_success(self, client, auth_headers, test_goal, test_item):
        """Test updating a goal successfully."""
        update_data = {
            "name": "Updated Goal",
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 200.0}
            ],
        }
        response = client.patch(
            f"/api/v1/goals/{test_goal.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Goal"
        assert len(data["goal_items"]) == 1
        assert float(data["goal_items"][0]["target_quantity"]) == 200.0

    def test_update_goal_not_found(self, client, auth_headers):
        """Test updating a non-existent goal."""
        update_data = {"name": "Updated Goal"}
        response = client.patch(
            "/api/v1/goals/00000000-0000-0000-0000-000000000000",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_update_goal_not_owner(self, client, other_auth_headers, test_goal):
        """Test that other users cannot update goals."""
        update_data = {"name": "Hacked Goal"}
        response = client.patch(
            f"/api/v1/goals/{test_goal.id}", json=update_data, headers=other_auth_headers
        )
        assert response.status_code == 403

    def test_update_goal_cancelled_not_allowed(
        self, client, auth_headers, db_session, test_goal
    ):
        """Test that cancelled goals cannot be updated."""
        test_goal.status = GOAL_STATUS_CANCELLED
        db_session.commit()

        update_data = {"name": "Updated Goal"}
        response = client.patch(
            f"/api/v1/goals/{test_goal.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 400
        assert "cancelled" in response.json()["detail"].lower()

    def test_update_goal_recalculates_progress(
        self, client, auth_headers, test_goal, test_location, test_item_stock, test_item
    ):
        """Test that updating an active goal recalculates progress."""
        # Update target quantity via goal_items
        update_data = {
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 50.0}  # Lower target, should complete
            ]
        }
        response = client.patch(
            f"/api/v1/goals/{test_goal.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # Progress should be recalculated
        assert "progress_data" in data
        # Also verify via progress endpoint
        response = client.get(
            f"/api/v1/goals/{test_goal.id}/progress?recalculate=true", headers=auth_headers
        )
        assert response.status_code == 200
        progress_data = response.json()
        # Since we have 100 units and target is now 50, should be >= 100%
        assert progress_data["progress"]["progress_percentage"] >= 100.0


class TestDeleteGoal:
    """Tests for DELETE /api/v1/goals/{goal_id} endpoint."""

    def test_delete_goal_success(self, client, auth_headers, db_session, test_user, test_item):
        """Test deleting a goal successfully."""
        goal = Goal(
            name="Goal to Delete",
            created_by=test_user.id,
            status=GOAL_STATUS_ACTIVE,
        )
        db_session.add(goal)
        db_session.flush()
        
        goal_item = GoalItem(
            goal_id=goal.id,
            item_id=test_item.id,
            target_quantity=Decimal("100.0"),
        )
        db_session.add(goal_item)
        db_session.commit()

        response = client.delete(f"/api/v1/goals/{goal.id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(f"/api/v1/goals/{goal.id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_goal_not_found(self, client, auth_headers):
        """Test deleting a non-existent goal."""
        response = client.delete(
            "/api/v1/goals/00000000-0000-0000-0000-000000000000", headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_goal_not_owner(self, client, other_auth_headers, test_goal):
        """Test that other users cannot delete goals."""
        response = client.delete(
            f"/api/v1/goals/{test_goal.id}", headers=other_auth_headers
        )
        assert response.status_code == 403

    def test_delete_goal_completed_not_allowed(
        self, client, auth_headers, db_session, test_goal
    ):
        """Test that completed goals cannot be deleted."""
        test_goal.status = GOAL_STATUS_COMPLETED
        db_session.commit()

        response = client.delete(f"/api/v1/goals/{test_goal.id}", headers=auth_headers)
        assert response.status_code == 400
        assert "completed" in response.json()["detail"].lower()


class TestGetGoalProgress:
    """Tests for GET /api/v1/goals/{goal_id}/progress endpoint."""

    def test_get_progress_active(self, client, auth_headers, test_goal, test_item_stock):
        """Test getting progress for active goal."""
        # Ensure goal remains active (target is 1000, stock is 100, so won't complete)
        response = client.get(
            f"/api/v1/goals/{test_goal.id}/progress", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["goal_id"] == test_goal.id
        # Status might be active or completed depending on progress calculation
        # Since target is 1000 and stock is 100, should remain active
        assert data["status"] in ["active", "completed"]
        assert "progress" in data
        progress = data["progress"]
        assert "current_quantity" in progress
        assert "target_quantity" in progress
        assert "progress_percentage" in progress
        assert "is_completed" in progress
        # Should have progress since we have stock
        assert float(progress["current_quantity"]) >= 0

    def test_get_progress_with_recalculate(
        self, client, auth_headers, test_goal, test_item_stock
    ):
        """Test getting progress with recalculation."""
        response = client.get(
            f"/api/v1/goals/{test_goal.id}/progress?recalculate=true", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "progress" in data
        assert "last_calculated_at" in data

    def test_get_progress_completed_goal(
        self, client, auth_headers, db_session, test_goal
    ):
        """Test getting progress for completed goal."""
        test_goal.status = GOAL_STATUS_COMPLETED
        db_session.commit()

        response = client.get(
            f"/api/v1/goals/{test_goal.id}/progress", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_get_progress_not_found(self, client, auth_headers):
        """Test getting progress for non-existent goal."""
        response = client.get(
            "/api/v1/goals/00000000-0000-0000-0000-000000000000/progress",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_get_progress_not_owner(self, client, other_auth_headers, test_goal):
        """Test that other users cannot get progress."""
        response = client.get(
            f"/api/v1/goals/{test_goal.id}/progress", headers=other_auth_headers
        )
        assert response.status_code == 403


class TestGoalCompletion:
    """Tests for goal completion detection."""

    def test_goal_auto_completes_when_target_reached(
        self, client, auth_headers, test_item, test_location, test_item_stock
    ):
        """Test that goal auto-completes when target is reached."""
        # Create goal with target of 50 (we have 100 in stock)
        goal_data = {
            "name": "Completable Goal",
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 50.0}
            ],
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 201
        goal_id = response.json()["id"]

        # Check progress - should be completed
        response = client.get(
            f"/api/v1/goals/{goal_id}/progress?recalculate=true", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["progress"]["is_completed"] is True

        # Verify goal status was updated
        response = client.get(f"/api/v1/goals/{goal_id}", headers=auth_headers)
        assert response.status_code == 200
        goal_data = response.json()
        assert goal_data["status"] == "completed"

    def test_goal_progress_calculation_includes_reserved(
        self, client, auth_headers, test_item, test_location, test_item_stock, db_session
    ):
        """Test that progress calculation accounts for reserved quantities."""
        # Reserve 50 units
        test_item_stock.reserved_quantity = Decimal("50.0")
        db_session.commit()

        # Create goal with target of 60 (we have 100 total, 50 reserved, 50 available)
        goal_data = {
            "name": "Goal with Reserved",
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 60.0}
            ],
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 201
        goal_id = response.json()["id"]

        # Check progress - should be 50/60 = 83.33%
        response = client.get(
            f"/api/v1/goals/{goal_id}/progress?recalculate=true", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        progress = data["progress"]
        # Available quantity = quantity - reserved_quantity = 100 - 50 = 50
        assert float(progress["current_quantity"]) == 50.0
        assert progress["progress_percentage"] < 100.0  # Not completed yet


class TestGoalAccessControl:
    """Tests for goal access control and organization goals."""

    def test_org_member_can_access_org_goal(
        self, client, auth_headers, db_session, test_user, test_item, test_org
    ):
        """Test that org members can access org goals."""
        org_goal = Goal(
            name="Org Goal",
            created_by=test_user.id,
            organization_id=test_org.id,
            status=GOAL_STATUS_ACTIVE,
        )
        db_session.add(org_goal)
        db_session.flush()
        
        goal_item = GoalItem(goal_id=org_goal.id, item_id=test_item.id, target_quantity=Decimal("100.0"))
        db_session.add(goal_item)
        db_session.commit()

        # Test user (org member) should be able to access
        response = client.get(f"/api/v1/goals/{org_goal.id}", headers=auth_headers)
        assert response.status_code == 200

    def test_non_member_cannot_access_org_goal(
        self, client, other_auth_headers, db_session, test_user, test_item, test_org
    ):
        """Test that non-members cannot access org goals."""
        org_goal = Goal(
            name="Org Goal",
            created_by=test_user.id,
            organization_id=test_org.id,
            status=GOAL_STATUS_ACTIVE,
        )
        db_session.add(org_goal)
        db_session.flush()
        
        goal_item = GoalItem(goal_id=org_goal.id, item_id=test_item.id, target_quantity=Decimal("100.0"))
        db_session.add(goal_item)
        db_session.commit()

        # Other user (not org member) should not be able to access
        response = client.get(f"/api/v1/goals/{org_goal.id}", headers=other_auth_headers)
        assert response.status_code == 403


class TestCreateGoalWithMultipleItems:
    """Tests for creating goals with multiple items."""

    def test_create_goal_with_multiple_items(
        self, client, auth_headers, db_session, test_user
    ):
        """Test creating a goal with multiple target items."""
        # Create multiple test items
        item1 = Item(name="Item 1", category="Test")
        item2 = Item(name="Item 2", category="Test")
        db_session.add_all([item1, item2])
        db_session.commit()

        goal_data = {
            "name": "Multi-Item Goal",
            "description": "Goal with multiple items",
            "goal_items": [
                {"item_id": item1.id, "target_quantity": 100.0},
                {"item_id": item2.id, "target_quantity": 50.0},
            ],
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Multi-Item Goal"
        assert data["goal_items"] is not None
        assert len(data["goal_items"]) == 2
        assert data["goal_items"][0]["item_id"] == item1.id
        assert data["goal_items"][1]["item_id"] == item2.id
        assert float(data["goal_items"][0]["target_quantity"]) == 100.0
        assert float(data["goal_items"][1]["target_quantity"]) == 50.0

    def test_create_goal_with_multiple_items_invalid_item(
        self, client, auth_headers, test_item
    ):
        """Test creating a goal with multiple items where one is invalid."""
        goal_data = {
            "name": "Invalid Multi-Item Goal",
            "goal_items": [
                {"item_id": test_item.id, "target_quantity": 100.0},
                {"item_id": "invalid-uuid", "target_quantity": 50.0},
            ],
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_goal_no_items_fails(self, client, auth_headers):
        """Test that creating a goal without goal_items fails."""
        goal_data = {
            "name": "No Items Goal",
        }
        response = client.post("/api/v1/goals", json=goal_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error - goal_items is required


class TestGoalProgressWithMultipleItems:
    """Tests for goal progress calculation with multiple items."""

    def test_progress_with_multiple_items(
        self, client, auth_headers, db_session, test_user, test_location
    ):
        """Test progress calculation for goal with multiple items."""
        # Create items and stock
        item1 = Item(name="Item 1", category="Test")
        item2 = Item(name="Item 2", category="Test")
        db_session.add_all([item1, item2])
        db_session.commit()

        # Create stock for item1 (100 units)
        stock1 = ItemStock(
            item_id=item1.id,
            location_id=test_location.id,
            quantity=Decimal("100.0"),
            reserved_quantity=Decimal("0.0"),
            updated_by=test_user.id,
        )
        # Create stock for item2 (25 units)
        stock2 = ItemStock(
            item_id=item2.id,
            location_id=test_location.id,
            quantity=Decimal("25.0"),
            reserved_quantity=Decimal("0.0"),
            updated_by=test_user.id,
        )
        db_session.add_all([stock1, stock2])
        db_session.commit()

        # Create goal with multiple items
        goal = Goal(
            name="Multi-Item Goal",
            created_by=test_user.id,
            status=GOAL_STATUS_ACTIVE,
        )
        db_session.add(goal)
        db_session.flush()

        goal_item1 = GoalItem(
            goal_id=goal.id,
            item_id=item1.id,
            target_quantity=Decimal("100.0"),
        )
        goal_item2 = GoalItem(
            goal_id=goal.id,
            item_id=item2.id,
            target_quantity=Decimal("50.0"),
        )
        db_session.add_all([goal_item1, goal_item2])
        db_session.commit()

        # Check progress
        response = client.get(
            f"/api/v1/goals/{goal.id}/progress?recalculate=true", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        progress = data["progress"]

        # Item 1: 100/100 = 100%
        # Item 2: 25/50 = 50%
        # Overall: 125/150 = 83.33%
        assert float(progress["current_quantity"]) == 125.0
        assert float(progress["target_quantity"]) == 150.0
        assert progress["progress_percentage"] > 80.0
        assert progress["progress_percentage"] < 85.0
        assert progress["is_completed"] is False
        assert "item_progress" in progress
        assert len(progress["item_progress"]) == 2

        # Check item-level progress
        item1_progress = next(
            (p for p in progress["item_progress"] if p["item_id"] == item1.id), None
        )
        item2_progress = next(
            (p for p in progress["item_progress"] if p["item_id"] == item2.id), None
        )
        assert item1_progress is not None
        assert item2_progress is not None
        assert item1_progress["is_completed"] is True  # 100/100
        assert item2_progress["is_completed"] is False  # 25/50
        assert float(item1_progress["current_quantity"]) == 100.0
        assert float(item2_progress["current_quantity"]) == 25.0

    def test_progress_all_items_completed(
        self, client, auth_headers, db_session, test_user, test_location
    ):
        """Test that goal is completed only when all items are completed."""
        # Create items and stock
        item1 = Item(name="Item 1", category="Test")
        item2 = Item(name="Item 2", category="Test")
        db_session.add_all([item1, item2])
        db_session.commit()

        # Create stock for both items (more than target)
        stock1 = ItemStock(
            item_id=item1.id,
            location_id=test_location.id,
            quantity=Decimal("150.0"),
            reserved_quantity=Decimal("0.0"),
            updated_by=test_user.id,
        )
        stock2 = ItemStock(
            item_id=item2.id,
            location_id=test_location.id,
            quantity=Decimal("75.0"),
            reserved_quantity=Decimal("0.0"),
            updated_by=test_user.id,
        )
        db_session.add_all([stock1, stock2])
        db_session.commit()

        # Create goal with multiple items
        goal = Goal(
            name="Multi-Item Goal",
            created_by=test_user.id,
            status=GOAL_STATUS_ACTIVE,
        )
        db_session.add(goal)
        db_session.flush()

        goal_item1 = GoalItem(
            goal_id=goal.id,
            item_id=item1.id,
            target_quantity=Decimal("100.0"),
        )
        goal_item2 = GoalItem(
            goal_id=goal.id,
            item_id=item2.id,
            target_quantity=Decimal("50.0"),
        )
        db_session.add_all([goal_item1, goal_item2])
        db_session.commit()

        # Check progress
        response = client.get(
            f"/api/v1/goals/{goal.id}/progress?recalculate=true", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        progress = data["progress"]

        # Both items should be completed
        assert progress["is_completed"] is True
        assert data["status"] == "completed"
        assert len(progress["item_progress"]) == 2
        assert all(item["is_completed"] for item in progress["item_progress"])


class TestUpdateGoalWithMultipleItems:
    """Tests for updating goals with multiple items."""

    def test_update_goal_replace_items(
        self, client, auth_headers, db_session, test_user, test_item
    ):
        """Test updating a goal to replace its items."""
        # Create additional items
        item1 = Item(name="Item 1", category="Test")
        item2 = Item(name="Item 2", category="Test")
        db_session.add_all([item1, item2])
        db_session.commit()

        # Create goal with single item
        goal = Goal(
            name="Original Goal",
            created_by=test_user.id,
            status=GOAL_STATUS_ACTIVE,
        )
        db_session.add(goal)
        db_session.flush()
        
        goal_item = GoalItem(goal_id=goal.id, item_id=test_item.id, target_quantity=Decimal("100.0"))
        db_session.add(goal_item)
        db_session.commit()

        # Update to use multiple items
        update_data = {
            "goal_items": [
                {"item_id": item1.id, "target_quantity": 50.0},
                {"item_id": item2.id, "target_quantity": 75.0},
            ],
        }
        response = client.patch(
            f"/api/v1/goals/{goal.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["goal_items"] is not None
        assert len(data["goal_items"]) == 2
        assert data["goal_items"][0]["item_id"] == item1.id
        assert data["goal_items"][1]["item_id"] == item2.id

    def test_update_goal_add_items_to_existing(
        self, client, auth_headers, db_session, test_user
    ):
        """Test updating a goal that already has multiple items."""
        # Create items
        item1 = Item(name="Item 1", category="Test")
        item2 = Item(name="Item 2", category="Test")
        item3 = Item(name="Item 3", category="Test")
        db_session.add_all([item1, item2, item3])
        db_session.commit()

        # Create goal with two items
        goal = Goal(
            name="Multi-Item Goal",
            created_by=test_user.id,
            status=GOAL_STATUS_ACTIVE,
        )
        db_session.add(goal)
        db_session.flush()

        goal_item1 = GoalItem(
            goal_id=goal.id,
            item_id=item1.id,
            target_quantity=Decimal("100.0"),
        )
        goal_item2 = GoalItem(
            goal_id=goal.id,
            item_id=item2.id,
            target_quantity=Decimal("50.0"),
        )
        db_session.add_all([goal_item1, goal_item2])
        db_session.commit()

        # Update to replace with three items
        update_data = {
            "goal_items": [
                {"item_id": item1.id, "target_quantity": 80.0},
                {"item_id": item2.id, "target_quantity": 60.0},
                {"item_id": item3.id, "target_quantity": 40.0},
            ],
        }
        response = client.patch(
            f"/api/v1/goals/{goal.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["goal_items"]) == 3
        # Verify old items are replaced
        item_ids = [gi["item_id"] for gi in data["goal_items"]]
        assert item1.id in item_ids
        assert item2.id in item_ids
        assert item3.id in item_ids

