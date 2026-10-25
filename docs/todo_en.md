# TODO / Backlog

Backlog for the auth service. Each item is one task with one clear, verifiable result.

## Rules for this document

- One ID = one task = one finished result. If a task can be split into intermediate results, it is split.
- A task is described on its own. It never mentions later tasks. **After** lists only what must exist before the task can be started; `—` means it can be done at any time.
- IDs are permanent: never renumbered, never reused. A new task takes the next free number.
- A finished task stays in the file. The only change is the `✅` mark next to it; its text is not edited.
- Every description is a declarative requirement that stays true at any moment, before and after the task is done. No notes about work that was just done and no temporary or interim rules.
- Tests are postponed until explicitly scheduled. Do not write, fix or run tests while implementing regular tasks. Section 2 (Tests) is deferred and must not be selected as the next task unless explicitly requested.

[//]: # (- Each task is finished only when its **Result** is verifiable and the related tests pass &#40;`python -m pytest`&#41;.)
- `docs/todo_uk.md` mirrors this file: same IDs, same order. The identity spec `docs/Users_Identity_en.md` and `_uk.md` stay symmetric.
- Terminology: "conflict" means the same identifier (for email, the same address) in identities of the same type; such an identity cannot be created, so it cannot exist and Merge never meets it. "Email match" (not "collision") means the same email in identities of different types, looked up among identities only, never among contacts; it is allowed and links nothing. "Type conflict" means both users of a Merge already have an identity of the same type; it blocks Merge.
- Link, Unlink, Split and Merge are personal operations of the signed-in user. No admin approval is involved; `self.*` permissions are enough.
- Terminology: "deactivation" sets a status other than `active` and removes no rows; "purge" is the physical removal of a user and everything that references it. The bare word "delete" is not used for users.
- Every table that references `users.id` is removed by `purge_user`; a task that adds such a table also adds the deletion of its rows to the repository.

---

## 1. Identity spec

Decisions are recorded in both spec versions (`Users_Identity_en.md`, `Users_Identity_uk.md`).

- ⬜ **ID-03 · Spec: identity operations are personal**
  - **Do:** in section 3 state that Link, Unlink, Merge and Split are personal operations of the user and need no admin approval.
  - **Result:** both spec versions contain the statement; section numbers match.
  - **After:** —

- ⬜ **ID-27 · Spec: Unlink rules**
  - **Do:** in section 5 add: the last identity cannot be removed; the identity used by the current session cannot be removed; sessions created through the removed identity are revoked.
  - **Result:** both spec versions contain the rules; section numbers match.
  - **After:** —

- ⬜ **ID-28 · Spec: Merge ownership proof and limits**
  - **Do:** in section 6 add: ownership of the source account is proven by signing in to it with its own method (including its 2FA); both users must be active; a user cannot be merged with itself; the last active superadmin cannot be the source; the role of the target is kept and never elevated.
  - **Result:** both spec versions contain the rules; section numbers match.
  - **After:** —

- ⬜ **ID-29 · Spec: identifier normalization**
  - **Do:** in section 2 add a subsection: email and username are normalized with `strip()` + `casefold()` and stored normalized; allowed characters are out of scope.
  - **Result:** both spec versions contain the subsection; section numbers match.
  - **After:** —

- ✅ **ID-97 · Spec: conflict and email match**
  - **Do:** in section 2.1 state that an identifier already used by an identity of the same type is a conflict: such an identity is never created (registration, Link) and Merge cannot meet one; in section 4.2 state that the same email in identities of different types is an email match, is allowed whenever an identity is created (registration, Link, Merge) and links nothing.
  - **Result:** both spec versions contain the statements; section numbers match.
  - **After:** —

- ✅ **ID-105 · Spec: user status, deactivation and purge**
  - **Do:** record in both spec versions: the user statuses; a deactivated user never becomes active again; Merge sets the source to `deactivated_by_merge`; purge is a separate superadmin operation for non-active users.
  - **Result:** both spec versions contain the statements; section numbers match.
  - **After:** —

---

## 2. Tests

Existing tests use outdated model fields and request schemas.

- ⬜ **ID-04 · Fix `tests/conftest.py` fixtures**
  - **Do:** create users with the current models (`User` without `email`, `UsernameIdentity(username=...)`); store the username normalized.
  - **Result:** `regular_user_token`, `admin_user_token` and `superadmin_user_token` return valid tokens; `GET /api/v1/users/me` with each returns 200.
  - **After:** —

- ⬜ **ID-30 · Tests: repository methods with their own session use the test database**
  - **Do:** make repository methods that open `session_factory` (attempt counters) use the test database during tests.
  - **Result:** an invalid code increments `attempts` in the test database for both email registration and 2FA challenges; a test proves it.
  - **After:** ID-04

- ⬜ **ID-31 · Fix `tests/test_authentication.py`**
  - **Do:** align requests and expectations with the current schemas (registration has no `email`; logout needs a bearer token).
  - **Result:** the file passes.
  - **After:** ID-04

- ⬜ **ID-32 · Fix `tests/test_user_sessions.py`**
  - **Do:** replace `login` with `username` in registration payloads; align expectations with current endpoints.
  - **Result:** the file passes.
  - **After:** ID-04

- ⬜ **ID-33 · Fix `tests/test_user_roles.py`**
  - **Do:** same alignment as for sessions tests; remove `email` from registration payloads.
  - **Result:** the file passes.
  - **After:** ID-04

- ⬜ **ID-34 · Tests: email registration API**
  - **Do:** override `EmailService` with a fake that captures the code; cover register, confirm, wrong code, too many attempts, expired code, already registered email.
  - **Result:** the tests pass and assert status codes and error codes.
  - **After:** ID-04, ID-30

- ⬜ **ID-35 · Tests: two-factor API**
  - **Do:** cover enable, login challenge and confirm, disable, wrong code, too many attempts.
  - **Result:** the tests pass.
  - **After:** ID-04, ID-30

- ⬜ **ID-36 · Tests: Google login callback**
  - **Do:** mock the functions of `app.infrastructure.google.oauth`; cover new user, existing user, unverified email, invalid / used / expired state.
  - **Result:** the tests pass without network access.
  - **After:** ID-04

---

## 3. Dependencies, database and startup

- ✅ **ID-01 · Valid `requirements.txt`**
  - **Do:** keep only valid packages that the project needs.
  - **Result:** `python -m pip install -r requirements.txt` completes without errors.
  - **After:** —

- ⬜ **ID-05 · Add Alembic configuration**
  - **Do:** add Alembic with an async environment reading `DATABASE_URL`, importing all models.
  - **Result:** `python -m alembic current` runs against the configured database.
  - **After:** —

- ⬜ **ID-37 · Baseline migration**
  - **Do:** generate the migration for the current models.
  - **Result:** `python -m alembic upgrade head` creates the full schema on an empty database.
  - **After:** ID-05

- ⬜ **ID-38 · Make `create_all` optional**
  - **Do:** add a setting that controls whether the application calls `SQLModel.metadata.create_all` at startup.
  - **Result:** with the setting off, startup creates no tables.
  - **After:** ID-37

- ✅ **ID-39 · Superadmin bootstrap depends only on the users table**
  - **Do:** create the initial superadmin when the users table is empty, regardless of how tables were created.
  - **Result:** a database with tables and no users gets the superadmin at startup; a database with users does not.
  - **After:** —

- ✅ **ID-108 · Enforce foreign keys on SQLite**
  - **Do:** enable `PRAGMA foreign_keys=ON` on every connection of the application engine when the database is SQLite.
  - **Result:** on SQLite, saving a row with a non-existent `user_id` and deleting a user that still has dependent rows both fail with an integrity error, as on PostgreSQL.
  - **After:** —

---

## 4. Cleanup of temporary rows

- ✅ **ID-06 · Delete expired email registrations**
  - **Do:** add a repository method that deletes expired `EmailRegistration` rows.
  - **Result:** a test shows expired rows are removed and valid ones stay.
  - **After:** —

- ✅ **ID-40 · Delete expired or used OAuth states**
  - **Do:** add a repository method that deletes expired or used `GoogleOAuthState` rows.
  - **Result:** a test shows expired and used rows are removed and valid ones stay.
  - **After:** —

- ✅ **ID-41 · Delete expired or used 2FA challenges**
  - **Do:** add a repository method that deletes expired or used `TwoFactorChallenge` rows.
  - **Result:** a test shows expired and used rows are removed and valid ones stay.
  - **After:** —

- ✅ **ID-42 · Periodic cleanup job**
  - **Do:** run the three cleanup methods from a background task started in the application lifespan, with the interval in settings.
  - **Result:** expired rows disappear without any request; the task stops on shutdown.
  - **After:** ID-06, ID-40, ID-41

---

## 5. Verification codes, Google email and rate limiting

- ✅ **ID-07 · Confirm email before creating `EmailIdentity`**
  - **Do:** pending registration table with `register` and `register/confirm` endpoints.
  - **Result:** `EmailIdentity` exists only after the code is confirmed.
  - **After:** —

- ✅ **ID-08 · Reject unverified Google email**
  - **Do:** read `email_verified` from the ID token.
  - **Result:** Google login is refused when the flag is false.
  - **After:** —

- ✅ **ID-09 · Failed-code attempts survive request rollback**
  - **Do:** increment attempt counters in a separate short transaction (email registration and 2FA).
  - **Result:** the counter keeps its value after the request transaction rolls back, so codes cannot be guessed without limit.
  - **After:** —

- ✅ **ID-10 · Resend email registration code**
  - **Do:** `POST /auth/email/register/resend` with `registration_id`; store the send time; refuse inside the cooldown; issue a new code, new expiry and reset attempts.
  - **Result:** a second request inside the cooldown returns 429; after it a new code works and the old one does not.
  - **After:** —

- ⬜ **ID-43 · Resend 2FA login code**
  - **Do:** `POST /auth/2fa/login/resend` with `challenge_id`; same cooldown rule; the new code replaces the old one.
  - **Result:** a request inside the cooldown returns 429; after it only the new code works.
  - **After:** —

- ⬜ **ID-12 · Verification link in the registration email**
  - **Do:** add a client base URL setting; put a link containing `registration_id` into the email body; the code is still entered by the user.
  - **Result:** the registration email contains the link built from the setting.
  - **After:** —

- ✅ **ID-11 · Rate limiter component**
  - **Do:** add a limiter interface in `infrastructure` with an in-memory implementation: key, limit, window; raises an `AppError` with status 429.
  - **Result:** unit tests show the limit blocks the extra call and resets after the window.
  - **After:** —

- ✅ **ID-44 · Rate limit login endpoints**
  - **Do:** apply the limiter to username login and email login, by IP and by identifier.
  - **Result:** exceeding the limit returns 429 on both endpoints.
  - **After:** ID-11

- ✅ **ID-45 · Rate limit registration endpoints**
  - **Do:** apply the limiter to username register and email register, by IP and by identifier.
  - **Result:** exceeding the limit returns 429 on both endpoints.
  - **After:** ID-11

- ✅ **ID-46 · Rate limit code confirmation endpoints**
  - **Do:** apply the limiter by IP to email registration confirm and 2FA login confirm.
  - **Result:** exceeding the limit returns 429 on both endpoints.
  - **After:** ID-11

---

## 6. Identity service and locking

- ✅ **ID-14 · Identifier normalization helpers**
  - **Do:** one helper per identifier type (`normalize_email`, `normalize_username`: `strip()` + `casefold()`), used by registration, login, superadmin bootstrap and the dev seed script.
  - **Result:** `Admin`, `   Admin   ` and `adMin` resolve to the same username.
  - **After:** —

- ✅ **ID-13 · `IdentityService.list_identities`**
  - **Do:** add the service, its interface and dependency; add `get_by_user_id` to the Google repository; return the user's identities as the existing model objects.
  - **Result:** a test shows identities of all three types are listed for one user.
  - **After:** —

- ✅ **ID-47 · `IdentityService.get_identity`**
  - **Do:** find an identity of any type by its id.
  - **Result:** a test finds username, email and Google identities by id and returns nothing for an unknown id.
  - **After:** ID-13

- ✅ **ID-48 · `IdentityService.delete_identity`**
  - **Do:** add `delete` to the three identity repositories and call the right one by identity type.
  - **Result:** a test shows the identity is gone and other identities of the user remain.
  - **After:** ID-13

- ✅ **ID-49 · `IdentityService.transfer_identity`**
  - **Do:** change the owner of an identity; refuse when the new owner already has an identity of that type.
  - **Result:** a test shows a successful transfer and a refusal on type conflict.
  - **After:** ID-13

- ✅ **ID-15 · `UserRepository.get_for_update`**
  - **Do:** select a user with `FOR UPDATE`.
  - **Result:** the method returns the user; on PostgreSQL the row is locked until the transaction ends (SQLite does not lock rows).
  - **After:** —

- ✅ **ID-50 · Lock two users in a fixed order**
  - **Do:** add a repository method that locks two users ordered by `id`.
  - **Result:** the same pair requested in either order is locked in the same order.
  - **After:** ID-15

---

## 7. Identity endpoints: permissions, list, Unlink

- ✅ **ID-51 · Identity permissions**
  - **Do:** add `SELF_IDENTITIES_READ` and `SELF_IDENTITIES_WRITE` to `Permission`, grant them to every role that has the other `self.*` permissions, add `require_self_identities_read` and `require_self_identities_write`.
  - **Result:** RBAC validation at import passes; the `user` role has both permissions.
  - **After:** —

- ✅ **ID-53 · Current session dependency**
  - **Do:** add a dependency returning the session id and identity id of the current token.
  - **Result:** a test shows the values equal the ones used at login.
  - **After:** —

- ✅ **ID-52 · `GET /identities`**
  - **Do:** return the current user's identities: id, type, a display identifier (username, masked email, none for Google), `created_at`.
  - **Result:** the endpoint returns the user's identities and requires authentication and the read permission.
  - **After:** ID-13, ID-51

- ⬜ **ID-16 · `DELETE /identities/{identity_id}` (Unlink)**
  - **Do:** remove an identity of the current user; refuse an unknown id, another user's id and the last identity; lock the user first.
  - **Result:** a test shows removal of a non-last identity, 404 / 403 for foreign or unknown ids, and refusal for the last one.
  - **After:** ID-47, ID-48, ID-15, ID-51, ID-79

- ⬜ **ID-55 · Unlink refuses the current session's identity**
  - **Do:** reject removal of the identity the current session was created through.
  - **Result:** a test shows the refusal.
  - **After:** ID-16, ID-53

- ⬜ **ID-56 · Unlink revokes sessions of the removed identity**
  - **Do:** revoke active sessions created through the removed identity; sessions of other identities stay active.
  - **Result:** a test shows the removed identity's session cannot be used and another session still works.
  - **After:** ID-16

---

## 8. Link

- ✅ **ID-17 · Link username**
  - **Do:** `POST /identities/username` with username and password; normalize the username; refuse when the user already has a username identity or the name is taken.
  - **Result:** a test shows the username can then be used to sign in; refusals return 409.
  - **After:** ID-51

- ✅ **ID-58 · Link email: request**
  - **Do:** `POST /identities/email` with email and password; store a pending link request (new table, separate from registrations); send a code; refuse when the user already has an email identity or the address is taken.
  - **Result:** the request returns a challenge id and the code is sent; no identity exists yet.
  - **After:** ID-51

- ✅ **ID-59 · Link email: confirm**
  - **Do:** `POST /identities/email/confirm` with the challenge id and code; count failed attempts in a separate transaction; create `EmailIdentity` for the current user and delete the request.
  - **Result:** a test shows a correct code creates the identity and a wrong code does not; attempts are limited.
  - **After:** ID-58

- ✅ **ID-60 · `GoogleOAuthState` purpose and user**
  - **Do:** add `purpose` (default `login`) and nullable `user_id` to the model; the service saves them.
  - **Result:** login states keep working with the default purpose; the fields are stored when set.
  - **After:** —

- ✅ **ID-61 · Link Google: start**
  - **Do:** `POST /identities/google`, authenticated; create a state with purpose `link` and the user id; return the authorization URL.
  - **Result:** a test shows the saved state has the purpose and the user id.
  - **After:** ID-51, ID-60

- ✅ **ID-62 · Link Google: callback**
  - **Do:** for states with purpose `link` create `GoogleIdentity` for the state's user without issuing tokens; refuse when the Google account belongs to another user or the user already has a Google identity.
  - **Result:** a test with mocked Google shows the identity is created for the right user; refusals return errors; login states still behave as before.
  - **After:** ID-60, ID-61

---

## 9. Merge

- ✅ **ID-18 · Identity type conflict detection**
  - **Do:** add `IdentityService` method returning the identity types present on both users.
  - **Result:** a test shows the correct types for overlapping and non-overlapping users.
  - **After:** ID-13

- ✅ **ID-63 · `MergeProof` model and repository**
  - **Do:** model with active user id, source user id, expiry, used flag; repository to create, get, mark used.
  - **Result:** repository test passes.
  - **After:** —

- ✅ **ID-64 · Merge proof by username and password**
  - **Do:** authenticated endpoint accepting the source username and password; create a short-lived single-use proof bound to both users; refuse an inactive source.
  - **Result:** a test shows a proof is created for correct credentials and refused for wrong ones.
  - **After:** ID-63

- ✅ **ID-65 · Merge proof by email and password**
  - **Do:** same as ID-64 using email identity credentials.
  - **Result:** a test shows a proof is created for correct credentials and refused for wrong ones.
  - **After:** ID-63

- ✅ **ID-66 · Merge proof by Google**
  - **Do:** OAuth flow with purpose `merge`; the callback creates a proof bound to the state's user and the Google account's user.
  - **Result:** a test with mocked Google shows the proof is created.
  - **After:** ID-60, ID-63

- ✅ **ID-67 · 2FA step for merge proof**
  - **Do:** when the source user has 2FA enabled, the proof is created only after a confirmed challenge.
  - **Result:** a test shows no proof without the code and a proof with the correct code.
  - **After:** ID-64, ID-65, ID-66

- ✅ **ID-68 · Merge validation**
  - **Do:** service method that raises specific errors when the source or the target is not `active` (the error names the user and its status), source equals target, or the source is the last active superadmin.
  - **Result:** a test per error and one for the valid case.
  - **After:** ID-98

- ✅ **ID-69 · Merge execution**
  - **Do:** in one transaction check type conflicts, transfer the source identities to the target, delete the source's 2FA settings and challenges, deactivate the source with the status `deactivated_by_merge` (its sessions are revoked); the target's role does not change.
  - **Result:** a test shows the target owns all identities, the source has the status `deactivated_by_merge` and no identities, sessions or 2FA rows, a type conflict aborts with nothing changed.
  - **After:** ID-18, ID-49, ID-50, ID-68, ID-99

- ✅ **ID-70 · `POST /users/me/merge`**
  - **Do:** accept a proof id; check it is valid, unused and bound to the current user; mark it used; run the merge.
  - **Result:** a test shows a full merge through the endpoint and refusal for a used, expired or foreign proof.
  - **After:** ID-69, and ID-64 or ID-65 or ID-66

- ✅ **ID-71 · Merge security notification**
  - **Do:** add an email template and send it to the email identities of both accounts after a merge; accounts without an email identity are skipped.
  - **Result:** a test with a fake email service shows the messages sent.
  - **After:** ID-70

---

## 10. Split

- ⬜ **ID-19 · Decide whether Split stays**
  - **Do:** record the decision in both spec versions: keep section 7 and rule 7, or remove them.
  - **Result:** both spec versions reflect the decision.
  - **After:** ID-16, ID-62, ID-70

- ⬜ **ID-72 · Split execution**
  - **Do:** create a new user like a regular registration (names given manually, role `DEFAULT_ROLE`), transfer the selected identities, revoke their sessions; refuse when the original user would be left without identities.
  - **Result:** a test shows the new user owns the selected identities and the original keeps the rest; refusal is tested.
  - **After:** ID-19 (decision: keep), ID-49, ID-50

- ⬜ **ID-73 · Split endpoint**
  - **Do:** `POST /identities/split` with identity ids and names of the new user, protected by `self.*` permissions.
  - **Result:** a test shows the endpoint splits the user.
  - **After:** ID-72, ID-51

---

## 11. Sessions

- ✅ **ID-20 · Check identity ownership when authenticating a token**
  - **Do:** in `TokenService.authenticate` reject a token whose session identity is not owned by the session's user.
  - **Result:** a test shows a token with a foreign identity id is rejected.
  - **After:** ID-47

- ✅ **ID-21 · `deactivate_user_sessions` updates only active sessions**
  - **Do:** add the `is_active` filter to the update.
  - **Result:** a test shows `revoked_at` of an already revoked session does not change.
  - **After:** ID-04

---

## 12. Two-factor: independent of identities

- ✅ **ID-22 · 2FA applies to every login method**
  - **Do:** call the 2FA check in the username, email and Google login flows.
  - **Result:** a user with 2FA enabled gets a challenge instead of tokens on any login method.
  - **After:** —

- ✅ **ID-23 · `TwoFactorMethod` model and repository**
  - **Do:** fields: user id, type, delivery address or secret, verified flag, default flag; repository to create, list, get, delete.
  - **Result:** repository test passes.
  - **After:** —

- ✅ **ID-74 · `method_id` in `TwoFactorChallenge`**
  - **Do:** add a nullable reference to the method; `identity_id` stays as the sign-in identity of a login challenge.
  - **Result:** challenges can be saved with and without a method.
  - **After:** ID-23

- ✅ **ID-75 · 2FA sender interface**
  - **Do:** interface that delivers a code to a method; email implementation on top of `EmailService`.
  - **Result:** a test with a fake email service shows the code is delivered to the method's address.
  - **After:** ID-23

- ✅ **ID-76 · Add email method: request**
  - **Do:** `POST /auth/2fa/methods/email` with an address; create an unverified method and send a code.
  - **Result:** the response contains a challenge id; the method exists as unverified.
  - **After:** ID-23, ID-74, ID-75

- ✅ **ID-77 · Add email method: confirm**
  - **Do:** `POST /auth/2fa/methods/email/confirm`; a correct code marks the method verified.
  - **Result:** a test shows the method becomes verified only with the correct code.
  - **After:** ID-76

- ✅ **ID-78 · Status lists methods from `TwoFactorMethod`**
  - **Do:** `GET /auth/2fa/status` returns the user's verified methods.
  - **Result:** a test shows the list matches stored methods.
  - **After:** ID-23

- ✅ **ID-79 · Deliver codes through the default method**
  - **Do:** login, enable and disable challenges go to the user's default verified method; enabling requires one; the sign-in identity of a login challenge is unchanged; update the affected tests.
  - **Result:** a user without an email identity can enable and use 2FA; removing an email identity does not affect 2FA.
  - **After:** ID-23, ID-74, ID-75, ID-77

- ✅ **ID-80 · Remove a method**
  - **Do:** `DELETE /auth/2fa/methods/{method_id}`; refuse removing the last verified method while 2FA is enabled.
  - **Result:** a test shows removal and the refusal.
  - **After:** ID-23

- ⬜ **ID-81 · Recovery codes: generate**
  - **Do:** model storing hashed one-time codes; endpoint that requires enabled 2FA, replaces existing codes and returns the new codes once.
  - **Result:** a test shows codes are returned once and only hashes are stored.
  - **After:** —

- ⬜ **ID-82 · Recovery codes: use at login**
  - **Do:** 2FA login confirm accepts a recovery code instead of the emailed code and marks it used.
  - **Result:** a test shows a recovery code works once.
  - **After:** ID-81

- ⬜ **ID-83 · Secret encryption helper**
  - **Do:** add encrypt / decrypt functions in `infrastructure` with the key from settings.
  - **Result:** unit test: round trip works, a wrong key fails.
  - **After:** —

- ⬜ **ID-84 · Authenticator app method: enroll**
  - **Do:** endpoint that creates a TOTP method with an encrypted secret and returns the provisioning URI; a confirm endpoint verifies a code and marks the method verified.
  - **Result:** a test shows the method becomes verified with a valid TOTP code.
  - **After:** ID-23, ID-83

- ⬜ **ID-85 · Authenticator app method: verification**
  - **Do:** for a TOTP method, challenges are verified against the secret and nothing is sent.
  - **Result:** a test shows login with 2FA works with a valid TOTP code.
  - **After:** ID-79, ID-84

---

## 13. Access protection

- ✅ **ID-92 · Require authentication on `POST /api/v1/dev/email/send`**
  - **Do:** add the current-user dependency to the endpoint.
  - **Result:** a request without a token returns 401; a request with a valid token reaches the endpoint.
  - **After:** —

- ✅ **ID-93 · Restrict `POST /api/v1/dev/email/send` to superadmin**
  - **Do:** require superadmin access on the endpoint, using the checks from `app/auth/rbac/dependencies.py`.
  - **Result:** a request from `user` or `admin` returns 403; a request from `superadmin` returns 204.
  - **After:** ID-92

---

## 14. Service health

- ✅ **ID-94 · `GET /health`**
  - **Do:** add an endpoint at the application root, outside `API_V1_PREFIX`, without authentication and without database access; it returns `{"status": "ok"}`.
  - **Result:** `GET /health` without a token returns 200 with `{"status": "ok"}`.
  - **After:** —

- ✅ **ID-95 · `GET /health/ready`: database reachable**
  - **Do:** add an endpoint at the application root, outside `API_V1_PREFIX`, without authentication; it runs `SELECT 1` through the application engine and returns `{"status": "ok"}`.
  - **Result:** with the database available, `GET /health/ready` without a token returns 200 with `{"status": "ok"}`.
  - **After:** —

- ✅ **ID-96 · `GET /health/ready`: database unreachable**
  - **Do:** when the database check fails, return 503 with `{"status": "unavailable"}`; the response, logs of the endpoint and headers contain no error details, connection string or credentials.
  - **Result:** with the database stopped or `DATABASE_URL` wrong, `GET /health/ready` returns 503 with `{"status": "unavailable"}` and no other data; `GET /health` still returns 200.
  - **After:** ID-95

---

## 15. User status, deactivation and purge

A user has one status. Deactivation sets a status other than `active` and removes no rows; a deactivated user never becomes active again. Purge is the only operation that physically removes a user.

- ✅ **ID-100 · Deactivation endpoints**
  - **Do:** `POST /users/me/deactivate` and `POST /users/{user_id}/deactivate` deactivate the user and return 204; deactivation through `DELETE` is removed; rename `SELF_DELETE` to `SELF_DEACTIVATE` and `USERS_DELETE` to `USERS_DEACTIVATE` with their `require_*` dependencies, grants per role unchanged.
  - **Result:** each endpoint deactivates its target and requires its permission; `USERS_DEACTIVATE` is held only by `superadmin`; RBAC validation at import passes; no `DELETE` endpoint deactivates a user.
  - **After:** —

- ✅ **ID-98 · `UserStatus` and `User.status`**
  - **Do:** add the enum `UserStatus` (`active`, `deactivated_by_admin`, `deactivated_by_user`, `deactivated_by_merge`) and the field `User.status` in place of `is_active`; keep `is_active` as a read-only property that is true only for `active`; use `status` in queries, bootstrap, the dev seed script and the detailed user response.
  - **Result:** a new user has the status `active`; `count_active_superadmins` counts only active superadmins; the detailed user response returns `status`.
  - **After:** —

- ✅ **ID-99 · `UserService.deactivate_user` with a status**
  - **Do:** take one of the three `deactivated_*` statuses and set it; `POST /users/me/deactivate` passes `deactivated_by_user` and `POST /users/{user_id}/deactivate` passes `deactivated_by_admin`; revoke all active sessions of the user; refuse an already deactivated user and the last active superadmin.
  - **Result:** a deactivated user cannot sign in, refresh or use an issued token; each endpoint stores its own status; a second deactivation is refused.
  - **After:** ID-98, ID-100

- ✅ **ID-101 · Delete the rows of a user in the repositories**
  - **Do:** add `delete_by_user_id` to the repositories of the three identity types, sessions and two-factor (settings and challenges).
  - **Result:** a test shows the rows of the given user are gone and the rows of other users remain.
  - **After:** —

- ✅ **ID-102 · `UserService.purge_user`**
  - **Do:** in one transaction delete every row that references the user, then the user; refuse a user with the status `active`.
  - **Result:** a test shows no row referencing the user remains, other users are untouched, an active user is refused.
  - **After:** ID-98, ID-101

- ✅ **ID-103 · Permission `USERS_PURGE`**
  - **Do:** add `USERS_PURGE` to `Permission`, grant it only to `superadmin`, add `require_users_purge`.
  - **Result:** RBAC validation at import passes; only `superadmin` has the permission.
  - **After:** —

- ✅ **ID-104 · `DELETE /users/{user_id}` (purge)**
  - **Do:** protected by `USERS_PURGE`; the query parameter `confirm_user_id` must equal `user_id`; runs `purge_user`; returns 204.
  - **Result:** a test shows 204 for a deactivated user, 400 for a wrong confirmation, 409 for an active user, 404 for an unknown user, 403 for `user` and `admin`.
  - **After:** ID-100, ID-102, ID-103

---

## 16. Later / ideas

- ⬜ **ID-24 · Email match flag in Google login**
  - **Do:** when a new Google user's verified email matches an `EmailIdentity`, add a flag to the callback response; create no link.
  - **Result:** a test shows the flag is set on a match and unset otherwise.
  - **After:** —

- ⬜ **ID-25 · Spec: per-type identity limit**
  - **Do:** move the per-type limit table from section 12 into the rules in both spec versions, or reject it.
  - **Result:** both spec versions reflect the decision.
  - **After:** —

- ⬜ **ID-89 · Several Google identities per user**
  - **Do:** drop the unique constraint on `GoogleIdentity.user_id`; update Link Google and the Merge conflict check.
  - **Result:** a test shows a user links two Google accounts and Merge reports no Google conflict.
  - **After:** ID-25 (decision: accept), ID-18, ID-62

- ⬜ **ID-26 · `Contact` model and repository**
  - **Do:** store unverified emails and phones per user; never used for login or linking.
  - **Result:** repository test passes.
  - **After:** —

- ⬜ **ID-90 · Merge moves contacts**
  - **Do:** transfer the source user's contacts to the target during Merge.
  - **Result:** a test shows contacts belong to the target after Merge.
  - **After:** ID-26, ID-69

- ✅ **ID-91 · Fresh re-authentication before Merge**
  - **Do:** require the active account to re-authenticate within a time window before `POST /users/me/merge`.
  - **Result:** a test shows Merge is refused without recent re-authentication.
  - **After:** ID-70, ID-106

- ✅ **ID-106 · Fresh session dependency**
  - **Do:** add a dependency that refuses a session created earlier than the configured window (`FRESH_SESSION_MINUTES`) with a dedicated error asking to sign in again.
  - **Result:** a test shows a fresh session passes and an older one is refused.
  - **After:** ID-53

- ✅ **ID-107 · Fresh session before purge**
  - **Do:** require the fresh session on `DELETE /users/{user_id}`.
  - **Result:** a test shows purge is refused with an old session.
  - **After:** ID-104, ID-106

- ⬜ **ID-86 · SMS sender**
  - **Do:** sender implementation for the 2FA sender interface with a provider and a dummy provider that logs messages.
  - **Result:** a test with the dummy provider shows the code is logged.
  - **After:** ID-75

- ⬜ **ID-87 · Add phone method (SMS): request and confirm**
  - **Do:** endpoints that add a phone number as a 2FA method and verify it with a code; the number is not an identity and not a `Contact`.
  - **Result:** a test shows the method becomes verified with the correct code.
  - **After:** ID-23, ID-86

- ⬜ **ID-88 · WhatsApp sender**
  - **Do:** sender implementation for the 2FA sender interface with a provider and a dummy provider.
  - **Result:** a test with the dummy provider shows the code is logged.
  - **After:** ID-75
