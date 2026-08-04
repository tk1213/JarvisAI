from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.tools.safe import ReadOnlyToolDefinitionFactory


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(start_background_tasks=False)

        definitions = container.resolve(
            "tool_definitions",
            ReadOnlyToolDefinitionFactory,
        )

        names = [
            tool.name
            for tool in definitions.list_definitions()
        ]

        print("Execution coordination")
        print("-" * 60)
        print("Native read-only tools:")

        for name in names:
            print(f"- {name}")

        forbidden = {
            "smart_home_toggle",
            "smart_home_turn_off",
            "smart_home_turn_on",
        }

        exposed_forbidden = sorted(
            forbidden.intersection(names)
        )

        print()
        print(
            "Forbidden side-effect tools exposed: "
            f"{exposed_forbidden}"
        )

        if exposed_forbidden:
            raise RuntimeError(
                "Side-effect tools are exposed through "
                "native tool calling."
            )

        print("Coordination safety gate: PASS")

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
