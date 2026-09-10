from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import cast

from fastapi import FastAPI, Request

from jarvis.api.contracts import (
    APIHealthResponse,
    APISmartHomeDevice,
    APISmartHomeDevicesResponse,
)
from jarvis.services.health_service import HealthService
from jarvis.smart_home.service import SmartHomeService
from jarvis.version import __version__

type APILifespan = Callable[
    [FastAPI],
    AbstractAsyncContextManager[None],
]


def create_api_app(
    *,
    health: HealthService | None = None,
    smart_home: SmartHomeService | None = None,
    lifespan: APILifespan | None = None,
) -> FastAPI:
    app = FastAPI(
        title="JarvisAI API",
        version=__version__,
        lifespan=lifespan,
    )

    if health is not None:
        app.state.health = health

    if smart_home is not None:
        app.state.smart_home = smart_home

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

    @app.get(
        "/api/v1/smart-home/devices",
        response_model=APISmartHomeDevicesResponse,
        tags=["smart-home"],
    )
    async def get_smart_home_devices(
        request: Request,
    ) -> APISmartHomeDevicesResponse:
        smart_home_service = cast(
            SmartHomeService,
            request.app.state.smart_home,
        )

        devices = await smart_home_service.list_devices()

        return APISmartHomeDevicesResponse(
            connected=smart_home_service.connected,
            devices=[
                APISmartHomeDevice(
                    id=device.id,
                    name=device.name,
                    room=device.room,
                    device_type=device.device_type,
                    online=device.online,
                    power=device.power,
                )
                for device in devices
            ],
        )

    return app