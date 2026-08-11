from __future__ import annotations

from datetime import UTC, datetime

from jarvis.agent.session import AIAgentSessionSnapshot


def test_session_snapshot_old_constructor_remains_compatible() -> None:
    snapshot = AIAgentSessionSnapshot(
        has_pending_plan=False,
        memory_records=1,
        latest_goal="Check Jarvis",
        latest_success=True,
        created_at=datetime(
            2026,
            8,
            5,
            10,
            0,
            tzinfo=UTC,
        ),
    )

    assert snapshot.latest_memory_source is None
    assert snapshot.last_run_status is None
    assert snapshot.last_replan_attempts == 0
