# scripts/tools/h_f_prj.py

#!/usr/bin/env python
# h_f_prj.py

# Project Preparation Script
#
# This standalone script:
# 1. Adds relative repository path headers to Python files.
# 2. Formats the entire project using isort and Black.
#
# Usage:
#   python h_f_prj.py
#   python h_f_prj.py app
#   python h_f_prj.py tests

import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path header
# ---------------------------------------------------------------------------

EXCLUDE_DIRS = {
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".git",
}

LOCK_FILE = ".add_path_header.lock"

PATH_LIKE_REGEX = re.compile(r"^\s*#\s*[\w\-.\/]+\.[\w]+$|^\s*#\s*[\w\-.\/]+$")


def should_process(path: Path, target_dir: Path) -> bool:
    if path.suffix != ".py":
        return False

    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False

    try:
        path.relative_to(target_dir)
        return True
    except ValueError:
        return False


def build_header_path(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def process_file(file_path: Path, repo_root: Path) -> None:
    lines = file_path.read_text(encoding="utf-8-sig").splitlines(keepends=True)

    index = 0

    while index < len(lines) and lines[index].strip() == "":
        index += 1

    while index < len(lines) and PATH_LIKE_REGEX.fullmatch(lines[index].rstrip("\r\n")):
        index += 1

        while index < len(lines) and lines[index].strip() == "":
            index += 1

    remaining_lines = lines[index:]

    header = f"# {build_header_path(file_path, repo_root)}\n" "\n"

    file_path.write_text(
        header + "".join(remaining_lines),
        encoding="utf-8",
    )


def add_path_headers(repo_root: Path, target_arg: str) -> None:
    lock_path = repo_root / LOCK_FILE
    target_path = (repo_root / target_arg).resolve()

    if not target_path.exists():
        print(f"Target path '{target_arg}' does not exist.")
        sys.exit(1)

    if lock_path.exists():
        print("Script already running.")
        sys.exit(1)

    processed_files = 0

    try:
        lock_path.write_text("lock")

        for py_file in repo_root.rglob("*.py"):
            if should_process(py_file, target_path):
                process_file(py_file, repo_root)
                processed_files += 1

    finally:
        if lock_path.exists():
            lock_path.unlink()

    print(f"Processed {processed_files} file(s) under '{target_arg}'.")


# ---------------------------------------------------------------------------
# Project formatter
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    repo_root = Path.cwd().resolve()
    target = sys.argv[1] if len(sys.argv) > 1 else "app"

    print(f"Preparing project. Target: {target}")

    add_path_headers(repo_root, target)
    run_formatter(repo_root)

    print("Project preparation complete.")


if __name__ == "__main__":
    main()
