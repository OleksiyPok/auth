from pathlib import Path
from datetime import datetime
import shutil
import sys

# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# Input
# ============================================================

if len(sys.argv) < 2:
    print("Usage:")
    print("  py pack_src.py <source_path>")
    sys.exit(1)

SOURCE_DIR = Path(sys.argv[1]).expanduser().resolve()

if not SOURCE_DIR.exists() or not SOURCE_DIR.is_dir():
    print(f"Error: invalid source directory:")
    print(f"  {SOURCE_DIR}")
    sys.exit(1)


# ============================================================
# Target
# ============================================================

print(f"Source directory: {SOURCE_DIR}")

target_input = input("Package to [script directory]: ").strip()

if target_input == "" or target_input == ".":
    TARGET_BASE_DIR = BASE_DIR
else:
    TARGET_BASE_DIR = Path(target_input).expanduser().resolve()

TARGET_BASE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Derived paths
# ============================================================

PACKAGE_NAME = SOURCE_DIR.name

TARGET_DIR = TARGET_BASE_DIR / PACKAGE_NAME
ARCHIVE = TARGET_BASE_DIR / f"{PACKAGE_NAME}.zip"

CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M")


# ============================================================
# Info
# ============================================================

print()
print(f"SOURCE_DIR : {SOURCE_DIR}")
print(f"TARGET_DIR : {TARGET_DIR}")
print(f"ARCHIVE    : {ARCHIVE}")
print(f"TIME       : {CURRENT_TIME}")


# ============================================================
# Step 1: Copy source
# ============================================================

print("\n1. Copying source...")

if TARGET_DIR.exists():
    shutil.rmtree(TARGET_DIR)

shutil.copytree(SOURCE_DIR, TARGET_DIR)


# ============================================================
# Step 2: Remove unnecessary files
# ============================================================

print("2. Removing unnecessary files...")

ALLOWED_EXTENSIONS = {
    ".cpp",
    ".h",
    ".hpp",
    ".c",
    ".cc",
    ".cxx",
}


for path in list(TARGET_DIR.rglob("*")):
    if not path.is_file():
        continue

    # Remove Python cache files/directories
    if "__pycache__" in path.parts:
        path.unlink()
        continue

    # Remove README files
    if path.name.lower().startswith("readme"):
        path.unlink()
        continue

    # Remove everything except source files
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        path.unlink()


# Remove empty directories
for path in sorted(TARGET_DIR.rglob("*"), reverse=True):
    if path.is_dir():
        try:
            path.rmdir()
        except OSError:
            pass


# ============================================================
# Step 3: Create archive
# ============================================================

print("3. Creating archive...")

if ARCHIVE.exists():
    ARCHIVE.unlink()

shutil.make_archive(
    base_name=str(ARCHIVE.with_suffix("")),
    format="zip",
    root_dir=TARGET_BASE_DIR,
    base_dir=TARGET_DIR.name,
)


# ============================================================
# Step 4: Remove temporary directory
# ============================================================

print("4. Removing temporary directory...")

shutil.rmtree(TARGET_DIR)


# ============================================================
# Done
# ============================================================

print()
print(f"Done! {CURRENT_TIME}")
print(f"Archive: {ARCHIVE}")
