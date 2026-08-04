from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.capability_registry import (
    CapabilityRegistry,
)
from jarvis.tools.definitions import ToolDefinitionFactory


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        registry = container.resolve(
            "capability_registry",
            CapabilityRegistry,
        )

        factory = ToolDefinitionFactory(
            registry
        )

        definitions = factory.list_definitions()

        history_tools = [
            definition
            for definition in definitions
            if (
                factory.resolve_capability_name(
                    definition.name
                )
                == "system.execution_history"
            )
        ]

        print(
            "Sprint 3.5 Execution History Tool Surface"
        )
        print(
            "-" * 60
        )

        print(
            f"Tool count: {len(definitions)}"
        )

        for definition in history_tools:
            capability = (
                factory.resolve_capability_name(
                    definition.name
                )
            )

            print(
                f"Tool: {definition.name}"
            )
            print(
                f"Capability: {capability}"
            )
            print(
                f"Parameters: {definition.parameters}"
            )

        if len(history_tools) != 1:
            raise RuntimeError(
                "Execution history tool surface is incorrect."
            )

        definition = history_tools[0]

        if (
            definition.name
            != "system_execution_history"
        ):
            raise RuntimeError(
                "Execution history tool name is incorrect."
            )

        if (
            factory.resolve_capability_name(
                definition.name
            )
            != "system.execution_history"
        ):
            raise RuntimeError(
                "Execution history capability mapping "
                "is incorrect."
            )

        print(
            "Execution history tool surface gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )