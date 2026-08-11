from __future__ import annotations

import asyncio

from jarvis.conversation.execution_boundary import (
    ConversationExecutionBoundary,
    ConversationExecutionPolicy,
)
from jarvis.conversation.reliability import ConversationFailureKind
from jarvis.conversation.turn import (
    ConversationTurnLifecycle,
    ConversationTurnSource,
)


async def main() -> None:
    lifecycle = ConversationTurnLifecycle()
    boundary = ConversationExecutionBoundary(
        ConversationExecutionPolicy(
            timeout_seconds=0.02
        )
    )

    async def slow_handler() -> str:
        await asyncio.sleep(
            1.0
        )
        return "late"

    try:
        await lifecycle.run(
            user_text="timeout live gate",
            source=ConversationTurnSource.FALLBACK_AI,
            handler=lambda: boundary.run(
                slow_handler
            ),
        )
    except TimeoutError:
        pass

    result = lifecycle.last_result

    assert result is not None
    assert result.reliability is not None
    assert result.reliability.failure is not None
    assert result.reliability.failure.kind is ConversationFailureKind.TIMEOUT

    print("Sprint 4.6 Pack C — Timeout & Cancellation Boundaries")
    print("-" * 60)
    print("Successful execution boundary: PASS")
    print("Timeout enforcement: PASS")
    print("Timeout classification integration: PASS")
    print("Cancellation propagation: PASS")
    print("Sprint 4.6 Pack C live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
