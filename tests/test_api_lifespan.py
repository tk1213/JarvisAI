from __future__ import annotations

from unittest.mock import AsyncMock, Mock, call

import pytest
from httpx import ASGITransport, AsyncClient

from jarvis.api import create_production_api_app
from jarvis.core.application import JarvisApplication
from jarvis.core.container import ServiceContainer
from jarvis.services.health_service import HealthService
from jarvis.smart_home.service import SmartHomeService


@pytest.mark.asyncio
async def test_production_api_uses_headless_lifecycle() -> None:
    application = Mock(
        spec=JarvisApplication,
    )
    application.start = AsyncMock()
    application.shutdown = AsyncMock()

    health = Mock(
        spec=HealthService,
    )
    health.check = AsyncMock(
        return_value={
            "database": True,
        }
    )
    health.is_operationally_ready = AsyncMock(
        return_value=True,
    )

    smart_home = Mock(
        spec=SmartHomeService,
    )

    services = Mock(
        spec=ServiceContainer,
    )
    services.resolve.side_effect = (
        health,
        smart_home,
    )

    app = create_production_api_app(
        application=application,
        services=services,
    )

    transport = ASGITransport(
        app=app,
    )

    async with app.router.lifespan_context(app), AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        assert app.state.health is health
        assert app.state.smart_home is smart_home

        response = await client.get(
            "/api/v1/health"
        )

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "checks": {
            "database": True,
        },
    }

    application.start.assert_awaited_once_with(
        start_background_tasks=True,
        include_voice=False,
    )
    application.shutdown.assert_awaited_once_with()

    assert services.resolve.call_args_list == [
        call(
            "health",
            HealthService,
        ),
        call(
            "smart_home",
            SmartHomeService,
        ),
    ]

    health.check.assert_awaited_once_with()
    health.is_operationally_ready.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_production_api_does_not_shutdown_after_failed_start() -> None:
    application = Mock(
        spec=JarvisApplication,
    )
    application.start = AsyncMock(
        side_effect=RuntimeError(
            "controlled startup failure"
        )
    )
    application.shutdown = AsyncMock()

    services = Mock(
        spec=ServiceContainer,
    )

    app = create_production_api_app(
        application=application,
        services=services,
    )

    with pytest.raises(
        RuntimeError,
        match="controlled startup failure",
    ):
        async with app.router.lifespan_context(app):
            pass

    application.start.assert_awaited_once_with(
        start_background_tasks=True,
        include_voice=False,
    )

    application.shutdown.assert_not_awaited()
    services.resolve.assert_not_called()


@pytest.mark.asyncio
async def test_production_api_shuts_down_after_smart_home_resolution_failure(
) -> None:
    application = Mock(
        spec=JarvisApplication,
    )
    application.start = AsyncMock()
    application.shutdown = AsyncMock()

    health = Mock(
        spec=HealthService,
    )

    services = Mock(
        spec=ServiceContainer,
    )
    services.resolve.side_effect = (
        health,
        RuntimeError(
            "controlled Smart Home resolution failure"
        ),
    )

    app = create_production_api_app(
        application=application,
        services=services,
    )

    with pytest.raises(
        RuntimeError,
        match="controlled Smart Home resolution failure",
    ):
        async with app.router.lifespan_context(app):
            pass

    application.start.assert_awaited_once_with(
        start_background_tasks=True,
        include_voice=False,
    )
    application.shutdown.assert_awaited_once_with()

    assert services.resolve.call_args_list == [
        call(
            "health",
            HealthService,
        ),
        call(
            "smart_home",
            SmartHomeService,
        ),
    ]