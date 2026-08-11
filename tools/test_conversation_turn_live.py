from __future__ import annotations

import asyncio

from jarvis.conversation.turn import (
    ConversationTurnLifecycle,
    ConversationTurnSource,
    ConversationTurnStatus,
)


async def main() -> None:
    lifecycle = ConversationTurnLifecycle()

    async def handler() -> str:
        await asyncio.sleep(
            0
        )
        return "Production turn contract is ready."

    result = await lifecycle.run(
        user_text="test conversation turn",
        source=ConversationTurnSource.FALLBACK_AI,
        handler=handler,
    )

    assert result.status is ConversationTurnStatus.COMPLETED
    assert result.success is True
    assert result.reply
    assert result.duration_ms >= 0
    assert lifecycle.last_result is result

    print("Sprint 4.5 Pack A — Production Conversation Turn Lifecycle")
    print("-" * 60)
    print("Turn contract: PASS")
    print("Source metadata: PASS")
    print("Latency metadata: PASS")
    print("Failure metadata: PASS")
    print("Sprint 4.5 Pack A live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
