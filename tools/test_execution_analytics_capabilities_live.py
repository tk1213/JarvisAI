from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_router import CapabilityRouter


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        router = container.resolve(
            "capability_router",
            CapabilityRouter,
        )

        capabilities = (
            "system.execution_statistics",
            "system.capability_reliability",
            "system.execution_health",
            "system.execution_health_trend",
        )

        print(
            "Sprint 3.7 Execution Analytics Capabilities"
        )
        print(
            "-" * 60
        )

        for capability in capabilities:
            result = await router.execute_request(
                CapabilityRequest(
                    capability=capability,
                )
            )

            print(
                f"{capability}:"
            )
            print(
                f"  available={result['available']}"
            )
            print(
                f"  summary={result['summary']}"
            )

            if not result[
                "available"
            ]:
                raise RuntimeError(
                    f"{capability} is unavailable."
                )

        print(
            "Execution analytics capability gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
