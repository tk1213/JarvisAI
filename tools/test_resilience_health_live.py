from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.resilience_runtime import (
    ResilienceRuntime,
)
from jarvis.services.health_service import HealthService


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        runtime = container.resolve(
            "resilience_runtime",
            ResilienceRuntime,
        )

        health = HealthService()

        snapshot = runtime.snapshot()
        details = await health.details()

        print(
            "Sprint 3.4 Resilience Health Wiring"
        )
        print(
            "-" * 60
        )
        print(
            "Runtime registered: "
            f"{container.has('resilience_runtime')}"
        )
        print(
            f"Resilience summary: {snapshot.summary}"
        )
        print(
            "Health check resilience_runtime: "
            f"{details['checks']['resilience_runtime']}"
        )
        print(
            "Plans observed: "
            f"{snapshot.metrics.plans_started}"
        )

        if not container.has(
            "resilience_runtime"
        ):
            raise RuntimeError(
                "Resilience runtime is not registered."
            )

        if not details[
            "checks"
        ][
            "resilience_runtime"
        ]:
            raise RuntimeError(
                "Health service did not see resilience runtime."
            )

        print(
            "Resilience health wiring gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
