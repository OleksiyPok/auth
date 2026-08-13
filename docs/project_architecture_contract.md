# Project Architecture Contract

## 1. General Principles

### User

`User` is a stable internal entity in the backend identified by a unique system ID.

`User` is independent of any particular authentication method.

`User` does not contain provider-specific authentication data.

`User` itself does not represent an authentication method. Authentication data belongs to `Identity`.

A `User` may exist with only one `Identity` or with multiple identities.

The `User` ID is the stable internal reference used by the rest of the application.

The architecture does not require `User` to represent a unique real-world person independently of the application's identity-management rules.

### Identity

`Identity` represents a specific authentication identity belonging to a `User`.

Authentication methods are extensible and are not limited to any fixed list. Examples may include:

- local username/password;
- Google;
- phone;
- GitHub;
- Microsoft;
- Apple;
- other authentication providers added in the future.

One `User` may have multiple identities.

A `User` may have at most one `Identity` of each authentication provider/type.

Each `Identity` belongs to exactly one `User`.

Provider-specific authentication data belongs to the corresponding `Identity`, not to `User`.

### Authentication

`Authentication` verifies an `Identity` and provides access to the corresponding `User`.

The general flow is:

```text
Authentication
      ↓
Identity
      ↓
User
      ↓
Session
```

Different authentication providers are independent.

Authentication must not automatically merge identities based on email, username, name, phone number, provider data, or other matching attributes.

Authentication verifies an identity. It does not decide whether two existing identities belong to the same User.

---

## 2. Identity Management

Identity management is a separate account-management mechanism responsible for explicit operations on `Identity` and `User`.

Its initial scope includes:

- `Identity Merge`;
- `Identity Separation`.

Both operations must be explicitly initiated and verified.

Authentication remains responsible for verifying identities and creating authenticated sessions.

Identity management is responsible for changing the relationship between identities and users.

### Identity Merge

`Identity Merge` moves an explicitly selected identity from one `User` to another existing `User`.

The merge operation is performed in the context of an authenticated `User`.

**The currently authenticated User is always the resulting User.**

The other User, which owns the identity being merged, is the source User and is not preserved as an active User after a successful merge.

Example:

```text
Authenticated User A
└── LocalIdentity

User B
└── GoogleIdentity

        ↓ merge

User A
├── LocalIdentity
└── GoogleIdentity
```

User B is no longer an active User.

The Google identity previously belonging to User B now belongs to User A.

The `User A` ID remains unchanged.

The `User B` record may be deactivated or retained according to the application's data-retention policy, but it is no longer an active User.

#### Merge Invariant

The resulting User must have at most one Identity of each authentication provider/type.

If both Users have identities of the same authentication provider/type, this is an identity conflict and must be handled explicitly.

Authentication must not resolve such conflicts automatically.

#### Related Application Data

`User` itself does not contain provider-specific authentication data.

Other application entities may reference `User.id`.

Identity Merge may therefore require additional handling of application data associated with the source User.

The merge mechanism must explicitly define whether related application data is:

- transferred to the resulting User;
- merged;
- retained separately;
- or handled according to another domain-specific rule.

Identity Merge must not silently discard application data.

### Identity Separation

`Identity Separation` removes an explicitly selected identity from its current `User` and creates a new `User` for that identity.

Before:

```text
User A
├── LocalIdentity
└── GoogleIdentity
```

After:

```text
User A
└── LocalIdentity

User B
└── GoogleIdentity
```

The new User receives a new internal User ID.

The separated identity becomes the identity of the new User.

Identity Separation operates only on explicitly selected identities.

It does not automatically select or separate identities based on email, username, name, phone number, provider data, or other matching attributes.

#### Related Application Data

If application data references the original User, the separation mechanism must explicitly define how that data is handled.

Possible rules may include:

- retaining the data with the original User;
- transferring selected data to the new User;
- splitting data according to domain-specific rules;
- preventing separation while certain data exists.

Identity Separation must not silently create inconsistent ownership of application data.

---

## 3. Session

`Session` represents an authenticated User session.

After successfully verifying an identity, authentication resolves the corresponding `User` and creates or updates a `Session`.

```text
Identity
   ↓
User
   ↓
Session
   ↓
Access / Refresh Tokens
```

The session identifies the current authenticated `User`, not a specific authentication provider.

Local and Google authentication may therefore produce sessions for the same User.

After Identity Merge, the resulting User is the User of the authenticated merge initiator.

After Identity Separation, the resulting identities may belong to different Users and require separate authentication sessions according to the application's session policy.

---

## 4. SystemInstance

`SystemInstance` represents one concrete installed or deployed instance of the application.

It represents the application instance itself, not a User.

A `SystemInstance` has its own configuration and integrations.

---

## 5. Integration

`Integration` represents a connection between a particular `SystemInstance` and an external service.

```text
SystemInstance
       ↓
Integration
       ↓
External Provider
```

