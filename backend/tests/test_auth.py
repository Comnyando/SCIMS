"""
Tests for authentication endpoints and utilities.

This test suite covers:
- User registration
- User login
- Token refresh
- Current user endpoint
- Password hashing and verification
- JWT token generation and validation
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, decode_token

client = TestClient(app)


@pytest.fixture
def test_user_data():
    """Fixture for test user data."""
    return {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }


@pytest.fixture
def registered_user(test_user_data):
    """Fixture that creates a registered user and returns user data."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    return response.json()


class TestPasswordHashing:
    """Tests for password hashing utilities."""
    
    def test_hash_password(self):
        """Test that password hashing produces a different string."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash prefix
    
    def test_verify_password_correct(self):
        """Test that correct password verifies successfully."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test that incorrect password fails verification."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestJWTTokens:
    """Tests for JWT token utilities."""
    
    def test_create_access_token(self):
        """Test that access token can be created."""
        data = {"sub": "user123", "email": "user@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test that valid token can be decoded."""
        data = {"sub": "user123", "email": "user@example.com"}
        token = create_access_token(data)
        
        payload = decode_token(token, token_type="access")
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "user@example.com"
        assert payload["type"] == "access"
    
    def test_decode_invalid_token(self):
        """Test that invalid token returns None."""
        invalid_token = "invalid.token.here"
        payload = decode_token(invalid_token, token_type="access")
        
        assert payload is None


class TestRegistration:
    """Tests for user registration endpoint."""
    
    def test_register_success(self, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
        assert data["user"]["username"] == test_user_data["username"]
        assert "id" in data["user"]
        assert data["user"]["is_active"] is True
        assert data["user"]["is_verified"] is False
        # Password should never be in response
        assert "password" not in data["user"]
        assert "hashed_password" not in data["user"]
    
    def test_register_duplicate_email(self, test_user_data):
        """Test that registering with duplicate email fails."""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register with same email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "different_username"
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_register_duplicate_username(self, test_user_data):
        """Test that registering with duplicate username fails."""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register with same username
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()
    
    def test_register_weak_password(self, test_user_data):
        """Test that weak password is rejected."""
        weak_password_data = test_user_data.copy()
        weak_password_data["password"] = "short"  # Too short
        
        response = client.post("/api/v1/auth/register", json=weak_password_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_invalid_email(self, test_user_data):
        """Test that invalid email format is rejected."""
        invalid_email_data = test_user_data.copy()
        invalid_email_data["email"] = "not-an-email"
        
        response = client.post("/api/v1/auth/register", json=invalid_email_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_no_username(self, test_user_data):
        """Test that registration works without username."""
        data_without_username = {
            "email": "nousername@example.com",
            "password": test_user_data["password"],
        }
        
        response = client.post("/api/v1/auth/register", json=data_without_username)
        
        assert response.status_code == 201
        assert response.json()["user"]["username"] is None


class TestLogin:
    """Tests for user login endpoint."""
    
    def test_login_success(self, registered_user, test_user_data):
        """Test successful login."""
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
    
    def test_login_wrong_password(self, registered_user, test_user_data):
        """Test that wrong password fails login."""
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword",
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "password" in response.json()["detail"].lower() or "email" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self):
        """Test that login with nonexistent user fails."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword",
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "password" in response.json()["detail"].lower() or "email" in response.json()["detail"].lower()


class TestRefreshToken:
    """Tests for token refresh endpoint."""
    
    def test_refresh_token_success(self, registered_user):
        """Test successful token refresh."""
        refresh_token = registered_user["refresh_token"]
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # New tokens should be different
        assert data["access_token"] != registered_user["access_token"]
    
    def test_refresh_invalid_token(self):
        """Test that invalid refresh token is rejected."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        
        assert response.status_code == 401
        assert "token" in response.json()["detail"].lower()
    
    def test_refresh_access_token_fails(self, registered_user):
        """Test that using access token as refresh token fails."""
        access_token = registered_user["access_token"]
        
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        
        assert response.status_code == 401


class TestCurrentUser:
    """Tests for current user endpoint."""
    
    def test_get_current_user_success(self, registered_user):
        """Test that authenticated user can get their info."""
        access_token = registered_user["access_token"]
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == registered_user["user"]["email"]
        assert data["id"] == registered_user["user"]["id"]
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_get_current_user_no_token(self):
        """Test that unauthenticated request is rejected."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # FastAPI OAuth2PasswordBearer returns 403
    
    def test_get_current_user_invalid_token(self):
        """Test that invalid token is rejected."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        
        assert response.status_code == 401

