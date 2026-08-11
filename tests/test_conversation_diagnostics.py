from __future__ import annotations

from datetime import UTC, datetime

from jarvis.conversation.diagnostics import ConversationDiagnosticsBuilder
from jarvis.conversation.reliability import (
    ConversationFailure,
    ConversationFailureKind,
    ConversationFallback,
    ConversationFallbackKind,
    ConversationReliabilityOutcome,
)
from jarvis.conversation.turn import (
    ConversationTurnResult,
    ConversationTurnSource,
    ConversationTurnStatus,
)


def make_turn() -> ConversationTurnResult:
    now = datetime(
        2026,
        8,
        6,
        12,
        0,
        tzinfo=UTC,
    )

    return ConversationTurnResult(
        turn_id="turn-1",
        user_text="hello",
        reply="safe",
        source=ConversationTurnSource.FALLBACK_AI,
        status=ConversationTurnStatus.FAILED,
        duration_ms=25.0,
        started_at=now,
        completed_at=now,
        error_type="TimeoutError",
        reliability=ConversationReliabilityOutcome(
            failure=ConversationFailure(
                kind=ConversationFailureKind.TIMEOUT,
                error_type="TimeoutError",
                retryable=True,
            ),
            fallback=ConversationFallback(
                kind=ConversationFallbackKind.SAFE_MESSAGE,
                reason="timeout",
            ),
        ),
    )


def test_builder_maps_turn_and_reliability() -> None:
    snapshot = ConversationDiagnosticsBuilder().build(
        make_turn()
    )

    assert snapshot.turn.turn_id == "turn-1"
    assert snapshot.turn.status is ConversationTurnStatus.FAILED
    assert snapshot.turn.error_type == "TimeoutError"
    assert (
        snapshot.reliability.failure_kind
        is ConversationFailureKind.TIMEOUT
    )
    assert snapshot.reliability.retryable is True


def test_builder_has_safe_empty_recovery_defaults() -> None:
    snapshot = ConversationDiagnosticsBuilder().build(
        make_turn()
    )

    assert snapshot.recovery.executed is False
    assert snapshot.recovery.fallback_kind is None
    assert snapshot.recovery.attempts_used is None
    assert snapshot.recovery.fallback_error_type is None
