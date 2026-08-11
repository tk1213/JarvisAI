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


def outcome(
    fallback_kind: ConversationFallbackKind,
) -> ConversationReliabilityOutcome:
    return ConversationReliabilityOutcome(
        failure=ConversationFailure(
            kind=ConversationFailureKind.TIMEOUT,
            error_type="TimeoutError",
            retryable=True,
        ),
        fallback=ConversationFallback(
            kind=fallback_kind,
            reason="test",
        ),
    )


@pytest.mark.asyncio
async def test_safe_message_recovery_executes_without_ai_call() -> None:
    executor = ConversationRecoveryExecutor(
        safe_message="safe"
    )

    fallback = AsyncMock(
        return_value="unused"
    )

    result = await executor.execute(
        outcome=outcome(
            ConversationFallbackKind.SAFE_MESSAGE
        ),
        attempts_used=1,
        standard_ai_fallback=fallback,
    )

    assert result.executed is True
    assert result.reply == "safe"
    assert result.used_safe_message is True
    fallback.assert_not_awaited()


@pytest.mark.asyncio
async def test_standard_ai_recovery_calls_fallback_once() -> None:
    executor = ConversationRecoveryExecutor()

    fallback = AsyncMock(
        return_value="fallback reply"
    )

    result = await executor.execute(
        outcome=outcome(
            ConversationFallbackKind.STANDARD_AI
        ),
        attempts_used=1,
        standard_ai_fallback=fallback,
    )

    assert result.executed is True
    assert result.reply == "fallback reply"
    assert result.used_standard_ai is True
    fallback.assert_awaited_once()


@pytest.mark.asyncio
async def test_missing_standard_ai_fallback_degrades_to_safe_message() -> None:
    executor = ConversationRecoveryExecutor(
        safe_message="safe"
    )

    result = await executor.execute(
        outcome=outcome(
            ConversationFallbackKind.STANDARD_AI
        ),
        attempts_used=1,
        standard_ai_fallback=None,
    )

    assert result.executed is True
    assert result.reply == "safe"
    assert result.used_safe_message is True


@pytest.mark.asyncio
async def test_non_recovered_outcome_does_not_execute() -> None:
    executor = ConversationRecoveryExecutor()

    result = await executor.execute(
        outcome=ConversationReliabilityOutcome(
            failure=ConversationFailure(
                kind=ConversationFailureKind.INTERNAL,
                error_type="RuntimeError",
                retryable=False,
            )
        ),
        attempts_used=0,
    )

    assert result.executed is False
    assert result.reply == ""
    assert result.fallback_kind is ConversationFallbackKind.NONE


def test_safe_message_is_observable() -> None:
    executor = ConversationRecoveryExecutor(
        safe_message="custom safe reply"
    )

    assert executor.safe_message == "custom safe reply"
