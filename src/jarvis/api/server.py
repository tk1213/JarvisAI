from __future__ import annotations

import uvicorn

from jarvis.api.composition import create_production_api_app
from jarvis.config import settings


def run_api_server() -> None:
    app = create_production_api_app()

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )