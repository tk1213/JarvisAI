from __future__ import annotations

import asyncio

from jarvis.conversation.turn import (
    ConversationTurnLifecycle,
    ConversationTurnSource,
)


async def main() -> None:
    lifecycle = ConversationTurnLifecycle(
        max_history=3
    )

    async def handler() -> str:
        lifecycle.mark_source(
            ConversationTurnSource.NATIVE_TOOL
        )
        return "traced"

    for index in range(4):
        await lifecycle.run(
            user_text=f"turn-{index}",
            source=ConversationTurnSource.UNKNOWN,
            handler=handler,
        )

    history = lifecycle.list_recent(
        limit=10
    )

    assert len(history) == 3
    assert history[0].user_text == "turn-3"
    assert history[0].source is ConversationTurnSource.NATIVE_TOOL
    assert history[0].turn_id
    assert history[0].started_at is not None
    assert history[0].completed_at is not None

    print("Sprint 4.5 Pack D — Production Turn Tracing")
    print("-" * 60)
    print("Turn ID tracing: PASS")
    print("Timestamp tracing: PASS")
    print("Bounded history: PASS")
    print("Actual route preserved: PASS")
    print("Sprint 4.5 Pack D live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
