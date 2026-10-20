# AGENTS.md

Instructions for AI coding agents working in this repository.

## Project

- Stack: Python, FastAPI, SQLModel / SQLAlchemy (async), Pydantic, REST.
- Developer environment: Windows 11, Windows PowerShell.
- Identity model specification: `docs/Users_Identity_en.md` and `docs/Users_Identity_ru.md`.
  Both versions must stay symmetric. The spec is a working hypothesis, not a law: decisions may be revisited when there are good arguments.
- Backlog of planned work: `todo_en.md`.

---

## Terminal and environment rules

Always assume Windows PowerShell. Do not assume Linux, macOS, WSL, Bash or Git Bash.

All commands must be valid PowerShell, ready to copy and paste.

- Never chain commands (`&&`, `;`). Run them separately.
- Use Windows paths with `\`. Never invent paths; verify real ones first.
- Use PowerShell commands, not Unix ones: `Get-ChildItem`, `Get-Content`, `Select-String`, `Get-Location`, `New-Item`, `Remove-Item`, `Copy-Item`, `Move-Item`.
- Never use `ls`, `cat`, `grep`, `find`, `pwd`, `touch`, `rm`, `cp`, `mv`, `chmod`, `sudo`, `apt`, `bash`, `sh`.
- Use `python -m pytest` and `python -m pip install`, not `pytest` / `pip install`.
- Check existing dependencies before adding a new one.

---

## Project structure

One folder per feature inside `app/`:

```
app/
    users/  auth/  sessions/  username_auth/  email_auth/  google_auth/  two_factor/
    identities/         service over the three identity repositories (no models, no router)
    infrastructure/     external integrations: email, google, jwt, password
    core/               settings, base exceptions, exception handlers
    db/                 engine, session, custom column types
    bootstrap/          initial data (superadmin)
    router.py           collects all feature routers
    main.py             application entry point
tests/
scripts/
docs/
```

A feature folder normally contains:

```
models.py            database models
schemas.py           request / response models
exceptions.py        feature exceptions
dependencies.py      dependency wiring (Depends)
router.py            HTTP endpoints
repository/
    repository.py
    repository_interface.py
services/
    service.py                (or several, e.g. login_service.py, register_service.py)
    service_interface.py      (one interface per service)
```

`auth/` additionally contains `rbac/` (roles and permissions) and token / session-issuing services.
Follow this layout for new features. Do not introduce new top-level layers.

---

## Layer rules

- **Routers**: HTTP endpoints, request handling, response formatting, dependency injection. No business logic.
- **Services**: business logic, authentication and authorization logic. Depend on repository and service interfaces, never on concrete classes.
- **Repositories**: database access only, behind an abstract interface. They use `flush`, not `commit`.
- **Schemas**: request and response models and validation. Never mix them with database models.
- **Models**: database tables only.
- **Dependencies** (`dependencies.py`): build repositories and services from `Depends(get_session)` and other dependencies, including current-user and permission checks. Never create sessions manually in route handlers.
- **Exceptions**: each feature has a base exception derived from `AppError` (`app/core/exceptions.py`) with `status_code`, `code` and `message`. Services raise them; a global handler turns them into responses.
- **Infrastructure**: wrappers around external systems. No business logic.
- Do not mix authentication, authorization and user management in one module.
- When authentication changes, check all related parts: token creation and validation, current-user dependency, permissions and roles, session revocation, logout.

---

## Database and transactions

- `get_session` runs one transaction per request: commit at the end, rollback on any exception.
- Consequence: any write made before an error is raised is rolled back. Data that must survive an error (for example failed-code attempt counters) needs its own short transaction, as in the `increment_*_attempts` repository methods. Explain such cases with a short comment.
- Models are registered by being imported; tables are created by `create_all` on startup. There is no Alembic yet, so the schema may be changed directly in models while the database is disposable.
- The default database is SQLite. Row-level locks (`with_for_update`) have no effect on SQLite; real concurrency protection needs PostgreSQL.

---

## Identity rules (from the spec)

- There is one identity of each type (email, username, Google) per user.
- A session stores the identity it was created through (`identity_id` + `identity_type`, no foreign key). `authenticate` and `refresh` check that this identity still exists and belongs to the session's user (`IdentityService.get_owner_id`), so sessions of an unlinked, merged or split identity stop working even if they were not revoked.
- An identity is created only after ownership of its identifier is verified. A pending registration is not an identity.
- A match of email or other attributes never links identities or merges users automatically. Consolidation requires Link from an authenticated session, or an explicit Merge.
- Email identifiers are normalized with `strip()` + `casefold()`.
- Terminology: say "email match", not "collision": the same email in identities of different types, looked up among identities only; it is allowed and links nothing. "Conflict" means the same identifier in identities of the same type; such an identity is never created. "Type conflict" means both users of a Merge have an identity of the same type; it blocks Merge.
- A `Contact` entity does not exist yet. When it appears, it holds unverified data and is never used for login or linking.

---

## Working rules

Before modifying code:

1. Read the complete file.
2. Understand its imports.
3. Find all usages of the classes and functions you change.
4. Check related files and affected tests.
5. Update all required imports.

When moving or renaming code, check imports, routers, services, schemas, models, dependencies, tests and `__init__.py` exports. Never leave broken or unused imports, duplicate code, or circular imports.

Code style: follow the existing project style. Prefer clear names, simple structure and explicit code. Do not introduce unnecessary abstractions, classes or premature optimization.

Do not modify isolated files when a change affects other modules. For large refactoring, work in small logical groups and do not rewrite the project without confirmation.

When proposing changes, first state which files change, why, and which dependencies are affected. Then make the changes.

---

## Security rules

- Never log or return secrets, password hashes or verification codes. Store codes only as hashes.
- Verification codes must have an expiry and a limited number of attempts.
- Every protected endpoint needs an authentication dependency and, where relevant, a permission check.
- Do not weaken existing checks (identity ownership, role changes, last-superadmin protection) to make a task easier.

---

## Git

- Do not commit, push, or create branches unless explicitly asked.
- If asked to hand over changes without committing, provide file contents or precise edits (file, what to replace, where to add).
- Before finishing, run `git status`, review the changed files, and remove temporary files.

---

## Testing

- Tests are out of scope for now. Do not write, fix or run tests unless the task explicitly asks for it. Section 2 of `todo_en.md` is not worked on unless requested.
- A task is verified by reading the code and the related files, not by running tests.
- Permanent tests live only in `tests/`, run with `python -m pytest`, and test real backend behavior: API, authentication, authorization, database operations, validation, errors.
- Existing tests may lag behind the models. Update them when you touch related code.
- Do not create temporary or debugging tests. If a temporary script is unavoidable, use it for investigation and delete it afterwards.
- Do not write trivial tests only to increase the count.

---

## Before finishing any task

1. Review all changed files.
2. Check imports, references, circular imports and syntax.

[//]: # (3. Run relevant tests &#40;`python -m pytest`&#41;.&#41;)
3. Verify by code review; do not run tests unless asked.
4. Run `git status` and remove temporary artifacts.
5. Report: files changed, added and removed; tests executed; verification result.

Do not claim completion if the code was not verified. If something could not be run, say so explicitly.
