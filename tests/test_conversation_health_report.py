from __future__ import annotations

from jarvis.conversation.health_report import ConversationHealthReporter
from jarvis.conversation.operational_metrics import ConversationOperationalSnapshot


def test_report_combines_operational_and_latest_turn() -> None:
    operational = ConversationOperationalSnapshot(
        total_turns=3,
        completed_turns=2,
        failed_turns=1,
        recovered_turns=1,
        timeout_failures=1,
        last_turn_id=None,
        last_status=None,
        last_failure_kind=None,
    )

    report = ConversationHealthReporter().build(
        operational=operational,
        latest_turn=None,
    )

    assert report.operational.total_turns == 3
    assert report.latest_turn is None
    assert report.healthy is True
