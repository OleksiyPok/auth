# scripts/tools/path_header.py

# Path Header Script
#
# Description:
# This script adds a header with the relative path to each Python file
# inside the specified target directory.
# It removes any existing path-like header before adding the new one.
#
# By default, the script processes Python files inside the "app" directory.
# The following directories are excluded:
# .venv, __pycache__, .pytest_cache, and .git.
#
# A lock file is used to prevent multiple instances of the script
# from running at the same time.
#
# Usage:
# python scripts/path_header.py
#
# Or specify a target directory:
# python scripts/path_header.py <directory>
#
# Examples:
# python scripts/path_header.py
# python scripts/path_header.py app
# python scripts/path_header.py tests
#
# The script:
# 1. Checks that the target directory exists.
# 2. Prevents multiple instances from running simultaneously.
# 3. Finds Python files inside the target directory.
# 4. Removes existing path headers.
# 5. Adds the file's relative repository path as a header.
# 6. Removes the lock file after processing.
#
# Example result:
# Before:
# from app.services.user import User
#
# After:
# # app/services/user.py
#
# from app.services.user import User

import re
import sys
from pathlib import Path

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


def main():
    repo_root = Path.cwd().resolve()
    lock_path = repo_root / LOCK_FILE

    target_arg = sys.argv[1] if len(sys.argv) > 1 else "app"

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


if __name__ == "__main__":
    main()
