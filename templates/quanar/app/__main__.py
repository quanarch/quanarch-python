"""python -m app"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from starlette.applications import Starlette

from .config import settings
from .core import create_app
from .services import quan_service, system_service


@asynccontextmanager
async def lifespan(_app: Starlette) -> AsyncIterator[None]:
    quan_service.start()
    yield
    await quan_service.stop()


app = create_app(system_service.routes, lifespan)


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=settings.port, log_level="warning")


if __name__ == "__main__":
    main()
