from __future__ import annotations

from typing import Any

from jarvis.core.container import container
from jarvis.core.task_manager import task_manager
from jarvis.planner.resilience_runtime import (
    ResilienceRuntime,
)


class HealthService:
    async def check(self) -> dict[str, bool]:
        results: dict[str, bool] = {}

        results["service_container"] = (
            container.has("system")
            and container.has("commands")
            and container.has("database")
            and container.has("heartbeat")
        )

        database = container.get(
            "database"
        )
        results["database"] = (
            await database.health_check()
        )

        results["heartbeat_task"] = (
            "heartbeat"
            in task_manager.list_tasks()
        )

        system = container.get(
            "system"
        )
        results["system_service"] = (
            system is not None
        )

        results["resilience_runtime"] = (
            container.has(
                "resilience_runtime"
            )
        )

        return results

    async def details(
        self,
    ) -> dict[str, Any]:
        checks = await self.check()

        details: dict[str, Any] = {
            "checks": checks,
            "healthy": all(
                checks.values()
            ),
        }

        if container.has(
            "resilience_runtime"
        ):
            runtime = container.resolve(
                "resilience_runtime",
                ResilienceRuntime,
            )
            snapshot = runtime.snapshot()

            details["resilience"] = {
                "healthy": snapshot.healthy,
                "summary": snapshot.summary,
                "metrics": {
                    "plans_started": (
                        snapshot.metrics.plans_started
                    ),
                    "plans_completed": (
                        snapshot.metrics.plans_completed
                    ),
                    "plans_failed": (
                        snapshot.metrics.plans_failed
                    ),
                    "steps_started": (
                        snapshot.metrics.steps_started
                    ),
                    "steps_completed": (
                        snapshot.metrics.steps_completed
                    ),
                    "steps_failed": (
                        snapshot.metrics.steps_failed
                    ),
                    "retries": (
                        snapshot.metrics.retries
                    ),
                    "timeouts": (
                        snapshot.metrics.timeouts
                    ),
                    "circuit_rejections": (
                        snapshot.metrics.circuit_rejections
                    ),
                    "bulkhead_rejections": (
                        snapshot.metrics.bulkhead_rejections
                    ),
                    "capability_failures": dict(
                        snapshot.metrics.capability_failures
                    ),
                },
            }

        return details

    async def is_healthy(self) -> bool:
        results = await self.check()
        return all(
            results.values()
        )
