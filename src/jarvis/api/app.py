from __future__ import annotations

from fastapi import FastAPI

from jarvis.api.contracts import APIHealthResponse
from jarvis.services.health_service import HealthService
from jarvis.version import __version__


def create_api_app(
    *,
    health: HealthService,
) -> FastAPI:
    app = FastAPI(
        title="JarvisAI API",
        version=__version__,
    )

    @app.get(
        "/api/v1/health",
        response_model=APIHealthResponse,
        tags=["system"],
    )
    async def get_health() -> APIHealthResponse:
        checks = await health.check()

        healthy = (
            bool(checks)
            and all(checks.values())
        )

        return APIHealthResponse(
            status=(
                "healthy"
                if healthy
                else "degraded"
            ),
            checks=checks,
        )

    return app