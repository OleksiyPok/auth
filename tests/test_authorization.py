# tests/test_authorization.py
"""
Tests for authorization dependencies.

Tests cover:
- require_permissions dependency
- require_any_permission dependency
- require_role dependency
- Convenience dependencies
"""

from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.auth.authorization import (
    InsufficientPermissionsError,
    get_user_permissions,
    require_any_permission,
    require_permissions,
    require_role,
)
from app.core.rbac import Permission, Role
from app.users.models import User


class MockUser:
    """Mock user for testing."""

    def __init__(self, role: str = "user"):
        self.id = "test-user-id"
        self.login = "testuser"
        self.email = "test@test.com"
        self.first_name = "Test"
        self.last_name = "User"
        self.role = role
        self.is_active = True


class TestGetUserPermissions:
    """Tests for get_user_permissions function."""

    def test_user_role_permissions(self):
        """User role should get self permissions."""
        user = MockUser(role="user")
        perms = get_user_permissions(user)
        assert Permission.SELF_READ in perms
        assert Permission.SELF_WRITE in perms
        assert Permission.ADMIN_ACCESS not in perms

    def test_admin_role_permissions(self):
        """Admin role should get admin permissions."""
        user = MockUser(role="admin")
        perms = get_user_permissions(user)
        assert Permission.SELF_READ in perms
        assert Permission.USERS_READ in perms
        assert Permission.ADMIN_ACCESS in perms
        assert Permission.ADMIN_MANAGE_ROLES not in perms

    def test_superadmin_role_permissions(self):
        """Superadmin role should get all permissions."""
        user = MockUser(role="superadmin")
        perms = get_user_permissions(user)
        assert Permission.SELF_READ in perms
        assert Permission.USERS_READ in perms
        assert Permission.ADMIN_ACCESS in perms
        assert Permission.ADMIN_MANAGE_ROLES in perms
        assert Permission.ROLES_DELETE in perms

    def test_invalid_role_no_permissions(self):
        """Invalid role should get no permissions."""
        user = MockUser(role="invalid")
        perms = get_user_permissions(user)
        assert perms == set()


class TestRequirePermissions:
    """Tests for require_permissions dependency factory."""

    @pytest.mark.asyncio
    async def test_user_with_required_permission(self):
        """User with required permission should pass."""
        user = MockUser(role="admin")
        user_getter = AsyncMock(return_value=user)
        dependency = require_permissions(Permission.USERS_READ, user_getter=user_getter)

        result = await dependency()
        assert result == user

    @pytest.mark.asyncio
    async def test_user_without_required_permission(self):
        """User without required permission should raise 403."""
        user = MockUser(role="user")
        user_getter = AsyncMock(return_value=user)
        dependency = require_permissions(Permission.USERS_READ, user_getter=user_getter)

        with pytest.raises(InsufficientPermissionsError) as exc_info:
            await dependency()

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "INSUFFICIENT_PERMISSIONS"
        assert Permission.USERS_READ in exc_info.value.detail["missing_permissions"]

    @pytest.mark.asyncio
    async def test_multiple_required_permissions_all_needed(self):
        """All required permissions must be present."""
        user = MockUser(role="admin")  # Has USERS_READ but not USERS_DELETE
        user_getter = AsyncMock(return_value=user)
        dependency = require_permissions(
            Permission.USERS_READ, Permission.USERS_DELETE, user_getter=user_getter
        )

        with pytest.raises(InsufficientPermissionsError) as exc_info:
            await dependency()

        assert Permission.USERS_DELETE in exc_info.value.detail["missing_permissions"]

    @pytest.mark.asyncio
    async def test_superadmin_has_all_permissions(self):
        """Superadmin should pass all permission checks."""
        user = MockUser(role="superadmin")
        user_getter = AsyncMock(return_value=user)
        dependency = require_permissions(
            Permission.USERS_READ,
            Permission.USERS_WRITE,
            Permission.USERS_DELETE,
            Permission.ADMIN_MANAGE_ROLES,
            Permission.ROLES_DELETE,
            user_getter=user_getter,
        )

        result = await dependency()
        assert result == user

    def test_invalid_permission_raises_at_startup(self):
        """Invalid permission should raise ValueError at dependency creation."""
        user_getter = AsyncMock(return_value=MockUser(role="user"))
        with pytest.raises(ValueError) as exc_info:
            require_permissions("invalid.permission", user_getter=user_getter)
        assert "Invalid permission" in str(exc_info.value)


