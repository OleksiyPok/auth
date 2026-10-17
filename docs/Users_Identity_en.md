# Architecture of Accounts, Identities, and Authentication

## 1. Core Model

The system contains the following entities:

- **User** — a user account in the application and the owner of the user data associated with it.
- **Identity** — an identifier of a subject in an external or local system that can be used for authentication.
- **Contact** — a user's contact data that by itself does not grant sign-in rights.
- **Session** — the state of active access created after successful authentication.

These entities have different responsibilities and are not interchangeable.

A single **User** may have multiple **Identity** of different types, such as EmailIdentity, UsernameIdentity, and GoogleIdentity, as well as multiple Contacts.

The mere presence of an **Identity** does not mean that the corresponding sign-in method is enabled or available. This is determined by the application's authentication rules.

## 2. Model Invariants

### 2.1. Identity Ownership

Each **Identity** belongs to exactly one **User**.

- An **Identity** cannot simultaneously belong to multiple **Users**.
- An **Identity** cannot exist without an associated **User**.
- Each **User** must have at least one **Identity**.
- A single **User** may have at most one **Identity** of each type.
- The identifier of a particular **Identity** type must be globally unique within that type.

### 2.2. Independence of Contact and Identity

**Contact** and **Identity** are different entities.

The presence of an email or phone number in a **User**'s contact data does not automatically create the corresponding **Identity**.

For example, an email obtained from a GoogleIdentity does not become an EmailIdentity without a separately defined process and the necessary verification.

Deleting an **Identity** must not automatically delete separately stored Contacts.

### 2.3. Preserving Integrity

Any operation on a **User** or **Identity** must preserve all model invariants.

An operation must not leave a **User** without an **Identity**, create multiple **Identity** of the same type for a single **User**, or violate the global uniqueness of identifiers.

## 3. Operations on Identity and User

The **Link** and **Unlink** operations relate exclusively to **Identity**.

The **Merge** and **Split** operations relate exclusively to **User**.

These operations have different purposes and must not substitute for one another.

| Operation  | Object of operation | Purpose                                                                                     |
|------------|---------------------|---------------------------------------------------------------------------------------------|
| **Link**   | **Identity**        | Link a new **Identity** to an existing **User**                                             |
| **Unlink** | **Identity**        | Remove a specific **Identity** from a **User** and delete its authentication data           |
| **Merge**  | **User**            | Merge multiple **Users** into one                                                           |
| **Split**  | **User**            | Split one **User** into multiple, distributing the existing **Identity** among them          |

## 4. Link

**Link** is the operation of linking a new **Identity** to an existing **User**.

<img src="./images/Account Operations_Link.png" alt="Link operation" width="400">

The operation is performed after verifying ownership of the corresponding **Identity**.

Rules:

1. If the corresponding **Identity** does not yet exist, it is created and linked to the target **User**.
2. If the **Identity** already belongs to the target **User**, re-linking is not performed.
3. If the **Identity** belongs to another **User**, the **Link** operation is not performed. **Merge** is used for consolidation.

**Link** does not merge different **Identity**, does not merge **Users**, and does not transfer contact data automatically.

The presence of data within one **Identity** does not automatically create other **Identity**.

## 5. Unlink

**Unlink** is the operation of removing a specific **Identity** from a **User**.

<img src="./images/Account Operations_Unlink.png" alt="Unlink operation" width="400">

On successful execution:

- the selected **Identity** is removed from the system;
- the authentication data associated with it is deleted;
- other **Identity** of the same **User** continue to exist;
- separately stored Contacts are not deleted automatically.

**Unlink** does not create a new **User** and does not transfer an **Identity** to another **User**.

### Constraint

If the selected **Identity** is the last one for the **User**, the **Unlink** operation is rejected.

This is necessary because a **User** cannot exist without at least one **Identity**.

If an **Identity** needs to be preserved but transferred to another **User**, **Split** should be considered rather than **Unlink**.

## 6. Merge

**Merge** is the operation of merging two or more **Users** into one target **User**.

<img src="./images/Account Operations_Merge.png" alt="Merge operation" width="400">

As a result of a successful **Merge**:

1. All **Identity** of the source **Users** are transferred to the target **User**.
2. Associated user data is handled according to the rules of the relevant domain.
3. The source **Users** are removed from the active **Users** after all **Identity** have been successfully transferred.
4. The target **User** retains its identifier.
5. The **Identity** themselves and their authentication data remain independent entities.

### 6.1. Merge Constraints

**Merge** is permitted only when the result satisfies all model invariants.

In particular:

- the target **User** must not end up with multiple **Identity** of the same type;
- global uniqueness of identifiers must be preserved;
- no source **User** must be left without an **Identity** during an incomplete operation;
- data associated with the source **Users** must not be lost without an explicitly defined handling rule.

If the target and source **Users** already have **Identity** of the same type, **Merge** is blocked until the conflict is explicitly resolved.

The system must not automatically merge such **Identity**, delete one of them, or transfer authentication data between them.

### 6.2. Independence of Identity After Merge

**Merge** changes the ownership of **Identity** with respect to **User**, but does not merge the **Identity** themselves.

