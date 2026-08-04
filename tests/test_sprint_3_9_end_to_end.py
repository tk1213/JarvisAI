from __future__ import annotations

from datetime import UTC, datetime, timedelta

from jarvis.planner.execution_incident_correlation import (
    ExecutionIncidentCorrelationService,
)
from jarvis.planner.execution_incident_dashboard import (
    ExecutionIncidentDashboardService,
)
from jarvis.planner.execution_incident_grouping import (
    ExecutionIncidentGroupingService,
)
from jarvis.planner.execution_incident_timeline import (
    ExecutionIncidentTimelineService,
)
from jarvis.planner.execution_incidents import (
    ExecutionIncident,
    ExecutionIncidentSeverity,
)


def make_incident(
    *,
    incident_id: str,
    severity: ExecutionIncidentSeverity,
    created_at: datetime,
) -> ExecutionIncident:
    return ExecutionIncident(
        incident_id=incident_id,
        severity=severity,
        title="Execution incident: system.health",
        summary="Incident summary.",
        anomaly_codes=(
            "execution_timeout",
            "unreliable_capability",
        ),
        capabilities=(
            "system.health",
        ),
        created_at=created_at,
    )


def test_incident_pipeline_builds_dashboard_snapshot() -> None:
    base = datetime(
        2026,
        8,
        4,
        10,
        0,
        tzinfo=UTC,
    )

    incidents = [
        make_incident(
            incident_id="execution-1",
            severity=ExecutionIncidentSeverity.HIGH,
            created_at=base,
        ),
        make_incident(
            incident_id="execution-2",
            severity=ExecutionIncidentSeverity.CRITICAL,
            created_at=base + timedelta(
                hours=2
            ),
        ),
    ]

    correlation_service = ExecutionIncidentCorrelationService()

    correlations = [
        correlation_service.correlate(
            incident
        )
        for incident in incidents
    ]

    assert (
        correlations[0].fingerprint
        == correlations[1].fingerprint
    )

    grouping = ExecutionIncidentGroupingService().group(
        correlations
    )

    assert grouping.total_incidents == 2
    assert grouping.total_groups == 1

    timeline = ExecutionIncidentTimelineService().build(
        fingerprint=correlations[0].fingerprint,
        incidents=incidents,
        now=base + timedelta(
            hours=4
        ),
    )

    assert timeline is not None
    assert timeline.occurrence_count == 2
    assert timeline.latest_severity == "critical"

    dashboard = ExecutionIncidentDashboardService().build(
        grouping=grouping,
        timelines=[
            timeline
        ],
    )

    assert dashboard.total_incidents == 2
    assert dashboard.total_groups == 1
    assert dashboard.latest_incident_id == "execution-2"
    assert dashboard.latest_severity == "critical"
