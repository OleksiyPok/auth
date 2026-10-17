# scripts/tools/path_header_python.py

import re
import sys
from pathlib import Path

EXCLUDE_DIRS = {
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".git",
    "build",
    "cmake-build-debug",
    "cmake-build-release",
}

LOCK_FILE = ".path_header_python.lock"

EXTENSIONS = {
    ".py",
}

PATH_LIKE_REGEX = re.compile(r"^\s*#\s*[\w\-.\/\\]+\.[\w]+$" r"|^\s*#\s*[\w\-.\/\\]+$")


def get_script_dir() -> Path:
    return Path(__file__).resolve().parent


def resolve_path(script_dir: Path, value: str) -> Path:
    value = value.strip()

    if value in ("", "."):
        return script_dir

    path = Path(value)

    if path.is_absolute():
        return path.resolve()

    return (script_dir / path).resolve()


def request_existing_path(
    script_dir: Path,
    message: str,
) -> Path | None:

    while True:
        try:
            value = input(message).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if value.lower() in {"q", "quit", "cancel"}:
            return None

        path = resolve_path(script_dir, value)

        if path.exists() and path.is_dir():
            return path

        print(f"Path '{value}' does not exist " "or is not a directory.")
        print("Try again or enter 'q' to cancel.")


def get_header_base_path(target_dir: Path) -> list[str]:
    return [target_dir.name]


def parse_header_path(
    target_dir: Path,
    file_relative: Path,
    specification: str,
) -> str:

    specification = specification.strip()

    parts = [part for part in specification.replace("\\", "/").split("/") if part]

    if not parts or parts == ["."]:
        remove_count = 0
        parent_count = 0
    else:
        remove_count = 0
        parent_count = 0

        for part in parts:
            if part == "*":
                remove_count += 1

            elif part == "..":
                parent_count += 1

            elif part == ".":
                continue

            else:
                raise ValueError(f"Unsupported path component: '{part}'")

    base_parts = get_header_base_path(target_dir)

    if remove_count > len(base_parts):
        raise ValueError("Too many '*' components for the scan path.")

    base_parts = base_parts[remove_count:]

    parent_parts = []

    parent_dir = target_dir

    for _ in range(parent_count):
        parent_dir = parent_dir.parent

        if parent_dir == parent_dir.parent:
            raise ValueError("Cannot go above the filesystem root.")

        parent_parts.insert(
            0,
            parent_dir.name,
        )

    all_parts = parent_parts + base_parts + list(file_relative.parts)

    return Path(*all_parts).as_posix()


def request_header_specification(
    target_dir: Path,
) -> str | None:

    while True:
        try:
            value = input("Path in header [., */ or ../]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if value.lower() in {"q", "quit", "cancel"}:
            return None

        try:
            parse_header_path(
                target_dir,
                Path("file.py"),
                value,
            )
            return value

        except ValueError as error:
            print(f"Invalid path specification: {error}")
            print("Try again or enter 'q' to cancel.")


def should_process(
    path: Path,
    target_dir: Path,
) -> bool:

    if not path.is_file():
        return False

    if path.suffix.lower() not in EXTENSIONS:
        return False

    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False

    try:
        path.relative_to(target_dir)
        return True
    except ValueError:
        return False


def remove_existing_header(
    lines: list[str],
) -> list[str]:

    index = 0

    while index < len(lines) and lines[index].strip() == "":
        index += 1

    while index < len(lines):
        line = lines[index].rstrip("\r\n")

        if not PATH_LIKE_REGEX.fullmatch(line):
            break

        index += 1

        while index < len(lines) and lines[index].strip() == "":
            index += 1

    return lines[index:]


def process_file(
    file_path: Path,
    target_dir: Path,
    specification: str,
) -> None:

    lines = file_path.read_text(encoding="utf-8-sig").splitlines(keepends=True)

    remaining_lines = remove_existing_header(lines)

    file_relative = file_path.relative_to(target_dir)

    header_path = parse_header_path(
        target_dir,
        file_relative,
        specification,
    )

    header = f"# {header_path}\n\n"

    file_path.write_text(
        header + "".join(remaining_lines),
        encoding="utf-8",
    )


def main():
    script_dir = get_script_dir()

    target_arg = sys.argv[1] if len(sys.argv) > 1 else "."

    target_path = resolve_path(
        script_dir,
        target_arg,
    )

    if not target_path.exists() or not target_path.is_dir():
        print(f"Target path '{target_arg}' does not exist " "or is not a directory.")

        target_path = request_existing_path(
            script_dir,
            "Scan path: ",
        )

        if target_path is None:
            print("Cancelled.")
            return

    print(f"Scanning from: {target_path}")

    specification = request_header_specification(
        target_path,
    )

    if specification is None:
        print("Cancelled.")
        return

    lock_path = script_dir / LOCK_FILE

    if lock_path.exists():
        print("Script already running.")
        sys.exit(1)

    processed_files = 0

    try:
        lock_path.write_text(
            "lock",
            encoding="utf-8",
        )

        for file_path in target_path.rglob("*"):
            if should_process(
                file_path,
                target_path,
            ):
                process_file(
                    file_path,
                    target_path,
                    specification,
                )

                processed_files += 1

    finally:
        if lock_path.exists():
            lock_path.unlink()

    print(f"Processed {processed_files} Python file(s).")


if __name__ == "__main__":
    main()
