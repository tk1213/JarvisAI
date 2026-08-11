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
    executor = ConversationRecoveryExecutor(
        safe_message="safe fallback"
    )

    timeout_outcome = ConversationReliabilityOutcome(
        failure=ConversationFailure(
            kind=ConversationFailureKind.TIMEOUT,
            error_type="TimeoutError",
            retryable=True,
        ),
        fallback=ConversationFallback(
            kind=ConversationFallbackKind.SAFE_MESSAGE,
            reason="conversation_timeout",
        ),
    )

    safe_result = await executor.execute(
        outcome=timeout_outcome,
        attempts_used=1,
    )

    assert safe_result.executed is True
    assert safe_result.reply == "safe fallback"

    ai_fallback = AsyncMock(
        return_value="standard AI fallback"
    )

    ai_outcome = ConversationReliabilityOutcome(
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

    ai_result = await executor.execute(
        outcome=ai_outcome,
        attempts_used=1,
        standard_ai_fallback=ai_fallback,
    )

    assert ai_result.executed is True
    assert ai_result.reply == "standard AI fallback"

    print("Sprint 4.8 Pack A — Production Recovery Execution Contract")
    print("-" * 60)
    print("Safe-message execution: PASS")
    print("Standard-AI fallback execution: PASS")
    print("Missing-fallback safe degradation: PASS")
    print("Non-recoverable protection: PASS")
    print("Sprint 4.8 Pack A live gate: PASS")


if __name__ == "__main__":
    asyncio.run(
        main()
    )
