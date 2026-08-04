from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        tool_definitions = container.get(
            "tool_definitions"
        )

        definitions = (
            tool_definitions.list_definitions()
        )

        names = {
            definition.name
            for definition in definitions
        }

        expected = "system_execution_anomalies"

        forbidden = {
            "smart_home_turn_on",
            "smart_home_turn_off",
            "smart_home_toggle",
        }

        print(
            "Sprint 3.8 Native Execution Anomaly Tool"
        )
        print(
            "-" * 60
        )
        print(
            f"Native tool count: {len(definitions)}"
        )
        print(
            f"{expected}: {expected in names}"
        )

        exposed_forbidden = sorted(
            forbidden & names
        )

        print(
            "Forbidden side-effect tools exposed: "
            f"{exposed_forbidden}"
        )

        if expected not in names:
            raise RuntimeError(
                "system_execution_anomalies is missing "
                "from the native read-only tool surface."
            )

        if exposed_forbidden:
            raise RuntimeError(
                "Side-effect tools leaked onto the "
                "native read-only surface."
            )

        print(
            "Native execution anomaly tool gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
