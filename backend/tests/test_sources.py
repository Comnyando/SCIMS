"""
Tests for Resource Sources API.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.resource_source import (
    ResourceSource,
    SOURCE_TYPE_PLAYER_STOCK,
    SOURCE_TYPE_UNIVERSE_LOCATION,
    SOURCE_TYPE_TRADING_POST,
)
from app.models.source_verification_log import SourceVerificationLog
from app.models.item import Item
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
def test_item(db_session: Session, test_user: User) -> Item:
    """Create a test item."""
    item = Item(
        name="Test Item",
        description="A test item",
        category="Test",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def test_source(db_session: Session, test_item: Item) -> ResourceSource:
    """Create a test resource source."""
    source = ResourceSource(
        item_id=test_item.id,
        source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
        source_identifier="Test Location Alpha",
        available_quantity=Decimal("100.0"),
        cost_per_unit=None,
        reliability_score=Decimal("0.5"),
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    return source


@pytest.fixture
def test_verified_source(
    db_session: Session, test_item: Item, test_user: User
) -> ResourceSource:
    """Create a test resource source with verification history."""
    source = ResourceSource(
        item_id=test_item.id,
        source_type=SOURCE_TYPE_PLAYER_STOCK,
        source_identifier=test_user.id,
        available_quantity=Decimal("50.0"),
        cost_per_unit=Decimal("10.5"),
        reliability_score=Decimal("0.75"),
        last_verified=datetime.now(timezone.utc),
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)

    # Add verification logs
    for i in range(3):
        log = SourceVerificationLog(
            source_id=source.id,
            verified_by=test_user.id,
            was_accurate=True,
            verified_at=datetime.now(timezone.utc) - timedelta(days=i * 7),
        )
        db_session.add(log)
    db_session.commit()

    return source


class TestListSources:
    """Test GET /api/v1/sources endpoint."""

    def test_list_sources_empty(self, client: TestClient, auth_headers: dict):
        """Test listing sources when none exist."""
        response = client.get("/api/v1/sources", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_list_sources_with_data(
        self, client: TestClient, auth_headers: dict, test_source: ResourceSource
    ):
        """Test listing sources with existing data."""
        response = client.get("/api/v1/sources", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == test_source.id

    def test_list_sources_filter_by_item_id(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_item: Item,
        test_user: User,
    ):
        """Test filtering sources by item_id."""
        # Create another item and source
        item2 = Item(name="Other Item", category="Test")
        db_session.add(item2)
        db_session.commit()
        db_session.refresh(item2)

        source1 = ResourceSource(
            item_id=test_item.id,
            source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
            source_identifier="Location 1",
            available_quantity=Decimal("100.0"),
        )
        source2 = ResourceSource(
            item_id=item2.id,
            source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
            source_identifier="Location 2",
            available_quantity=Decimal("200.0"),
        )
        db_session.add_all([source1, source2])
        db_session.commit()

        response = client.get(
            f"/api/v1/sources?item_id={test_item.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == source1.id
        assert data["items"][0]["item_id"] == test_item.id

    def test_list_sources_filter_by_type(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_item: Item,
    ):
        """Test filtering sources by source_type."""
        source1 = ResourceSource(
            item_id=test_item.id,
            source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
            source_identifier="Location 1",
            available_quantity=Decimal("100.0"),
        )
        source2 = ResourceSource(
            item_id=test_item.id,
            source_type=SOURCE_TYPE_PLAYER_STOCK,
            source_identifier="Player 1",
            available_quantity=Decimal("50.0"),
        )
        db_session.add_all([source1, source2])
        db_session.commit()

        response = client.get(
            f"/api/v1/sources?source_type={SOURCE_TYPE_UNIVERSE_LOCATION}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["source_type"] == SOURCE_TYPE_UNIVERSE_LOCATION

    def test_list_sources_filter_by_min_reliability(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_item: Item,
    ):
        """Test filtering sources by minimum reliability score."""
        source1 = ResourceSource(
            item_id=test_item.id,
            source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
            source_identifier="Location 1",
            available_quantity=Decimal("100.0"),
            reliability_score=Decimal("0.8"),
        )
        source2 = ResourceSource(
            item_id=test_item.id,
            source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
            source_identifier="Location 2",
            available_quantity=Decimal("50.0"),
            reliability_score=Decimal("0.3"),
        )
        db_session.add_all([source1, source2])
        db_session.commit()

        response = client.get(
            "/api/v1/sources?min_reliability=0.5", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["reliability_score"] >= 0.5

    def test_list_sources_pagination(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session: Session,
        test_item: Item,
    ):
        """Test pagination of sources list."""
        # Create multiple sources
        for i in range(5):
            source = ResourceSource(
                item_id=test_item.id,
                source_type=SOURCE_TYPE_UNIVERSE_LOCATION,
                source_identifier=f"Location {i}",
                available_quantity=Decimal("100.0"),
            )
            db_session.add(source)
        db_session.commit()

        # Test first page
        response = client.get("/api/v1/sources?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2

        # Test second page
        response = client.get("/api/v1/sources?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2


class TestCreateSource:
    """Test POST /api/v1/sources endpoint."""

    def test_create_source_success(
        self, client: TestClient, auth_headers: dict, test_item: Item
    ):
        """Test creating a source successfully."""
        source_data = {
            "item_id": test_item.id,
            "source_type": SOURCE_TYPE_UNIVERSE_LOCATION,
            "source_identifier": "New Location",
            "available_quantity": 150.0,
            "reliability_score": 0.6,
        }
        response = client.post("/api/v1/sources", json=source_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["source_identifier"] == "New Location"
        assert data["available_quantity"] == 150.0
        assert data["item_id"] == test_item.id

    def test_create_source_invalid_item_id(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating a source with invalid item_id."""
        source_data = {
            "item_id": "00000000-0000-0000-0000-000000000000",
            "source_type": SOURCE_TYPE_UNIVERSE_LOCATION,
            "source_identifier": "Test Location",
            "available_quantity": 100.0,
        }
        response = client.post("/api/v1/sources", json=source_data, headers=auth_headers)
        assert response.status_code == 404
        assert "Item" in response.json()["detail"]

    def test_create_source_invalid_source_type(
        self, client: TestClient, auth_headers: dict, test_item: Item
    ):
        """Test creating a source with invalid source_type."""
        source_data = {
            "item_id": test_item.id,
            "source_type": "invalid_type",
            "source_identifier": "Test Location",
            "available_quantity": 100.0,
        }
        response = client.post("/api/v1/sources", json=source_data, headers=auth_headers)
        assert response.status_code == 422

    def test_create_source_with_cost(
        self, client: TestClient, auth_headers: dict, test_item: Item
    ):
        """Test creating a source with cost_per_unit."""
        source_data = {
            "item_id": test_item.id,
            "source_type": SOURCE_TYPE_TRADING_POST,
            "source_identifier": "Trading Post Alpha",
            "available_quantity": 200.0,
            "cost_per_unit": 15.5,
        }
        response = client.post("/api/v1/sources", json=source_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["cost_per_unit"] == 15.5


class TestGetSource:
    """Test GET /api/v1/sources/{source_id} endpoint."""

    def test_get_source_success(
        self, client: TestClient, auth_headers: dict, test_source: ResourceSource
    ):
        """Test getting a source by ID."""
        response = client.get(f"/api/v1/sources/{test_source.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_source.id
        assert data["source_identifier"] == test_source.source_identifier

    def test_get_source_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting a non-existent source."""
        response = client.get(
            "/api/v1/sources/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestUpdateSource:
    """Test PATCH /api/v1/sources/{source_id} endpoint."""

    def test_update_source_success(
        self, client: TestClient, auth_headers: dict, test_source: ResourceSource
    ):
        """Test updating a source."""
        update_data = {
            "available_quantity": 250.0,
            "cost_per_unit": 12.5,
        }
        response = client.patch(
            f"/api/v1/sources/{test_source.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["available_quantity"] == 250.0
        assert data["cost_per_unit"] == 12.5

    def test_update_source_partial(
        self, client: TestClient, auth_headers: dict, test_source: ResourceSource
    ):
        """Test partial update of a source."""
        original_quantity = test_source.available_quantity
        update_data = {
            "source_identifier": "Updated Location Name",
        }
        response = client.patch(
            f"/api/v1/sources/{test_source.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source_identifier"] == "Updated Location Name"
        assert data["available_quantity"] == float(original_quantity)

    def test_update_source_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating a non-existent source."""
        update_data = {"available_quantity": 100.0}
        response = client.patch(
            "/api/v1/sources/00000000-0000-0000-0000-000000000000",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestVerifySource:
    """Test POST /api/v1/sources/{source_id}/verify endpoint."""

    def test_verify_source_accurate(
        self,
        client: TestClient,
        auth_headers: dict,
        test_source: ResourceSource,
        db_session: Session,
    ):
        """Test verifying a source as accurate."""
        verification_data = {
            "source_id": test_source.id,
            "was_accurate": True,
            "notes": "Verified in-game, stock accurate",
        }
        response = client.post(
            f"/api/v1/sources/{test_source.id}/verify",
            json=verification_data,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["was_accurate"] is True
        assert data["source_id"] == test_source.id

        # Check that source's last_verified was updated
        db_session.refresh(test_source)
        assert test_source.last_verified is not None

        # Check that reliability score was recalculated
        assert test_source.reliability_score > Decimal("0.5")

    def test_verify_source_inaccurate(
        self,
        client: TestClient,
        auth_headers: dict,
        test_source: ResourceSource,
        db_session: Session,
    ):
        """Test verifying a source as inaccurate."""
        verification_data = {
            "source_id": test_source.id,
            "was_accurate": False,
            "notes": "Stock levels were incorrect",
        }
        response = client.post(
            f"/api/v1/sources/{test_source.id}/verify",
            json=verification_data,
            headers=auth_headers,
        )
        assert response.status_code == 201

        # Check that reliability score decreased
        db_session.refresh(test_source)
        assert test_source.reliability_score < Decimal("0.5")

    def test_verify_source_multiple_verifications(
        self,
        client: TestClient,
        auth_headers: dict,
        test_source: ResourceSource,
        db_session: Session,
    ):
        """Test multiple verifications affect reliability score."""
        # Verify as accurate multiple times
        for _ in range(3):
            verification_data = {
                "source_id": test_source.id,
                "was_accurate": True,
            }
            client.post(
                f"/api/v1/sources/{test_source.id}/verify",
                json=verification_data,
                headers=auth_headers,
            )

        db_session.refresh(test_source)
        # Reliability should improve with multiple accurate verifications
        assert test_source.reliability_score > Decimal("0.7")

    def test_verify_source_id_mismatch(
        self, client: TestClient, auth_headers: dict, test_source: ResourceSource
    ):
        """Test verification with mismatched source_id."""
        verification_data = {
            "source_id": "00000000-0000-0000-0000-000000000000",
            "was_accurate": True,
        }
        response = client.post(
            f"/api/v1/sources/{test_source.id}/verify",
            json=verification_data,
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_verify_source_not_found(self, client: TestClient, auth_headers: dict):
        """Test verifying a non-existent source."""
        verification_data = {
            "source_id": "00000000-0000-0000-0000-000000000000",
            "was_accurate": True,
        }
        response = client.post(
            "/api/v1/sources/00000000-0000-0000-0000-000000000000/verify",
            json=verification_data,
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestReliabilityScoring:
    """Test reliability scoring algorithm."""

    def test_reliability_with_no_verifications(
        self, db_session: Session, test_source: ResourceSource
    ):
        """Test reliability score defaults to 0.5 for unverified sources."""
        from app.routers.sources import calculate_reliability_score

        score = calculate_reliability_score(db_session, test_source.id)
        assert score == Decimal("0.5")

    def test_reliability_with_accurate_verifications(
        self,
        client: TestClient,
        auth_headers: dict,
        test_source: ResourceSource,
        db_session: Session,
        test_user: User,
    ):
        """Test reliability improves with accurate verifications."""
        # Add accurate verifications
        for _ in range(5):
            verification = SourceVerificationLog(
                source_id=test_source.id,
                verified_by=test_user.id,
                was_accurate=True,
                verified_at=datetime.now(timezone.utc),
            )
            db_session.add(verification)
        db_session.commit()

        from app.routers.sources import calculate_reliability_score

        score = calculate_reliability_score(db_session, test_source.id)
        assert score > Decimal("0.5")

    def test_reliability_with_inaccurate_verifications(
        self,
        client: TestClient,
        auth_headers: dict,
        test_source: ResourceSource,
        db_session: Session,
        test_user: User,
    ):
        """Test reliability decreases with inaccurate verifications."""
        # Add inaccurate verifications
        for _ in range(3):
            verification = SourceVerificationLog(
                source_id=test_source.id,
                verified_by=test_user.id,
                was_accurate=False,
                verified_at=datetime.now(timezone.utc),
            )
            db_session.add(verification)
        db_session.commit()

        from app.routers.sources import calculate_reliability_score

        score = calculate_reliability_score(db_session, test_source.id)
        assert score < Decimal("0.5")

    def test_reliability_staleness_penalty(
        self,
        db_session: Session,
        test_source: ResourceSource,
        test_user: User,
    ):
        """Test reliability decreases with stale data."""
        # Add old verification
        old_verification = SourceVerificationLog(
            source_id=test_source.id,
            verified_by=test_user.id,
            was_accurate=True,
            verified_at=datetime.now(timezone.utc) - timedelta(days=60),
        )
        db_session.add(old_verification)
        test_source.last_verified = datetime.now(timezone.utc) - timedelta(days=60)
        db_session.commit()

        from app.routers.sources import calculate_reliability_score

        score = calculate_reliability_score(db_session, test_source.id)
        # Score should be penalized for staleness
        assert score < Decimal("1.0")

