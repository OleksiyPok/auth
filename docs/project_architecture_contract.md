# Project project description has been added Contract

## 1. General Principles

### User

`User` represents a person using the system.

`User` is independent of any particular authentication method and does not contain provider-specific authentication data.

### Identity

`Identity` represents a specific authentication method belonging to a `User`.

Authentication methods are extensible and are not limited to any fixed list. Examples may include local credentials, Google, phone, GitHub, Microsoft, or other providers added in the future.

One `User` may have multiple identities:

```text
User
├── Identity
├── Identity
└── ...
```

Each `Identity` belongs to exactly one `User`.

An `Authentication` provider works only with its own identity type.

### Authentication

`Authentication` is the mechanism that verifies an `Identity` and provides access to the corresponding `User`.

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

Different authentication providers are independent:

```text
Local Authentication ──→ LocalIdentity ──→ User
Google Authentication ─→ GoogleIdentity ─→ User
```

Authentication must not automatically merge identities based on email address, name, phone number, or any other matching attributes.

### Identity Merge and Identity Separation

Identity management is a separate account-management mechanism responsible for explicit operations on `Identity` and `User`.

#### Identity Merge

`Identity Merge` combines identities that currently belong to different users under a single `User`.

Before merge:

```text
User A
└── LocalIdentity

User B
└── GoogleIdentity
```

After merge:

```text
User A
├── LocalIdentity
└── GoogleIdentity
```

The exact rules for selecting the resulting `User`, transferring identities, and handling related data are defined by the identity-merge mechanism.

#### Identity Separation

`Identity Separation` separates an identity from its current `User` and creates a new `User` for that identity.

Before separation:

```text
User A
├── LocalIdentity
└── GoogleIdentity
```

After separation:

```text
User A
└── LocalIdentity

User B
└── GoogleIdentity
```

The exact rules for creating the new `User`, transferring related data, and establishing the resulting account state are defined by the identity-separation mechanism.

Both `Identity Merge` and `Identity Separation` are explicit account-management operations. They are not part of ordinary authentication.

Authentication must never automatically merge or separate identities based on email address, name, phone number, provider data, or any other matching attributes.


### Session

`Session` represents an authenticated user session.

After successfully verifying an identity, authentication resolves the corresponding `User` and creates a `Session`.

```text
Identity
   ↓
User
   ↓
Session
   ↓
Access / Refresh Tokens
```

`Session` is independent of the authentication provider.

---

## 2. SystemInstance

`SystemInstance` represents one concrete installed or deployed instance of the application.

It represents the application instance itself, not a user.

A `SystemInstance` is created as part of project/system provisioning and exists independently of the user domain.

A `SystemInstance` has its own configuration and its own integrations.

---

## 3. Integration

`Integration` represents a connection between a particular `SystemInstance` and an external service.

```text
SystemInstance
       ↓
Integration
       ↓
External Provider
```

For example:

```text
SystemInstance
       ↓
Integration(provider=google)
       ↓
Google
```

An `Integration` exists for the application to interact with an external service. It is not a mechanism for authenticating users.

---

## 4. IntegrationCredential

`IntegrationCredential` represents credentials belonging to a particular `Integration`.

```text
SystemInstance
       ↓
Integration
       ↓
IntegrationCredential
       ├── Service Account
       └── Credentials
```

Integration credentials belong to the `Integration` and `SystemInstance`. They are not user identities.

For example, a Google integration may use a service account or another supported credential mechanism to access Google APIs.

---

## 5. Authentication and Integration Are Completely Separate

This is a fundamental architectural rule.

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

The user's Google account is used exclusively to authenticate the user.

### System Integration

```text
SystemInstance
       ↓
Integration
provider = google
       ↓
IntegrationCredential
       ├── Service Account
       └── Credentials
       ↓
Google APIs
```

The Google account or credentials used by an integration belong to the application and are used to access Google APIs.

They are not a `GoogleIdentity`.

The same separation applies to all future providers.

---

## 6. Target Application Structure

The application structure should follow the existing project conventions while organizing the architecture around clear bounded contexts.

A generalized structure is:

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

The names of directories may follow the project's established conventions. The important architectural rule is that each bounded context owns its provider-specific or domain-specific behavior.

Individual files such as repositories, services, interfaces, schemas, and routers are implementation details. The architecture defines them as folders/modules by responsibility rather than prescribing individual filenames.

### Authentication Contexts

Each authentication provider is autonomous:

```text
authentication/
├── local_auth/
└── google_auth/
```

The existing project structure may use `local_auth/` and `google_auth/` as top-level application modules rather than introducing an additional `authentication/` directory.

The important rule is provider isolation, not the exact directory name.

### Identity Management Context

Identity management is a separate bounded context responsible for account-level operations involving identities and users.

Its scope includes:

- `Identity Merge` — combining identities from different users under one `User`;
- `Identity Separation` — separating an identity and creating a new `User`;
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


### Integration Context

Integrations form a separate system-level bounded context:

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

## 7. Implementation Sequence

The project should be implemented in the following order.

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

The ownership and boundaries between the user domain and system domain must be explicit from the beginning.

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

Support the required registration and login flows.

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

### Step 4 — Establish Shared Session Management

Use one provider-independent session mechanism:

```text
Local Authentication ──┐
                       ├──→ Session
Google Authentication ─┘
```

Authentication providers must not introduce separate provider-specific session types.

### Step 5 — Implement Identity Management

Introduce identity management as a separate account-management context.

The initial scope includes two explicit operations:

```text
Identity Merge
       ↓
Identities from different Users
       ↓
One User
```

and:

```text
Identity Separation
       ↓
Selected Identity
       ↓
New User
```

Both operations must be explicitly initiated and verified.

Authentication must remain independent and must not perform automatic merge or separation.


### Step 6 — Introduce SystemInstance

Define `SystemInstance` as the entity representing a concrete installed or deployed application instance.

The model should support creation and configuration before deployment.

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

## 8. Final Architectural Model

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

## 9. Architectural Contract

The central architectural rule is:

> **User Authentication provides a person with access to a `User`. Integration provides a `SystemInstance` with access to external services. These mechanisms must not share credentials or be mixed together.**

The following boundaries are therefore mandatory:

- `User` is independent of authentication providers.
- `Identity` belongs to exactly one `User`.
- Each authentication provider manages only its own identity type.
- Authentication never performs automatic identity merging or separation.
- `Identity Merge` and `Identity Separation` are separate, explicit account-management operations.
- `Identity Merge` combines identities from different users under one `User`.
- `Identity Separation` removes selected identities from a `User` and creates a new `User` for them.
- Identity merge combines identities from different users under one `User`.
- Identity separation removes selected identities from a `User` and creates a new `User` for them.
- `Session` is provider-independent.
- `SystemInstance` represents the application instance, not a user.
- `Integration` belongs to a `SystemInstance`.
- `IntegrationCredential` belongs to an `Integration` and is not a user identity.
- User authentication credentials and integration credentials are separate concepts.
- Provider-specific authentication code remains inside its authentication boundary.
- Provider-specific integration code remains inside its integration-provider boundary.
- Authentication and integrations evolve independently.

This document defines the target architecture before implementation and serves as the architectural contract for the project.
