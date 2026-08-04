from jarvis.planner.execution_incident_dashboard import (
    ExecutionIncidentDashboardSnapshot,
)
from jarvis.planner.execution_incident_dashboard_report import (
    ExecutionIncidentDashboardReportBuilder,
)


def test_dashboard_report_formats_snapshot() -> None:
    snapshot = ExecutionIncidentDashboardSnapshot(
        total_incidents=3,
        total_groups=2,
        active_fingerprints=(
            "abc",
            "xyz",
        ),
        latest_severity="high",
        latest_incident_id="execution-3",
        oldest_first_seen="2026-08-01T10:00:00+00:00",
        newest_last_seen="2026-08-01T15:00:00+00:00",
    )

    report = ExecutionIncidentDashboardReportBuilder().build(
        snapshot
    )

    assert (
        "3 incident(s), 2 group(s)"
        in report.summary
    )
    assert (
        "latest_severity=high"
        in report.summary
    )
    assert (
        "Active fingerprints: abc, xyz"
        in report.lines
    )
    assert (
        "Latest incident ID: execution-3"
        in report.lines
    )


def test_dashboard_report_handles_empty_snapshot() -> None:
    snapshot = ExecutionIncidentDashboardSnapshot(
        total_incidents=0,
        total_groups=0,
        active_fingerprints=(),
        latest_severity="none",
        latest_incident_id=None,
        oldest_first_seen=None,
        newest_last_seen=None,
    )

    report = ExecutionIncidentDashboardReportBuilder().build(
        snapshot
    )

    assert (
        "Active fingerprints: none"
        in report.lines
    )
    assert (
        "Latest incident ID: none"
        in report.lines
    )
