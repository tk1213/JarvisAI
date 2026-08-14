from __future__ import annotations

from typing import Any

from jarvis.config import settings
from jarvis.core.container import container
from jarvis.core.task_manager import task_manager
from jarvis.planner.resilience_runtime import (
    ResilienceRuntime,
)
from jarvis.services.health_contracts import (
    HealthCheckResult,
    HealthState,
)


class HealthService:
    async def readiness(
        self,
    ) -> dict[str, HealthCheckResult]:
        results: dict[str, HealthCheckResult] = {}

        openai_ready = settings.has_openai_credentials

        results["openai_configuration"] = HealthCheckResult(
            name="openai_configuration",
            state=(HealthState.HEALTHY if openai_ready else HealthState.UNAVAILABLE),
            reason=(None if openai_ready else "OpenAI API credentials are missing."),
        )

        provider = settings.smart_home_provider.strip().lower()

        if provider == "mock":
            smart_home_state = HealthState.HEALTHY
            smart_home_reason = None

        elif provider == "tuya":
            if settings.has_tuya_credentials:
                smart_home_state = HealthState.HEALTHY
                smart_home_reason = None
            else:
                smart_home_state = HealthState.UNAVAILABLE
                smart_home_reason = "Tuya credentials are missing."

        else:
            smart_home_state = HealthState.UNAVAILABLE
            smart_home_reason = f"Unsupported smart-home provider: {provider}"

        results["smart_home_configuration"] = HealthCheckResult(
            name="smart_home_configuration",
            state=smart_home_state,
            reason=smart_home_reason,
            details={
                "provider": provider,
            },
        )

        return results

    async def runtime_readiness(
        self,
    ) -> dict[str, HealthCheckResult]:
        service_names = (
            "audio",
            "stt",
            "tts",
            "wake_word",
            "assistant_runtime",
            "smart_home",
            "smart_home_adapter",
        )

        results: dict[str, HealthCheckResult] = {}

        for name in service_names:
            available = container.has(name) and container.get(name) is not None

            results[name] = HealthCheckResult(
                name=name,
                state=(HealthState.HEALTHY if available else HealthState.UNAVAILABLE),
                reason=(
                    None if available else (f"Runtime service is unavailable: {name}")
                ),
            )

        return results

    async def full_readiness(
        self,
    ) -> dict[str, HealthCheckResult]:
        configuration = await self.readiness()
        runtime = await self.runtime_readiness()

        return {
            **configuration,
            **runtime,
        }

    async def operational_diagnostics(
        self,
    ) -> dict[str, HealthCheckResult]:
        diagnostics = await self.diagnostics()
        readiness = await self.full_readiness()

        return {
            **diagnostics,
            **readiness,
        }

    async def is_operationally_ready(
        self,
    ) -> bool:
        results = await self.operational_diagnostics()

        return all(result.passed for result in results.values() if result.critical)

    async def diagnostics(
        self,
    ) -> dict[str, HealthCheckResult]:
        results: dict[str, HealthCheckResult] = {}

        service_container_healthy = (
            container.has("system")
            and container.has("commands")
            and container.has("database")
            and container.has("heartbeat")
        )

        results["service_container"] = HealthCheckResult(
            name="service_container",
            state=(
                HealthState.HEALTHY
                if service_container_healthy
                else HealthState.UNAVAILABLE
            ),
            reason=(
                None
                if service_container_healthy
                else "Required services are missing from the container."
            ),
        )

        database_healthy = False
        database_reason: str | None = None

        if container.has("database"):
            database = container.get("database")

            try:
                database_healthy = await database.health_check()
            except Exception as exc:  # noqa: BLE001
                database_reason = (
                    f"Database health check raised {type(exc).__name__}: {exc}"
                )
        else:
            database_reason = "Database service is unavailable."

        results["database"] = HealthCheckResult(
            name="database",
            state=(
                HealthState.HEALTHY if database_healthy else HealthState.UNAVAILABLE
            ),
            reason=(
                None
                if database_healthy
                else (database_reason or "Database health check failed.")
            ),
        )

        heartbeat_task_running = "heartbeat" in task_manager.list_tasks()

        heartbeat_service_running = False

        if container.has("heartbeat"):
            heartbeat_service = container.get("heartbeat")
            heartbeat_service_running = bool(
                getattr(
                    heartbeat_service,
                    "running",
                    False,
                )
            )

        heartbeat_healthy = heartbeat_task_running and heartbeat_service_running

        results["heartbeat_task"] = HealthCheckResult(
            name="heartbeat_task",
            state=(
                HealthState.HEALTHY if heartbeat_healthy else HealthState.UNAVAILABLE
            ),
            reason=(
                None
                if heartbeat_healthy
                else (
                    "Heartbeat task is not running."
                    if not heartbeat_task_running
                    else "Heartbeat service is not running."
                )
            ),
        )

        system_healthy = container.has("system") and container.get("system") is not None

        results["system_service"] = HealthCheckResult(
            name="system_service",
            state=(HealthState.HEALTHY if system_healthy else HealthState.UNAVAILABLE),
            reason=(None if system_healthy else "System service is unavailable."),
        )

        resilience_healthy = container.has("resilience_runtime")

        results["resilience_runtime"] = HealthCheckResult(
            name="resilience_runtime",
            state=(
                HealthState.HEALTHY if resilience_healthy else HealthState.UNAVAILABLE
            ),
            reason=(
                None if resilience_healthy else "Resilience runtime is unavailable."
            ),
        )

        return results

    async def check(self) -> dict[str, bool]:
        diagnostics = await self.diagnostics()

        return {name: result.passed for name, result in diagnostics.items()}

    async def details(
        self,
    ) -> dict[str, Any]:
        checks = await self.check()

        details: dict[str, Any] = {
            "checks": checks,
            "healthy": all(checks.values()),
        }

        if container.has("resilience_runtime"):
            runtime = container.resolve(
                "resilience_runtime",
                ResilienceRuntime,
            )
            snapshot = runtime.snapshot()

            details["resilience"] = {
                "healthy": snapshot.healthy,
                "summary": snapshot.summary,
                "metrics": {
                    "plans_started": (snapshot.metrics.plans_started),
                    "plans_completed": (snapshot.metrics.plans_completed),
                    "plans_failed": (snapshot.metrics.plans_failed),
                    "steps_started": (snapshot.metrics.steps_started),
                    "steps_completed": (snapshot.metrics.steps_completed),
                    "steps_failed": (snapshot.metrics.steps_failed),
                    "retries": (snapshot.metrics.retries),
                    "timeouts": (snapshot.metrics.timeouts),
                    "circuit_rejections": (snapshot.metrics.circuit_rejections),
                    "bulkhead_rejections": (snapshot.metrics.bulkhead_rejections),
                    "capability_failures": dict(snapshot.metrics.capability_failures),
                },
            }

        return details

    async def is_healthy(self) -> bool:
        results = await self.check()

        return all(results.values())