class TestRequireAnyPermission:
    """Tests for require_any_permission dependency factory."""

    @pytest.mark.asyncio
    async def test_user_with_one_of_required_permissions(self):
        """User with at least one required permission should pass."""
        user = MockUser(role="admin")  # Has USERS_READ
        user_getter = AsyncMock(return_value=user)
        dependency = require_any_permission(
            Permission.USERS_READ,
            Permission.ADMIN_MANAGE_ROLES,
            user_getter=user_getter,
        )

        result = await dependency()
        assert result == user

    @pytest.mark.asyncio
    async def test_user_without_any_required_permission(self):
        """User without any required permission should raise 403."""
        user = MockUser(role="user")
        user_getter = AsyncMock(return_value=user)
        dependency = require_any_permission(
            Permission.USERS_READ, Permission.ADMIN_ACCESS, user_getter=user_getter
        )

        with pytest.raises(InsufficientPermissionsError) as exc_info:
            await dependency()

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "INSUFFICIENT_PERMISSIONS"

    def test_invalid_permission_raises_at_startup(self):
        """Invalid permission should raise ValueError at dependency creation."""
        user_getter = AsyncMock(return_value=MockUser(role="user"))
        with pytest.raises(ValueError) as exc_info:
            require_any_permission("invalid.permission", user_getter=user_getter)
        assert "Invalid permission" in str(exc_info.value)


class TestRequireRole:
    """Tests for require_role dependency factory."""

    @pytest.mark.asyncio
    async def test_user_with_allowed_role(self):
        """User with allowed role should pass."""
        user = MockUser(role="admin")
        user_getter = AsyncMock(return_value=user)
        dependency = require_role("admin", "superadmin", user_getter=user_getter)

        result = await dependency()
        assert result == user

    @pytest.mark.asyncio
    async def test_user_without_allowed_role(self):
        """User without allowed role should raise 403."""
        user = MockUser(role="user")
        user_getter = AsyncMock(return_value=user)
        dependency = require_role("admin", "superadmin", user_getter=user_getter)

        with pytest.raises(HTTPException) as exc_info:
            await dependency()

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "INSUFFICIENT_ROLE"
        assert exc_info.value.detail["user_role"] == "user"
        assert "admin" in exc_info.value.detail["required_roles"]

    def test_invalid_role_raises_at_startup(self):
        """Invalid role should raise ValueError at dependency creation."""
        user_getter = AsyncMock(return_value=MockUser(role="user"))
        with pytest.raises(ValueError) as exc_info:
            require_role("invalid_role", user_getter=user_getter)
        assert "Invalid role" in str(exc_info.value)


class TestConvenienceDependencies:
    """Tests for convenience dependencies."""

    @pytest.mark.asyncio
    async def test_require_admin_access(self):
        """require_admin_access should work for admin and superadmin."""
        from app.auth.authorization import require_admin_access

        admin_user = MockUser(role="admin")
        superadmin_user = MockUser(role="superadmin")
        regular_user = MockUser(role="user")

        admin_getter = AsyncMock(return_value=admin_user)
        superadmin_getter = AsyncMock(return_value=superadmin_user)
        user_getter = AsyncMock(return_value=regular_user)

        # Test with custom user_getter for testing
        admin_dep = require_admin_access(user_getter=admin_getter)
        superadmin_dep = require_admin_access(user_getter=superadmin_getter)
        user_dep = require_admin_access(user_getter=user_getter)

        result = await admin_dep()
        assert result == admin_user

        result = await superadmin_dep()
        assert result == superadmin_user

        with pytest.raises(InsufficientPermissionsError):
            await user_dep()

    @pytest.mark.asyncio
    async def test_require_self_read(self):
        """require_self_read should work for all roles."""
        from app.auth.authorization import require_self_read

        for role in ["user", "admin", "superadmin"]:
            user = MockUser(role=role)
            user_getter = AsyncMock(return_value=user)
            dep = require_self_read(user_getter=user_getter)
            result = await dep()
            assert result == user

    @pytest.mark.asyncio
    async def test_require_users_read(self):
        """require_users_read should work for admin and superadmin."""
        from app.auth.authorization import require_users_read

        admin_user = MockUser(role="admin")
        superadmin_user = MockUser(role="superadmin")
        regular_user = MockUser(role="user")

        admin_getter = AsyncMock(return_value=admin_user)
        superadmin_getter = AsyncMock(return_value=superadmin_user)
        user_getter = AsyncMock(return_value=regular_user)

        admin_dep = require_users_read(user_getter=admin_getter)
        superadmin_dep = require_users_read(user_getter=superadmin_getter)
        user_dep = require_users_read(user_getter=user_getter)

        result = await admin_dep()
        assert result == admin_user

        result = await superadmin_dep()
        assert result == superadmin_user

        with pytest.raises(InsufficientPermissionsError):
            await user_dep()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