An `Integration` exists for the application to interact with an external service.

It is not a mechanism for authenticating Users.

---

## 6. IntegrationCredential

`IntegrationCredential` represents credentials belonging to a particular `Integration`.

```text
SystemInstance
       ↓
Integration
       ↓
IntegrationCredential
       ↓
External Provider
```

Integration credentials belong to the `Integration` and `SystemInstance`.

They are not user identities.

For example, a Google integration may use a service account or another supported credential mechanism to access Google APIs.

---

## 7. Authentication and Integration Are Completely Separate

### User Authentication

```text
User
  ↓
GoogleIdentity
  ↓
Google Authentication
  ↓
Session
```

The user's Google account is used to authenticate the User.

### System Integration

```text
SystemInstance
       ↓
Integration
       ↓
IntegrationCredential
       ↓
Google APIs
```

The credentials used by an integration belong to the application and are used to access external APIs.

They are not a `GoogleIdentity`.

The same separation applies to all future providers.

---

## 8. Target Application Structure

The application structure should follow the existing project conventions while organizing the architecture around clear bounded contexts.

```text
app/
├── main.py
├── router.py
│
├── core/
├── db/
├── infrastructure/
│
├── users/
│   ├── models/
│   ├── repository/
│   ├── services/
│   ├── dependencies/
│   ├── schemas/
│   ├── exceptions/
│   └── router/
│
├── local_auth/
│   ├── models/
│   ├── repository/
│   ├── services/
│   ├── dependencies/
│   ├── schemas/
│   ├── exceptions/
│   └── router/
│
├── google_auth/
│   ├── models/
│   ├── repository/
│   ├── services/
│   ├── dependencies/
│   ├── schemas/
│   ├── exceptions/
│   └── router/
│
├── sessions/
│   ├── models/
│   ├── repository/
│   ├── services/
│   ├── dependencies/
│   ├── schemas/
│   ├── exceptions/
│   └── router/
│
├── identity_management/
│   ├── models/
│   ├── repository/
│   ├── services/
│   ├── dependencies/
│   ├── schemas/
│   ├── exceptions/
│   └── router/
│
├── integrations/
│   ├── models/
│   ├── repository/
│   ├── services/
│   ├── dependencies/
│   ├── schemas/
│   ├── exceptions/
│   ├── router/
│   └── providers/
│       ├── google/
│       ├── microsoft/
│       └── ...
│
└── bootstrap/
```

The exact filenames and directories may follow established project conventions.

The important architectural rule is that each bounded context owns its provider-specific or domain-specific behavior.

---

## 9. Authentication Contexts

Each authentication provider is autonomous.

### Local Authentication

The initial local authentication mechanism uses:

```text
username + password
```

The local authentication identity contains the local authentication data, for example:

```text
LocalIdentity
├── username
└── password_hash
```

`username` is a local authentication identifier. It does not have to represent the user's real-world name.

### Google Authentication

Google authentication uses Google as an external identity provider.

The Google-specific identity contains the provider-specific identity data required to identify the Google account.

Google authentication is used only for user authentication.

Google APIs and other Google services are handled by the separate `integrations` context.

---

## 10. Identity Management Context

Identity management is a separate bounded context responsible for account-level operations involving identities and users.

Its scope includes:

- `Identity Merge` — moving an explicitly selected identity from another User to the authenticated User;
- `Identity Separation` — removing an identity from a User and creating a new User for it;
- other explicit identity-management operations defined independently of authentication.

The context is represented as:

```text
identity_management/
├── models/
├── repository/
├── services/
├── dependencies/
├── schemas/
├── exceptions/
└── router/
```

It operates on existing `Identity` and `User` entities and does not belong to an individual authentication provider.

---

## 11. Integration Context

Integrations form a separate system-level bounded context.

```text
integrations/
├── models/
├── repository/
├── services/
├── dependencies/
├── schemas/
├── exceptions/
├── router/
└── providers/
    ├── google/
    ├── microsoft/
    └── ...
```

Provider-specific integration code remains inside its corresponding provider.

---

## 12. Implementation Sequence

### Step 1 — Define the Core Domain Model

Establish the fundamental entities and their relationships:

```text
User
Identity
Session
SystemInstance
Integration
IntegrationCredential
```

The ownership and boundaries between the User domain and system domain must be explicit from the beginning.

The core User model must remain independent of authentication providers.

The Identity model must reference exactly one User.

### Step 2 — Implement Local Authentication

Implement the complete local authentication flow:

```text
Local Authentication
        ↓
LocalIdentity
        ↓
User
        ↓
Session
        ↓
Tokens
```

The initial local credential model is:

```text
username + password
```

### Step 3 — Implement Google Authentication

Implement Google authentication as an independent authentication provider:

```text
Google OAuth
      ↓
GoogleIdentity
      ↓
User
      ↓
Session
      ↓
Tokens
```

