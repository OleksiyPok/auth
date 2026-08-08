# scripts/tools/isort_black_formatter.py

# Isort and Black Formatter
#
# Description:
# This script formats a Python file or directory using isort and Black.
# It is designed to be launched from PyCharm by passing a file or directory path.
#
# The script uses the Python interpreter from the project's .venv environment.
# If the virtual environment is not found next to the target path,
# it also checks the current working directory.
#
# Usage:
# Run the script from PyCharm and pass the target file or directory as an argument.
#
# Examples:
# python scripts/isort_black_formatter.py app/main.py
# python scripts/isort_black_formatter.py app
#
# The script:
# 1. Resolves the provided target path.
# 2. Finds the Python interpreter inside .venv.
# 3. Runs isort to organize imports.
# 4. Runs Black to format the code.
# 5. Supports both individual files and directories.
#
# The target path must exist, and the project must contain a .venv
# with a valid Python interpreter.

#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

# Path from PyCharm click
target = Path(sys.argv[1]).resolve()

# Python in .venv project
python_exe = target.parent / ".venv" / "Scripts" / "python.exe"
if not python_exe.exists():
    python_exe = Path.cwd() / ".venv" / "Scripts" / "python.exe"

if not python_exe.exists():
    print("Python not found in .venv")
    sys.exit(1)


def run(path):
    subprocess.run([str(python_exe), "-m", "isort", str(path)], check=True)
    subprocess.run([str(python_exe), "-m", "black", str(path)], check=True)


if target.is_file():
    run(target)
elif target.is_dir():
    run(target)
else:
    print(f"Invalid path: {target}")
    sys.exit(1)
