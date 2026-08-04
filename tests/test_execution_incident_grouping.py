from jarvis.planner.execution_incident_correlation import (
    ExecutionIncidentCorrelation,
)
from jarvis.planner.execution_incident_grouping import (
    ExecutionIncidentGroupingService,
)


def make_correlation(
    *,
    fingerprint: str,
    incident_id: str,
    severity: str,
    capability: str,
) -> ExecutionIncidentCorrelation:
    return ExecutionIncidentCorrelation(
        fingerprint=fingerprint,
        incident_id=incident_id,
        severity=severity,
        anomaly_codes=(
            "execution_timeout",
        ),
        capabilities=(
            capability,
        ),
        correlation_key=(
            "anomalies=execution_timeout"
            f"|capabilities={capability}"
        ),
    )


def test_grouping_combines_matching_fingerprints() -> None:
    service = ExecutionIncidentGroupingService()

    summary = service.group(
        [
            make_correlation(
                fingerprint="same",
                incident_id="execution-1",
                severity="high",
                capability="system.health",
            ),
            make_correlation(
                fingerprint="same",
                incident_id="execution-2",
                severity="critical",
                capability="system.health",
            ),
            make_correlation(
                fingerprint="other",
                incident_id="execution-3",
                severity="medium",
                capability="system.ping",
            ),
        ]
    )

    assert summary.total_incidents == 3
    assert summary.total_groups == 2

    by_fingerprint = {
        group.fingerprint: group
        for group in summary.groups
    }

    same = by_fingerprint[
        "same"
    ]

    assert same.occurrence_count == 2
    assert same.incident_ids == (
        "execution-1",
        "execution-2",
    )
    assert same.severities == (
        "critical",
        "high",
    )
    assert same.capabilities == (
        "system.health",
    )


def test_grouping_handles_empty_input() -> None:
    summary = ExecutionIncidentGroupingService().group(
        []
    )

    assert summary.total_incidents == 0
    assert summary.total_groups == 0
    assert summary.groups == ()
