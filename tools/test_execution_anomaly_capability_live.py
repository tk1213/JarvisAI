from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_router import CapabilityRouter


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(start_background_tasks=False)

        router = container.resolve(
            "capability_router",
            CapabilityRouter,
        )

        result = await router.execute_request(
            CapabilityRequest(
                capability="system.execution_anomalies",
            )
        )

        print("Sprint 3.8 Execution Anomaly Capability")
        print("-" * 60)
        print(f"Available: {result['available']}")
        print(f"Summary: {result['summary']}")
        print(f"Triage: {result['triage_summary']}")
        print(f"Advice: {result['advice_summary']}")

        for line in result["anomalies"]:
            print(line)

        for line in result["advice"]:
            print(line)

        if not result["available"]:
            raise RuntimeError(
                "Execution anomaly capability is unavailable."
            )

        print("Execution anomaly capability gate: PASS")

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
