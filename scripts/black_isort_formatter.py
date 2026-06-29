# scripts/black_isort_formatter.py

#!/usr/bin/env python
import sys
import subprocess
from pathlib import Path

# Path from PyCharm click
target = Path(sys.argv[1]).resolve()

# Python in .venv project
python_exe = target.parent / ".venv" / "Scripts" / "python.exe"
if not python_exe.exists():
    python_exe = Path.cwd() / ".venv" / "Scripts" / "python.exe"

if not python_exe.exists():
    print("Python not found in .venv")
    sys.exit(1)


def run(path):
    subprocess.run([str(python_exe), "-m", "black", str(path)], check=True)
    subprocess.run([str(python_exe), "-m", "isort", str(path)], check=True)


if target.is_file():
    run(target)
elif target.is_dir():
    run(target)
else:
    print(f"Invalid path: {target}")
    sys.exit(1)
