"""
Tests for Analytics API endpoints and consent management.
"""

import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.models.usage_event import UsageEvent
from app.models.blueprint import Blueprint
from app.models.recipe_usage_stats import RecipeUsageStats
from app.core.security import create_access_token, hash_password


@pytest.fixture
def test_user(client, db_session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("testpass123"),
        is_active=True,
        analytics_consent=False,  # Default to no consent
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_with_consent(client, db_session):
    """Create a test user with analytics consent."""
    user = User(
        email="consented@example.com",
        username="consented",
        hashed_password=hash_password("testpass123"),
        is_active=True,
        analytics_consent=True,
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
def consent_headers(test_user_with_consent):
    """Return auth headers for user with consent."""
    token = create_access_token({"sub": test_user_with_consent.id})
    return {"Authorization": f"Bearer {token}"}


class TestConsentManagement:
    """Tests for analytics consent management."""

    def test_get_consent_default_false(self, client, auth_headers, test_user):
        """Test that consent defaults to False."""
        response = client.get("/api/v1/analytics/consent", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["analytics_consent"] is False

    def test_update_consent_to_true(self, client, auth_headers, test_user, db_session):
        """Test updating consent to True."""
        response = client.put(
            "/api/v1/analytics/consent",
            json={"analytics_consent": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analytics_consent"] is True
        
        # Verify in database
        db_session.refresh(test_user)
        assert test_user.analytics_consent is True

    def test_update_consent_to_false(self, client, consent_headers, test_user_with_consent, db_session):
        """Test updating consent to False."""
        response = client.put(
            "/api/v1/analytics/consent",
            json={"analytics_consent": False},
            headers=consent_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["analytics_consent"] is False
        
        # Verify in database
        db_session.refresh(test_user_with_consent)
        assert test_user_with_consent.analytics_consent is False


class TestUsageStats:
    """Tests for usage statistics endpoint."""

    def test_get_usage_stats_requires_consent(self, client, auth_headers):
        """Test that usage stats require consent."""
        response = client.get("/api/v1/analytics/usage-stats", headers=auth_headers)
        assert response.status_code == 403
        assert "consent" in response.json()["detail"].lower()

    def test_get_usage_stats_with_consent(
        self, client, consent_headers, test_user_with_consent, db_session
    ):
        """Test getting usage stats with consent."""
        from datetime import datetime, timezone

        # Create some test events with explicit timestamps to ensure they're within the period
        now = datetime.now(timezone.utc)
        event1 = UsageEvent(
            user_id=test_user_with_consent.id,
            event_type="blueprint_used",
            entity_type="blueprint",
            entity_id="test-blueprint-id",
            created_at=now,
        )
        event2 = UsageEvent(
            user_id=test_user_with_consent.id,
            event_type="goal_created",
            entity_type="goal",
            entity_id="test-goal-id",
            created_at=now,
        )
        db_session.add_all([event1, event2])
        db_session.commit()

        response = client.get("/api/v1/analytics/usage-stats", headers=consent_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_events"] >= 2
        assert "blueprint_used" in data["events_by_type"]
        assert "goal_created" in data["events_by_type"]


class TestRecipeStats:
    """Tests for recipe/blueprint statistics endpoint."""

    def test_get_recipe_stats_not_found(self, client, consent_headers):
        """Test getting stats for non-existent blueprint."""
        response = client.get(
            "/api/v1/analytics/recipe-stats/00000000-0000-0000-0000-000000000000",
            headers=consent_headers,
        )
        assert response.status_code == 404

    def test_get_recipe_stats_invalid_period(
        self, client, consent_headers, db_session, test_user_with_consent
    ):
        """Test getting stats with invalid period type."""
        # Create a test blueprint
        from app.models.item import Item
        item = Item(name="Test Item", category="Test")
        db_session.add(item)
        db_session.flush()

        blueprint = Blueprint(
            name="Test Blueprint",
            output_item_id=item.id,
            output_quantity=1.0,
            blueprint_data={"ingredients": []},
            created_by=test_user_with_consent.id,
        )
        db_session.add(blueprint)
        db_session.commit()

        response = client.get(
            f"/api/v1/analytics/recipe-stats/{blueprint.id}?period_type=invalid",
            headers=consent_headers,
        )
        assert response.status_code == 400

