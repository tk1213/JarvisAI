from jarvis.planner.execution_anomalies import (
    ExecutionAnomaly,
    ExecutionAnomalySeverity,
    ExecutionAnomalySummary,
)
from jarvis.planner.execution_incidents import (
    ExecutionIncidentService,
    ExecutionIncidentSeverity,
)


def test_incident_builds_from_prioritized_anomalies() -> None:
    anomalies = ExecutionAnomalySummary(
        total=3,
        critical=1,
        warnings=2,
        anomalies=(
            ExecutionAnomaly(
                code="execution_timeout",
                severity=ExecutionAnomalySeverity.WARNING,
                message="Timeout detected.",
            ),
            ExecutionAnomaly(
                code="unreliable_capability",
                severity=ExecutionAnomalySeverity.CRITICAL,
                capability="system.health",
                message="Reliability is low.",
            ),
            ExecutionAnomaly(
                code="worsening_execution_trend",
                severity=ExecutionAnomalySeverity.WARNING,
                message="Trend is worsening.",
            ),
        ),
    )

    incident = ExecutionIncidentService().build(
        anomalies
    )

    assert incident is not None
    assert (
        incident.severity
        is ExecutionIncidentSeverity.HIGH
    )
    assert incident.title == (
        "Execution incident: system.health"
    )
    assert incident.anomaly_codes[0] == (
        "unreliable_capability"
    )
    assert incident.capabilities == (
        "system.health",
    )
    assert incident.incident_id.startswith(
        "execution-"
    )


def test_incident_is_none_without_anomalies() -> None:
    anomalies = ExecutionAnomalySummary(
        total=0,
        critical=0,
        warnings=0,
        anomalies=(),
    )

    assert (
        ExecutionIncidentService().build(
            anomalies
        )
        is None
    )


def test_incident_critical_requires_multiple_critical_items() -> None:
    anomalies = ExecutionAnomalySummary(
        total=2,
        critical=2,
        warnings=0,
        anomalies=(
            ExecutionAnomaly(
                code="low_success_rate",
                severity=ExecutionAnomalySeverity.CRITICAL,
                message="Low success rate.",
            ),
            ExecutionAnomaly(
                code="repeated_timeouts",
                severity=ExecutionAnomalySeverity.CRITICAL,
                message="Repeated timeouts.",
            ),
        ),
    )

    incident = ExecutionIncidentService().build(
        anomalies
    )

    assert incident is not None
    assert (
        incident.severity
        is ExecutionIncidentSeverity.CRITICAL
    )
