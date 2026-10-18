"""Seals every built quan: hashes its file in the artifacts and writes the quanar's list.
In a real system CI does this after uploading the file. With --open no hash is written, so
a quan rebuilt by its watch is taken in as it is.

    uv run scripts/register.py [--open]
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = os.environ.get("ARTIFACTS_URL", f"http://localhost:{os.environ.get('ARTIFACTS_PORT', '4100')}")


def main() -> None:
    open_ = "--open" in sys.argv
    listed = []
    for quan in sorted((ROOT / "quans").iterdir()):
        project = tomllib.loads((quan / "pyproject.toml").read_text())["project"]
        name, version = project["name"], project["version"]
        file = ROOT / "artifacts" / "quans" / name / version / f"{name}.pyz"
        entry = {"name": name, "version": version, "url": f"{ARTIFACTS}/quans/{name}/{version}/{name}.pyz"}
        if not open_:
            entry["hash"] = hashlib.sha256(file.read_bytes()).hexdigest()
        listed.append({**entry, "events": f"{ARTIFACTS}/events/{name}", "quas": ["shop-qua"]})
        print(f"{name}@{version}  {entry['hash'][:12] + '…' if 'hash' in entry else 'no hash'}")
    target = ROOT / "quanar" / "data" / "quans.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(listed, indent=2) + "\n")


if __name__ == "__main__":
    main()
