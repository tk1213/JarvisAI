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

        result = await router.execute_request(
            CapabilityRequest(
                capability="system.execution_anomalies",
            )
        )

        tool_definitions = container.get(
            "tool_definitions"
        )

        native_names = {
            definition.name
            for definition
            in tool_definitions.list_definitions()
        }

        expected_native = (
            "system_execution_anomalies"
        )

        forbidden_native = {
            "smart_home_toggle",
            "smart_home_turn_off",
            "smart_home_turn_on",
        }

        print(
            "Sprint 3.8 End-to-End Execution Anomaly Gate"
        )
        print(
            "=" * 60
        )

        print(
            "[Gate 1] Anomaly capability"
        )
        print(
            f"Available: {result['available']}"
        )
        print(
            f"Summary: {result['summary']}"
        )

        print()
        print(
            "[Gate 2] Triage"
        )
        print(
            f"Summary: {result['triage_summary']}"
        )

        print()
        print(
            "[Gate 3] Advice"
        )
        print(
            f"Summary: {result['advice_summary']}"
        )

        print()
        print(
            "[Gate 4] Native read-only tool surface"
        )
        print(
            f"{expected_native}: "
            f"{expected_native in native_names}"
        )

        exposed_forbidden = sorted(
            forbidden_native
            & native_names
        )

        print(
            "Forbidden side-effect tools exposed: "
            f"{exposed_forbidden}"
        )

        if not result[
            "available"
        ]:
            raise RuntimeError(
                "Execution anomaly capability is unavailable."
            )

        if expected_native not in native_names:
            raise RuntimeError(
                "Execution anomaly native tool is missing."
            )

        if exposed_forbidden:
            raise RuntimeError(
                "Side-effect tools leaked onto the "
                "native read-only surface."
            )

        print()
        print(
            "Sprint 3.8 end-to-end gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
