# AGENTS.md

# Project Environment

This project runs in the following environment:

- Operating System: Windows 11
- Terminal: Windows PowerShell
- Language: Python
- Framework: FastAPI
- ORM: SQLModel / SQLAlchemy
- Validation: Pydantic
- API style: REST

Always assume Windows PowerShell environment.

Do not assume:
- Linux
- Unix
- Bash
- macOS
- WSL
- Git Bash

---

# Terminal Command Rules

## IMPORTANT

All terminal commands must be valid Windows PowerShell commands.

Commands must be ready to copy and paste directly into PowerShell.

Never generate:

- Unix syntax
- Bash syntax
- Linux paths
- macOS commands
- CMD-specific syntax

---

# Forbidden Shell Commands

Never use:

```
ls
ls -la
cat
grep
find
pwd
touch
rm
cp
mv
chmod
sudo
apt
bash
sh
```

Use PowerShell equivalents:

```
Get-ChildItem
Get-Content
Select-String
Get-Location
New-Item
Remove-Item
Copy-Item
Move-Item
```

---

# Command Execution Rules

Never chain commands.

Do not use:

```
command1 && command2
command1 ; command2
```

Run commands separately.

Wrong:

```powershell
cd C:\Projects\FastApi\auth\auth-prj && python -m pytest
```

Correct:

```powershell
cd C:\Projects\FastApi\auth\auth-prj

python -m pytest
```

---

# Path Rules

Always use Windows paths.

Correct:

```
C:\Projects\FastApi\auth\auth-prj
```

Wrong:

```
/Projects/FastApi/auth/auth-prj
```

Never replace Windows path separators:

```
\
```

with:

```
/
```

Never generate Unix-style absolute paths.

Never invent paths.

Before executing commands:
- verify current project location
- verify existing folders
- use real project paths only

---

# Project Structure

Follow this architecture:

```
app/
    routers/
    services/
    schemas/
    models/
    dependencies/
    core/

tests/
```

---

# File Inspection Rules

Before modifying code:

1. Read the complete file.
2. Understand imports.
3. Find all usages of classes, functions and modules.
4. Check related files.
5. Check affected tests.
6. Update all required imports.

Do not modify isolated files when changes affect other modules.

---

# Refactoring Rules

When moving or renaming code:

Always check:

- imports
- routers
- services
- schemas
- models
- dependencies
- tests
- __init__.py exports

Never leave:

- broken imports
- unused imports
- duplicate classes
- duplicate functions
- circular imports

After refactoring:

Verify project consistency.

---

# FastAPI Architecture Rules

Follow separation of responsibilities.

## Routers

Routers contain only:

- HTTP endpoints
- request handling
- response formatting
- dependency injection

Business logic does not belong in routers.

---

## Services

Services contain:

- business logic
- authentication logic
- authorization logic
- database operations

---

## Schemas

Schemas contain:

- request models
- response models
- validation rules

Do not mix schemas with database models.

---

## Dependencies

Dependencies contain:

- database sessions
- authentication dependencies
- authorization dependencies

Use:

```python
Depends()
```

Do not create sessions manually inside route handlers.

Correct:

```python
def route(
    session: Session = Depends(get_session)
):
    return service_function(session)
```

Incorrect:

```python
session = create_session()
```

---

# Authentication / Authorization

For authentication changes check all related components:

- token creation
- token validation
- current user dependency
- permissions
- roles
- RBAC checks
- logout logic

Do not mix:

- authentication
- authorization
- user management

into one module.

---

# Python Rules

Use:

```powershell
python -m pytest
```

instead of:

```powershell
pytest
```

Use:

```powershell
python -m pip install
```

instead of:

```powershell
pip install
```

Before adding dependencies:

Check existing project dependencies first.

---

# Testing Rules

Tests are allowed and encouraged.

Permanent tests must:

- be located only inside `tests/`
- test real backend functionality
- follow existing test structure
- be maintained as part of the project

Create tests when:

- implementing new functionality
- fixing bugs
- increasing backend coverage
- verifying important behavior

---

# Temporary Test Rules

Do not create temporary debugging tests.

Forbidden examples:

```
test_debug.py
test_temp.py
test_check.py
debug_test.py
temporary_test.py
```

Do not create tests only to verify your own intermediate changes.

If a temporary test or script is created:

1. Use it only for investigation.
2. Run it.
3. Remove it before finishing the task.

---

# Test Quality Rules

Tests inside `tests/` must be:

- meaningful
- maintainable
- related to backend functionality
- written according to existing project testing style

Do not create trivial tests only to increase the number of tests.

Prefer tests that verify:

- API behavior
- authentication
- authorization
- database operations
- validation
- error handling
- integration between components

---

# Temporary Files Cleanup

Before completing any task:

Run:

```powershell
git status
```

Review created files.

Remove:

- debug scripts
- temporary tests
- generated files
- temporary logs
- experimental files
- unused files

Do not remove:

- existing project files
- permanent tests
- intentionally added files

The final repository state must contain only intentional changes.

---

# Test Execution

Before running tests:

Check:

- project configuration
- dependencies
- test structure

Use:

```powershell
python -m pytest
```

Do not create temporary test files for simple verification.

---

# Code Style

Follow existing project style.

Do not introduce:

- unnecessary abstractions
- unnecessary classes
- premature optimization

Prefer:

- clear names
- simple structure
- explicit code
- maintainable architecture

---

# Before Finishing Any Task

Before saying the task is complete:

1. Review all changed files.
2. Check imports.
3. Check references.
4. Check circular imports.
5. Check syntax errors.
6. Run relevant tests.
7. Run:

```powershell
git status
```

8. Remove temporary artifacts.

Report:

- files changed
- files added
- files removed
- tests executed
- verification result

Do not claim completion if code was not verified.

---

# Communication Rules

When proposing changes:

First explain:

- what files will change
- why they change
- what dependencies are affected

Then modify files.

For large refactoring:

Work in small logical groups.

Do not rewrite the whole project without confirmation.