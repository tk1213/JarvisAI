from __future__ import annotations

import pytest

from jarvis.conversation.recovery import (
    ConversationRecoveryPolicy,
    ConversationRecoveryService,
)
from jarvis.conversation.reliability import (
    ConversationFailure,
    ConversationFailureKind,
    ConversationFallbackKind,
)


def failure(
    kind: ConversationFailureKind,
    *,
    retryable: bool,
) -> ConversationFailure:
    return ConversationFailure(
        kind=kind,
        error_type="RuntimeError",
        retryable=retryable,
    )


def test_timeout_uses_safe_message_fallback() -> None:
    outcome = ConversationRecoveryService().plan(
        failure=failure(
            ConversationFailureKind.TIMEOUT,
            retryable=True,
        ),
        attempts=0,
    )

    assert outcome.recovered is True
    assert outcome.fallback.kind is ConversationFallbackKind.SAFE_MESSAGE


def test_tool_failure_can_use_standard_ai_fallback() -> None:
    outcome = ConversationRecoveryService().plan(
        failure=failure(
            ConversationFailureKind.TOOL,
            retryable=True,
        ),
        attempts=0,
    )

    assert outcome.recovered is True
    assert outcome.fallback.kind is ConversationFallbackKind.STANDARD_AI


def test_non_retryable_failure_does_not_recover() -> None:
    outcome = ConversationRecoveryService().plan(
        failure=failure(
            ConversationFailureKind.INTERNAL,
            retryable=False,
        ),
        attempts=0,
    )

    assert outcome.recovered is False
    assert outcome.fallback.used is False


def test_recovery_attempts_are_bounded() -> None:
    service = ConversationRecoveryService(
        ConversationRecoveryPolicy(
            max_recovery_attempts=1
        )
    )

    first = service.plan(
        failure=failure(
            ConversationFailureKind.TIMEOUT,
            retryable=True,
        ),
        attempts=0,
    )

    second = service.plan(
        failure=failure(
            ConversationFailureKind.TIMEOUT,
            retryable=True,
        ),
        attempts=1,
    )

    assert first.recovered is True
    assert second.recovered is False


def test_invalid_recovery_limit_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="max_recovery_attempts",
    ):
        ConversationRecoveryPolicy(
            max_recovery_attempts=-1
        )
