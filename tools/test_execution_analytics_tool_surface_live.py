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

        expected = {
            "system_execution_statistics",
            "system_capability_reliability",
            "system_execution_health",
            "system_execution_health_trend",
        }

        forbidden = {
            "smart_home_turn_on",
            "smart_home_turn_off",
            "smart_home_toggle",
        }

        print(
            "Sprint 3.7 Native Execution Analytics Tools"
        )
        print(
            "-" * 60
        )
        print(
            f"Native tool count: {len(definitions)}"
        )

        for name in sorted(
            expected
        ):
            print(
                f"{name}: {name in names}"
            )

        exposed_forbidden = sorted(
            forbidden & names
        )

        print(
            f"Forbidden side-effect tools exposed: {exposed_forbidden}"
        )

        missing = sorted(
            expected - names
        )

        if missing:
            raise RuntimeError(
                "Missing execution analytics tool(s): "
                + ", ".join(
                    missing
                )
            )

        if exposed_forbidden:
            raise RuntimeError(
                "Side-effect tool(s) leaked onto read-only surface: "
                + ", ".join(
                    exposed_forbidden
                )
            )

        print(
            "Native execution analytics tool gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
