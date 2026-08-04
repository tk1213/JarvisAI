from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.services.capability_router import CapabilityRouter
from jarvis.tools.contracts import ToolCall
from jarvis.tools.executor import ToolExecutor


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
        router = container.resolve(
            "capability_router",
            CapabilityRouter,
        )

        executor = ToolExecutor(
            registry=registry,
            router=router,
        )

        capability = (
            "system.ping"
            if registry.is_allowed("system.ping")
            else registry.list_capabilities()[0]
        )

        result = await executor.execute(
            ToolCall(
                name=capability,
                call_id="live-test-1",
            )
        )

        print(
            f"Tool: {result.name}"
        )
        print(
            f"Success: {result.success}"
        )
        print(
            f"Call ID: {result.call_id}"
        )
        print(
            f"Output: {result.output!r}"
        )
        print(
            f"Error: {result.error!r}"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
