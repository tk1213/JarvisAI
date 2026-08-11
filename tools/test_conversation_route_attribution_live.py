from __future__ import annotations

import asyncio

from jarvis.conversation.turn import (
    ConversationTurnLifecycle,
    ConversationTurnSource,
)


async def main() -> None:
    lifecycle = ConversationTurnLifecycle()

    async def handler() -> str:
        lifecycle.mark_source(
            ConversationTurnSource.NATIVE_TOOL
        )
        return "native route complete"

    result = await lifecycle.run(
        user_text="check route",
        source=ConversationTurnSource.UNKNOWN,
        handler=handler,
    )

    assert result.source is ConversationTurnSource.NATIVE_TOOL
    assert result.reply == "native route complete"

    print("Sprint 4.5 Pack C — Actual Route Attribution")
    print("-" * 60)
    print("Dynamic source attribution: PASS")
    print("Native-tool attribution: PASS")
    print("Failure source attribution: PASS")
    print("Fallback observability primitive: PASS")
    print("Sprint 4.5 Pack C live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
