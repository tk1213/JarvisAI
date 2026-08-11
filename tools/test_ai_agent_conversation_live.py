from __future__ import annotations

import asyncio

from jarvis.agent.conversation_bridge import (
    AIAgentConversationBridge,
)
from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import (
    ConversationManager,
)


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        bridge = container.resolve(
            "ai_agent_conversation",
            AIAgentConversationBridge,
        )

        conversation = container.resolve(
            "conversation",
            ConversationManager,
        )

        print(
            "Sprint 4.1 AI Agent Conversation Integration"
        )
        print(
            "-" * 60
        )
        print(
            f"Bridge registered: {bridge is not None}"
        )
        print(
            f"Conversation available: {conversation is not None}"
        )

        reply = await conversation.ask(
            
                "Check whether JarvisAI is responding "
                "and healthy using read-only capabilities."
            
        )

        print(
            f"Reply: {reply}"
        )

        if not reply.strip():
            raise RuntimeError(
                "Conversation returned an empty reply."
            )

        print(
            "AI agent conversation integration gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
