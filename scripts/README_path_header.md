# File Path Header Script

## Overview

This script automatically inserts a file path comment at the top of Python files.
The path is written relative to the project root.

Example result:
``` python
# app/services/auth_service.py

import asyncio
import time
```
The script removes existing path-like header comments at the beginning of the file before inserting the updated one.

This keeps file headers consistent across the project.


## Features

- Adds a file path comment as the first line of Python files
- The path is always relative to the project root
- Removes existing path-like comments at the beginning of the file
- Removes leading empty lines before inserting the header
- Safe for repeated execution
- Supports processing a folder or a single file
- Prevents concurrent execution using a lock file
- Skips common directories such as `.venv`, `.git`, and `__pycache__`


## Script Location

Place the script inside the project, for example:

scripts/path_header.py

Run the script from the project root directory.

Example project structure:

```text
project_root/
│
├─ app/
├─ tests/
└─ scripts/
      └─ path_header.py
```

## Basic Usage

Run the script from the project root.

Default behavior processes the `app` directory.
In this case, all matching Python files inside the `app` directory and its subdirectories will be processed.

```bash
  python scripts/path_header.py
```

## Processing a Specific Directory

You can pass a directory path relative to the project root.

Example:

```bash
  python scripts/path_header.py tests
```

```bash
  python scripts/path_header.py tests/integration
```

## Processing a Single File

You can also pass a specific Python file.

Example:
```bash
  python scripts/path_header.py   tests/integration/users/test_users_read.py
````

## Example Transformation

### Adding a header when none exists

Before:
``` python
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
```

After running the script:
```python
# app/models/db_request_type.py

from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
```

### If an old header already exists, it will be replaced.

Before:
```python
# old/path/file.py

from sqlalchemy import Column
from sqlalchemy.orm import relationship
```

After running the script:
```python
# app/models/db_request_type.py

from sqlalchemy import Column
from sqlalchemy.orm import relationship
```

## Lock Protection

To prevent concurrent execution, the script creates a lock file:

```bash
  .path_header.lock
```
If the script is already running, another execution will exit with a message:

Script already running. Exiting.

If the script crashes unexpectedly, you may need to remove the lock file manually.


Linux / macOS:

```bash
    rm .path_header.lock
```

Windows:

```bash
    del .path_header.lock
```

## Notes

- The script processes only `.py` files.
- File paths are always written relative to the project root.
- The script should always be executed from the root directory of the project.
- The script is safe to run multiple times.
- Existing headers that look like file paths are automatically removed and replaced.