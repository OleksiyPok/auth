# Architecture Contract vs. Actual Project — Comparison Analysis

## Executive Summary

The `project_architecture_contract.md` document describes a **target architecture** that was written **before implementation**. The actual project has diverged significantly from this target in several key areas:

1. **A new `auth/` context was introduced** (shared authentication, token management, RBAC) that is **not mentioned** in the document at all.
2. **Three contexts described in the document do not exist** in the actual project: `identity_management/`, `integrations/`, and the `SystemInstance` entity.
3. **RBAC (Role-Based Access Control)** is fully implemented in the project but **completely absent** from the document.
4. **File structure conventions differ**: the document describes subdirectory-per-concern (`models/`, `schemas/`, `exceptions/`, `dependencies/`, `router/`), but the actual project uses **flat files** (`models.py`, `schemas.py`, `exceptions.py`, `dependencies.py`, `router.py`) with only `repository/` and `services/` as subdirectories.
5. **Entity models have additional fields** not described in the document (e.g., `User.role`, `User.is_active`, `Session.provider`, `Session.refresh_token_hash`, etc.).
6. **The implementation sequence** in the document describes 9 steps; the project has implemented steps 1–4 but **not** steps 5–9.

---

## Detailed Comparison

### 1. `auth/` Context — MISSING from document, EXISTS in project

**Document says:** Authentication is split between `local_auth/` and `google_auth/` contexts. There is no shared `auth/` context.

**Actual project has:** `app/auth/` containing:

| File/Dir | Purpose |
|---|---|
| `auth/dependencies.py` | Shared auth dependencies: `get_current_user`, `get_token_service`, `get_auth_session_service` |
| `auth/exceptions.py` | Shared auth exceptions: `AuthError`, `InvalidAccessTokenError`, `InsufficientPermissionsError`, `InvalidRoleError` |
| `auth/router.py` | Shared auth router: `/auth/refresh`, `/auth/logout` |
| `auth/rbac/roles.py` | `Role` enum: USER, MANAGER, ADMIN, SUPERADMIN |
| `auth/rbac/permissions.py` | `Permission` enum: atomic permission identifiers (e.g., `users.read`, `admin.access`) |
| `auth/rbac/role_permissions.py` | Declarative role→permission mapping (`ROLE_PERMISSIONS`) |
| `auth/rbac/user_permissions.py` | Resolves permissions for a given user |
| `auth/rbac/dependencies.py` | FastAPI dependency factories: `require_permissions`, `require_role`, `require_admin_access`, etc. |
| `auth/services/token_service.py` | `TokenService` — validates JWT access tokens, resolves `User` from token |
| `auth/services/token_service_interface.py` | `TokenServiceInterface` ABC |
| `auth/services/auth_session_service.py` | `AuthSessionService` — creates access/refresh token pairs, rotates refresh tokens |
| `auth/services/auth_session_service_interface.py` | `AuthSessionServiceInterface` ABC |

**Key insight:** The `auth/` context is the **shared authentication backbone**. Both `local_auth/` and `google_auth/` depend on it (via `AuthSessionServiceInterface` and `TokenServiceInterface`). The document's architecture implicitly assumes this shared layer exists but never names or documents it.

### 2. `identity_management/` Context — IN document, NOT in project

**Document says (Section 8, 10, 12):** There should be an `identity_management/` context with `Identity Merge` and `Identity Separation` operations.

**Actual project:** This directory **does not exist**. There is no identity merge or separation functionality implemented. No models, services, routers, or schemas for identity management.

### 3. `integrations/` Context — IN document, NOT in project

**Document says (Section 8, 11, 12):** There should be an `integrations/` context with `SystemInstance`, `Integration`, `IntegrationCredential`, and provider-specific integration code under `integrations/providers/`.

**Actual project:** This directory **does not exist**. There is no `SystemInstance` model, no `Integration` model, no `IntegrationCredential` model. Google OAuth infrastructure lives in `app/infrastructure/google/` instead, which is used **only for user authentication** (not for system-level API access).

### 4. RBAC — NOT in document, EXISTS in project

**Document says:** Nothing about roles, permissions, or authorization beyond basic authentication.

**Actual project has:** A full RBAC system in `app/auth/rbac/`:

