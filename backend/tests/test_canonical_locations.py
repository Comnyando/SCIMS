"""
Tests for Canonical Locations API endpoints.
"""

import pytest
from app.models.location import Location
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
def auth_headers(test_user):
    """Return auth headers for test user."""
    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def canonical_location(test_user, db_session):
    """Create a test canonical location."""
    location = Location(
        name="New Babbage Landing Zone",
        type="station",
        owner_type="system",
        owner_id="00000000-0000-0000-0000-000000000000",
        is_canonical=True,
        created_by=test_user.id,
        meta={"planet": "microTech", "system": "Stanton"},
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


class TestListCanonicalLocations:
    """Test list canonical locations endpoint (public read)."""

    def test_list_canonical_locations_no_auth(self, client, db_session, canonical_location):
        """Test that canonical locations can be listed without authentication."""
        response = client.get("/api/v1/canonical-locations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(loc["id"] == canonical_location.id for loc in data["locations"])

    def test_list_canonical_locations_filter_type(self, client, db_session, canonical_location):
        """Test filtering canonical locations by type."""
        response = client.get("/api/v1/canonical-locations?type=station")
        assert response.status_code == 200
        data = response.json()
        assert all(loc["type"] == "station" for loc in data["locations"])

    def test_list_canonical_locations_search(self, client, db_session, canonical_location):
        """Test searching canonical locations by name."""
        response = client.get("/api/v1/canonical-locations?search=Babbage")
        assert response.status_code == 200
        data = response.json()
        assert any("Babbage" in loc["name"] for loc in data["locations"])


class TestGetCanonicalLocation:
    """Test get canonical location endpoint (public read)."""

    def test_get_canonical_location_no_auth(self, client, canonical_location):
        """Test that canonical locations can be retrieved without authentication."""
        response = client.get(f"/api/v1/canonical-locations/{canonical_location.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Babbage Landing Zone"
        assert data["is_canonical"] == True

    def test_get_canonical_location_not_found(self, client):
        """Test getting non-existent canonical location."""
        response = client.get("/api/v1/canonical-locations/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


class TestCreateCanonicalLocation:
    """Test create canonical location endpoint (admin only)."""

    def test_create_canonical_location_success(self, client, auth_headers, test_user):
        """Test successful canonical location creation."""
        response = client.post(
            "/api/v1/canonical-locations",
            headers=auth_headers,
            json={
                "name": "Area18 Landing Zone",
                "type": "station",
                "metadata": {"planet": "ArcCorp", "system": "Stanton"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Area18 Landing Zone"
        assert data["is_canonical"] == True
        assert data["created_by"] == test_user.id

    def test_create_canonical_location_duplicate_name(self, client, auth_headers, canonical_location):
        """Test that duplicate canonical location names are rejected."""
        response = client.post(
            "/api/v1/canonical-locations",
            headers=auth_headers,
            json={
                "name": canonical_location.name,
                "type": "station",
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_canonical_location_with_parent(self, client, auth_headers, canonical_location):
        """Test creating canonical location with parent."""
        response = client.post(
            "/api/v1/canonical-locations",
            headers=auth_headers,
            json={
                "name": "New Babbage Local Inventory",
                "type": "warehouse",
                "parent_location_id": canonical_location.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["parent_location_id"] == canonical_location.id


class TestUpdateCanonicalLocation:
    """Test update canonical location endpoint (admin only)."""

    def test_update_canonical_location_success(self, client, auth_headers, canonical_location):
        """Test successful canonical location update."""
        response = client.patch(
            f"/api/v1/canonical-locations/{canonical_location.id}",
            headers=auth_headers,
            json={
                "metadata": {"planet": "microTech", "system": "Stanton", "updated": True},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["updated"] == True

    def test_update_canonical_location_not_found(self, client, auth_headers):
        """Test updating non-existent canonical location."""
        response = client.patch(
            "/api/v1/canonical-locations/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
            json={"name": "Updated Name"},
        )
        assert response.status_code == 404


class TestDeleteCanonicalLocation:
    """Test delete canonical location endpoint (admin only)."""

    def test_delete_canonical_location_success(self, client, auth_headers, test_user, db_session):
        """Test successful canonical location deletion."""
        # Create a canonical location
        location = Location(
            name="Temporary Location",
            type="station",
            owner_type="system",
            owner_id="00000000-0000-0000-0000-000000000000",
            is_canonical=True,
            created_by=test_user.id,
        )
        db_session.add(location)
        db_session.commit()
        location_id = location.id

        response = client.delete(
            f"/api/v1/canonical-locations/{location_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/v1/canonical-locations/{location_id}")
        assert response.status_code == 404

    def test_delete_canonical_location_with_references(self, client, auth_headers, test_user, db_session, canonical_location):
        """Test that canonical locations with references cannot be deleted."""
        # Create a player location referencing the canonical location
        player_location = Location(
            name="My Inventory",
            type="player_inventory",
            owner_type="user",
            owner_id=test_user.id,
            canonical_location_id=canonical_location.id,
            is_canonical=False,
        )
        db_session.add(player_location)
        db_session.commit()

        response = client.delete(
            f"/api/v1/canonical-locations/{canonical_location.id}",
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "reference" in response.json()["detail"].lower()


class TestLocationWithCanonicalReference:
    """Test creating locations that reference canonical locations."""

    def test_create_location_with_canonical_reference(self, client, auth_headers, test_user, canonical_location):
        """Test creating a player location that references a canonical location."""
        response = client.post(
            "/api/v1/locations",
            headers=auth_headers,
            json={
                "name": "My Inventory at New Babbage",
                "type": "player_inventory",
                "owner_type": "user",
                "owner_id": test_user.id,
                "canonical_location_id": canonical_location.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["canonical_location_id"] == canonical_location.id
        assert data["is_canonical"] == False

    def test_create_location_with_invalid_canonical_reference(self, client, auth_headers, test_user):
        """Test that referencing a non-canonical location fails."""
        response = client.post(
            "/api/v1/locations",
            headers=auth_headers,
            json={
                "name": "My Inventory",
                "type": "player_inventory",
                "owner_type": "user",
                "owner_id": test_user.id,
                "canonical_location_id": "00000000-0000-0000-0000-000000000000",
            },
        )
        assert response.status_code == 404

