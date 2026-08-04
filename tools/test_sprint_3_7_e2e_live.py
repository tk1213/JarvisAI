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
            "Sprint 3.7 End-to-End Execution Analytics Gate"
        )
        print(
            "=" * 60
        )

        for index, capability in enumerate(
            capabilities,
            start=1,
        ):
            result = await router.execute_request(
                CapabilityRequest(
                    capability=capability,
                )
            )

            print()
            print(
                f"[Gate {index}] {capability}"
            )
            print(
                f"Available: {result['available']}"
            )
            print(
                f"Summary: {result['summary']}"
            )

            if not result[
                "available"
            ]:
                raise RuntimeError(
                    f"{capability} is unavailable."
                )

        tool_definitions = container.get(
            "tool_definitions"
        )

        native_names = {
            definition.name
            for definition
            in tool_definitions.list_definitions()
        }

        expected_native = {
            "system_capability_reliability",
            "system_execution_health",
            "system_execution_health_trend",
            "system_execution_statistics",
        }

        forbidden_native = {
            "smart_home_toggle",
            "smart_home_turn_off",
            "smart_home_turn_on",
        }

        print()
        print(
            "[Gate 5] Native read-only tool surface"
        )
        print(
            "Analytics tools present: "
            f"{expected_native.issubset(native_names)}"
        )
        print(
            "Forbidden side-effect tools exposed: "
            f"{sorted(forbidden_native & native_names)}"
        )

        if not expected_native.issubset(
            native_names
        ):
            raise RuntimeError(
                "One or more analytics native tools are missing."
            )

        if forbidden_native & native_names:
            raise RuntimeError(
                "Side-effect tools leaked onto the read-only surface."
            )

        print()
        print(
            "Sprint 3.7 end-to-end gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
