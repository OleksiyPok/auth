# TODO / Backlog

A living backlog for the auth service. Tick `[x]` when an item is done.
Each item says why it exists (**Why**) and what to do (**Do**).
Order inside a section is roughly by priority and dependency.

The identity model is described in `docs/Users_Identity_en.md` (and `_ru.md`, kept symmetric).
Terminology: "email match" (not "collision"); "conflict" means two identities of the same type during Merge.

---

## 1. Housekeeping

- [x] **Fix `requirements.txt`**
  - **Why:** an invalid package line breaks `pip install -r`.
  - **Do:** keep only valid, actually needed packages.

- [ ] **Keep both spec versions symmetric**
  - **Why:** `Users_Identity_en.md` and `Users_Identity_ru.md` must say the same thing.
  - **Do:** after any spec change, update both and compare section numbers.

- [ ] **Bring tests back**
  - **Why:** `tests/conftest.py` uses outdated model fields (`User(email=...)`, `UsernameIdentity(login=...)`); new code has no tests.
  - **Do:** update fixtures to the current models, then add API tests for registration, login, 2FA and (later) identity operations. Note: repository methods that open their own session (`session_factory`) bypass a test-overridden `get_session`; the test setup must account for that.

- [ ] **Introduce Alembic migrations**
  - **Why:** schema is currently changed directly in models (`create_all`), which is only safe while the database is disposable.
  - **Do:** add Alembic, generate the baseline migration, stop relying on `create_all` outside development.

- [ ] **Clean up expired temporary rows**
  - **Why:** expired email registrations, OAuth states and 2FA challenges stay in their tables forever.
  - **Do:** add a periodic cleanup (scheduled job or on-write cleanup) that deletes expired and used rows.

---

## 2. Email verification and Google

- [x] **Confirm email before creating `EmailIdentity`**
  - **Why:** an identity must exist only after ownership of its identifier is verified (spec 4.1).
  - **Do:** pending registration table + `register` / `register/confirm` endpoints.

- [x] **Check `email_verified` in Google login**
  - **Why:** an unverified Google email must not be trusted.
  - **Do:** read the flag from the ID token and reject login when it is false.

- [x] **Make failed-code attempts survive request rollback**
  - **Why:** `get_session` runs a request in one transaction; raising an error rolled back the attempt counter, so codes could be guessed without limit.
  - **Do:** increment attempts in a separate short transaction (done for registration and 2FA).

- [ ] **Resend verification code**
  - **Why:** the user may not receive or may lose the email.
  - **Do:** add an endpoint that issues a new code for an existing pending registration with a cooldown; consider the same for 2FA.

- [ ] **Rate limiting**
  - **Why:** registration, login and code confirmation can be abused (email spam, password and code guessing).
  - **Do:** limit by IP and by email on `register`, `login`, `confirm` endpoints.

- [ ] **Optional: verification link in the email**
  - **Why:** lets the user confirm from another device or after closing the page.
  - **Do:** include `registration_id` in a link to the client page; the code is still entered by the user.

---

## 3. Foundation for identity operations

- [ ] **`IdentityService`**
  - **Why:** Link, Unlink, Split and Merge all need the same basic actions on identities of all three types.
  - **Do:** small service on top of the three existing repositories: list identities of a user, delete one, change its owner. Add repository methods: `delete`, Google `get_by_user_id`, change `user_id`. No unified `identities` table, no adapters.

- [ ] **Single place for identifier normalization**
  - **Why:** email is normalized (`strip` + `casefold`) in several services; username is not normalized at all.
  - **Do:** one helper per identifier type, used everywhere; decide the username policy.

- [ ] **`UserRepository.get_for_update`**
  - **Why:** Link/Merge/Split must not race with each other.
  - **Do:** `SELECT ... FOR UPDATE` on users. SQLite does not lock rows; real protection needs PostgreSQL.

- [ ] **Permissions for Merge and Split**
  - **Why:** these operations affect other accounts.
  - **Do:** add two permissions (merge, split) for administrators. Link and Unlink only need `self.*`.

- [ ] **Decide open policy questions**
  - **Why:** the operations below depend on them.
  - **Do:** decide and record in the spec:
    - 2FA policy: block Unlink/Split of the last email identity while 2FA is on, or disable 2FA automatically.
    - Who authorizes Merge: an administrator or the owner of both accounts.
    - Where a new user in Split gets name and role (default role, never elevated).

---

## 4. Identity operations (by increasing complexity)

- [ ] **Unlink**
  - **Why:** the user must be able to remove a login method.
  - **Do:** refuse to remove the last identity; delete it; revoke sessions created through it; do not remove the last email identity while 2FA is enabled (per the policy above).

- [ ] **Link**
  - **Why:** explicit, authenticated linking is the only way identities are combined (spec rule 12).
  - **Do:** username and email first (prove ownership of the new identifier), then Google (add `purpose` and `user_id` to `GoogleOAuthState`). Never link by email match alone.

- [ ] **Split**
  - **Why:** separate selected identities into a new user.
  - **Do:** create the new user, move chosen identities, revoke sessions of moved identities, refuse if it would leave the original user without identities or remove the last active superadmin.

- [ ] **Merge**
  - **Why:** combine two users into one.
  - **Do:** check identity type conflicts (spec 6.1), move identities, revoke sessions, delete the source user with its sessions, 2FA settings and challenges, all in one transaction. Decide the contact transfer rule first if `Contact` exists by then.

---

## 5. Sessions and 2FA hardening

- [ ] **Verify identity ownership on authenticate**
  - **Why:** `Session.identity_id` has no foreign key and `authenticate` does not check that the identity belongs to the session's user.
  - **Do:** check ownership when authenticating a token (the key cannot be a single FK across three tables, so check in code).

- [ ] **Fix `deactivate_user_sessions`**
  - **Why:** it does not filter by `is_active` and overwrites `revoked_at` of already revoked sessions.
  - **Do:** update only active sessions.

- [ ] **Cover username and Google logins with 2FA**
  - **Why:** 2FA is enabled only through the email identity, and username and Google logins skip it.
  - **Do:** decide the rule (2FA is per user, so it should apply to every login method) and apply it to all login flows.

---

## 6. Later / ideas

- [ ] **Pending link on Google login with a matching email**
  - **Why:** a verified Google email may match another user's `EmailIdentity`; spec 4.2 says this must not link anything automatically.
  - **Do:** offer to sign in to the existing account, then run a normal Link. Use only verified emails and only match against identities (not contacts).

- [ ] **Per-type identity limit**
  - **Why:** the current rule is one identity per type per user; the spec (section 11) allows more, for example several Google identities.
  - **Do:** replace the `unique` constraint on `user_id` with a per-type limit and update Link/Merge conflict rules.

- [ ] **`Contact` entity**
  - **Why:** store unverified user information (extra emails, phones) separately from identities.
  - **Do:** contacts are never used for login or linking; define the transfer rule for Merge; Unlink and Split do not touch contacts.
