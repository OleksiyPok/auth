# tests/test_user_roles.py
"""
Tests for user role management.

Tests cover:
- User role assignment
- Role validation
- Role-based access control
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.users.models import User
from app.users.schemas import UserRoleAssignRequestSchema


class TestUserRoleAssignment:
    """Tests for user role assignment endpoint."""

    def test_assign_role_success(self, client: TestClient, admin_user_token: str):
        """Admin assigning role to user should return 200."""
        # Create a regular user first
        register_data = {
            "login": "regularuser",
            "password": "password123",
            "email": "regular@example.com",
            "first_name": "Regular",
            "last_name": "User",
        }
        client.post("/api/v1/auth/register", json=register_data)

        # Assign admin role to the user
        role_data = UserRoleAssignRequestSchema(role="admin")

        headers = {"Authorization": f"Bearer {admin_user_token}"}
        response = client.patch(
            "/api/v1/users/{user_id}/role",
            json=role_data.model_dump(),
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["role"] == "admin"

    def test_assign_role_unauthorized(
        self, client: TestClient, regular_user_token: str
    ):
        """Regular user trying to assign role should return 403."""
        # Create another user
        register_data = {
            "login": "targetuser",
            "password": "password123",
            "email": "target@example.com",
            "first_name": "Target",
            "last_name": "User",
        }
        client.post("/api/v1/auth/register", json=register_data)

        # Try to assign role as regular user
        role_data = UserRoleAssignRequestSchema(role="admin")

        headers = {"Authorization": f"Bearer {regular_user_token}"}
        response = client.patch(
            "/api/v1/users/{user_id}/role",
            json=role_data.model_dump(),
            headers=headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_assign_role_invalid_role(self, client: TestClient, admin_user_token: str):
        """Assigning invalid role should return 400."""
        # Create a user
        register_data = {
            "login": "invalidroleuser",
            "password": "password123",
            "email": "invalid@example.com",
            "first_name": "Invalid",
            "last_name": "Role",
        }
        client.post("/api/v1/auth/register", json=register_data)

        # Try to assign invalid role
        role_data = UserRoleAssignRequestSchema(role="invalid_role")

        headers = {"Authorization": f"Bearer {admin_user_token}"}
        response = client.patch(
            "/api/v1/users/{user_id}/role",
            json=role_data.model_dump(),
            headers=headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRoleValidation:
    """Tests for role validation."""

    def test_valid_roles(self, client: TestClient, admin_user_token: str):
        """Valid roles should be accepted."""
        valid_roles = ["user", "admin", "superadmin"]

        for role in valid_roles:
            # Create a user
            register_data = {
                "login": f"user_{role}",
                "password": "password123",
                "email": f"{role}@example.com",
                "first_name": role.capitalize(),
                "last_name": "User",
            }
            client.post("/api/v1/auth/register", json=register_data)

            # Assign role
            role_data = UserRoleAssignRequestSchema(role=role)

            headers = {"Authorization": f"Bearer {admin_user_token}"}
            response = client.patch(
                "/api/v1/users/{user_id}/role",
                json=role_data.model_dump(),
                headers=headers,
            )

            assert response.status_code == status.HTTP_200_OK
            assert response.json()["role"] == role

    def test_case_sensitive_role_validation(
        self, client: TestClient, admin_user_token: str
    ):
        """Role validation should be case-sensitive."""
        # Create a user
        register_data = {
            "login": "caseuser",
            "password": "password123",
            "email": "case@example.com",
            "first_name": "Case",
            "last_name": "Sensitive",
        }
        client.post("/api/v1/auth/register", json=register_data)

        # Try to assign uppercase role (should fail)
        role_data = UserRoleAssignRequestSchema(role="USER")

        headers = {"Authorization": f"Bearer {admin_user_token}"}
        response = client.patch(
            "/api/v1/users/{user_id}/role",
            json=role_data.model_dump(),
            headers=headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRoleBasedAccessControl:
    """Tests for role-based access control."""

    def test_admin_can_access_user_endpoints(
        self, client: TestClient, admin_user_token: str
    ):
        """Admin should be able to access user management endpoints."""
        # Get all users (admin-only endpoint)
        headers = {"Authorization": f"Bearer {admin_user_token}"}
        response = client.get("/api/v1/users", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_user_cannot_access_admin_endpoints(
        self, client: TestClient, regular_user_token: str
    ):
        """Regular user should not be able to access admin-only endpoints."""
        # Try to get all users as regular user
        headers = {"Authorization": f"Bearer {regular_user_token}"}
        response = client.get("/api/v1/users", headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_superadmin_has_all_permissions(
        self, client: TestClient, superadmin_user_token: str
    ):
        """Superadmin should have access to all endpoints."""
        # Get all users (admin-only endpoint)
        headers = {"Authorization": f"Bearer {superadmin_user_token}"}
        response = client.get("/api/v1/users", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
