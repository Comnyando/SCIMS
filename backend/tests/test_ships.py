"""
Tests for Ships API endpoints.
"""

import pytest
from app.models.ship import Ship
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


class TestListShips:
    """Test list ships endpoint."""

    def test_list_ships_empty(self, client, auth_headers):
        """Test listing ships when none exist."""
        response = client.get("/api/v1/ships", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_list_user_ships(self, client, auth_headers, db_session, test_user, test_location):
        """Test listing user-owned ships."""
        # Create ship first (with temporary owner_id for cargo)
        import uuid
        temp_owner_id = str(uuid.uuid4())
        
        # Create cargo location
        cargo_loc = Location(
            name="Ship Cargo",
            type="ship",
            owner_type="ship",
            owner_id=temp_owner_id,  # Temporary, will be updated
        )
        db_session.add(cargo_loc)
        db_session.flush()

        ship = Ship(
            name="My Ship",
            ship_type="Constellation",
            owner_type="user",
            owner_id=test_user.id,
            current_location_id=test_location.id,
            cargo_location_id=cargo_loc.id,
        )
        db_session.add(ship)
        db_session.flush()  # Flush to get ship.id
        
        # Now update cargo location with actual ship.id
        cargo_loc.owner_id = ship.id
        db_session.commit()

        response = client.get("/api/v1/ships", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1


class TestCreateShip:
    """Test create ship endpoint."""

    def test_create_ship_success(self, client, auth_headers, test_user, test_location):
        """Test successful ship creation."""
        response = client.post(
            "/api/v1/ships",
            headers=auth_headers,
            json={
                "name": "My Ship",
                "ship_type": "Constellation Andromeda",
                "owner_type": "user",
                "owner_id": test_user.id,
                "current_location_id": test_location.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Ship"
        assert data["ship_type"] == "Constellation Andromeda"
        assert "cargo_location_id" in data

    def test_create_ship_wrong_owner(self, client, auth_headers, test_location):
        """Test that user cannot create ship for another user."""
        response = client.post(
            "/api/v1/ships",
            headers=auth_headers,
            json={
                "name": "Other User Ship",
                "owner_type": "user",
                "owner_id": "00000000-0000-0000-0000-000000000000",
                "current_location_id": test_location.id,
            },
        )
        assert response.status_code == 403


class TestGetShip:
    """Test get ship endpoint."""

    def test_get_ship_success(self, client, auth_headers, db_session, test_user, test_location):
        """Test getting an accessible ship."""
        # Create cargo location
        import uuid
        temp_owner_id = str(uuid.uuid4())
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
            owner_type="user",
            owner_id=test_user.id,
            current_location_id=test_location.id,
            cargo_location_id=cargo_loc.id,
        )
        db_session.add(ship)
        db_session.flush()
        cargo_loc.owner_id = ship.id
        db_session.commit()

        response = client.get(f"/api/v1/ships/{ship.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Ship"

    def test_get_ship_not_found(self, client, auth_headers):
        """Test getting non-existent ship."""
        response = client.get("/api/v1/ships/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateShip:
    """Test update ship endpoint."""

    def test_update_ship_success(self, client, auth_headers, db_session, test_user, test_location):
        """Test successful ship update."""
        # Create cargo location
        import uuid
        temp_owner_id = str(uuid.uuid4())
        cargo_loc = Location(
            name="Ship Cargo",
            type="ship",
            owner_type="ship",
            owner_id=temp_owner_id,
        )
        db_session.add(cargo_loc)
        db_session.flush()

        ship = Ship(
            name="Original Name",
            owner_type="user",
            owner_id=test_user.id,
            current_location_id=test_location.id,
            cargo_location_id=cargo_loc.id,
        )
        db_session.add(ship)
        db_session.flush()
        cargo_loc.owner_id = ship.id
        db_session.commit()

        response = client.patch(
            f"/api/v1/ships/{ship.id}",
            headers=auth_headers,
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_move_ship(self, client, auth_headers, db_session, test_user, test_location):
        """Test moving ship to new location."""
        # Create new location
        new_location = Location(
            name="New Station",
            type="station",
            owner_type="user",
            owner_id=test_user.id,
        )
        db_session.add(new_location)
        db_session.flush()

        # Create cargo location
        import uuid
        temp_owner_id = str(uuid.uuid4())
        cargo_loc = Location(
            name="Ship Cargo",
            type="ship",
            owner_type="ship",
            owner_id=temp_owner_id,
        )
        db_session.add(cargo_loc)
        db_session.flush()

        ship = Ship(
            name="Movable Ship",
            owner_type="user",
            owner_id=test_user.id,
            current_location_id=test_location.id,
            cargo_location_id=cargo_loc.id,
        )
        db_session.add(ship)
        db_session.flush()
        cargo_loc.owner_id = ship.id
        db_session.commit()

        # Move ship
        response = client.patch(
            f"/api/v1/ships/{ship.id}",
            headers=auth_headers,
            json={"current_location_id": new_location.id},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["current_location_id"] == new_location.id


class TestDeleteShip:
    """Test delete ship endpoint."""

    def test_delete_ship_success(self, client, auth_headers, db_session, test_user, test_location):
        """Test successful ship deletion."""
        # Create cargo location
        import uuid
        temp_owner_id = str(uuid.uuid4())
        cargo_loc = Location(
            name="Ship Cargo",
            type="ship",
            owner_type="ship",
            owner_id=temp_owner_id,
        )
        db_session.add(cargo_loc)
        db_session.flush()

        ship = Ship(
            name="To Delete",
            owner_type="user",
            owner_id=test_user.id,
            current_location_id=test_location.id,
            cargo_location_id=cargo_loc.id,
        )
        db_session.add(ship)
        db_session.flush()
        cargo_loc.owner_id = ship.id
        db_session.commit()
        ship_id = ship.id

        response = client.delete(f"/api/v1/ships/{ship_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/v1/ships/{ship_id}", headers=auth_headers)
        assert response.status_code == 404

