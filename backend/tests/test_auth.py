"""
Tests for authentication system.

This test suite verifies:
- Password hashing and verification (Argon2)
- User registration endpoint
- User login endpoint
- Token refresh endpoint
- Current user endpoint
"""

import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_token


class TestPasswordHashing:
    """Test password hashing utilities."""
    
    def test_hash_password(self):
        """Test that passwords are hashed correctly."""
        password = "testpass123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$argon2")
    
    def test_verify_password_correct(self):
        """Test that correct password verifies."""
        password = "testpass123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test that incorrect password fails."""
        password = "testpass123"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False


class TestJWTTokens:
    """Test JWT token utilities."""
    
    def test_create_and_decode_access_token(self):
        """Test that access tokens can be created and decoded."""
        data = {"sub": "user123", "email": "user@example.com"}
        token = create_access_token(data)
        
        payload = decode_token(token, token_type="access")
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "user@example.com"
        assert payload["type"] == "access"
    
    def test_decode_invalid_token(self):
        """Test that invalid tokens return None."""
        assert decode_token("invalid.token.here", token_type="access") is None


class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_register_new_user(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepassword123",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        # Check user data
        user = data["user"]
        assert user["email"] == "newuser@example.com"
        assert user["username"] == "newuser"
        assert user["is_active"] is True
        assert user["is_verified"] is False
        assert "id" in user
        assert "password" not in user
        assert "hashed_password" not in user
    
    def test_register_duplicate_email(self, client):
        """Test that duplicate email registration fails."""
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user1",
                "password": "password123",
            },
        )
        
        # Try to register with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user2",
                "password": "password123",
            },
        )
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_register_without_username(self, client):
        """Test that registration works without username."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "nousername@example.com",
                "password": "password123",
            },
        )
        
        assert response.status_code == 201
        assert response.json()["user"]["username"] is None


class TestUserLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client):
        """Test successful login."""
        # Register a user first
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "loginuser@example.com",
                "password": "mypassword123",
            },
        )
        assert register_response.status_code == 201
        
        # Login with correct credentials
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "loginuser@example.com",
                "password": "mypassword123",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "loginuser@example.com"
    
    def test_login_wrong_password(self, client):
        """Test that wrong password fails login."""
        # Register a user first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "correctpassword123",
            },
        )
        
        # Try to login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test that login with nonexistent user fails."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword",
            },
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()


class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    def test_refresh_token_success(self, client):
        """Test successful token refresh."""
        # Register and get tokens
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "password123",
            },
        )
        refresh_token = register_response.json()["refresh_token"]
        
        # Refresh the token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_invalid_token(self, client):
        """Test that invalid refresh token is rejected."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        
        assert response.status_code == 401


class TestCurrentUser:
    """Test current user endpoint."""
    
    def test_get_current_user(self, client):
        """Test that authenticated user can get their info."""
        # Register and get token
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "currentuser@example.com",
                "username": "currentuser",
                "password": "password123",
            },
        )
        access_token = register_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "currentuser@example.com"
        assert data["username"] == "currentuser"
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_get_current_user_no_token(self, client):
        """Test that unauthenticated request is rejected."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test that invalid token is rejected."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401
