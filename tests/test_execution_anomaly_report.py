from jarvis.planner.execution_anomalies import (
    ExecutionAnomaly,
    ExecutionAnomalySeverity,
    ExecutionAnomalySummary,
)
from jarvis.planner.execution_anomaly_report import (
    ExecutionAnomalyReportBuilder,
)


def test_report_formats_anomalies() -> None:
    summary = ExecutionAnomalySummary(
        total=1,
        critical=1,
        warnings=0,
        anomalies=(
            ExecutionAnomaly(
                code="unreliable_capability",
                severity=ExecutionAnomalySeverity.CRITICAL,
                capability="system.health",
                message="Recent reliability is low.",
            ),
        ),
    )

    report = ExecutionAnomalyReportBuilder().build(
        summary
    )

    assert (
        "1 detected, 1 critical"
        in report.summary
    )
    assert (
        "critical: unreliable_capability "
        "[system.health]"
        in report.lines[0]
    )


def test_report_handles_no_anomalies() -> None:
    summary = ExecutionAnomalySummary(
        total=0,
        critical=0,
        warnings=0,
        anomalies=(),
    )

    report = ExecutionAnomalyReportBuilder().build(
        summary
    )

    assert report.lines == (
        "No execution anomalies detected.",
    )
