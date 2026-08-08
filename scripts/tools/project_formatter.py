# scripts/tools/project_formatter.py

# Project Formatter
#
# Description:
# This script formats the entire Python project using isort and Black.
# It sorts and organizes imports with isort and then formats the code
# according to Black's formatting rules.
#
# The script automatically uses the current working directory
# as the project directory.
#
# Usage:
# python scripts/project_formatter.py
#
# Run the command from the project root directory.
#
# Example:
# python scripts/project_formatter.py
#
# The script:
# 1. Runs isort on the entire project.
# 2. Runs Black on the entire project.
# 3. Prints a completion message after successful formatting.
#
# Both isort and Black must be installed in the current Python environment.

import subprocess
import sys
from pathlib import Path


def run_formatter(project_dir: Path) -> None:
    python = sys.executable

    print("Running isort...")

    subprocess.run(
        [
            python,
            "-m",
            "isort",
            str(project_dir),
        ],
        check=True,
    )

    print("Running black...")

    subprocess.run(
        [
            python,
            "-m",
            "black",
            str(project_dir),
        ],
        check=True,
    )

    print("Formatting complete.")


def main():
    run_formatter(Path.cwd())


if __name__ == "__main__":
    main()