- **Roles** (`roles.py`): `USER`, `MANAGER`, `ADMIN`, `SUPERADMIN` — stored as a `role` field on the `User` model.
- **Permissions** (`permissions.py`): Atomic permission strings like `users.read`, `users.write`, `users.delete`, `users.list`, `sessions.read`, `sessions.revoke`, `sessions.revoke_all`, `admin.access`, `admin.manage_users`, `admin.manage_roles`, `admin.view_logs`, `admin.view_metrics`, `roles.read`, `roles.write`, `roles.delete`, `self.read`, `self.write`, `self.delete`, `self.sessions.read`, `self.sessions.revoke`.
- **Role→Permission mapping** (`role_permissions.py`): Declarative `ROLE_PERMISSIONS` dict mapping each role to its set of permissions. Validated at module load time.
- **User permission resolution** (`user_permissions.py`): `get_user_permissions(user)` returns the permission set for a user based on their role.
- **Dependency factories** (`dependencies.py`): `require_permissions()`, `require_any_permission()`, `require_role()`, plus convenience wrappers like `require_admin_access()`, `require_users_read()`, `require_sessions_revoke()`, etc.

**Key insight:** RBAC is deeply integrated into the `User` model (the `role` field) and used throughout the `users/` and `sessions/` routers for authorization checks.

### 5. File Structure Convention Differences

**Document describes (Section 8):** Each bounded context has subdirectories:
```
context/
├── models/
├── repository/
├── services/
├── dependencies/
├── schemas/
├── exceptions/
└── router/
```

**Actual project uses:** A **hybrid** approach:
- `models.py` — flat file (not `models/` directory)
- `schemas.py` — flat file (not `schemas/` directory)
- `exceptions.py` — flat file (not `exceptions/` directory)
- `dependencies.py` — flat file (not `dependencies/` directory)
- `router.py` — flat file (not `router/` directory)
- `repository/` — subdirectory with `repository.py` and `repository_interface.py`
- `services/` — subdirectory with `service.py` and `service_interface.py`

This applies to `users/`, `local_auth/`, `google_auth/`, and `sessions/`.

### 6. Entity Model Differences

#### User Model

**Document says:** `User` is a stable internal entity with a unique system ID. Independent of authentication providers. Does not contain provider-specific data.

**Actual `User` model** (`app/users/models.py`):
- `id: str` — UUID7
- `email: str`
- `first_name: str`
- `last_name: str`
- `role: str` — **NOT mentioned in document** (RBAC role, defaults to `DEFAULT_ROLE` = "user")
- `is_active: bool` — **NOT mentioned in document** (soft-delete flag)
- `created_at: datetime`
- `updated_at: datetime`

The `role` field is validated via `validate_role()` from `app.auth.rbac.role_permissions`.

#### LocalIdentity Model

**Document says (Section 9):** `LocalIdentity` contains `username` and `password_hash`.

**Actual `LocalIdentity` model** (`app/local_auth/models.py`):
- `id: str` — UUID7
- `user_id: str` — FK to `users.id`, unique (one local identity per user)
- `login: str` — **Document calls this `username`**
- `password_hash: str`
- `created_at: datetime`
- `updated_at: datetime`

#### GoogleIdentity Model

**Document says (Section 9):** Google-specific identity contains provider-specific data to identify the Google account.

**Actual `GoogleIdentity` model** (`app/google_auth/models.py`):
- `id: str` — UUID7
- `user_id: str` — FK to `users.id`, unique (one Google identity per user)
- `google_user_id: str` — unique Google subject identifier
- `created_at: datetime`
- `updated_at: datetime`

#### GoogleOAuthState Model

**Document says:** Nothing about OAuth state management.

**Actual project has** (`app/google_auth/models.py`): `GoogleOAuthState` model for PKCE/OAuth state:
- `id: str` — UUID7
- `state: str` — unique OAuth state parameter
- `code_verifier: str` — PKCE code verifier
- `expires_at: datetime`
- `used: bool`
- `created_at: datetime`

#### Session Model

**Document says (Section 3):** `Session` represents an authenticated user session. References the authenticated `User`.

**Actual `Session` model** (`app/sessions/models.py`):
- `id: str` — UUID7
- `user_id: str` — FK to `users.id`
- `provider: str` — **NOT mentioned in document** (default "local"; tracks which auth provider created the session)
- `refresh_token_hash: str` — **NOT mentioned in document** (hashed refresh token stored server-side)
- `is_active: bool` — **NOT mentioned in document**
- `ip_address: str | None` — **NOT mentioned in document**
- `user_agent: str | None` — **NOT mentioned in document**
- `created_at: datetime`
- `updated_at: datetime`
- `last_used_at: datetime` — **NOT mentioned in document**
- `revoked_at: datetime | None` — **NOT mentioned in document**
- `expires_at: datetime` — **NOT mentioned in document**

### 7. Token Management

**Document says (Section 3):** Session → Access/Refresh Tokens. No detail on token implementation.

