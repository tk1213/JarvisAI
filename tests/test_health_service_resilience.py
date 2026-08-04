from __future__ import annotations

import pytest

from jarvis.core.container import container
from jarvis.planner.resilience_runtime import (
    resilience_runtime,
)
from jarvis.services.health_service import HealthService


class HealthyDatabase:
    async def health_check(
        self,
    ) -> bool:
        return True


@pytest.mark.asyncio
async def test_health_details_expose_resilience_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        container.register(
            "system",
            object(),
        )
        container.register(
            "commands",
            object(),
        )
        container.register(
            "database",
            HealthyDatabase(),
        )
        container.register(
            "heartbeat",
            object(),
        )
        container.register(
            "resilience_runtime",
            resilience_runtime,
        )

        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            lambda: [
                "heartbeat",
            ],
        )

        service = HealthService()
        details = await service.details()

        assert (
            details["checks"][
                "resilience_runtime"
            ]
            is True
        )
        assert "resilience" in details
        assert "metrics" in details[
            "resilience"
        ]

    finally:
        container.clear()

        for name, service in existing.items():
            container.register(
                name,
                service,
            )
