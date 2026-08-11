from datetime import UTC, datetime

from jarvis.agent.session import AIAgentSessionSnapshot
from jarvis.agent.session_report import (
    AIAgentSessionReportBuilder,
)


def test_session_report_formats_snapshot() -> None:
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

    report = AIAgentSessionReportBuilder().build(
        snapshot
    )

    assert (
        "pending_plan=False"
        in report.summary
    )
    assert (
        "memory_records=1"
        in report.summary
    )
    assert (
        "Latest goal: Check Jarvis"
        in report.lines
    )
