"""Type-checks every part: the qua, the quanar and each quan with mypy, the web client with tsc.

    uv run scripts/check.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    # Each quan is its own project, with its own build.py: one mypy run each.
    parts = [ROOT / "packages" / "shop-qua" / "src", ROOT / "quanar" / "app", *sorted((ROOT / "quans").iterdir()), ROOT / "scripts", ROOT / "artifacts"]
    failed = [part for part in parts if subprocess.run([sys.executable, "-m", "mypy", str(part)], cwd=ROOT).returncode != 0]
    if subprocess.run(["npm", "run", "typecheck", "--prefix", str(ROOT / "web")]).returncode != 0:
        failed.append(ROOT / "web")
    if failed:
        sys.exit(f"failed: {', '.join(str(p.relative_to(ROOT)) for p in failed)}")


if __name__ == "__main__":
    main()
