from __future__ import annotations

import asyncio

from jarvis.ai.openai_client import OpenAIClient
from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.capability_registry import CapabilityRegistry
from jarvis.services.capability_router import CapabilityRouter
from jarvis.tools.definitions import ToolDefinitionFactory
from jarvis.tools.executor import ToolExecutor
from jarvis.tools.openai_runner import OpenAIToolCallingRunner


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

        definitions = ToolDefinitionFactory(
            registry
        )

        executor = ToolExecutor(
            registry=registry,
            router=router,
        )

        runner = OpenAIToolCallingRunner(
            ai=OpenAIClient(),
            definitions=definitions,
            executor=executor,
        )

        result = await runner.run(
            "Check whether JarvisAI is running. "
            "Use the system ping tool if appropriate."
        )

        print(
            f"Final text: {result.text}"
        )
        print(
            f"Rounds: {result.rounds}"
        )
        print(
            f"Tool results: {len(result.tool_results)}"
        )

        for tool_result in result.tool_results:
            print(
                f"- {tool_result.name}: "
                f"success={tool_result.success} "
                f"output={tool_result.output!r} "
                f"error={tool_result.error!r}"
            )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
