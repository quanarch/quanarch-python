"""The quanar's one database connection. Quans never see it; they send operations."""

from __future__ import annotations

import sqlite3

from ..config import settings

settings.database_file.parent.mkdir(parents=True, exist_ok=True)

#: Autocommit: transactions are opened explicitly, by the db_manager.
database = sqlite3.connect(settings.database_file, isolation_level=None)
database.row_factory = sqlite3.Row
# WAL with synchronous NORMAL: a crash of the process loses nothing; only a power cut may
# lose the last commit. FULL would wait for the disk on every write.
database.executescript("PRAGMA journal_mode = WAL; PRAGMA synchronous = NORMAL; PRAGMA busy_timeout = 3000;")
