# TODO / Backlog

A living backlog for the auth service. Tick `[x]` when an item is done.
Each item says why it exists (**Why**) and what to do (**Do**).
Order inside a section is roughly by priority and dependency.

Every item has a permanent ID (`ID-NN`). IDs are never renumbered or reused: a new item takes the next free number, a finished item keeps its own. Refer to items by ID.

The identity model is described in `docs/Users_Identity_en.md` (and `_ru.md`, kept symmetric).
Terminology: "email match" (not "collision"); "conflict" means two identities of the same type during Merge.

Principles for identity operations: Link, Unlink, Split and Merge are personal operations of the user, no admin approval is involved. To the user an identity looks like a sign-in method: they add or remove it.

---

## 1. Housekeeping

- [x] **ID-01 · Fix `requirements.txt`**
  - **Why:** an invalid package line breaks `pip install -r`.
  - **Do:** keep only valid, actually needed packages.

- [ ] **ID-02 · Keep both spec versions symmetric**
  - **Why:** `Users_Identity_en.md` and `Users_Identity_ru.md` must say the same thing.
  - **Do:** after any spec change, update both and compare section numbers.

- [ ] **ID-03 · Record the identity-operation decisions in the spec**
  - **Why:** the decisions below must live in the spec, not only in chat history.
  - **Do:** add to both spec versions: Link/Unlink/Split/Merge are personal operations without admin approval; Merge requires proof of ownership of the attached account; Unlink rules; username normalization; Split is optional and creates a user like a regular registration.

- [ ] **ID-04 · Bring tests back**
  - **Why:** `tests/conftest.py` uses outdated model fields (`User(email=...)`, `UsernameIdentity(login=...)`); new code has no tests.
  - **Do:** update fixtures to the current models, then add API tests for registration, login, 2FA and (later) identity operations. Note: repository methods that open their own session (`session_factory`) bypass a test-overridden `get_session`; the test setup must account for that.

- [ ] **ID-05 · Introduce Alembic migrations**
  - **Why:** schema is currently changed directly in models (`create_all`), which is only safe while the database is disposable.
  - **Do:** add Alembic, generate the baseline migration, stop relying on `create_all` outside development.

- [ ] **ID-06 · Clean up expired temporary rows**
  - **Why:** expired email registrations, OAuth states and 2FA challenges stay in their tables forever.
  - **Do:** add a periodic cleanup (scheduled job or on-write cleanup) that deletes expired and used rows.

---

## 2. Email verification and Google

- [x] **ID-07 · Confirm email before creating `EmailIdentity`**
  - **Why:** an identity must exist only after ownership of its identifier is verified (spec 4.1).
  - **Do:** pending registration table + `register` / `register/confirm` endpoints.

- [x] **ID-08 · Check `email_verified` in Google login**
  - **Why:** an unverified Google email must not be trusted.
  - **Do:** read the flag from the ID token and reject login when it is false.

- [x] **ID-09 · Make failed-code attempts survive request rollback**
  - **Why:** `get_session` runs a request in one transaction; raising an error rolled back the attempt counter, so codes could be guessed without limit.
  - **Do:** increment attempts in a separate short transaction (done for registration and 2FA).

- [x] **ID-10 · Resend verification code**
  - **Why:** the user may not receive or may lose the email.
  - **Do:** add an endpoint that issues a new code for an existing pending registration with a cooldown; consider the same for 2FA.

- [ ] **ID-11 · Rate limiting**
  - **Why:** registration, login and code confirmation can be abused (email spam, password and code guessing).
  - **Do:** limit by IP and by email on `register`, `login`, `confirm` endpoints.

- [ ] **ID-12 · Optional: verification link in the email**
  - **Why:** lets the user confirm from another device or after closing the page.
  - **Do:** include `registration_id` in a link to the client page; the code is still entered by the user.

---

## 3. Foundation for identity operations

- [ ] **ID-13 · `IdentityService`**
  - **Why:** Link, Unlink, Split and Merge all need the same basic actions on identities of all three types.
  - **Do:** small service on top of the three existing repositories, already started in ID-20 (`IdentityService.get_owner_id`, `IdentityType`). Add: list identities of a user; delete one together with revoking its sessions; change its owner. Add repository methods `delete` and Google `get_by_user_id`; changing the owner needs no new method (set `user_id`, call `update`). No unified `identities` table, no adapters.

- [ ] **ID-14 · Single place for identifier normalization**
  - **Why:** email is normalized (`strip` + `casefold`) in several services; username is not normalized at all, so `Admin` and `admin` are different names.
  - **Do:** one helper per identifier type, used everywhere. Username policy (decided): `strip()` + `casefold()`, so `Admin`, `   Admin   ` and `adMin` are the same name; the name is stored normalized. Apply it in username registration and login, the superadmin bootstrap and `scripts/seed_dev_users.py`. Allowed characters and inner spaces are a separate validation task.

- [ ] **ID-15 · `UserRepository.get_for_update`**
  - **Why:** Link/Unlink/Merge/Split must not race with each other.
  - **Do:** `SELECT ... FOR UPDATE` on users; when locking two users (Merge), lock them in a fixed order (for example by `id`) to avoid deadlocks. SQLite does not lock rows; real protection needs PostgreSQL.