**Actual project has:**
- **JWT access tokens** (`app/infrastructure/jwt/security.py`): Created with `sub` (user_id) and `sid` (session_id) claims. Validated via `decode_access_token()`.
- **Refresh tokens** (`app/infrastructure/jwt/refresh_token.py`): Random tokens, hashed before storage (`hash_refresh_token()`), stored as `refresh_token_hash` in `Session`.
- **TokenService** (`app/auth/services/token_service.py`): Validates access tokens, resolves `User` from token claims, validates session.
- **AuthSessionService** (`app/auth/services/auth_session_service.py`): Creates token pairs (access + refresh), rotates refresh tokens on refresh.
- **Refresh token rotation**: Old refresh token is invalidated after use (tested in `test_authentication.py`).

### 8. Implementation Sequence Status

**Document describes (Section 12):** 9 implementation steps.

| Step | Document | Actual Project Status |
|---|---|---|
| 1 — Core Domain Model | User, Identity, Session, SystemInstance, Integration, IntegrationCredential | **Partially implemented**: User, LocalIdentity, GoogleIdentity, Session exist. SystemInstance, Integration, IntegrationCredential do **not** exist. |
| 2 — Local Authentication | Local auth flow | **Implemented**: register, login, LocalIdentity model, LocalLoginService, LocalRegisterService |
| 3 — Google Authentication | Google OAuth flow | **Implemented**: GoogleIdentity model, GoogleAuthService, OAuth state management, callback handling |
| 4 — Shared Session Management | Provider-independent session | **Implemented**: Session model, SessionService, shared AuthSessionService, TokenService |
| 5 — Identity Management | Identity Merge, Identity Separation | **NOT implemented**: No `identity_management/` directory |
| 6 — SystemInstance | SystemInstance entity | **NOT implemented**: No SystemInstance model |
| 7 — Integrations | Integration lifecycle | **NOT implemented**: No `integrations/` directory |
| 8 — Google Integration | Google as external-service integration | **NOT implemented**: No integration context; Google OAuth is only for user auth |
| 9 — Additional Providers | Microsoft, etc. | **NOT implemented** |

### 9. Infrastructure Directory

**Document says (Section 8):** `infrastructure/` exists but contents are not detailed.

**Actual `app/infrastructure/`:**
- `password.py` — Password hashing using `pwdlib` (`hash_password`, `verify_password`)
- `google/config.py` — Google OAuth scopes
- `google/exceptions.py` — `GoogleOAuthError`
- `google/oauth.py` — Google OAuth flow functions (`create_google_oauth_flow`, `get_google_authorization_url`, `exchange_google_code`, `get_google_user_info`)
- `jwt/refresh_token.py` — Refresh token generation and hashing
- `jwt/security.py` — JWT access token creation and validation

### 10. API Endpoints

**Document says:** No specific API endpoints described.

**Actual project endpoints** (all under `/api/v1/`):

| Method | Path | Context | Description |
|---|---|---|---|
| POST | `/auth/register` | local_auth | Register new user with login + password |
| POST | `/auth/login` | local_auth | Login with login + password, returns tokens |
| POST | `/auth/refresh` | auth | Refresh access token using refresh token |
| POST | `/auth/logout` | auth | Logout (revoke session via refresh token) |
| GET | `/auth/google` | google_auth | Initiate Google OAuth flow |
| GET | `/auth/google/callback` | google_auth | Google OAuth callback |
| GET | `/users` | users | List all users (requires `users.read` permission) |
| GET | `/users/me` | users | Get current user (requires `self.read` permission) |
| GET | `/users/{user_id}` | users | Get user by ID (requires `users.read` permission) |
| PATCH | `/users/me` | users | Update own profile (requires `self.write` permission) |
| PATCH | `/users/{user_id}/role` | users | Assign role to user (requires `admin.manage_roles` permission) |
| DELETE | `/users/me` | users | Deactivate own account (requires `self.delete` permission) |
| DELETE | `/users/{user_id}` | users | Deactivate user (requires `users.delete` permission) |
| GET | `/sessions` | sessions | List current user's sessions (requires `self.sessions.read` permission) |
| POST | `/sessions/revoke_all_session` | sessions | Revoke all sessions (requires `self.sessions.revoke` permission) |
| POST | `/sessions/{session_id}/revoke` | sessions | Revoke specific session (requires `self.sessions.revoke` permission) |

### 11. Router Registration

**Document says (Section 8):** `app/router.py` exists.

**Actual `app/router.py`:** Includes routers from:
- `app.auth.router` (auth_router)
- `app.local_auth.router` (local_auth_router)
- `app.google_auth.router` (google_auth_router)
- `app.sessions.router` (sessions_router)
- `app.users.router` (users_router)

