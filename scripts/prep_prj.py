# scripts/prep_prj.py

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
