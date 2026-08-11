from __future__ import annotations

from dataclasses import dataclass

from jarvis.conversation.diagnostics import ConversationDiagnosticsSnapshot
from jarvis.conversation.reliability import ConversationFailureKind
from jarvis.conversation.turn import ConversationTurnStatus


@dataclass(slots=True, frozen=True)
class ConversationOperationalSnapshot:
    total_turns: int
    completed_turns: int
    failed_turns: int
    recovered_turns: int
    timeout_failures: int
    last_turn_id: str | None
    last_status: ConversationTurnStatus | None
    last_failure_kind: ConversationFailureKind | None

    @property
    def healthy(self) -> bool:
        return self.last_status is not ConversationTurnStatus.FAILED


class ConversationOperationalMetrics:
    """Lightweight in-memory counters for conversation runtime health."""

    def __init__(self) -> None:
        self._total_turns = 0
        self._completed_turns = 0
        self._failed_turns = 0
        self._recovered_turns = 0
        self._timeout_failures = 0
        self._last_snapshot: ConversationDiagnosticsSnapshot | None = None

    def observe(
        self,
        snapshot: ConversationDiagnosticsSnapshot,
    ) -> None:
        self._total_turns += 1
        self._last_snapshot = snapshot

        if snapshot.turn.status is ConversationTurnStatus.COMPLETED:
            self._completed_turns += 1

        if snapshot.turn.status is ConversationTurnStatus.FAILED:
            self._failed_turns += 1

        if snapshot.recovery.executed:
            self._recovered_turns += 1

        if (
            snapshot.reliability.failure_kind
            is ConversationFailureKind.TIMEOUT
        ):
            self._timeout_failures += 1

    def snapshot(
        self,
    ) -> ConversationOperationalSnapshot:
        last = self._last_snapshot

        return ConversationOperationalSnapshot(
            total_turns=self._total_turns,
            completed_turns=self._completed_turns,
            failed_turns=self._failed_turns,
            recovered_turns=self._recovered_turns,
            timeout_failures=self._timeout_failures,
            last_turn_id=(
                last.turn.turn_id
                if last is not None
                else None
            ),
            last_status=(
                last.turn.status
                if last is not None
                else None
            ),
            last_failure_kind=(
                last.reliability.failure_kind
                if last is not None
                else None
            ),
        )