Note: `auth/`, `local_auth/`, `google_auth/`, `sessions/`, and `users/` all share the `/auth` prefix for their endpoints (local_auth and google_auth use `/auth` prefix, auth uses `/auth` prefix, sessions uses `/sessions` prefix, users uses `/users` prefix).

### 12. Bootstrap

**Document says (Section 8):** `bootstrap/` directory exists.

**Actual `app/bootstrap/superadmin.py`:** Creates initial superadmin user with `LocalIdentity` on first database initialization. Uses `Role.SUPERADMIN` from RBAC.

### 13. Database

**Document says:** Uses SQLModel/SQLAlchemy (implied by AGENTS.md).

**Actual project:**
- `app/db/engine.py` — Async engine using `aiosqlite`
- `app/db/session.py` — `session_factory` and `get_session` dependency
- `app/db/types.py` — `UTCDateTime` custom type
- `alembic/` — Alembic migrations directory (empty `versions/` directory)
- No `SystemInstance` table, no `Integration` table, no `IntegrationCredential` table

### 14. Final Architectural Model

**Document says (Section 13):** Two domains — USER DOMAIN and SYSTEM DOMAIN.

**Actual project architecture:**

```
app/
├── main.py              # FastAPI app creation, lifespan, middleware
├── router.py            # Root API router, includes all sub-routers
│
├── core/                # Core configuration and exceptions
├── db/                  # Database engine, session, types
├── infrastructure/      # Password hashing, JWT, Google OAuth
│
├── auth/                # SHARED AUTHENTICATION CONTEXT (not in document)
│   ├── dependencies.py  # get_current_user, get_token_service, get_auth_session_service
│   ├── exceptions.py    # AuthError, InvalidAccessTokenError, etc.
│   ├── router.py        # /auth/refresh, /auth/logout
│   ├── rbac/            # RBAC system (not in document)
│   │   ├── roles.py
│   │   ├── permissions.py
│   │   ├── role_permissions.py
│   │   ├── user_permissions.py
│   │   └── dependencies.py
│   └── services/        # TokenService, AuthSessionService
│       ├── token_service.py
│       ├── token_service_interface.py
│       ├── auth_session_service.py
│       └── auth_session_service_interface.py
│
├── users/               # User management
├── local_auth/          # Local authentication (register, login)
├── google_auth/         # Google authentication (OAuth)
├── sessions/            # Session management
├── bootstrap/           # Initial superadmin creation
```

**Key difference:** The document's "SYSTEM DOMAIN" (SystemInstance, Integration, IntegrationCredential) does not exist. The `auth/` context (shared authentication backbone + RBAC) is the most significant addition not covered by the document.

---

## Summary of Required Document Changes

### A. Add new sections

1. **Section: `auth/` Context** — Document the shared authentication context containing token service, auth session service, RBAC, and shared auth router.
2. **Section: RBAC** — Document roles, permissions, role-permission mapping, and authorization dependencies.
3. **Section: Token Management** — Document JWT access tokens, refresh tokens, token rotation, and the TokenService/AuthSessionService.
4. **Section: API Endpoints** — Document the actual REST API endpoints.
5. **Section: Infrastructure** — Document the actual infrastructure structure (password, JWT, Google OAuth).

### B. Remove or mark as not-yet-implemented

1. **`identity_management/` context** — Does not exist in the project.
2. **`integrations/` context** — Does not exist in the project.
3. **`SystemInstance` entity** — Does not exist in the project.
4. **`Integration` and `IntegrationCredential` entities** — Do not exist in the project.
5. **Implementation Steps 5–9** — Not yet implemented.

### C. Update existing sections

1. **Section 8 (Target Application Structure)** — Update to reflect actual file structure (flat files instead of subdirectories, add `auth/` context, remove `identity_management/` and `integrations/`).
2. **Section 1 (General Principles)** — Add `role` and `is_active` fields to User model description.
3. **Section 9 (Authentication Contexts)** — Update `LocalIdentity` to use `login` instead of `username`. Add `GoogleIdentity` model details. Add `GoogleOAuthState` model.
4. **Section 3 (Session)** — Add `provider`, `refresh_token_hash`, `ip_address`, `user_agent`, `last_used_at`, `revoked_at`, `expires_at` fields.
5. **Section 12 (Implementation Sequence)** — Update to reflect actual implementation status (steps 1–4 done, steps 5–9 not started).
6. **Section 13 (Final Architectural Model)** — Update to reflect actual architecture (add `auth/` context, remove SYSTEM DOMAIN).
7. **Section 14 (Architectural Contract)** — Add RBAC-related boundaries, token management rules, and update existing rules to match actual implementation.
