"""Builds every quan into the artifacts, then seals them into the quanar's list.

    uv run scripts/build.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    for quan in sorted((ROOT / "quans").iterdir()):
        subprocess.run([sys.executable, "build.py"], cwd=quan, check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "register.py")], check=True)


if __name__ == "__main__":
    main()
