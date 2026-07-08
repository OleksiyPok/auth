# scripts/file_formatter.py

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
