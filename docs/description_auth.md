# Unified Authentication System

## Technical Specification v1

---

# 1. Overview

The Authentication System is an independent backend service responsible only for authentication and authorization.

The service must not depend on any external business domain or application-specific entities.

The architecture must be generic, reusable, scalable, and extensible.

---

# 2. Scope

## Included

- User authentication
- User authorization
- Role-Based Access Control (RBAC)
- Authentication providers
- JWT authentication
- Refresh Tokens
- Email verification
- Password reset

## Excluded

The service MUST NOT manage:

- Business entities
- User profiles
- Organizations
- Contacts
- Any application-specific data

---

# 3. Authentication Providers

The initial version must support:

- Local (Email + Password)
- Google OAuth2 / OpenID Connect

The architecture must allow adding new providers without changing existing authentication logic.

---

# 4. Authorization

Authorization is based on Role-Based Access Control (RBAC).

Rules:

- Every user has exactly one role.
- Permissions belong only to roles.
- Permissions are never assigned directly to users.

Default roles:

- SuperAdmin
- Admin
- Viewer

---

# 5. Core Entities

The authentication domain consists of the following entities:

- SystemUser
- Role
- Permission
- AuthIdentity
- RefreshToken

---

# 6. Entity Specifications

## SystemUser

> TODO

---

## Role

> TODO

---

## Permission

> TODO

---

## AuthIdentity

> TODO

---

## RefreshToken

> TODO

---

# 7. Database Schema

> TODO

---

# 8. API

## Authentication

> TODO

---

## Users

> TODO

---

## Roles

> TODO

---

## Permissions

> TODO

---

# 9. Authentication Flows

The system must support:

- Registration
- Login
- Logout
- Refresh Token
- Google Login
- Email Verification
- Forgot Password
- Reset Password

Flow details:

> TODO

---

# 10. Security

The implementation must include:

- Password hashing
- JWT Access Tokens
- Refresh Tokens
- Email verification
- Secure password reset

Security details:

> TODO

---

# 11. Configuration

Configuration values:

- DATABASE_URL
- JWT_SECRET
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE
- REFRESH_TOKEN_EXPIRE
- SMTP configuration
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET

Additional configuration:

> TODO
