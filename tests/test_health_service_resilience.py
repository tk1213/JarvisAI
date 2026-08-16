from __future__ import annotations

from typing import ClassVar

import pytest

from jarvis.core.container import container
from jarvis.planner.resilience_runtime import (
    resilience_runtime,
)
from jarvis.services.health_contracts import HealthState
from jarvis.services.health_service import HealthService


class HealthyDatabase:
    async def health_check(
        self,
    ) -> bool:
        return True


class RunningHeartbeat:
    running = True




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

        assert details["checks"]["resilience_runtime"] is True
        assert "resilience" in details
        assert "metrics" in details["resilience"]

    finally:
        container.clear()

        for name, service in existing.items():
            container.register(
                name,
                service,
            )


@pytest.mark.asyncio
async def test_health_diagnostics_expose_structured_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        container.register("system", object())
        container.register("commands", object())
        container.register(
            "database",
            HealthyDatabase(),
        )
        container.register(
            "heartbeat",
            RunningHeartbeat(),
        )

        container.register(
            "resilience_runtime",
            resilience_runtime,
        )

        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            lambda: ["heartbeat"],
        )

        service = HealthService()
        results = await service.diagnostics()

        assert results["service_container"].passed is True
        assert results["database"].passed is True
        assert results["heartbeat_task"].passed is True
        assert results["system_service"].passed is True
        assert results["resilience_runtime"].passed is True

    finally:
        container.clear()

        for name, service in existing.items():
            container.register(name, service)


@pytest.mark.asyncio
async def test_health_check_preserves_boolean_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        container.register("system", object())
        container.register("commands", object())
        container.register(
            "database",
            HealthyDatabase(),
        )
        container.register(
            "heartbeat",
            RunningHeartbeat(),
        )
        container.register(
            "resilience_runtime",
            resilience_runtime,
        )

        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            lambda: ["heartbeat"],
        )

        service = HealthService()
        results = await service.check()

        assert results == {
            "service_container": True,
            "database": True,
            "heartbeat_task": True,
            "system_service": True,
            "resilience_runtime": True,
        }

        assert all(isinstance(value, bool) for value in results.values())

    finally:
        container.clear()

        for name, service in existing.items():
            container.register(name, service)


class UnhealthyDatabase:
    async def health_check(
        self,
    ) -> bool:
        return False


@pytest.mark.asyncio
async def test_health_diagnostics_expose_failure_reasons(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        container.register(
            "database",
            UnhealthyDatabase(),
        )

        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            list,
        )

        service = HealthService()
        results = await service.diagnostics()

        assert results["service_container"].passed is False
        assert (
            results["service_container"].reason
            == "Required services are missing from the container."
        )

        assert results["database"].passed is False
        assert results["database"].reason == "Database health check failed."

        assert results["heartbeat_task"].passed is False
        assert results["heartbeat_task"].reason == "Heartbeat task is not running."

        assert results["system_service"].passed is False
        assert results["system_service"].reason == "System service is unavailable."

        assert results["resilience_runtime"].passed is False
        assert (
            results["resilience_runtime"].reason == "Resilience runtime is unavailable."
        )

    finally:
        container.clear()

        for name, service in existing.items():
            container.register(
                name,
                service,
            )


@pytest.mark.asyncio
async def test_health_details_preserve_boolean_checks_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        container.register(
            "database",
            UnhealthyDatabase(),
        )

        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            list,
        )

        service = HealthService()
        details = await service.details()

        assert details["healthy"] is False

        assert details["checks"] == {
            "service_container": False,
            "database": False,
            "heartbeat_task": False,
            "system_service": False,
            "resilience_runtime": False,
        }

    finally:
        container.clear()

        for name, service in existing.items():
            container.register(
                name,
                service,
            )


class FailingDatabase:
    async def health_check(
        self,
    ) -> bool:
        raise RuntimeError("database unavailable")


@pytest.mark.asyncio
async def test_health_diagnostics_isolate_database_exception(
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
            FailingDatabase(),
        )
        container.register(
            "heartbeat",
            RunningHeartbeat(),
        )
        container.register(
            "resilience_runtime",
            resilience_runtime,
        )

        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            lambda: ["heartbeat"],
        )

        service = HealthService()
        results = await service.diagnostics()

        database = results["database"]

        assert database.passed is False
        assert database.available is False
        assert database.reason == (
            "Database health check raised RuntimeError: database unavailable"
        )

        assert results["service_container"].passed is True
        assert results["heartbeat_task"].passed is True
        assert results["system_service"].passed is True
        assert results["resilience_runtime"].passed is True

    finally:
        container.clear()

        for name, service in existing.items():
            container.register(
                name,
                service,
            )


@pytest.mark.asyncio
async def test_heartbeat_health_requires_running_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    class StoppedHeartbeat:
        running = False

    try:
        container.clear()

        container.register(
            "heartbeat",
            StoppedHeartbeat(),
        )

        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            lambda: ["heartbeat"],
        )

        service = HealthService()
        results = await service.diagnostics()

        heartbeat = results["heartbeat_task"]

        assert heartbeat.passed is False
        assert heartbeat.reason == ("Heartbeat service is not running.")

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )


@pytest.mark.asyncio
async def test_heartbeat_health_passes_when_task_and_service_are_running(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    class RunningHeartbeat:
        running = True

    try:
        container.clear()

        container.register(
            "heartbeat",
            RunningHeartbeat(),
        )

        monkeypatch.setattr(
            "jarvis.services.health_service.task_manager.list_tasks",
            lambda: ["heartbeat"],
        )

        service = HealthService()
        results = await service.diagnostics()

        assert results["heartbeat_task"].passed is True
        assert results["heartbeat_task"].reason is None

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )

class DegradedResilienceSnapshot:
    healthy = False
    summary = "resilience degraded"

    class Metrics:
        plans_started = 4
        plans_completed = 2
        plans_failed = 2

        steps_started = 8
        steps_completed = 5
        steps_failed = 3

        retries = 2
        timeouts = 1
        circuit_rejections = 1
        bulkhead_rejections = 0

        capability_failures: ClassVar[dict[str, int]] = {
            "smart_home.control": 2,
        }

    metrics = Metrics()


class DegradedResilienceRuntime:
    def snapshot(
        self,
    ) -> DegradedResilienceSnapshot:
        return DegradedResilienceSnapshot()


@pytest.mark.asyncio
async def test_diagnostics_reports_degraded_resilience_runtime() -> None:
    existing = dict(
        container._services  # type: ignore[attr-defined]
    )

    try:
        container.clear()

        container.register(
            "resilience_runtime",
            DegradedResilienceRuntime(),
        )

        service = HealthService()
        results = await service.diagnostics()

        result = results["resilience_runtime"]

        assert result.state is HealthState.DEGRADED
        assert result.passed is False
        assert result.available is True
        assert result.critical is False

        assert result.reason == (
            "Resilience runtime reports degraded state."
        )

        assert result.details == {
            "summary": "resilience degraded",
            "metrics": {
                "plans_started": 4,
                "plans_completed": 2,
                "plans_failed": 2,
                "steps_started": 8,
                "steps_completed": 5,
                "steps_failed": 3,
                "retries": 2,
                "timeouts": 1,
                "circuit_rejections": 1,
                "bulkhead_rejections": 0,
                "capability_failures": {
                    "smart_home.control": 2,
                },
            },
        }

    finally:
        container.clear()

        for name, registered_service in existing.items():
            container.register(
                name,
                registered_service,
            )