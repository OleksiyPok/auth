# tests/test_authentication.py
"""
Tests for user authentication.

Tests cover:
- User registration
- User login
- Token refresh
- User logout

Note: All tests only check response codes, not response text.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.auth.schemas import (
    LoginRequestSchema,
    RefreshTokenRequestSchema,
    RegisterRequestSchema,
)
from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestUserRegistration:
    """Tests for user registration endpoint."""

    def test_register_success(self, client: TestClient):
        """Successful user registration should return 201."""
        data = RegisterRequestSchema(
            login="newuser",
            password="password123",
            email="newuser@example.com",
            first_name="New",
            last_name="User",
        )

        response = client.post("/api/v1/auth/register", json=data.model_dump())

        assert response.status_code == status.HTTP_201_CREATED

    def test_register_duplicate_login(self, client: TestClient):
        """Duplicate login should return 409."""
        # First register a user
        data = RegisterRequestSchema(
            login="duplicateuser",
            password="password123",
            email="duplicate@example.com",
            first_name="Duplicate",
            last_name="User",
        )
        client.post("/api/v1/auth/register", json=data.model_dump())

        # Try to register with same login
        response = client.post("/api/v1/auth/register", json=data.model_dump())

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_register_invalid_data(self, client: TestClient):
        """Invalid registration data should return 422."""
        # Missing required fields
        data = {}
        response = client.post("/api/v1/auth/register", json=data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, client: TestClient):
        """Successful login should return 200."""
        # First register a user
        register_data = RegisterRequestSchema(
            login="loginuser",
            password="password123",
            email="loginuser@example.com",
            first_name="Login",
            last_name="User",
        )
        client.post("/api/v1/auth/register", json=register_data.model_dump())

        # Login with correct credentials using form data (as expected by the API)
        form_data = {
            "username": "loginuser",
            "password": "password123",
        }

        response = client.post("/api/v1/auth/login", data=form_data)

        assert response.status_code == status.HTTP_200_OK

    def test_login_invalid_credentials(self, client: TestClient):
        """Invalid credentials should return 401."""
        # Login with incorrect credentials using form data
        form_data = {
            "username": "nonexistent",
            "password": "wrongpassword",
        }

        response = client.post("/api/v1/auth/login", data=form_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client: TestClient):
        """Login with inactive user should return 401."""
        # Register a user
        register_data = RegisterRequestSchema(
            login="inactiveuser",
            password="password123",
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
        )
        client.post("/api/v1/auth/register", json=register_data.model_dump())

        # Login with correct credentials
        form_data = {
            "username": "inactiveuser",
            "password": "password123",
        }

        response = client.post("/api/v1/auth/login", data=form_data)

        # Should return 401 for inactive user
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefresh:
    """Tests for token refresh endpoint."""

    def test_refresh_token_success(self, client: TestClient):
        """Valid refresh token should return new tokens."""
        # Register and login to get tokens
        register_data = RegisterRequestSchema(
            login="refreshuser",
            password="password123",
            email="refresh@example.com",
            first_name="Refresh",
            last_name="User",
        )
        client.post("/api/v1/auth/register", json=register_data.model_dump())

        # Login to get tokens
        form_data = {
            "username": "refreshuser",
            "password": "password123",
        }
        login_response = client.post("/api/v1/auth/login", data=form_data)

        # Get refresh token from response (it's in the JSON response)
        refresh_token = login_response.json()["refresh_token"]

        refresh_data = RefreshTokenRequestSchema(
            refresh_token=refresh_token,
        )

        response = client.post("/api/v1/auth/refresh", json=refresh_data.model_dump())

        assert response.status_code == status.HTTP_200_OK

    def test_refresh_token_invalid(self, client: TestClient):
        """Invalid refresh token should return 401."""
        refresh_data = RefreshTokenRequestSchema(
            refresh_token="invalid_token",
        )

        response = client.post("/api/v1/auth/refresh", json=refresh_data.model_dump())

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserLogout:
    """Tests for user logout endpoint."""

    def test_logout_success(self, client: TestClient):
        """Valid logout should return 204."""
        # Register and login to get tokens
        register_data = RegisterRequestSchema(
            login="logoutuser",
            password="password123",
            email="logout@example.com",
            first_name="Logout",
            last_name="User",
        )
        client.post("/api/v1/auth/register", json=register_data.model_dump())

        # Login to get tokens
        form_data = {
            "username": "logoutuser",
            "password": "password123",
        }
        login_response = client.post("/api/v1/auth/login", data=form_data)

        # Get refresh token from response
        refresh_token = login_response.json()["refresh_token"]

        refresh_data = RefreshTokenRequestSchema(
            refresh_token=refresh_token,
        )

        response = client.post("/api/v1/auth/logout", json=refresh_data.model_dump())

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_logout_invalid_token(self, client: TestClient):
        """Invalid logout token should return 401."""
        refresh_data = RefreshTokenRequestSchema(
            refresh_token="invalid_token",
        )

        response = client.post("/api/v1/auth/logout", json=refresh_data.model_dump())

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
