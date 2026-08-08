# Code Formatting


### Install dependencies
```bash
pip install -r requirements-dev.txt
```

## Code Formatting and Pre-commit Hooks
Enforce consistent code style using **Black** and **isort**. Checks run locally before commit and in CI.

#### One-time setup
- Install development dependencies 

```bash
pip install -r requirements-dev.txt
```

- Install the pre-commit Git hook to automatically format files before committing
```bash
pre-commit install
```

#### Local workflow
- Stage your files before committing
- Commit changes
  - If files are formatted correctly, the commit succeeds
  - If formatting issues exist, pre-commit fixes files automatically and stops the commit
  - Re-stage the fixed files and commit again

#### Manual formatting
- Run pre-commit on all files to format them manually
 ``` bash
pre-commit run --all-files
```

- Ensures consistency with rules defined in pyproject.toml and .pre-commit-config.yaml

#### CI enforcement
- On every push or pull request to dev branch Pre-commit formatting checks are run
- If formatting or tests fail, the workflow fails and the PR cannot be merged

#### Summary
- One-time: install pre-commit and Git hook

- Normal workflow: 
  - stage → commit → pre-commit auto-fixes if needed
- Optional manually: pre-commit on all files
``` bash
pre-commit run --all-files
```

- CI ensures code is formatted correctly before merge
