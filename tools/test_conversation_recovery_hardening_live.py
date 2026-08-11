from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

from jarvis.conversation.recovery_execution import ConversationRecoveryExecutor
from jarvis.conversation.reliability import (
    ConversationFailure,
    ConversationFailureKind,
    ConversationFallback,
    ConversationFallbackKind,
    ConversationReliabilityOutcome,
)


async def main() -> None:
    fallback = AsyncMock(
        side_effect=TimeoutError(
            "secondary timeout"
        )
    )

    outcome = ConversationReliabilityOutcome(
        failure=ConversationFailure(
            kind=ConversationFailureKind.TOOL,
            error_type="RuntimeError",
            retryable=True,
        ),
        fallback=ConversationFallback(
            kind=ConversationFallbackKind.STANDARD_AI,
            reason="tool",
        ),
    )

    result = await ConversationRecoveryExecutor(
        safe_message="safe"
    ).execute(
        outcome=outcome,
        attempts_used=1,
        standard_ai_fallback=fallback,
    )

    assert result.reply == "safe"
    assert result.fallback_kind is ConversationFallbackKind.SAFE_MESSAGE
    assert result.fallback_error_type == "TimeoutError"
    fallback.assert_awaited_once()

    print("Sprint 4.8 Pack D — Standard-AI Recovery Hardening")
    print("-" * 60)
    print("Single fallback attempt: PASS")
    print("Fallback-loop protection: PASS")
    print("Fallback failure safe degradation: PASS")
    print("Fallback error observability: PASS")
    print("Sprint 4.8 Pack D live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
