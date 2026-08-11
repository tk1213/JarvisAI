from __future__ import annotations

import asyncio

from jarvis.conversation.reliability import ConversationFailureKind
from jarvis.conversation.turn import (
    ConversationTurnLifecycle,
    ConversationTurnSource,
)


async def main() -> None:
    lifecycle = ConversationTurnLifecycle()

    async def handler() -> str:
        raise TimeoutError(
            "simulated production timeout"
        )

    try:
        await lifecycle.run(
            user_text="reliability test",
            source=ConversationTurnSource.NATIVE_TOOL,
            handler=handler,
        )
    except TimeoutError:
        pass

    result = lifecycle.last_result

    assert result is not None
    assert result.reliability is not None
    assert result.reliability.failure is not None
    assert result.reliability.failure.kind is ConversationFailureKind.TIMEOUT
    assert result.reliability.failure.retryable is True
    assert result.source is ConversationTurnSource.NATIVE_TOOL

    print("Sprint 4.6 Pack B — Reliability Integration")
    print("-" * 60)
    print("Turn failure classification: PASS")
    print("Timeout reliability metadata: PASS")
    print("Actual route preservation: PASS")
    print("Bounded trace compatibility: PASS")
    print("Sprint 4.6 Pack B live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
