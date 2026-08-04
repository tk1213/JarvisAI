from datetime import UTC, datetime, timedelta

import pytest

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
        title="Execution incident",
        summary="Incident summary.",
        anomaly_codes=(
            "execution_timeout",
        ),
        capabilities=(
            "system.health",
        ),
        created_at=created_at,
    )


def test_timeline_orders_incidents_and_calculates_intervals() -> None:
    base = datetime(
        2026,
        8,
        1,
        10,
        0,
        tzinfo=UTC,
    )

    incidents = [
        make_incident(
            incident_id="execution-3",
            severity=ExecutionIncidentSeverity.HIGH,
            created_at=base + timedelta(
                hours=6
            ),
        ),
        make_incident(
            incident_id="execution-1",
            severity=ExecutionIncidentSeverity.LOW,
            created_at=base,
        ),
        make_incident(
            incident_id="execution-2",
            severity=ExecutionIncidentSeverity.MEDIUM,
            created_at=base + timedelta(
                hours=2
            ),
        ),
    ]

    timeline = ExecutionIncidentTimelineService().build(
        fingerprint="abc123",
        incidents=incidents,
        now=base + timedelta(
            hours=10
        ),
    )

    assert timeline is not None
    assert timeline.occurrence_count == 3
    assert timeline.first_seen == base
    assert timeline.last_seen == (
        base
        + timedelta(
            hours=6
        )
    )
    assert timeline.latest_severity == "high"
    assert timeline.average_interval_seconds == pytest.approx(
        3 * 60 * 60
    )
    assert timeline.age_seconds == pytest.approx(
        10 * 60 * 60
    )
    assert timeline.seconds_since_last == pytest.approx(
        4 * 60 * 60
    )
    assert [
        entry.incident_id
        for entry in timeline.entries
    ] == [
        "execution-1",
        "execution-2",
        "execution-3",
    ]


def test_timeline_single_incident_has_no_average_interval() -> None:
    created_at = datetime.now(
        UTC
    )

    timeline = ExecutionIncidentTimelineService().build(
        fingerprint="single",
        incidents=[
            make_incident(
                incident_id="execution-1",
                severity=ExecutionIncidentSeverity.LOW,
                created_at=created_at,
            )
        ],
        now=created_at,
    )

    assert timeline is not None
    assert timeline.average_interval_seconds is None
    assert timeline.occurrence_count == 1


def test_timeline_returns_none_for_empty_incident_list() -> None:
    timeline = ExecutionIncidentTimelineService().build(
        fingerprint="empty",
        incidents=[],
    )

    assert timeline is None


def test_timeline_rejects_empty_fingerprint() -> None:
    with pytest.raises(
        ValueError,
        match="fingerprint cannot be empty",
    ):
        ExecutionIncidentTimelineService().build(
            fingerprint=" ",
            incidents=[],
        )


def test_timeline_rejects_naive_now() -> None:
    incident = make_incident(
        incident_id="execution-1",
        severity=ExecutionIncidentSeverity.LOW,
        created_at=datetime.now(
            UTC
        ),
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        ExecutionIncidentTimelineService().build(
            fingerprint="abc123",
            incidents=[
                incident,
            ],
            now=datetime(  # noqa: DTZ001
                2026,
                8,
                1,
                10,
                0,
            ),
        )