---

## 4. Identity operations (by increasing complexity)

All of these are personal operations of the signed-in user; `self.*` access is enough, no admin permission.

- [ ] **ID-16 · Unlink**
  - **Why:** the user must be able to remove a sign-in method.
  - **Do:** refuse to remove the last identity; refuse to remove the identity the current session was created through; revoke the other sessions created through the removed identity. If the removed identity is the email one, 2FA is reset (disabled) and the user is warned and must confirm. Until 2FA becomes independent (ID-23), this is the interim rule.

- [ ] **ID-17 · Link**
  - **Why:** explicit, authenticated linking is the only way identities are combined (spec rule 12).
  - **Do:** username and email first (prove ownership of the new identifier), then Google (add `purpose` and `user_id` to `GoogleOAuthState`). Never link by email match alone. Present it to the user as adding a sign-in method.

- [ ] **ID-18 · Merge**
  - **Why:** combine two accounts of the same person into one.
  - **Do:**
    - The user is signed in to the active account and attaches another (source) account.
    - Proof of ownership of the source account: the user signs in to it with its own method (password or Google, with 2FA if enabled); a code to the source's email can be an additional option only if it has an email identity. Consider fresh re-authentication of the active account as well.
    - Both users must be active; refuse to merge an account with itself; refuse if the source is the last active superadmin; the role of the active account is kept, never elevated.
    - Check identity type conflicts (spec 6.1), move identities, revoke sessions, delete the source user with its sessions, 2FA settings and challenges, all in one transaction. Decide the contact transfer rule first if `Contact` exists by then (ID-26).
    - Send a security notification to the emails of both accounts.

- [ ] **ID-19 · Split (optional, may be dropped)**
  - **Why:** separate selected identities into a new user. It is unclear whether this operation is needed at all.
  - **Do:** implement last and decide whether to keep it after ID-16, ID-17 and ID-18. If kept: the new user is created like a regular registration (first and last name entered manually, role `DEFAULT_ROLE`, never elevated), chosen identities are moved to it, sessions of moved identities are revoked, and the operation is refused if the original user would be left without identities.

---

## 5. Sessions and 2FA hardening

- [x] **ID-20 · Verify identity ownership on authenticate**
  - **Why:** `Session.identity_id` has no foreign key and `authenticate` does not check that the identity belongs to the session's user.
  - **Do:** check ownership when authenticating a token (the key cannot be a single FK across three tables, so check in code). Done: `Session.identity_type` tells which table to look in; `IdentityService.get_owner_id` is called from `authenticate` and `refresh`; a missing or foreign identity gives `SessionRevokedError`.

- [x] **ID-21 · Fix `deactivate_user_sessions`**
  - **Why:** it does not filter by `is_active` and overwrites `revoked_at` of already revoked sessions.
  - **Do:** update only active sessions.

- [ ] **ID-22 · Cover username and Google logins with 2FA**
  - **Why:** 2FA is enabled only through the email identity, and username and Google logins skip it.
  - **Do:** decide the rule (2FA is per user, so it should apply to every login method) and apply it to all login flows. Can be done as part of ID-23.

---

## 6. Independent 2FA resource with several methods

- [ ] **ID-23 · Make 2FA independent of identities**
  - **Why:** 2FA is currently tied to the email identity (endpoints `/auth/email/2fa/*`, `identity_id` in `TwoFactorChallenge`, the code goes to the email identity). More verification methods are planned (SMS, authenticator app, WhatsApp message), and deleting an email identity must not break 2FA.
  - **Do:**
    - Add a `TwoFactorMethod` model (`user_id`, type, delivery address or secret, verified flag, default flag). A phone number used for SMS is not an identity and not a `Contact`.
    - Move the API to one resource `/auth/2fa/*`: list methods, add and confirm a method, remove, enable, disable.
    - Add a method reference to `TwoFactorChallenge`; keep `identity_id` and `identity_type` for login challenges (the session is created from them after the code is confirmed); change `request_enable`, `request_disable` and `authenticate_or_challenge` accordingly.
    - Put delivery behind a common sender interface (email, SMS, WhatsApp). Authenticator app (TOTP) verifies a code against a secret instead of sending one; store the secret encrypted.
    - Add recovery codes for the case of a lost device or phone.
    - Call the 2FA check from every login flow (email, username, Google).
    - Remove the interim "reset 2FA on email Unlink" rule from ID-16.

---

## 7. Later / ideas

- [ ] **ID-24 · Pending link on Google login with a matching email**
  - **Why:** a verified Google email may match another user's `EmailIdentity`; spec 4.2 says this must not link anything automatically.
  - **Do:** offer to sign in to the existing account, then run a normal Link (ID-17). Use only verified emails and only match against identities (not contacts).

- [ ] **ID-25 · Per-type identity limit**
  - **Why:** the current rule is one identity per type per user; the spec (section 11) allows more, for example several Google identities.
  - **Do:** replace the `unique` constraint on `user_id` with a per-type limit and update Link/Merge conflict rules.

- [ ] **ID-26 · `Contact` entity**
  - **Why:** store unverified user information (extra emails, phones) separately from identities.
  - **Do:** contacts are never used for login or linking; define the transfer rule for Merge (ID-18); Unlink and Split do not touch contacts.
