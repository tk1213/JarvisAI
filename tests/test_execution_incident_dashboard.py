from datetime import UTC, datetime, timedelta

from jarvis.planner.execution_incident_dashboard import (
    ExecutionIncidentDashboardService,
)
from jarvis.planner.execution_incident_grouping import (
    ExecutionIncidentGroup,
    ExecutionIncidentGroupingSummary,
)
from jarvis.planner.execution_incident_timeline import (
    ExecutionIncidentTimeline,
    ExecutionIncidentTimelineEntry,
)


def make_timeline(
    *,
    fingerprint: str,
    incident_id: str,
    severity: str,
    first_seen: datetime,
    last_seen: datetime,
) -> ExecutionIncidentTimeline:
    return ExecutionIncidentTimeline(
        fingerprint=fingerprint,
        occurrence_count=1,
        first_seen=first_seen,
        last_seen=last_seen,
        latest_severity=severity,
        average_interval_seconds=None,
        age_seconds=0.0,
        seconds_since_last=0.0,
        entries=(
            ExecutionIncidentTimelineEntry(
                incident_id=incident_id,
                severity=severity,
                title="Execution incident",
                occurred_at=last_seen,
            ),
        ),
    )


def test_dashboard_summarizes_groups_and_timelines() -> None:
    base = datetime(
        2026,
        8,
        1,
        10,
        0,
        tzinfo=UTC,
    )

    grouping = ExecutionIncidentGroupingSummary(
        total_incidents=3,
        total_groups=2,
        groups=(
            ExecutionIncidentGroup(
                fingerprint="abc",
                incident_ids=(
                    "execution-1",
                    "execution-2",
                ),
                severities=(
                    "high",
                ),
                anomaly_codes=(
                    "execution_timeout",
                ),
                capabilities=(
                    "system.health",
                ),
                occurrence_count=2,
            ),
            ExecutionIncidentGroup(
                fingerprint="xyz",
                incident_ids=(
                    "execution-3",
                ),
                severities=(
                    "medium",
                ),
                anomaly_codes=(
                    "degraded_success_rate",
                ),
                capabilities=(),
                occurrence_count=1,
            ),
        ),
    )

    snapshot = ExecutionIncidentDashboardService().build(
        grouping=grouping,
        timelines=[
            make_timeline(
                fingerprint="abc",
                incident_id="execution-2",
                severity="high",
                first_seen=base,
                last_seen=base + timedelta(
                    hours=3
                ),
            ),
            make_timeline(
                fingerprint="xyz",
                incident_id="execution-3",
                severity="medium",
                first_seen=base + timedelta(
                    hours=1
                ),
                last_seen=base + timedelta(
                    hours=5
                ),
            ),
        ],
    )

    assert snapshot.total_incidents == 3
    assert snapshot.total_groups == 2
    assert snapshot.active_fingerprints == (
        "abc",
        "xyz",
    )
    assert snapshot.latest_severity == "medium"
    assert snapshot.latest_incident_id == "execution-3"
    assert snapshot.oldest_first_seen == base.isoformat()
    assert snapshot.newest_last_seen == (
        base
        + timedelta(
            hours=5
        )
    ).isoformat()


def test_dashboard_handles_empty_data() -> None:
    snapshot = ExecutionIncidentDashboardService().build(
        grouping=ExecutionIncidentGroupingSummary(
            total_incidents=0,
            total_groups=0,
            groups=(),
        ),
        timelines=[],
    )

    assert snapshot.total_incidents == 0
    assert snapshot.total_groups == 0
    assert snapshot.active_fingerprints == ()
    assert snapshot.latest_severity == "none"
    assert snapshot.latest_incident_id is None
