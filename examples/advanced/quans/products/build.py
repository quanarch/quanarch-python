"""Builds the quan into the artifacts, under its version: artifacts/quans/<name>/<version>/<name>.pyz

    python build.py            build once
    python build.py --watch    rebuild on every change; the artifacts server announces each build
"""

from __future__ import annotations

import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
_project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
NAME: str = _project["name"]
VERSION: str = _project["version"]
SOURCE = ROOT / NAME.replace("-", "_")
OUT = ROOT.parent.parent / "artifacts" / "quans" / NAME / VERSION / f"{NAME}.pyz"


def build() -> None:
    """One zip with the quan's package. shop_qua is not in it: the quanar provides it."""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(SOURCE.rglob("*.py")):
            # A fixed date: the same source always makes the same file, and the same hash.
            info = zipfile.ZipInfo(str(file.relative_to(ROOT)), date_time=(1980, 1, 1, 0, 0, 0))
            archive.writestr(info, file.read_bytes())
    tmp.replace(OUT)
    print(f"built {NAME}@{VERSION} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
    if "--watch" in sys.argv:
        from watchfiles import watch

        try:
            for _ in watch(SOURCE, watch_filter=lambda _change, path: path.endswith(".py")):
                build()
        except KeyboardInterrupt:
            pass
