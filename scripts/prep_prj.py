# scripts/prep_prj.py

# Project Preparation Script
#
# Description:
# This script prepares the project for development or submission by
# running the path header and project formatting scripts in sequence.
#
# By default, the "app" directory is used as the target.
# A different target directory can be provided as a command-line argument.
#
# Usage:
# python scripts/prep_prj.py
#
# Or specify a target directory:
# python scripts/prep_prj.py <directory>
#
# Examples:
# python scripts/prep_prj.py
# python scripts/prep_prj.py app
# python scripts/prep_prj.py tests
#
# The script:
# 1. Runs path_header.py for the specified target directory.
# 2. Runs project_formatter.py for the entire project.
# 3. Prints a completion message after successful execution.
#
# Both scripts must be located in the same "scripts" directory.

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def run_script(script: str, *args: str) -> None:
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / script),
            *args,
        ],
        check=True,
    )


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "app"

    print(f"Preparing project. Target: {target}")

    run_script(
        "path_header.py",
        target,
    )

    run_script(
        "project_formatter.py",
    )

    print("Project preparation complete.")


if __name__ == "__main__":
    main()
