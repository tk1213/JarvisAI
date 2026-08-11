from __future__ import annotations

from dataclasses import dataclass

from jarvis.conversation.reliability import (
    ConversationFailureKind,
    ConversationFallbackKind,
)
from jarvis.conversation.turn import (
    ConversationTurnResult,
    ConversationTurnSource,
    ConversationTurnStatus,
)


@dataclass(slots=True, frozen=True)
class ConversationRecoveryDiagnostics:
    executed: bool
    fallback_kind: ConversationFallbackKind | None
    attempts_used: int | None
    fallback_error_type: str | None


@dataclass(slots=True, frozen=True)
class ConversationReliabilityDiagnostics:
    failure_kind: ConversationFailureKind | None
    retryable: bool | None


@dataclass(slots=True, frozen=True)
class ConversationTurnDiagnostics:
    turn_id: str
    source: ConversationTurnSource
    status: ConversationTurnStatus
    duration_ms: float
    error_type: str | None


@dataclass(slots=True, frozen=True)
class ConversationDiagnosticsSnapshot:
    turn: ConversationTurnDiagnostics
    reliability: ConversationReliabilityDiagnostics
    recovery: ConversationRecoveryDiagnostics


class ConversationDiagnosticsBuilder:
    """Build a stable, read-only operational snapshot from a turn result."""

    def build(
        self,
        turn: ConversationTurnResult,
    ) -> ConversationDiagnosticsSnapshot:
        failure = (
            turn.reliability.failure
            if turn.reliability is not None
            else None
        )

        recovery = turn.recovery_execution

        fallback_kind = getattr(
            recovery,
            "fallback_kind",
            None,
        )
        attempts_used = getattr(
            recovery,
            "attempts_used",
            None,
        )
        fallback_error_type = getattr(
            recovery,
            "fallback_error_type",
            None,
        )
        executed = bool(
            getattr(
                recovery,
                "executed",
                False,
            )
        )

        return ConversationDiagnosticsSnapshot(
            turn=ConversationTurnDiagnostics(
                turn_id=turn.turn_id,
                source=turn.source,
                status=turn.status,
                duration_ms=turn.duration_ms,
                error_type=turn.error_type,
            ),
            reliability=ConversationReliabilityDiagnostics(
                failure_kind=(
                    failure.kind
                    if failure is not None
                    else None
                ),
                retryable=(
                    failure.retryable
                    if failure is not None
                    else None
                ),
            ),
            recovery=ConversationRecoveryDiagnostics(
                executed=executed,
                fallback_kind=fallback_kind,
                attempts_used=attempts_used,
                fallback_error_type=fallback_error_type,
            ),
        )
