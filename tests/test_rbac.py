# tests/test_rbac.py
"""
Tests for RBAC (Role-Based Access Control) system.

Tests cover:
- Permission and Role enums
- Role-permission mapping
- User role assignment and validation
- Authorization dependencies
"""

import pytest

from app.auth.rbac import (
    DEFAULT_ROLE,
    ROLE_PERMISSIONS,
    Permission,
    Role,
    get_all_permissions,
    get_all_roles,
    get_permissions_for_role,
    get_roles_with_permission,
    is_valid_role,
    validate_role,
)
from app.users.models import User


class TestPermissionEnum:
    """Tests for Permission enum."""

    def test_permission_values_are_strings(self):
        """All permission values should be strings."""
        for perm in Permission:
            assert isinstance(perm.value, str)

    def test_permission_naming_convention(self):
        """Permissions should follow RESOURCE_ACTION convention."""
        for perm in Permission:
            # Should contain a dot separating resource and action
            assert "." in perm.value
            resource, action = perm.value.split(".", 1)
            assert resource
            assert action

    def test_validate_method(self):
        """Permission.validate() should correctly identify valid permissions."""
        assert Permission.validate("users.read") is True
        assert Permission.validate("admin.access") is True
        assert Permission.validate("invalid.permission") is False
        assert Permission.validate("") is False

    def test_all_method(self):
        """Permission.all() should return all defined permissions."""
        all_perms = Permission.all()
        assert len(all_perms) == len(list(Permission))
        assert "users.read" in all_perms
        assert "admin.access" in all_perms


class TestRoleEnum:
    """Tests for Role enum."""

    def test_role_values(self):
        """Roles should have expected values."""
        assert Role.USER == "user"
        assert Role.ADMIN == "admin"
        assert Role.SUPERADMIN == "superadmin"

    def test_validate_method(self):
        """Role.validate() should correctly identify valid roles."""
        assert Role.validate("user") is True
        assert Role.validate("admin") is True
        assert Role.validate("superadmin") is True
        assert Role.validate("invalid") is False
        assert Role.validate("") is False


class TestRolePermissionsMapping:
    """Tests for ROLE_PERMISSIONS mapping."""

    def test_all_roles_have_permissions(self):
        """Every role in ROLE_PERMISSIONS should have at least one permission."""
        for role, perms in ROLE_PERMISSIONS.items():
            assert len(perms) > 0, f"Role '{role}' has no permissions"

    def test_all_permissions_are_valid(self):
        """All permissions in ROLE_PERMISSIONS should be valid Permission enum values."""
        all_perms = Permission.all()
        for role, perms in ROLE_PERMISSIONS.items():
            for perm in perms:
                assert (
                    perm in all_perms
                ), f"Role '{role}' has invalid permission: '{perm}'"

    def test_user_role_permissions(self):
        """User role should have self permissions only."""
        user_perms = get_permissions_for_role("user")
        expected = {
            Permission.SELF_READ,
            Permission.SELF_WRITE,
            Permission.SELF_DELETE,
            Permission.SELF_SESSIONS_READ,
            Permission.SELF_SESSIONS_REVOKE,
        }
        assert user_perms == expected

    def test_admin_role_permissions(self):
        """Admin role should have user permissions plus admin permissions."""
        admin_perms = get_permissions_for_role("admin")
        user_perms = get_permissions_for_role("user")

        # Admin should have all user permissions
        assert user_perms.issubset(admin_perms)

        # Admin should have additional permissions
        assert Permission.USERS_READ in admin_perms
        assert Permission.USERS_WRITE in admin_perms
        assert Permission.USERS_LIST in admin_perms
        assert Permission.SESSIONS_READ in admin_perms
        assert Permission.SESSIONS_REVOKE in admin_perms
        assert Permission.ADMIN_ACCESS in admin_perms
        assert Permission.ADMIN_VIEW_LOGS in admin_perms
        assert Permission.ADMIN_VIEW_METRICS in admin_perms

    def test_superadmin_role_permissions(self):
        """Superadmin role should have all permissions."""
        superadmin_perms = get_permissions_for_role("superadmin")
        all_perms = get_all_permissions()
        assert superadmin_perms == all_perms

    def test_unknown_role_returns_empty_set(self):
        """Unknown role should return empty permission set."""
        assert get_permissions_for_role("unknown") == set()

    def test_is_valid_role(self):
        """is_valid_role should correctly identify valid roles."""
        assert is_valid_role("user") is True
        assert is_valid_role("admin") is True
        assert is_valid_role("superadmin") is True
        assert is_valid_role("unknown") is False

    def test_validate_role(self):
        """validate_role should return valid role or raise ValueError."""
        assert validate_role("user") == "user"
        assert validate_role("admin") == "admin"
        assert validate_role("superadmin") == "superadmin"

        with pytest.raises(ValueError) as exc_info:
            validate_role("invalid")
        assert "Invalid role" in str(exc_info.value)

    def test_get_all_roles(self):
        """get_all_roles should return all defined roles."""
        roles = get_all_roles()
        assert "user" in roles
        assert "admin" in roles
        assert "superadmin" in roles
        assert len(roles) == 3

    def test_get_all_permissions(self):
        """get_all_permissions should return union of all role permissions."""
        all_perms = get_all_permissions()
        assert len(all_perms) > 0
        # Should include permissions from all roles
        assert Permission.SELF_READ in all_perms
        assert Permission.ADMIN_ACCESS in all_perms
        assert Permission.ROLES_DELETE in all_perms

    def test_get_roles_with_permission(self):
        """get_roles_with_permission should return roles that have the permission."""
        roles = get_roles_with_permission(Permission.SELF_READ)
        assert "user" in roles
        assert "admin" in roles
        assert "superadmin" in roles

        roles = get_roles_with_permission(Permission.ADMIN_MANAGE_ROLES)
        assert "superadmin" in roles
        assert "admin" not in roles
        assert "user" not in roles


class TestUserModelRole:
    """Tests for User model role assignment and validation."""

    def test_default_role(self):
        """New users should get default role."""
        user = User(
            login="test",
            password_hash="hash",
            email="test@test.com",
            first_name="Test",
            last_name="User",
        )
        assert user.role == DEFAULT_ROLE
        assert user.role == "user"

    def test_explicit_role_assignment(self):
        """Users can be created with explicit role."""
        user = User(
            login="test",
            password_hash="hash",
            email="test@test.com",
            first_name="Test",
            last_name="User",
            role="admin",
        )
        assert user.role == "admin"

    def test_invalid_role_raises_error(self):
        """Creating user with invalid role should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            User(
                login="test",
                password_hash="hash",
                email="test@test.com",
                first_name="Test",
                last_name="User",
                role="invalid_role",
            )
        assert "Invalid role" in str(exc_info.value)

    def test_role_validation_case_sensitive(self):
        """Role validation should be case-sensitive."""
        with pytest.raises(ValueError):
            User(
                login="test",
                password_hash="hash",
                email="test@test.com",
                first_name="Test",
                last_name="User",
                role="USER",  # uppercase
            )


class TestDefaultRole:
    """Tests for DEFAULT_ROLE constant."""

    def test_default_role_is_user(self):
        """DEFAULT_ROLE should be 'user'."""
        assert DEFAULT_ROLE == "user"
        assert DEFAULT_ROLE == Role.USER


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
