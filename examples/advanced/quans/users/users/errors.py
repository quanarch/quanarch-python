from __future__ import annotations


class AppError(Exception):
    """A failure the quan expects and answers on purpose, with its own status and code."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
