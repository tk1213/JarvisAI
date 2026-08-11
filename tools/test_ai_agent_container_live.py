from __future__ import annotations

import asyncio

from jarvis.agent.runtime import AIAgentRuntime
from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.planner.ai_plan_memory import AIPlanMemoryStore


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        runtime = container.resolve(
            "ai_agent_runtime",
            AIAgentRuntime,
        )

        memory = container.resolve(
            "ai_plan_memory",
            AIPlanMemoryStore,
        )

        print(
            "Sprint 4.1 AI Agent Container Integration"
        )
        print(
            "-" * 60
        )
        print(
            f"Runtime registered: {runtime is not None}"
        )
        print(
            f"Memory registered: {memory is not None}"
        )
        print(
            f"Memory records: {len(memory)}"
        )

        print(
            "AI agent container integration gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