For example, if one **User** has an EmailIdentity with a password and another **User** has a GoogleIdentity, after **Merge** both **Identity** belong to the target **User** but continue to use independent authentication mechanisms.

The password remains associated with the EmailIdentity, and OAuth/OIDC authentication remains associated with the GoogleIdentity.

## 7. Split

**Split** is the operation of splitting one **User** into two or more **Users** by transferring selected **Identity** to new **Users**.

<img src="./images/Account Operations_Split.png" alt="Split operation" width="400">

Unlike **Unlink**, the **Split** operation does not delete the selected **Identity**.

On a successful **Split**:

1. A new **User** is created with a new identifier.
2. The selected **Identity** are transferred from the source **User** to the new **User**.
3. **Identity** not selected for transfer remain with the source **User**.
4. The source and new **Users** must each have at least one **Identity**.
5. The constraint of at most one **Identity** of each type per **User** must be preserved.

**Split** is performed only for explicitly selected **Identity**. The system must not select them on its own based on matching email, name, phone number, or other attributes.

### Example

Before **Split**:

```
User A
├── EmailIdentity
├── UsernameIdentity
└── GoogleIdentity
```

After **Split**:

```
User A
├── EmailIdentity
└── UsernameIdentity

User B
└── GoogleIdentity
```

The GoogleIdentity continues to exist but now belongs to **User B**.

**Split** must not be performed as a side effect of **Unlink**.

## 8. Authentication and Credentials

Authentication is responsible for verifying ownership of a specific **Identity** and creating a **Session** after successful authentication.

Each **Identity** is an independent means of identification and may have its own authentication mechanism and its own credentials.

For example:

- the password of an EmailIdentity belongs to the EmailIdentity;
- the password of a UsernameIdentity belongs to the UsernameIdentity;
- OAuth/OIDC authentication belongs to the GoogleIdentity.

Multiple **Identity** belonging to the same **User** are not required to use the same credentials.

The **Link**, **Unlink**, **Merge**, and **Split** operations must not automatically merge or transfer credentials between different **Identity**.

Changing credentials does not change the ownership of an **Identity** with respect to a **User** unless a corresponding model operation is performed separately.

## 9. Session and Operations on User

A **Session** is created after successful authentication and is associated with the **User** and the **Identity** through which authentication was performed.

Conceptually:

```
Session
├── user_id
└── identity_id
```

After **Merge** or **Split**, the ownership of an **Identity** with respect to a **User** may change. Therefore, the system must ensure that **Session** are consistent with the current model.

For each active **Session**, one of the following conditions must hold:

- user_id corresponds to the current owner of the **Identity** specified in identity_id;
- the **Session** is revoked.

When an **Identity** is deleted, its associated sessions must be terminated or revoked. **Session** of other **Identity** must not be automatically terminated without a corresponding rule.

**Session** and tokens are not part of the **User** or **Identity** entity and are managed by separate authentication logic.

## 10. Final Rules

1. **User** is the account and the owner of user data.
2. An **Identity** belongs to exactly one **User**. Each **User** must have at least one **Identity** and at most one **Identity** of each type.
3. **Contact** is a separate entity. **Contact** data does not automatically become an **Identity**.
4. **Link** links a new **Identity** to an existing **User**. If the **Identity** belongs to another **User**, **Merge** is applied.
5. **Unlink** removes a specific **Identity** from a **User** along with its authentication data. The last **Identity** cannot be removed.
6. **Merge** consolidates **Users** by transferring their **Identity** to the target **User**. **Identity** type conflicts must be resolved explicitly.
7. **Split** separates a **User** by transferring selected **Identity** to new **Users**. Each resulting **User** must have at least one **Identity**.
8. Authentication verifies ownership of an **Identity**, and a **Session** records the result of successful authentication.
9. **Merge** and **Split** do not merge the **Identity** themselves or their credentials.
10. All operations must preserve the integrity of the model and the consistency of **Session** with the current ownership of **Identity**.

## 11. Possible Extensions

The rules in sections 1–10 are fixed for the current version of the model. The extensions below are not part of it and are recorded only as a direction for future development.

### 11.1. Per-Type Limit on Identity

Instead of a single rule of "at most one **Identity** of each type per **User**", the maximum number of **Identity** may be defined separately for each type:

| Identity type                            | Maximum per **User** | Comment                                                                                                                             |
|------------------------------------------|----------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| External providers (e.g. GoogleIdentity) | several              | For example, a work and a personal Google account. They have no credentials of their own, so they add no complexity.                |
| UsernameIdentity                         | one                  | Several local logins with different passwords complicate credential management.                                                     |
| EmailIdentity                            | one                  | Additional addresses remain **Contact**. Several confirmed addresses may be introduced later as a separate feature.                 |

Consequences of this extension:

- **Merge** conflicts (6.1) would remain only for types with a limit of one. For external providers such conflicts disappear.
- The wording of rules 2.1, 2.3, 7.5 and 10.2 would change from "at most one **Identity** of each type" to "at most the number of **Identity** allowed for the type".
- Global uniqueness of an identifier within its type and the requirement that a **User** has at least one **Identity** remain unchanged.
- Credentials still belong to a specific **Identity** (section 8). Several EmailIdentity per **User** would require a separate decision, because a password would then more naturally belong to the **User** than to each address.