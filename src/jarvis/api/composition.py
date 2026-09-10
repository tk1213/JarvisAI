from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from jarvis.api.app import create_api_app
from jarvis.core.application import JarvisApplication
from jarvis.core.container import ServiceContainer, container
from jarvis.services.health_service import HealthService


def create_production_api_app(
    *,
    application: JarvisApplication | None = None,
    services: ServiceContainer = container,
) -> FastAPI:
    jarvis_application = (
        application
        if application is not None
        else JarvisApplication()
    )

    @asynccontextmanager
    async def lifespan(
        app: FastAPI,
    ) -> AsyncIterator[None]:
        await jarvis_application.start(
            start_background_tasks=False,
            include_voice=False,
        )

        try:
            app.state.health = services.resolve(
                "health",
                HealthService,
            )

            yield

        finally:
            await jarvis_application.shutdown()

    return create_api_app(
        lifespan=lifespan,
    )