from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from jarvis.conversation.recovery_execution import ConversationRecoveryExecutor
from jarvis.conversation.reliability import (
    ConversationFailure,
    ConversationFailureKind,
    ConversationFallback,
    ConversationFallbackKind,
    ConversationReliabilityOutcome,
)


def standard_ai_outcome() -> ConversationReliabilityOutcome:
    return ConversationReliabilityOutcome(
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


@pytest.mark.asyncio
async def test_standard_ai_fallback_runs_once() -> None:
    fallback = AsyncMock(
        return_value="recovered"
    )

    result = await ConversationRecoveryExecutor().execute(
        outcome=standard_ai_outcome(),
        attempts_used=1,
        standard_ai_fallback=fallback,
    )

    assert result.reply == "recovered"
    assert result.used_standard_ai is True
    assert result.fallback_failed is False
    fallback.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_standard_ai_fallback_degrades_to_safe_message() -> None:
    fallback = AsyncMock(
        side_effect=RuntimeError(
            "fallback failed"
        )
    )

    executor = ConversationRecoveryExecutor(
        safe_message="safe"
    )

    result = await executor.execute(
        outcome=standard_ai_outcome(),
        attempts_used=1,
        standard_ai_fallback=fallback,
    )

    assert result.reply == "safe"
    assert result.used_safe_message is True
    assert result.fallback_failed is True
    assert result.fallback_error_type == "RuntimeError"
    fallback.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_fallback_does_not_retry_itself() -> None:
    calls = 0

    async def fallback() -> str:
        nonlocal calls
        calls += 1
        raise TimeoutError(
            "fallback timeout"
        )

    result = await ConversationRecoveryExecutor(
        safe_message="safe"
    ).execute(
        outcome=standard_ai_outcome(),
        attempts_used=1,
        standard_ai_fallback=fallback,
    )

    assert calls == 1
    assert result.reply == "safe"
    assert result.fallback_error_type == "TimeoutError"


@pytest.mark.asyncio
async def test_non_recoverable_outcome_never_calls_fallback() -> None:
    fallback = AsyncMock(
        return_value="unused"
    )

    outcome = ConversationReliabilityOutcome(
        failure=ConversationFailure(
            kind=ConversationFailureKind.INTERNAL,
            error_type="RuntimeError",
            retryable=False,
        )
    )

    result = await ConversationRecoveryExecutor().execute(
        outcome=outcome,
        attempts_used=0,
        standard_ai_fallback=fallback,
    )

    assert result.executed is False
    fallback.assert_not_awaited()
