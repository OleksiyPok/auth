# scripts/project_formatter.py

import subprocess
from pathlib import Path

# Project directory = current working directory
project_dir = Path.cwd()

print(f"Formatting all Python files in {project_dir}...")

# Run isort
subprocess.run(
    [
        str(project_dir / ".venv" / "Scripts" / "python.exe"),
        "-m",
        "isort",
        str(project_dir),
    ],
    check=True,
)

# Run black
subprocess.run(
    [
        str(project_dir / ".venv" / "Scripts" / "python.exe"),
        "-m",
        "black",
        str(project_dir),
    ],
    check=True,
)

print("Formatting complete!")
