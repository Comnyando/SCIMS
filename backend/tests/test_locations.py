"""
Tests for Locations API endpoints.
"""

import pytest
from app.models.location import Location
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
def auth_headers(test_user):
    """Return auth headers for test user."""
    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


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


class TestListLocations:
    """Test list locations endpoint."""

    def test_list_locations_empty(self, client, auth_headers):
        """Test listing locations when none exist."""
        response = client.get("/api/v1/locations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_list_user_locations(self, client, auth_headers, db_session, test_user):
        """Test listing user-owned locations."""
        location = Location(
            name="My Location",
            type="station",
            owner_type="user",
            owner_id=test_user.id,
        )
        db_session.add(location)
        db_session.commit()

        response = client.get("/api/v1/locations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["locations"][0]["name"] == "My Location"

    def test_list_org_locations(self, client, auth_headers, db_session, test_user, test_org):
        """Test listing organization-owned locations."""
        location = Location(
            name="Org Location",
            type="warehouse",
            owner_type="organization",
            owner_id=test_org.id,
        )
        db_session.add(location)
        db_session.commit()

        response = client.get("/api/v1/locations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


class TestCreateLocation:
    """Test create location endpoint."""

    def test_create_user_location(self, client, auth_headers, test_user):
        """Test creating user-owned location."""
        response = client.post(
            "/api/v1/locations",
            headers=auth_headers,
            json={
                "name": "My Station",
                "type": "station",
                "owner_type": "user",
                "owner_id": test_user.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Station"
        assert data["owner_type"] == "user"

    def test_create_org_location(self, client, auth_headers, test_org):
        """Test creating organization-owned location."""
        response = client.post(
            "/api/v1/locations",
            headers=auth_headers,
            json={
                "name": "Org Warehouse",
                "type": "warehouse",
                "owner_type": "organization",
                "owner_id": test_org.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["owner_type"] == "organization"

    def test_create_location_wrong_owner(self, client, auth_headers):
        """Test that user cannot create location for another user."""
        response = client.post(
            "/api/v1/locations",
            headers=auth_headers,
            json={
                "name": "Other User Location",
                "type": "station",
                "owner_type": "user",
                "owner_id": "00000000-0000-0000-0000-000000000000",
            },
        )
        assert response.status_code == 403


class TestGetLocation:
    """Test get location endpoint."""

    def test_get_location_success(self, client, auth_headers, db_session, test_user):
        """Test getting an accessible location."""
        location = Location(
            name="Test Location",
            type="station",
            owner_type="user",
            owner_id=test_user.id,
        )
        db_session.add(location)
        db_session.commit()

        response = client.get(f"/api/v1/locations/{location.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Location"

    def test_get_location_not_found(self, client, auth_headers):
        """Test getting non-existent location."""
        response = client.get("/api/v1/locations/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateLocation:
    """Test update location endpoint."""

    def test_update_location_success(self, client, auth_headers, db_session, test_user):
        """Test successful location update."""
        location = Location(
            name="Original Name",
            type="station",
            owner_type="user",
            owner_id=test_user.id,
        )
        db_session.add(location)
        db_session.commit()

        response = client.patch(
            f"/api/v1/locations/{location.id}",
            headers=auth_headers,
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"


class TestDeleteLocation:
    """Test delete location endpoint."""

    def test_delete_location_success(self, client, auth_headers, db_session, test_user):
        """Test successful location deletion."""
        location = Location(
            name="To Delete",
            type="station",
            owner_type="user",
            owner_id=test_user.id,
        )
        db_session.add(location)
        db_session.commit()
        location_id = location.id

        response = client.delete(f"/api/v1/locations/{location_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/v1/locations/{location_id}", headers=auth_headers)
        assert response.status_code == 404

