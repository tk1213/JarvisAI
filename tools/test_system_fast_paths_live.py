from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.conversation_manager import ConversationManager


async def main() -> None:
    print("Sprint 6 Pack G3.3 — Deterministic System Fast Paths")
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

        cases = (
            (
                "system ping",
                "system.ping",
            ),
            (
                "system health",
                "system.health",
            ),
            (
                "Jarvis version",
                "system.version",
            ),
        )

        for text, expected_capability in cases:
            print()
            print(
                f"Input              : {text!r}"
            )

            resolved = (
                ConversationManager._resolve_system_capability(
                    text
                )
            )

            print(
                f"Resolved capability: {resolved!r}"
            )

            if resolved != expected_capability:
                raise RuntimeError(
                    f"Expected {expected_capability}, "
                    f"got {resolved!r}."
                )

            reply = await conversation.ask(
                text
            )

            print(
                f"Reply              : {reply!r}"
            )

            if not reply.strip():
                raise RuntimeError(
                    f"{expected_capability} returned an empty reply."
                )

            print(
                f"{expected_capability}: PASS"
            )

        print()
        print("Deterministic system ping   : PASS")
        print("Deterministic system health : PASS")
        print("Deterministic system version: PASS")
        print("Sprint 6 Pack G3.3: PASS")

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )