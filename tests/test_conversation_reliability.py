from __future__ import annotations

from jarvis.conversation.reliability import (
    ConversationFailure,
    ConversationFailureClassifier,
    ConversationFailureKind,
    ConversationFallback,
    ConversationFallbackKind,
    ConversationReliabilityOutcome,
)


def test_timeout_is_classified_as_retryable() -> None:
    failure = ConversationFailureClassifier().classify(
        TimeoutError(
            "turn timeout"
        )
    )

    assert failure.kind is ConversationFailureKind.TIMEOUT
    assert failure.retryable is True
    assert failure.error_type == "TimeoutError"


def test_unknown_exception_is_internal_and_not_retryable() -> None:
    failure = ConversationFailureClassifier().classify(
        RuntimeError(
            "boom"
        )
    )

    assert failure.kind is ConversationFailureKind.INTERNAL
    assert failure.retryable is False
    assert failure.error_type == "RuntimeError"


def test_fallback_used_property() -> None:
    assert ConversationFallback().used is False

    fallback = ConversationFallback(
        kind=ConversationFallbackKind.STANDARD_AI,
        reason="native tool failed",
    )

    assert fallback.used is True


def test_reliability_outcome_detects_recovery() -> None:
    outcome = ConversationReliabilityOutcome(
        failure=ConversationFailure(
            kind=ConversationFailureKind.TOOL,
            error_type="RuntimeError",
        ),
        fallback=ConversationFallback(
            kind=ConversationFallbackKind.STANDARD_AI,
            reason="tool runner failed",
        ),
    )

    assert outcome.failed is True
    assert outcome.recovered is True


def test_failure_without_fallback_is_not_recovered() -> None:
    outcome = ConversationReliabilityOutcome(
        failure=ConversationFailure(
            kind=ConversationFailureKind.PLANNER,
            error_type="ValueError",
        )
    )

    assert outcome.failed is True
    assert outcome.recovered is False
