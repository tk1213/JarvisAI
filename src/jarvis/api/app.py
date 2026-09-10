from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import cast

from fastapi import FastAPI, Request

from jarvis.api.contracts import APIHealthResponse
from jarvis.services.health_service import HealthService
from jarvis.version import __version__

type APILifespan = Callable[
    [FastAPI],
    AbstractAsyncContextManager[None],
]


def create_api_app(
    *,
    health: HealthService | None = None,
    lifespan: APILifespan | None = None,
) -> FastAPI:
    app = FastAPI(
        title="JarvisAI API",
        version=__version__,
        lifespan=lifespan,
    )

    if health is not None:
        app.state.health = health

    @app.get(
        "/api/v1/health",
        response_model=APIHealthResponse,
        tags=["system"],
    )
    async def get_health(
        request: Request,
    ) -> APIHealthResponse:
        health_service = cast(
            HealthService,
            request.app.state.health,
        )

        checks = await health_service.check()

        healthy = await health_service.is_operationally_ready()

        return APIHealthResponse(
            status=(
                "healthy"
                if healthy
                else "degraded"
            ),
            checks=checks,
        )

    return app