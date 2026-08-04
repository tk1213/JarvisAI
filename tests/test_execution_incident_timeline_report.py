from datetime import UTC, datetime, timedelta

from jarvis.planner.execution_incident_timeline import (
    ExecutionIncidentTimeline,
    ExecutionIncidentTimelineEntry,
)
from jarvis.planner.execution_incident_timeline_report import (
    ExecutionIncidentTimelineReportBuilder,
)


def test_timeline_report_formats_summary_and_entries() -> None:
    first_seen = datetime(
        2026,
        8,
        1,
        10,
        0,
        tzinfo=UTC,
    )

    timeline = ExecutionIncidentTimeline(
        fingerprint="abc123",
        occurrence_count=2,
        first_seen=first_seen,
        last_seen=first_seen + timedelta(
            hours=2
        ),
        latest_severity="high",
        average_interval_seconds=7200.0,
        age_seconds=36000.0,
        seconds_since_last=28800.0,
        entries=(
            ExecutionIncidentTimelineEntry(
                incident_id="execution-1",
                severity="low",
                title="Execution incident",
                occurred_at=first_seen,
            ),
            ExecutionIncidentTimelineEntry(
                incident_id="execution-2",
                severity="high",
                title="Execution incident",
                occurred_at=first_seen
                + timedelta(
                    hours=2
                ),
            ),
        ),
    )

    report = ExecutionIncidentTimelineReportBuilder().build(
        timeline
    )

    assert (
        "fingerprint=abc123"
        in report.summary
    )
    assert (
        "occurrences=2"
        in report.summary
    )
    assert (
        "Average interval: 2.0h"
        in report.lines
    )
    assert any(
        "execution-2"
        in line
        for line in report.lines
    )


def test_timeline_report_uses_na_for_single_incident() -> None:
    created_at = datetime.now(
        UTC
    )

    timeline = ExecutionIncidentTimeline(
        fingerprint="single",
        occurrence_count=1,
        first_seen=created_at,
        last_seen=created_at,
        latest_severity="low",
        average_interval_seconds=None,
        age_seconds=0.0,
        seconds_since_last=0.0,
        entries=(),
    )

    report = ExecutionIncidentTimelineReportBuilder().build(
        timeline
    )

    assert (
        "Average interval: n/a"
        in report.lines
    )
