from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest
from httpx import ASGITransport, AsyncClient

from jarvis.api import create_api_app
from jarvis.services.health_service import HealthService


@pytest.mark.parametrize(
    ("checks", "expected_status"),
    (
        (
            {
                "database": True,
                "openai": True,
            },
            "healthy",
        ),
        (
            {
                "database": True,
                "openai": False,
            },
            "degraded",
        ),
        (
            {},
            "degraded",
        ),
    ),
)
@pytest.mark.asyncio
async def test_health_endpoint(
    checks: dict[str, bool],
    expected_status: str,
) -> None:
    health = Mock(
        spec=HealthService,
    )
    health.check = AsyncMock(
        return_value=checks,
    )

    app = create_api_app(
        health=health,
    )

    transport = ASGITransport(
        app=app,
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/health"
        )

    assert response.status_code == 200
    assert response.json() == {
        "status": expected_status,
        "checks": checks,
    }

    health.check.assert_awaited_once_with()