from __future__ import annotations

from jarvis.conversation.diagnostics import (
    ConversationDiagnosticsSnapshot,
    ConversationRecoveryDiagnostics,
    ConversationReliabilityDiagnostics,
    ConversationTurnDiagnostics,
)
from jarvis.conversation.operational_metrics import ConversationOperationalMetrics
from jarvis.conversation.reliability import ConversationFailureKind
from jarvis.conversation.turn import (
    ConversationTurnSource,
    ConversationTurnStatus,
)


def snapshot(
    *,
    status: ConversationTurnStatus,
    failure: ConversationFailureKind | None = None,
    recovered: bool = False,
) -> ConversationDiagnosticsSnapshot:
    return ConversationDiagnosticsSnapshot(
        turn=ConversationTurnDiagnostics(
            turn_id="turn",
            source=ConversationTurnSource.FALLBACK_AI,
            status=status,
            duration_ms=1.0,
            error_type=None,
        ),
        reliability=ConversationReliabilityDiagnostics(
            failure_kind=failure,
            retryable=(
                True
                if failure is not None
                else None
            ),
        ),
        recovery=ConversationRecoveryDiagnostics(
            executed=recovered,
            fallback_kind=None,
            attempts_used=None,
            fallback_error_type=None,
        ),
    )


def test_metrics_count_completed_turn() -> None:
    metrics = ConversationOperationalMetrics()

    metrics.observe(
        snapshot(
            status=ConversationTurnStatus.COMPLETED
        )
    )

    state = metrics.snapshot()

    assert state.total_turns == 1
    assert state.completed_turns == 1
    assert state.failed_turns == 0


def test_metrics_count_failed_recovered_timeout() -> None:
    metrics = ConversationOperationalMetrics()

    metrics.observe(
        snapshot(
            status=ConversationTurnStatus.FAILED,
            failure=ConversationFailureKind.TIMEOUT,
            recovered=True,
        )
    )

    state = metrics.snapshot()

    assert state.total_turns == 1
    assert state.failed_turns == 1
    assert state.recovered_turns == 1
    assert state.timeout_failures == 1
    assert state.last_failure_kind is ConversationFailureKind.TIMEOUT


def test_empty_metrics_snapshot_is_healthy() -> None:
    state = ConversationOperationalMetrics().snapshot()

    assert state.total_turns == 0
    assert state.last_turn_id is None
    assert state.healthy is True
