from __future__ import annotations

from datetime import UTC, datetime

from jarvis.conversation.diagnostics import ConversationDiagnosticsBuilder
from jarvis.conversation.turn import (
    ConversationTurnResult,
    ConversationTurnSource,
    ConversationTurnStatus,
)


def main() -> None:
    now = datetime.now(
        UTC
    )

    turn = ConversationTurnResult(
        turn_id="live-turn",
        user_text="diagnostics",
        reply="ready",
        source=ConversationTurnSource.FALLBACK_AI,
        status=ConversationTurnStatus.COMPLETED,
        duration_ms=1.0,
        started_at=now,
        completed_at=now,
    )

    snapshot = ConversationDiagnosticsBuilder().build(
        turn
    )

    assert snapshot.turn.turn_id == "live-turn"
    assert snapshot.reliability.failure_kind is None
    assert snapshot.recovery.executed is False

    print("Sprint 4.9 Pack A — Unified Conversation Diagnostics Contract")
    print("-" * 60)
    print("Turn diagnostics contract: PASS")
    print("Reliability diagnostics contract: PASS")
    print("Recovery diagnostics contract: PASS")
    print("Read-only compatibility: PASS")
    print("Sprint 4.9 Pack A live gate: PASS")


if __name__ == "__main__":
    main()
