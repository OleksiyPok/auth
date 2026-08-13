# Architectural Contract of the Project

## 1. General Principles

### User

**User** is the human/user of the system.

User does not depend on a specific authentication method and does not contain provider-specific data.

### Identity

**Identity** is a specific authentication method belonging to a User.

One User may have multiple identities:

```text
User
├── Identity
├── Identity
└── ...
```

Each Identity belongs to exactly one User.

Authentication works only with its own Identity.

### Authentication

**Authentication** is the mechanism that verifies an Identity and provides access to the corresponding User.

General flow:

```text
Authentication
↓
Identity
↓
User
↓
Session
```

Different Authentication providers are independent:

```text
Local Authentication ──→ LocalIdentity ──→ User
Google Authentication ─→ GoogleIdentity ─→ User
```

Authentication does not automatically merge identities based on email, name, phone number, or any other matching data.

### Identity Linking

**Identity Linking** is a separate account-management mechanism that links multiple identities to one User.

Before linking:

```text
User A
└── LocalIdentity

User B
└── GoogleIdentity
```

After controlled linking:

```text
User A
├── LocalIdentity
└── GoogleIdentity
```

After linking, both Authentication providers return the same User.

Linking is a separate operation and is not part of normal Authentication.

### Session

**Session** is an authenticated user session.

After successfully verifying an Identity, Authentication obtains the User and creates a Session.

```text
Identity
↓
User
↓
Session
↓
Access / Refresh tokens
```

Session does not depend on a specific Authentication provider.

---

## 2. SystemInstance

**SystemInstance** is a specific installed/deployed instance of the system.

SystemInstance represents the application instance itself, not the user.

It is created as part of project preparation before deployment.

A SystemInstance has its own configuration and its own Integrations.

---

## 3. Integration

**Integration** is a connection between a specific SystemInstance and an external service.

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

Integration is intended for the application itself to work with an external service, not for user authentication.

---

## 4. IntegrationCredential

**IntegrationCredential** contains the credentials of a specific Integration.

```text
SystemInstance
↓
Integration
↓
IntegrationCredential
├── service account
└── credentials
```

Credentials belong to the Integration/SystemInstance and are not User Identities.

For example, a Google Integration may use a service account or another credential mechanism.

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

The user's Google account is used exclusively for user authentication.

### System Integration

```text
SystemInstance
↓
Integration
provider = google
↓
IntegrationCredential
├── service account
└── credentials
↓
Google APIs
```

Google accounts/credentials used by an Integration are used by the application to access Google APIs.

They are **not** GoogleIdentity objects.

The same rule applies to any future providers.

---

## 6. Target Structure

### Authentication

```text
app/
└── authentication/
    ├── local/
    │   ├── models/
    │   ├── repository/
    │   ├── services/
    │   ├── dependencies/
    │   ├── schemas/
    │   └── router/
    │
    └── google/
        ├── models/
        ├── repository/
        ├── services/
        ├── dependencies/
        ├── schemas/
        └── router/
```

Actual directory names may preserve the existing project conventions.

The main principle is that each Authentication provider is autonomous.

### Identity Linking

Identity Linking is a separate bounded context:

```text
app/
└── identity_linking/
    ├── models/
    ├── repository/
    ├── services/
    ├── dependencies/
    ├── schemas/
    └── router/
```

It works with already existing Identities and Users.

### Integrations

```text
app/
└── integrations/
    ├── models/
    │   ├── system_instance.py
    │   ├── integration.py
    │   └── integration_credential.py
    │
    ├── repository/
    │   ├── repository.py
    │   └── repository_interface.py
    │
    ├── services/
    │   ├── service.py
    │   └── service_interface.py
    │
    └── providers/
        ├── google/
        ├── microsoft/
        └── ...
```

---

## 7. Implementation Sequence

### Stage 1 — Fundamental Entities

Establish a stable model:

```text
User
Identity
Session
SystemInstance
Integration
IntegrationCredential
```

Define the relationships between them.

### Stage 2 — Local Authentication

Complete an independent Local Authentication flow:

```text
Local Authentication
↓
LocalIdentity
↓
User
↓
Session
```

Verify the complete flow:

```text
Register
→ LocalIdentity
→ User
```

```text
Login
→ LocalIdentity
→ User
→ Session
→ tokens
```

### Stage 3 — Google Authentication

Complete an independent Google Authentication flow:

```text
Google OAuth
↓
GoogleIdentity
↓
User
↓
Session
↓
tokens
```

Google Authentication contains only what is necessary for user Google login.

### Stage 4 — Authentication Cleanup

After completing Local + Google Authentication, remove from this part of the project everything related to:

- Google API Integration
- Contacts
- Gmail
- Maps
- service accounts
- Integration credentials

Authentication must remain completely independent from Integration.

### Stage 5 — Session Management

Establish one unified mechanism:

```text
Local Authentication ──┐
                       ├──→ Session
Google Authentication ─┘
```

An Authentication provider must not create its own session type.

### Stage 6 — Identity Linking

Implement a separate mechanism:

```text
Authenticated User
↓
Identity Linking
↓
Authenticate new Identity
↓
Verification
↓
Identity → existing User
```

The main purpose is to controllably add an Identity to an existing User.

There is no automatic linking based on matching data.

### Stage 7 — SystemInstance

Create:

```text
SystemInstance
```

as the entity representing a specific installed/deployed system.

Support creation of the instance before deployment.

### Stage 8 — Integration

Create the common lifecycle:

```text
SystemInstance
↓
Integration
↓
IntegrationCredential
↓
External Provider
```

Integration does not depend on User Authentication.

### Stage 9 — Google Integration

Implement Google as the first concrete Integration:

```text
SystemInstance
↓
Google Integration
↓
IntegrationCredential
↓
Google API
```

Move Contacts functionality and other Google API functionality here.

Google Authentication remains a separate system:

```text
User
↓
GoogleIdentity
↓
Google Authentication
```

### Stage 10 — Additional Providers

After the common model is stable, add new providers:

**Authentication:**

```text
Local
Google
Microsoft
...
```

**Integration:**

```text
Google
Microsoft
...
```

Provider-specific code remains inside the corresponding provider.

---

## 8. Final Architecture

```text
                         APPLICATION
                              │
                ┌─────────────┴─────────────┐
                │                           │
           USER DOMAIN                 SYSTEM DOMAIN
                │                           │
                │                      SystemInstance
                │                           │
          ┌─────┴─────┐                Integration
          │           │                     │
       Identity    Identity          IntegrationCredential
          │           │                     │
          │           │              External Services
          │           │
    Authentication  Authentication
          │           │
        Local       Google
          │           │
          └─────┬─────┘
                │
               User
                │
             Session
```

## Key Architectural Rule

**User Authentication** is responsible for providing a human user with access to a User.

**Integration** is responsible for providing a SystemInstance with access to external services.

These two mechanisms:

- do not share credentials;
- do not mix responsibilities;
- do not depend on each other;
- use separate credential models.

This is the target architecture and should be treated as the **Architectural Contract of the Project**.
