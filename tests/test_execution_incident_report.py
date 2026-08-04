from datetime import UTC, datetime

from jarvis.planner.execution_incident_report import (
    ExecutionIncidentReportBuilder,
)
from jarvis.planner.execution_incidents import (
    ExecutionIncident,
    ExecutionIncidentSeverity,
)


def test_incident_report_formats_snapshot() -> None:
    incident = ExecutionIncident(
        incident_id="execution-20260804T223400Z",
        severity=ExecutionIncidentSeverity.HIGH,
        title="Execution incident: system.health",
        summary=(
            "2 execution anomaly item(s) "
            "detected; severity=high."
        ),
        anomaly_codes=(
            "unreliable_capability",
            "execution_timeout",
        ),
        capabilities=(
            "system.health",
        ),
        created_at=datetime(
            2026,
            8,
            4,
            22,
            34,
            tzinfo=UTC,
        ),
    )

    report = ExecutionIncidentReportBuilder().build(
        incident
    )

    assert (
        "Execution incident: system.health [high]"
        in report.summary
    )
    assert (
        "Anomaly codes: unreliable_capability, "
        "execution_timeout"
        in report.lines
    )
    assert (
        "Capabilities: system.health"
        in report.lines
    )
