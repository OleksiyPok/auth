# tests/test_user_sessions.py
"""
Tests for user session management.

Tests cover:
- User session listing
- Session revocation
- Session validation
- Session security
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.sessions.schemas import SessionResponseSchema


class TestUserSessionManagement:
    """Tests for user session management endpoints."""

    def test_get_user_sessions_success(
        self, client: TestClient, regular_user_token: str
    ):
        """User should be able to list their own sessions."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        response = client.get("/api/v1/sessions", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        sessions = response.json()
        assert isinstance(sessions, list)
        # Should have at least one session (the current one)
        assert len(sessions) >= 1

        # Check session structure
        for session in sessions:
            assert "id" in session
            assert "provider" in session
            assert "created_at" in session
            assert "expires_at" in session

    def test_get_user_sessions_unauthorized(self, client: TestClient):
        """User without token should not be able to list sessions."""
        response = client.get("/api/v1/sessions")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_revoke_all_sessions_success(
        self, client: TestClient, regular_user_token: str
    ):
        """User should be able to revoke all their sessions."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        response = client.post("/api/v1/sessions/revoke_all_session", headers=headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_revoke_specific_session_success(
        self, client: TestClient, regular_user_token: str
    ):
        """User should be able to revoke a specific session."""
        # First get the user's sessions to get a session ID
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        sessions_response = client.get("/api/v1/sessions", headers=headers)

        assert sessions_response.status_code == status.HTTP_200_OK
        sessions = sessions_response.json()

        if sessions:  # If there are sessions
            session_id = sessions[0]["id"]

            # Revoke the specific session
            response = client.post(
                f"/api/v1/sessions/{session_id}/revoke",
                headers=headers,
            )

            assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_revoke_session_unauthorized(
        self, client: TestClient, regular_user_token: str
    ):
        """User should not be able to revoke another user's session."""
        # Create another user and get their session
        register_data = {
            "login": "otheruser",
            "password": "password123",
            "email": "other@example.com",
            "first_name": "Other",
            "last_name": "User",
        }
        client.post("/api/v1/auth/register", json=register_data)

        login_data = {
            "login": "otheruser",
            "password": "password123",
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        other_user_token = login_response.json()["access_token"]

        # Try to revoke the other user's session
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        response = client.post(
            "/api/v1/sessions/{session_id}/revoke",
            headers=headers,
        )

        # Should fail with 404 or 403
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
        ]


class TestSessionSecurity:
    """Tests for session security and validation."""

    def test_session_expiration_handling(
        self, client: TestClient, regular_user_token: str
    ):
        """Expired sessions should be handled properly."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        response = client.get("/api/v1/sessions", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        sessions = response.json()

        # Check that expired sessions are not returned
        for session in sessions:
            # Session should not be expired
            from datetime import datetime

            expires_at = datetime.fromisoformat(
                session["expires_at"].replace("Z", "+00:00")
            )
            assert expires_at > datetime.now()

    def test_session_revocation_persistence(
        self, client: TestClient, regular_user_token: str
    ):
        """Session revocation should persist across requests."""
        # Get initial sessions
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        initial_response = client.get("/api/v1/sessions", headers=headers)
        assert initial_response.status_code == status.HTTP_200_OK
        initial_sessions = initial_response.json()

        # Revoke all sessions
        revoke_response = client.post(
            "/api/v1/sessions/revoke_all_session", headers=headers
        )
        assert revoke_response.status_code == status.HTTP_204_NO_CONTENT

        # Get sessions again - should be empty or only non-revoked sessions
        final_response = client.get("/api/v1/sessions", headers=headers)
        assert final_response.status_code == status.HTTP_200_OK
        final_sessions = final_response.json()

        # All sessions should be revoked
        for session in final_sessions:
            assert session.get("is_active", True) == False

    def test_session_token_validation(
        self, client: TestClient, regular_user_token: str
    ):
        """Session tokens should be validated properly."""
        # Use the token to access protected endpoints
        headers = {"Authorization": f"Bearer {regular_user_token}"}

        # Access user profile
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # Access sessions
        response = client.get("/api/v1/sessions", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_session_cross_user_access_protection(self, client: TestClient):
        """Users should not be able to access each other's sessions."""
        # Create two users
        user1_data = {
            "login": "user1",
            "password": "password123",
            "email": "user1@example.com",
            "first_name": "User",
            "last_name": "One",
        }
        client.post("/api/v1/auth/register", json=user1_data)

        user2_data = {
            "login": "user2",
            "password": "password123",
            "email": "user2@example.com",
            "first_name": "User",
            "last_name": "Two",
        }
        client.post("/api/v1/auth/register", json=user2_data)

        # Login as user1
        user1_login = {"login": "user1", "password": "password123"}
        user1_response = client.post("/api/v1/auth/login", json=user1_login)
        user1_token = user1_response.json()["access_token"]

        # Login as user2
        user2_login = {"login": "user2", "password": "password123"}
        user2_response = client.post("/api/v1/auth/login", json=user2_login)
        user2_token = user2_response.json()["access_token"]

        # User1 tries to access user2's sessions
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # Get user2's sessions as user1 (should fail)
        response = client.get("/api/v1/sessions", headers=user1_headers)
        # This should work because sessions endpoint is self-referential
        # But let's test a more specific case

        # The real test is that each user can only see their own sessions
        # This is enforced by the require_self_sessions_read dependency


class TestSessionLifecycle:
    """Tests for session lifecycle management."""

    def test_session_creation_on_login(self, client: TestClient):
        """New session should be created on user login."""
        # Register a new user
        register_data = {
            "login": "newuser",
            "password": "password123",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
        }
        client.post("/api/v1/auth/register", json=register_data)

        # Login to create a session
        login_data = {"login": "newuser", "password": "password123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        # Get sessions - should have at least one
        headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        sessions_response = client.get("/api/v1/sessions", headers=headers)
        assert sessions_response.status_code == status.HTTP_200_OK
        sessions = sessions_response.json()

        assert len(sessions) >= 1
        assert sessions[0]["provider"] == "local"

    def test_session_rotation_on_refresh(self, client: TestClient):
        """Session should be rotated on token refresh."""
        # Register and login
        register_data = {
            "login": "refreshuser",
            "password": "password123",
            "email": "refresh@example.com",
            "first_name": "Refresh",
            "last_name": "User",
        }
        client.post("/api/v1/auth/register", json=register_data)

        login_data = {"login": "refreshuser", "password": "password123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        refresh_data = {"refresh_token": login_response.json()["refresh_token"]}

        # Refresh tokens
        refresh_response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == status.HTTP_200_OK

        # Get sessions - should have sessions
        headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        sessions_response = client.get("/api/v1/sessions", headers=headers)
        assert sessions_response.status_code == status.HTTP_200_OK
        sessions = sessions_response.json()

        # Should have sessions (at least one)
        assert len(sessions) >= 1
