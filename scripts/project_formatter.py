# scripts/project_formatter.py

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
