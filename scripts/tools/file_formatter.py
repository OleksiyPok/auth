# scripts/tools/file_formatter.py

# File Formatter
#
# Description:
# This script formats a Python file automatically.
# It first sorts and organizes imports using isort,
# then formats the code using Black.
#
# Usage:
# python scripts/file_formatter.py <file_path>
#
# Example:
# python scripts/file_formatter.py app/main.py
#
# The specified file must exist and be a valid file.
# Both isort and Black must be installed in the environment.
#
# Formatting steps:
# 1. Validate the provided file path.
# 2. Run isort to organize imports.
# 3. Run Black to format the code.
# 4. Display a completion message.

#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

# Check if a file path was provided
if len(sys.argv) < 2:
    print("Usage: format_file.py <file_path>")
    sys.exit(1)

file_path = Path(sys.argv[1])

# Make sure the path exists and is a file
if not file_path.is_file():
    print(f"Error: {file_path} is not a valid file.")
    sys.exit(1)

# Run isort first
print(f"Running isort on {file_path}...")
subprocess.run([sys.executable, "-m", "isort", str(file_path)], check=True)

# Then run black
print(f"Running black on {file_path}...")
subprocess.run([sys.executable, "-m", "black", str(file_path)], check=True)

print("Formatting complete!")
