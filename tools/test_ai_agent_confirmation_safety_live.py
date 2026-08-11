from __future__ import annotations

import asyncio

from jarvis.agent.conversation_bridge import (
    AIAgentConversationBridge,
)
from jarvis.agent.runtime import AIAgentRuntime
from jarvis.core.application import JarvisApplication
from jarvis.core.container import container


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

        bridge = container.resolve(
            "ai_agent_conversation",
            AIAgentConversationBridge,
        )

        print(
            "Sprint 4.1 AI Agent Confirmation Safety"
        )
        print(
            "-" * 60
        )
        print(
            "Runtime pending contract available: "
            f"{hasattr(runtime, 'has_pending_plan')}"
        )
        print(
            "Bridge pending state: "
            f"{bridge.has_pending_plan}"
        )

        if not hasattr(
            runtime,
            "has_pending_plan",
        ):
            raise RuntimeError(
                "AIAgentRuntime pending-plan contract "
                "is unavailable."
            )

        print(
            "AI agent confirmation safety gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
