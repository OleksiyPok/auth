# Auth Service Documentation

---

# 1. Overview

Auth Service is responsible for authentication and session management.

Main responsibilities:
- user registration
- user authentication
- session management
- password recovery

Supported authentication methods:
- Email + Password

Planned authentication methods:
- Google OAuth / OIDC
- Phone OTP

---

# 2. Scope

## Included
- registration
- login
- refresh token
- logout
- logout all sessions
- forgot password
- reset password

## Excluded
- user profile management
- billing
- notifications
- advanced authorization policies

---

# 3. Architecture

## Overview

The project follows Clean Architecture / Hexagonal Architecture principles.

Core business logic depends only on abstractions.
External systems are accessed through ports and adapters.

Dependency direction always points inward.

---

## Architecture Flow

```text
External World
     ↓
Router / Controller
     ↓
Service / Use Cases
     ↓
Ports (Contracts)
     ↑
Adapters (Infrastructure)
```

---

## Internal Flow

```text
Router → Service → Ports ← Adapters
```

---

## Layer Responsibilities

### Router
Handles HTTP requests and responses.

Responsibilities:
- request validation
- DTO mapping
- calling services
- formatting responses

Router must not contain business logic.

---

### Service
Contains business logic and use cases.

Examples:
- register user
- login user
- refresh token
- reset password

Service depends only on Ports.

Service must not depend on:
- database
- framework internals
- JWT library
- hashing library
- SMTP provider

---

### Ports
Defines contracts for external dependencies.

Examples:
- UserRepository
- RefreshTokenRepository
- PasswordResetTokenRepository
- TokenProvider
- PasswordHasher
- EmailSender

Ports define behavior, not implementation.

---

### Adapters
Contains implementations of Ports.

Examples:
- PostgresUserRepository
- RedisRefreshTokenRepository
- JWTTokenProvider
- ArgonPasswordHasher
- SMTPEmailSender

Adapters may depend on:
- PostgreSQL
- Redis
- SMTP
- external APIs
- third-party libraries

---

## Dependency Rules

### Rule 1
Dependencies point inward.

Correct:
```text
Router → Service → Ports
Adapters → Ports
```

Wrong:
```text
Service → PostgreSQL
Service → Redis
Service → SMTP
```

---

### Rule 2
Business logic must remain infrastructure-agnostic.

Service must not know:
- which database is used
- which email provider is used
- which token implementation is used

---

### Rule 3
Infrastructure is replaceable.

Examples:
```text
UserRepository
 ├── PostgresUserRepository
 ├── MongoUserRepository

EmailSender
 ├── SMTPEmailSender
 ├── SendgridEmailSender
```

---

# 4. Development Rules

Feature implementation order:

## 1. Define Use Cases
Describe what the system should do.

---

## 2. Define Domain Model
Define entities and relationships.

---

## 3. Define DTOs
Define request and response schemas.

---

## 4. Define Ports
Define contracts for external dependencies.

---

## 5. Implement Adapters
Implement infrastructure.

---

## 6. Implement Services
Implement business logic.

---

## 7. Implement Routers
Expose HTTP endpoints.

---

# 5. Authentication

## Purpose

Authentication system for the application.

Supports:
- Email + Password
- JWT Access Token
- JWT Refresh Token

---

## Use Cases

- register
- login
- refresh token
- logout
- logout all sessions
- forgot password
- reset password

---

# 6. Authentication Flows

## Register Flow

1. User submits email and password
2. Backend validates input
3. Password is hashed
4. User is created
5. Response returned

---

## Login Flow

1. Verify user credentials
2. Generate access token
3. Generate refresh token
4. Store refresh token
5. Return tokens

---

## Refresh Flow

1. Validate refresh token
2. Verify session
3. Issue new access token
4. Optionally rotate refresh token

---

## Logout Flow

1. Validate session
2. Remove refresh token
3. Return success

---

## Logout All Sessions Flow

1. Validate user
2. Remove all refresh tokens
3. Return success

---

## Password Reset Flow

1. Generate reset token
2. Send email
3. Validate token
4. Update password
5. Invalidate token

---

# 7. Domain Model

## Entities

### User

Fields:
- id
- email
- password_hash
- created_at
- updated_at

---

### RefreshToken

Fields:
- id
- user_id
- token_hash
- expires_at
- created_at

---

### PasswordResetToken

Fields:
- id
- user_id
- token_hash
- expires_at
- created_at

---

# 8. Ports

## Repositories
- UserRepository
- RefreshTokenRepository
- PasswordResetTokenRepository

---

## Providers
- TokenProvider
- PasswordHasher
- EmailSender

---

# 9. API Contract

## Authentication

---

### POST /auth/register

Request:
```json
{
  "email": "user@example.com",
  "password": "secret"
}
```

Response:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com"
  }
}
```

---

### POST /auth/login

Request:
```json
{
  "email": "user@example.com",
  "password": "secret"
}
```

Response:
```json
{
  "access_token": "jwt",
  "refresh_token": "jwt"
}
```

---

### POST /auth/refresh

Request:
```json
{
  "refresh_token": "jwt"
}
```

Response:
```json
{
  "access_token": "jwt"
}
```

---

### POST /auth/logout

Request:
```json
{
  "refresh_token": "jwt"
}
```

Response:
```json
{
  "success": true
}
```

---

### POST /auth/logout-all

Auth required.

Response:
```json
{
  "success": true
}
```

---

### POST /auth/forgot-password

Request:
```json
{
  "email": "user@example.com"
}
```

Response:
```json
{
  "success": true
}
```

---

### POST /auth/reset-password

Request:
```json
{
  "token": "reset-token",
  "new_password": "new-secret"
}
```

Response:
```json
{
  "success": true
}
```

---

## Users

### GET /users/me

Auth required.

Response:
```json
{
  "id": "uuid",
  "email": "user@example.com"
}
```

---

# 10. Security Rules

- Passwords must be stored hashed
- Recommended hashing algorithm: Argon2
- Access tokens must have short lifetime
- Refresh tokens must be securely stored
- Refresh tokens should be stored hashed
- Login must be rate-limited
- Reset tokens must expire
- Reset tokens must be single-use

Recommended token lifetime:
- Access token: 15 minutes
- Refresh token: 30 days
- Reset token: 15 minutes

---

# 11. Open Questions

- Should refresh tokens rotate?
- Should multiple sessions be supported?
- Should email verification be required?
- Should MFA be supported?
- Should OAuth providers be added?