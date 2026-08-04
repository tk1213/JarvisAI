from jarvis.planner.execution_incident_correlation import (
    ExecutionIncidentCorrelation,
)
from jarvis.planner.execution_incident_correlation_report import (
    ExecutionIncidentCorrelationReportBuilder,
)


def test_correlation_report_formats_fingerprint() -> None:
    correlation = ExecutionIncidentCorrelation(
        fingerprint="abc123def4567890",
        incident_id="execution-1",
        severity="high",
        anomaly_codes=(
            "execution_timeout",
        ),
        capabilities=(
            "system.health",
        ),
        correlation_key=(
            "anomalies=execution_timeout"
            "|capabilities=system.health"
        ),
    )

    report = ExecutionIncidentCorrelationReportBuilder().build(
        correlation
    )

    assert (
        "fingerprint=abc123def4567890"
        in report.summary
    )
    assert (
        "Anomaly codes: execution_timeout"
        in report.lines
    )
    assert (
        "Capabilities: system.health"
        in report.lines
    )
