from __future__ import annotations

import asyncio
import json

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.capability_registry import CapabilityRegistry
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

        tools = factory.to_openai_tools()

        print(
            f"Tool count: {len(tools)}"
        )

        for tool in tools:
            print(
                json.dumps(
                    tool,
                    ensure_ascii=False,
                )
            )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
