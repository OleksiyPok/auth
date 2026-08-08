# tests/test_user_roles.py

"""
Tests for user role management.

Tests cover:
- User role assignment
- Role validation
- Role-based access control
"""

from fastapi import status
from fastapi.testclient import TestClient

from app.users.schemas import UserRoleAssignRequestSchema


class TestUserRoleAssignment:
    """Tests for user role assignment endpoint."""

    def test_assign_role_success(
        self,
        client: TestClient,
        superadmin_user_token: str,
    ):
        """Admin assigning role to user should return 200."""
        register_data = {
            "login": "regularuser",
            "password": "password123",
            "email": "regular@example.com",
            "first_name": "Regular",
            "last_name": "User",
        }

        register_response = client.post(
            "/api/v1/auth/register",
            json=register_data,
        )

        assert register_response.status_code == status.HTTP_201_CREATED

        user_id = register_response.json()["id"]

        role_data = UserRoleAssignRequestSchema(role="admin")

        headers = {"Authorization": f"Bearer {superadmin_user_token}"}

        response = client.patch(
            f"/api/v1/users/{user_id}/role",
            json=role_data.model_dump(),
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["role"] == "admin"

    def test_assign_role_unauthorized(
        self,
        client: TestClient,
        regular_user_token: str,
    ):
        """Regular user trying to assign role should return 403."""
        register_data = {
            "login": "targetuser",
            "password": "password123",
            "email": "target@example.com",
            "first_name": "Target",
            "last_name": "User",
        }

        register_response = client.post(
            "/api/v1/auth/register",
            json=register_data,
        )

        assert register_response.status_code == status.HTTP_201_CREATED

        user_id = register_response.json()["id"]

        role_data = UserRoleAssignRequestSchema(role="admin")

        headers = {"Authorization": f"Bearer {regular_user_token}"}

        response = client.patch(
            f"/api/v1/users/{user_id}/role",
            json=role_data.model_dump(),
            headers=headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_assign_role_invalid_role(
        self,
        client: TestClient,
        superadmin_user_token: str,
    ):
        """Assigning invalid role should return 400."""
        register_data = {
            "login": "invalidroleuser",
            "password": "password123",
            "email": "invalid@example.com",
            "first_name": "Invalid",
            "last_name": "Role",
        }

        register_response = client.post(
            "/api/v1/auth/register",
            json=register_data,
        )

        assert register_response.status_code == status.HTTP_201_CREATED

        user_id = register_response.json()["id"]

        role_data = UserRoleAssignRequestSchema(role="invalid_role")

        headers = {"Authorization": f"Bearer {superadmin_user_token}"}

        response = client.patch(
            f"/api/v1/users/{user_id}/role",
            json=role_data.model_dump(),
            headers=headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRoleValidation:
    """Tests for role validation."""

    def test_valid_roles(
        self,
        client: TestClient,
        superadmin_user_token: str,
    ):
        """Valid roles should be accepted."""
        valid_roles = ["user", "admin", "superadmin"]

        headers = {"Authorization": f"Bearer {superadmin_user_token}"}

        for role in valid_roles:
            register_data = {
                "login": f"user_{role}",
                "password": "password123",
                "email": f"{role}@example.com",
                "first_name": role.capitalize(),
                "last_name": "User",
            }

            register_response = client.post(
                "/api/v1/auth/register",
                json=register_data,
            )

            assert register_response.status_code == status.HTTP_201_CREATED

            user_id = register_response.json()["id"]

            role_data = UserRoleAssignRequestSchema(role=role)

            response = client.patch(
                f"/api/v1/users/{user_id}/role",
                json=role_data.model_dump(),
                headers=headers,
            )

            assert response.status_code == status.HTTP_200_OK
            assert response.json()["role"] == role

    def test_case_sensitive_role_validation(
        self,
        client: TestClient,
        superadmin_user_token: str,
    ):
        """Role validation should be case-sensitive."""
        register_data = {
            "login": "caseuser",
            "password": "password123",
            "email": "case@example.com",
            "first_name": "Case",
            "last_name": "Sensitive",
        }

        register_response = client.post(
            "/api/v1/auth/register",
            json=register_data,
        )

        assert register_response.status_code == status.HTTP_201_CREATED

        user_id = register_response.json()["id"]

        role_data = UserRoleAssignRequestSchema(role="USER")

        headers = {"Authorization": f"Bearer {superadmin_user_token}"}

        response = client.patch(
            f"/api/v1/users/{user_id}/role",
            json=role_data.model_dump(),
            headers=headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRoleBasedAccessControl:
    """Tests for role-based access control."""

    def test_admin_can_access_user_endpoints(
        self,
        client: TestClient,
        admin_user_token: str,
    ):
        """Admin should be able to access user management endpoints."""
        headers = {"Authorization": f"Bearer {admin_user_token}"}

        response = client.get(
            "/api/v1/users",
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_user_cannot_access_admin_endpoints(
        self,
        client: TestClient,
        regular_user_token: str,
    ):
        """Regular user should not be able to access admin-only endpoints."""
        headers = {"Authorization": f"Bearer {regular_user_token}"}

        response = client.get(
            "/api/v1/users",
            headers=headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_superadmin_has_all_permissions(
        self,
        client: TestClient,
        superadmin_user_token: str,
    ):
        """Superadmin should have access to all endpoints."""
        headers = {"Authorization": f"Bearer {superadmin_user_token}"}

        response = client.get(
            "/api/v1/users",
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
