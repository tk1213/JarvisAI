from jarvis.planner.execution_diagnostics import ExecutionDiagnostics
from jarvis.planner.execution_diagnostics_report import (
    ExecutionDiagnosticsReportBuilder,
)


def test_report_formats_diagnostic_findings() -> None:
    diagnostics = ExecutionDiagnostics(
        record_id=8,
        goal="Diagnose failure",
        plan_status="failed",
        failed_steps=(
            "system.version",
        ),
        retry_steps=(
            "system.ping",
        ),
        timeout_steps=(),
        failure_messages=(
            "invalid request",
        ),
        event_types=(
            "plan_started",
            "step_failed",
            "plan_failed",
        ),
    )

    report = ExecutionDiagnosticsReportBuilder().build(
        diagnostics
    )

    assert (
        "status=failed"
        in report.summary
    )
    assert (
        "Failed capabilities: system.version"
        in report.lines
    )
    assert (
        "Retried capabilities: system.ping"
        in report.lines
    )
    assert (
        "Failure messages: invalid request"
        in report.lines
    )


def test_report_handles_clean_execution() -> None:
    diagnostics = ExecutionDiagnostics(
        record_id=9,
        goal="Healthy execution",
        plan_status="completed",
        failed_steps=(),
        retry_steps=(),
        timeout_steps=(),
        failure_messages=(),
        event_types=(
            "plan_started",
            "plan_completed",
        ),
    )

    report = ExecutionDiagnosticsReportBuilder().build(
        diagnostics
    )

    assert report.lines == (
        "No execution failures, retries, or timeouts detected.",
    )
