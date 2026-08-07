# tests/test_user_sessions.py

"""
Tests for user session management.

Tests cover:
- User session listing
- Session revocation
- Session validation
- Session security
"""

from datetime import datetime, timezone

from fastapi import status
from fastapi.testclient import TestClient


class TestUserSessionManagement:
    """Tests for user session management endpoints."""

    def test_get_user_sessions_success(
        self,
        client: TestClient,
        regular_user_token: str,
    ):
        """User should be able to list their own sessions."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}

        response = client.get(
            "/api/v1/sessions",
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK

        sessions = response.json()

        assert isinstance(sessions, list)
        assert len(sessions) >= 1

        for session in sessions:
            assert "id" in session
            assert "provider" in session
            assert "created_at" in session
            assert "expires_at" in session

    def test_get_user_sessions_unauthorized(
        self,
        client: TestClient,
    ):
        """User without token should not be able to list sessions."""
        response = client.get("/api/v1/sessions")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_revoke_all_sessions_success(
        self,
        client: TestClient,
        regular_user_token: str,
    ):
        """User should be able to revoke all their sessions."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}

        response = client.post(
            "/api/v1/sessions/revoke_all_session",
            headers=headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_revoke_specific_session_success(
        self,
        client: TestClient,
        regular_user_token: str,
    ):
        """User should be able to revoke a specific session."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}

        sessions_response = client.get(
            "/api/v1/sessions",
            headers=headers,
        )

        assert sessions_response.status_code == status.HTTP_200_OK

        sessions = sessions_response.json()

        assert sessions

        session_id = sessions[0]["id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/revoke",
            headers=headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_revoke_specific_session_persistence(
        self,
        client: TestClient,
        regular_user_token: str,
    ):
        """Revoked session should invalidate the current token."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}

        sessions_response = client.get(
            "/api/v1/sessions",
            headers=headers,
        )

        assert sessions_response.status_code == status.HTTP_200_OK

        sessions = sessions_response.json()

        assert sessions

        session_id = sessions[0]["id"]

        revoke_response = client.post(
            f"/api/v1/sessions/{session_id}/revoke",
            headers=headers,
        )

        assert revoke_response.status_code == status.HTTP_204_NO_CONTENT

        final_response = client.get(
            "/api/v1/sessions",
            headers=headers,
        )

        assert final_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_revoke_session_unauthorized(
        self,
        client: TestClient,
        regular_user_token: str,
    ):
        """User should not be able to revoke another user's session."""
        register_data = {
            "login": "otheruser",
            "password": "password123",
            "email": "other@example.com",
            "first_name": "Other",
            "last_name": "User",
        }

        register_response = client.post(
            "/api/v1/auth/register",
            json=register_data,
        )

        assert register_response.status_code == status.HTTP_201_CREATED

        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "otheruser",
                "password": "password123",
            },
        )

        assert login_response.status_code == status.HTTP_200_OK

        other_user_token = login_response.json()["access_token"]

        other_headers = {
            "Authorization": f"Bearer {other_user_token}",
        }

        sessions_response = client.get(
            "/api/v1/sessions",
            headers=other_headers,
        )

        assert sessions_response.status_code == status.HTTP_200_OK

        sessions = sessions_response.json()

        assert sessions

        session_id = sessions[0]["id"]

        headers = {
            "Authorization": f"Bearer {regular_user_token}",
        }

        response = client.post(
            f"/api/v1/sessions/{session_id}/revoke",
            headers=headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSessionSecurity:
    """Tests for session security and validation."""

    def test_session_expiration_handling(
        self,
        client: TestClient,
        regular_user_token: str,
    ):
        """Expired sessions should be handled properly."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}

        response = client.get(
            "/api/v1/sessions",
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK

        sessions = response.json()

        for session in sessions:
            expires_at = datetime.fromisoformat(
                session["expires_at"].replace("Z", "+00:00"),
            )

            assert expires_at > datetime.now(timezone.utc)

    def test_session_revocation_persistence(
        self,
        client: TestClient,
        regular_user_token: str,
    ):
        """Session revocation should invalidate the current token."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}

        initial_response = client.get(
            "/api/v1/sessions",
            headers=headers,
        )

        assert initial_response.status_code == status.HTTP_200_OK
        assert initial_response.json()

        revoke_response = client.post(
            "/api/v1/sessions/revoke_all_session",
            headers=headers,
        )

        assert revoke_response.status_code == status.HTTP_204_NO_CONTENT

        final_response = client.get(
            "/api/v1/sessions",
            headers=headers,
        )

        assert final_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_session_token_validation(
        self,
        client: TestClient,
        regular_user_token: str,
    ):
        """Session tokens should be validated properly."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}

        response = client.get(
            "/api/v1/users/me",
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK

        response = client.get(
            "/api/v1/sessions",
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK

    def test_session_cross_user_access_protection(
        self,
        client: TestClient,
    ):
        """Users should not be able to revoke each other's sessions."""
        user1_data = {
            "login": "user1",
            "password": "password123",
            "email": "user1@example.com",
            "first_name": "User",
            "last_name": "One",
        }

        user2_data = {
            "login": "user2",
            "password": "password123",
            "email": "user2@example.com",
            "first_name": "User",
            "last_name": "Two",
        }

        response = client.post(
            "/api/v1/auth/register",
            json=user1_data,
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = client.post(
            "/api/v1/auth/register",
            json=user2_data,
        )
        assert response.status_code == status.HTTP_201_CREATED

        user1_login = client.post(
            "/api/v1/auth/login",
            data={
                "username": "user1",
                "password": "password123",
            },
        )

        user2_login = client.post(
            "/api/v1/auth/login",
            data={
                "username": "user2",
                "password": "password123",
            },
        )

        assert user1_login.status_code == status.HTTP_200_OK
        assert user2_login.status_code == status.HTTP_200_OK

        user1_token = user1_login.json()["access_token"]
        user2_token = user2_login.json()["access_token"]

        user2_sessions = client.get(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {user2_token}"},
        )

        assert user2_sessions.status_code == status.HTTP_200_OK

        sessions = user2_sessions.json()
        assert sessions

        session_id = sessions[0]["id"]

        response = client.post(
            f"/api/v1/sessions/{session_id}/revoke",
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSessionLifecycle:
    """Tests for session lifecycle management."""

    def test_session_creation_on_login(
        self,
        client: TestClient,
    ):
        """New session should be created on user login."""
        register_data = {
            "login": "newuser",
            "password": "password123",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
        }

        register_response = client.post(
            "/api/v1/auth/register",
            json=register_data,
        )

        assert register_response.status_code == status.HTTP_201_CREATED

        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "newuser",
                "password": "password123",
            },
        )

        assert login_response.status_code == status.HTTP_200_OK

        access_token = login_response.json()["access_token"]

        response = client.get(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK

        sessions = response.json()

        assert len(sessions) >= 1
        assert sessions[0]["provider"] == "local"

    def test_session_rotation_on_refresh(
        self,
        client: TestClient,
    ):
        """Session should be rotated on token refresh."""
        register_data = {
            "login": "refreshuser",
            "password": "password123",
            "email": "refresh@example.com",
            "first_name": "Refresh",
            "last_name": "User",
        }

        register_response = client.post(
            "/api/v1/auth/register",
            json=register_data,
        )

        assert register_response.status_code == status.HTTP_201_CREATED

        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "refreshuser",
                "password": "password123",
            },
        )

        assert login_response.status_code == status.HTTP_200_OK

        login_data = login_response.json()

        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": login_data["refresh_token"],
            },
        )

        assert refresh_response.status_code == status.HTTP_200_OK

        response = client.get(
            "/api/v1/sessions",
            headers={
                "Authorization": f"Bearer {login_data['access_token']}",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()
