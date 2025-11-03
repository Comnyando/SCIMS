"""
Backend tests for Integrations API.
"""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models.integration import Integration
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
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
def other_user(client, db_session):
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


class TestListIntegrations:
    def test_list_integrations_empty(self, client, auth_headers):
        """Test listing integrations when user has none."""
        response = client.get("/api/v1/integrations", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["integrations"]) == 0

    def test_list_integrations_own(self, client, auth_headers, test_user: User, db_session: Session):
        """Test listing user's own integrations."""
        # Create a test integration
        integration = Integration(
            name="Test Integration",
            type="webhook",
            status="active",
            user_id=test_user.id,
            webhook_url="https://example.com/webhook",
        )
        db_session.add(integration)
        db_session.commit()

        response = client.get("/api/v1/integrations", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["integrations"]) == 1
        assert data["integrations"][0]["name"] == "Test Integration"

    def test_list_integrations_filter_status(self, client, auth_headers, test_user: User, db_session: Session):
        """Test filtering integrations by status."""
        # Create integrations with different statuses
        active_integration = Integration(
            name="Active Integration",
            type="webhook",
            status="active",
            user_id=test_user.id,
        )
        inactive_integration = Integration(
            name="Inactive Integration",
            type="webhook",
            status="inactive",
            user_id=test_user.id,
        )
        db_session.add_all([active_integration, inactive_integration])
        db_session.commit()

        response = client.get("/api/v1/integrations?status_filter=active", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["integrations"][0]["status"] == "active"

    def test_list_integrations_organization(self, client, auth_headers, test_user: User, db_session: Session):
        """Test listing organization integrations."""
        # Create organization and membership
        org = Organization(name="Test Org")
        db_session.add(org)
        db_session.flush()

        membership = OrganizationMember(
            organization_id=org.id, user_id=test_user.id, role="owner"
        )
        db_session.add(membership)
        db_session.flush()

        # Create org integration
        integration = Integration(
            name="Org Integration",
            type="webhook",
            status="active",
            user_id=test_user.id,
            organization_id=org.id,
        )
        db_session.add(integration)
        db_session.commit()

        response = client.get("/api/v1/integrations", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["integrations"][0]["organization_id"] == str(org.id)

    def test_list_integrations_not_visible_other_user(
        self, client, auth_headers, test_user: User, other_user: User, db_session: Session
    ):
        """Test that users cannot see other users' integrations."""
        # Create integration for other user
        integration = Integration(
            name="Other User Integration",
            type="webhook",
            status="active",
            user_id=other_user.id,
        )
        db_session.add(integration)
        db_session.commit()

        response = client.get("/api/v1/integrations", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0


class TestCreateIntegration:
    def test_create_integration_success(self, client, auth_headers, test_user: User, db_session: Session):
        """Test creating a new integration."""
        response = client.post(
            "/api/v1/integrations",
            json={
                "name": "My Webhook",
                "type": "webhook",
                "webhook_url": "https://example.com/webhook",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "My Webhook"
        assert data["type"] == "webhook"
        assert data["status"] == "active"
        assert data["user_id"] == test_user.id

    def test_create_integration_with_api_key(
        self, client, auth_headers, test_user: User, db_session: Session
    ):
        """Test creating integration with API key (should be encrypted)."""
        response = client.post(
            "/api/v1/integrations",
            json={
                "name": "API Integration",
                "type": "api",
                "api_key": "secret-api-key-123",
                "api_secret": "secret-secret-456",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "API Integration"

        # Verify API key is encrypted in database
        integration = db_session.query(Integration).filter(Integration.id == data["id"]).first()
        assert integration.api_key_encrypted is not None
        assert integration.api_key_encrypted != "secret-api-key-123"
        assert integration.api_secret_encrypted is not None
        assert integration.api_secret_encrypted != "secret-secret-456"

    def test_create_integration_with_organization(
        self, client, auth_headers, test_user: User, db_session: Session
    ):
        """Test creating integration for organization."""
        org = Organization(name="Test Org")
        db_session.add(org)
        db_session.flush()

        membership = OrganizationMember(
            organization_id=org.id, user_id=test_user.id, role="owner"
        )
        db_session.add(membership)
        db_session.commit()

        response = client.post(
            "/api/v1/integrations",
            json={
                "name": "Org Webhook",
                "type": "webhook",
                "organization_id": str(org.id),
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["organization_id"] == str(org.id)

    def test_create_integration_not_org_member(
        self, client, auth_headers, test_user: User, other_user: User, db_session: Session
    ):
        """Test that users cannot create integrations for orgs they're not members of."""
        org = Organization(name="Other Org")
        db_session.add(org)
        db_session.commit()

        response = client.post(
            "/api/v1/integrations",
            json={
                "name": "Unauthorized Integration",
                "type": "webhook",
                "organization_id": str(org.id),
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetIntegration:
    def test_get_integration_success(self, client, auth_headers, test_user: User, db_session: Session):
        """Test getting integration details."""
        integration = Integration(
            name="Test Integration",
            type="webhook",
            status="active",
            user_id=test_user.id,
        )
        db_session.add(integration)
        db_session.commit()

        response = client.get(f"/api/v1/integrations/{integration.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Integration"

    def test_get_integration_not_found(self, client, auth_headers):
        """Test getting non-existent integration."""
        response = client.get(
            "/api/v1/integrations/00000000-0000-0000-0000-000000000000", headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_integration_not_owner(
        self, client, auth_headers, test_user: User, other_user: User, db_session: Session
    ):
        """Test that users cannot access other users' integrations."""
        integration = Integration(
            name="Other User Integration",
            type="webhook",
            status="active",
            user_id=other_user.id,
        )
        db_session.add(integration)
        db_session.commit()

        response = client.get(f"/api/v1/integrations/{integration.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateIntegration:
    def test_update_integration_success(self, client, auth_headers, test_user: User, db_session: Session):
        """Test updating an integration."""
        integration = Integration(
            name="Original Name",
            type="webhook",
            status="active",
            user_id=test_user.id,
        )
        db_session.add(integration)
        db_session.commit()

        response = client.patch(
            f"/api/v1/integrations/{integration.id}",
            json={"name": "Updated Name", "status": "inactive"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["status"] == "inactive"

    def test_update_integration_not_found(self, client, auth_headers):
        """Test updating non-existent integration."""
        response = client.patch(
            "/api/v1/integrations/00000000-0000-0000-0000-000000000000",
            json={"name": "New Name"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_integration_clear_api_key(
        self, client, auth_headers, test_user: User, db_session: Session
    ):
        """Test clearing API key by setting it to empty string."""
        from app.utils.encryption import encrypt_value

        integration = Integration(
            name="API Integration",
            type="api",
            status="active",
            user_id=test_user.id,
            api_key_encrypted=encrypt_value("original-key"),
        )
        db_session.add(integration)
        db_session.commit()

        response = client.patch(
            f"/api/v1/integrations/{integration.id}",
            json={"api_key": ""},  # Empty string means clear it
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK

        db_session.refresh(integration)
        assert integration.api_key_encrypted is None


class TestDeleteIntegration:
    def test_delete_integration_success(self, client, auth_headers, test_user: User, db_session: Session):
        """Test deleting an integration."""
        integration = Integration(
            name="To Delete",
            type="webhook",
            status="active",
            user_id=test_user.id,
        )
        db_session.add(integration)
        db_session.commit()

        response = client.delete(f"/api/v1/integrations/{integration.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        deleted = db_session.query(Integration).filter(Integration.id == integration.id).first()
        assert deleted is None

    def test_delete_integration_not_found(self, client, auth_headers):
        """Test deleting non-existent integration."""
        response = client.delete(
            "/api/v1/integrations/00000000-0000-0000-0000-000000000000", headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTestIntegration:
    def test_test_integration_success(self, client, auth_headers, test_user: User, db_session: Session):
        """Test testing an integration."""
        integration = Integration(
            name="Test Integration",
            type="webhook",
            status="active",
            user_id=test_user.id,
            webhook_url="https://example.com/webhook",
        )
        db_session.add(integration)
        db_session.commit()

        response = client.post(f"/api/v1/integrations/{integration.id}/test", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True

        # Verify integration was updated
        db_session.refresh(integration)
        assert integration.last_tested_at is not None
        assert integration.status == "active"

    def test_test_integration_missing_webhook_url(
        self, client, auth_headers, test_user: User, db_session: Session
    ):
        """Test that webhook integration without URL fails."""
        integration = Integration(
            name="Invalid Webhook",
            type="webhook",
            status="active",
            user_id=test_user.id,
            # No webhook_url
        )
        db_session.add(integration)
        db_session.commit()

        response = client.post(f"/api/v1/integrations/{integration.id}/test", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is False
        assert "Webhook URL is required" in data["message"]


class TestGetIntegrationLogs:
    def test_get_integration_logs_empty(
        self, client, auth_headers, test_user: User, db_session: Session
    ):
        """Test getting logs for integration with no logs."""
        integration = Integration(
            name="No Logs Integration",
            type="webhook",
            status="active",
            user_id=test_user.id,
        )
        db_session.add(integration)
        db_session.commit()

        response = client.get(f"/api/v1/integrations/{integration.id}/logs", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["logs"]) == 0

    def test_get_integration_logs_with_data(
        self, client, auth_headers, test_user: User, db_session: Session
    ):
        """Test getting logs for integration with logs."""
        from app.models.integration_log import IntegrationLog
        from datetime import datetime, timezone

        integration = Integration(
            name="Has Logs Integration",
            type="webhook",
            status="active",
            user_id=test_user.id,
        )
        db_session.add(integration)
        db_session.flush()

        log = IntegrationLog(
            integration_id=integration.id,
            event_type="test",
            status="success",
            timestamp=datetime.now(timezone.utc),
        )
        db_session.add(log)
        db_session.commit()

        response = client.get(f"/api/v1/integrations/{integration.id}/logs", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["logs"]) == 1
        assert data["logs"][0]["event_type"] == "test"


