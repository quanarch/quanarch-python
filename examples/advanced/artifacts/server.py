"""A stand-in for S3 or a CDN: serves the built quans, and announces a new build of a quan on
/events/<quan> so a quanar following it picks the new file up at once.

    python artifacts/server.py      port 4100, or ARTIFACTS_PORT
"""

from __future__ import annotations

import io
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from watchfiles import watch

PORT = int(os.environ.get("ARTIFACTS_PORT", "4100"))
ROOT = (Path(__file__).parent / "quans").resolve()
_EVENTS = re.compile(r"^/events/([a-z0-9-]+)$")

#: quan → each open /events stream, with the event that releases its thread once it is gone
streams: dict[str, dict[io.BufferedIOBase, threading.Event]] = {}
lock = threading.Lock()


def announce(quan: str) -> None:
    with lock:
        for stream, gone in list(streams.get(quan, {}).items()):
            try:
                stream.write(b"event: change\ndata: {}\n\n")
                stream.flush()
            except OSError:
                del streams[quan][stream]
                gone.set()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        events = _EVENTS.match(self.path)
        if events:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(b": connected\n\n")
            self.wfile.flush()
            gone = threading.Event()
            with lock:
                streams.setdefault(events[1], {})[self.wfile] = gone
            gone.wait()  # until a write to this stream fails
            return
        file = (ROOT / self.path.removeprefix("/quans/").lstrip("/")).resolve()
        if not self.path.startswith("/quans/") or not file.is_relative_to(ROOT) or not file.is_file():
            self.send_response(404)
            self.end_headers()
            return
        data = file.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - quiet
        pass


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"artifacts on http://localhost:{PORT}", flush=True)
    # A build writes in bursts; watchfiles hands them over together, once they settle.
    for changes in watch(ROOT, watch_filter=lambda _change, path: path.endswith(".pyz")):
        for quan in {Path(path).relative_to(ROOT).parts[0] for _, path in changes}:
            announce(quan)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
