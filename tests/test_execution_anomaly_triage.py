from jarvis.planner.execution_anomalies import (
    ExecutionAnomaly,
    ExecutionAnomalySeverity,
    ExecutionAnomalySummary,
)
from jarvis.planner.execution_anomaly_triage import (
    ExecutionAnomalyTriageService,
)


def test_triage_orders_by_severity_then_capability() -> None:
    summary = ExecutionAnomalySummary(
        total=4,
        critical=2,
        warnings=1,
        anomalies=(
            ExecutionAnomaly(
                code="warning_b",
                severity=ExecutionAnomalySeverity.WARNING,
                message="warning",
                capability="system.version",
            ),
            ExecutionAnomaly(
                code="critical_b",
                severity=ExecutionAnomalySeverity.CRITICAL,
                message="critical",
                capability="system.version",
            ),
            ExecutionAnomaly(
                code="critical_a",
                severity=ExecutionAnomalySeverity.CRITICAL,
                message="critical",
                capability="system.health",
            ),
            ExecutionAnomaly(
                code="info_a",
                severity=ExecutionAnomalySeverity.INFO,
                message="info",
            ),
        ),
    )

    triage = ExecutionAnomalyTriageService().prioritize(
        summary
    )

    assert triage.total == 4
    assert (
        triage.highest_severity
        is ExecutionAnomalySeverity.CRITICAL
    )

    assert [
        item.anomaly.code
        for item in triage.items
    ] == [
        "critical_a",
        "critical_b",
        "warning_b",
        "info_a",
    ]

    assert [
        item.priority
        for item in triage.items
    ] == [
        1,
        2,
        3,
        4,
    ]


def test_triage_handles_empty_summary() -> None:
    summary = ExecutionAnomalySummary(
        total=0,
        critical=0,
        warnings=0,
        anomalies=(),
    )

    triage = ExecutionAnomalyTriageService().prioritize(
        summary
    )

    assert triage.total == 0
    assert triage.highest_severity is None
    assert triage.items == ()
