"""Builds and seals the quans, then starts the artifacts store, the quanar and the web client.
Ctrl+C stops all three.

    uv run scripts/start.py
"""

from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path
from typing import IO

ROOT = Path(__file__).resolve().parent.parent
PARTS = [
    ("artifacts", [sys.executable, "artifacts/server.py"], ROOT),
    ("quanar", [sys.executable, "-m", "app"], ROOT / "quanar"),
    ("web", ["npm", "run", "dev"], ROOT / "web"),
]


def _relay(name: str, stream: IO[str]) -> None:
    prefix = f"[{name}]".ljust(12)
    for line in stream:
        if line.strip():
            print(prefix + line.rstrip(), flush=True)


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py")], check=True)
    children = []
    for name, args, cwd in PARTS:
        child = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        threading.Thread(target=_relay, args=(name, child.stdout), daemon=True).start()
        children.append(child)
    try:
        for child in children:
            child.wait()
    except KeyboardInterrupt:
        # The terminal sent Ctrl+C to every part as well; give them a moment to stop.
        for child in children:
            try:
                child.wait(5)
            except subprocess.TimeoutExpired:
                child.kill()


if __name__ == "__main__":
    main()
