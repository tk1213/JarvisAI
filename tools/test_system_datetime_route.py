from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import ConversationManager


async def main() -> None:
    print("Sprint 6 Pack G1.3 — System Datetime Route Gate")
    print("-" * 60)

    app = JarvisApplication()

    await app.start(
        start_background_tasks=False,
    )

    try:
        conversation = container.resolve(
            "conversation",
            ConversationManager,
        )

        reply = await conversation.ask(
            "ตอนนี้กี่โมง"
        )

        print()
        print(
            f"Reply: {reply!r}"
        )

        normalized = reply.lower()

        if "ไม่มีเครื่องมือ" in normalized:
            raise RuntimeError(
                "Datetime tool was not used."
            )

        if "00:00" in normalized or "00:01" in normalized:
            raise RuntimeError(
                "Datetime route returned a placeholder time."
            )

        if ":" not in normalized:
            raise RuntimeError(
                "Datetime reply does not contain a time."
            )

        print()
        print("System datetime routing: PASS")

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )