from jarvis.planner.execution_incident_grouping import (
    ExecutionIncidentGroup,
    ExecutionIncidentGroupingSummary,
)
from jarvis.planner.execution_incident_grouping_report import (
    ExecutionIncidentGroupingReportBuilder,
)


def test_grouping_report_formats_groups() -> None:
    summary = ExecutionIncidentGroupingSummary(
        total_incidents=2,
        total_groups=1,
        groups=(
            ExecutionIncidentGroup(
                fingerprint="abc123",
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
        ),
    )

    report = ExecutionIncidentGroupingReportBuilder().build(
        summary
    )

    assert (
        "2 incident(s), 1 group(s)"
        in report.summary
    )

    assert (
        "abc123: occurrences=2"
        in report.lines[0]
    )

    assert (
        "capabilities=system.health"
        in report.lines[0]
    )


def test_grouping_report_handles_empty_summary() -> None:
    summary = ExecutionIncidentGroupingSummary(
        total_incidents=0,
        total_groups=0,
        groups=(),
    )

    report = ExecutionIncidentGroupingReportBuilder().build(
        summary
    )

    assert report.lines == (
        "No execution incidents are available for grouping.",
    )
