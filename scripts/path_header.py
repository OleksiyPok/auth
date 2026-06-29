# scripts/path_header.py

import re
import sys
from pathlib import Path

# Directories to exclude from processing
EXCLUDE_DIRS = {".venv", "__pycache__", ".pytest_cache", ".git"}

# Lock file to prevent concurrent runs
LOCK_FILE = ".add_path_header.lock"

# Regex to match path-like comments (e.g., "# app/models/db.py")
PATH_LIKE_REGEX = re.compile(r"^\s*#\s*[\w\-.\/]+\.[\w]+$|^\s*#\s*[\w\-.\/]+$")


def should_process(path: Path, target_dir: Path) -> bool:
    # Only process .py files
    if path.suffix != ".py":
        return False

    # Skip excluded directories
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False

    # Check if the file is inside the target directory
    try:
        path.relative_to(target_dir)
        return True
    except ValueError:
        return False


def build_header_path(path: Path, repo_root: Path) -> str:
    # Build path relative to the repository root
    return path.relative_to(repo_root).as_posix()


def process_file(file_path: Path, repo_root: Path) -> None:
    # Read the file and keep original line endings
    lines = file_path.read_text(encoding="utf-8-sig").splitlines(keepends=True)

    i = 0

    # Remove leading empty lines
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # Remove existing path-like comments at the top
    while i < len(lines) and PATH_LIKE_REGEX.fullmatch(lines[i].rstrip("\r\n")):
        i += 1

        # Remove empty lines following the path comment
        while i < len(lines) and lines[i].strip() == "":
            i += 1

    remaining_lines = lines[i:]

    # Create new header using path from repository root
    header = f"# {build_header_path(file_path, repo_root)}\n\n"

    new_text = header + "".join(remaining_lines)

    file_path.write_text(new_text, encoding="utf-8")


def main():
    repo_root = Path.cwd().resolve()
    lock_path = repo_root / LOCK_FILE

    # Prevent concurrent execution
    if lock_path.exists():
        print("Script already running. Exiting.")
        sys.exit(1)

    # Target folder or file from CLI argument, default = app
    target_arg = sys.argv[1] if len(sys.argv) > 1 else "app"
    target_path = (repo_root / target_arg).resolve()

    # Validate target path
    if not target_path.exists():
        print(f"Target path '{target_arg}' does not exist.")
        sys.exit(1)

    processed_files = 0

    try:
        # Create lock file
        lock_path.write_text("lock")

        # Iterate over Python files
        for py_file in repo_root.rglob("*.py"):
            if should_process(py_file, target_path):
                process_file(py_file, repo_root)
                processed_files += 1

    finally:
        # Remove lock file after execution
        if lock_path.exists():
            lock_path.unlink()

    # Print result
    if processed_files > 0:
        print(f"Successfully processed {processed_files} file(s) under '{target_arg}'.")
    else:
        print(f"No Python files found under '{target_arg}' to process.")


if __name__ == "__main__":
    main()