Google authentication should contain only functionality required for user authentication.

Google API access must not be implemented inside Google authentication.

### Step 4 — Establish Shared Session Management

Use one provider-independent session mechanism:

```text
Local Authentication ──┐
                       ├──→ Session
Google Authentication ─┘
```

Authentication providers must not introduce separate provider-specific session types.

The Session references the authenticated `User`.

### Step 5 — Implement Identity Management

Introduce identity management as a separate account-management context.

The initial scope includes two explicit operations.

#### Identity Merge

```text
Authenticated User A
└── LocalIdentity

User B
└── GoogleIdentity

        ↓ merge

User A
├── LocalIdentity
└── GoogleIdentity
```

The authenticated User is always the resulting User.

The source User whose identity was transferred is no longer an active User after successful merge.

#### Identity Separation

```text
User A
├── LocalIdentity
└── GoogleIdentity

        ↓ separation

User A
└── LocalIdentity

User B
└── GoogleIdentity
```

Both operations must be explicitly initiated and verified.

Authentication must remain independent and must not perform automatic merge or separation.

### Step 6 — Introduce SystemInstance

Define `SystemInstance` as the entity representing a concrete installed or deployed application instance.

### Step 7 — Introduce Integrations

Define the common integration lifecycle:

```text
SystemInstance
       ↓
Integration
       ↓
IntegrationCredential
       ↓
External Provider
```

Keep integration functionality independent from user authentication.

### Step 8 — Implement Google Integration

Implement Google as the first external-service integration:

```text
SystemInstance
       ↓
Google Integration
       ↓
IntegrationCredential
       ↓
Google APIs
```

Google API functionality belongs here, independently of Google user authentication.

### Step 9 — Add Additional Providers

After the common models and boundaries are stable, add additional providers as independent implementations.

Authentication providers:

```text
Local
Google
Microsoft
...
```

Integration providers:

```text
Google
Microsoft
...
```

Provider-specific code must remain within the corresponding provider boundary.

---

## 13. Final Architectural Model

```text
                              APPLICATION
                                   │
                  ┌────────────────┴────────────────┐
                  │                                 │
             USER DOMAIN                       SYSTEM DOMAIN
                  │                                 │
          ┌───────┴────────┐                 SystemInstance
          │                │                       │
       Identity         Identity               Integration
          │                │                       │
          │                │              IntegrationCredential
          │                │                       │
   Authentication    Authentication         External Services
          │                │
        Local           Google
          │                │
          └───────┬────────┘
                  │
                 User
                  │
                Session
```

The User domain is independent of the System domain.

The User domain contains:

```text
User
Identity
Authentication
Session
Identity Management
```

The System domain contains:

```text
SystemInstance
Integration
IntegrationCredential
External Services
```

---

## 14. Architectural Contract

The central architectural rule is:

> **User Authentication provides access to a `User`. Integration provides a `SystemInstance` with access to external services. These mechanisms must not share credentials or be mixed together.**

The following boundaries are mandatory:

- `User` is a stable internal backend entity identified by a unique system ID.
- `User` is independent of authentication providers.
- `User` does not contain provider-specific authentication data.
- `Identity` belongs to exactly one `User`.
- A `User` may have multiple `Identity` records.
- A `User` may have at most one `Identity` of each authentication provider/type.
- A `User` does not have to have an identity for every supported authentication provider.
- Each authentication provider manages only its own identity type.
- Local authentication initially uses `username + password`.
- Provider-specific authentication data belongs to `Identity`.
- Authentication verifies an `Identity` and resolves its corresponding `User`.
- Authentication never performs automatic identity merging or separation.
- Authentication never merges identities based on matching attributes.
- `Identity Merge` and `Identity Separation` are separate, explicit account-management operations.
- `Identity Merge` moves an explicitly selected identity from another User to the authenticated User.
- In `Identity Merge`, the authenticated User is always the resulting User.
- The source User is no longer an active User after a successful merge.
- Identity Merge must preserve the one-identity-per-provider/type invariant.
- Conflicts between identities of the same provider/type must be handled explicitly by identity management.
- Identity Merge must not silently discard application data associated with the source User.
- `Identity Separation` removes a selected identity from a User and creates a new User for it.
- Identity Separation must preserve the one-identity-per-provider/type invariant.
- Identity Separation must explicitly define how related application data is handled.
- `Session` is provider-independent.
- `SystemInstance` represents the application instance, not a User.
- `Integration` belongs to a `SystemInstance`.
- `IntegrationCredential` belongs to an `Integration` and is not a user identity.
- User authentication credentials and integration credentials are separate concepts.
- Provider-specific authentication code remains inside its authentication boundary.
- Provider-specific integration code remains inside its integration-provider boundary.
- Authentication and integrations evolve independently.

This document defines the target architecture before implementation and serves as the architectural contract for the project.
