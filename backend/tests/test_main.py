"""
Placeholder tests for the main application.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def test_client():
    """Create a test client for the app."""
    return TestClient(app)


def test_read_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "app" in data
    assert data["app"] == "SCIMS"
    assert "api" in data
    assert data["api"] == "v1"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_root():
    """Test API root endpoint."""
    response = client.get("/api/v1")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "api" in data
    assert data["api"] == "v1"

