"""python -m app"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from starlette.applications import Starlette

from .config import settings
from .core import create_app, database, get_logger
from .services import quan_service, system_service

log = get_logger("quanar")


@asynccontextmanager
async def lifespan(_app: Starlette) -> AsyncIterator[None]:
    log.info(f"listening on http://localhost:{settings.port}")
    quan_service.start()
    yield
    log.info("stopping")
    await quan_service.stop()
    database.close()


app = create_app(system_service.routes, lifespan)


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=settings.port, log_level="warning")


if __name__ == "__main__":
    main()
