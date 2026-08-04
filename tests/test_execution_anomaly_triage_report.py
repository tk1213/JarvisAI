from jarvis.planner.execution_anomalies import (
    ExecutionAnomaly,
    ExecutionAnomalySeverity,
)
from jarvis.planner.execution_anomaly_triage import (
    ExecutionAnomalyTriage,
    ExecutionAnomalyTriageItem,
)
from jarvis.planner.execution_anomaly_triage_report import (
    ExecutionAnomalyTriageReportBuilder,
)


def test_triage_report_formats_priority_order() -> None:
    triage = ExecutionAnomalyTriage(
        total=1,
        highest_severity=ExecutionAnomalySeverity.CRITICAL,
        items=(
            ExecutionAnomalyTriageItem(
                priority=1,
                anomaly=ExecutionAnomaly(
                    code="unreliable_capability",
                    severity=ExecutionAnomalySeverity.CRITICAL,
                    capability="system.health",
                    message="Recent reliability is low.",
                ),
            ),
        ),
    )

    report = ExecutionAnomalyTriageReportBuilder().build(
        triage
    )

    assert (
        "highest_severity=critical"
        in report.summary
    )
    assert (
        report.lines[0]
        == (
            "1. critical: unreliable_capability "
            "[system.health] - Recent reliability is low."
        )
    )


def test_triage_report_handles_empty_triage() -> None:
    triage = ExecutionAnomalyTriage(
        total=0,
        highest_severity=None,
        items=(),
    )

    report = ExecutionAnomalyTriageReportBuilder().build(
        triage
    )

    assert report.lines == (
        "No anomalies require triage.",
    )
