from jarvis.planner.execution_detail import (
    ExecutionDetail,
    ExecutionStepDetail,
    ExecutionTimelineEntry,
)
from jarvis.planner.execution_detail_report import (
    ExecutionDetailReportBuilder,
)


def test_detail_report_formats_failure_information() -> None:
    detail = ExecutionDetail(
        record_id=5,
        goal="Inspect failure",
        plan_status="failed",
        success=False,
        completed_steps=0,
        steps=(
            ExecutionStepDetail(
                step_index=1,
                capability="system.version",
                status="failed",
                attempts=2,
                error="invalid request",
            ),
        ),
        timeline=(
            ExecutionTimelineEntry(
                sequence=1,
                event_type="step_failed",
                timestamp="2026-08-04T12:00:00+00:00",
                step_index=1,
                capability="system.version",
                attempt=2,
                details={
                    "error": "invalid request",
                },
            ),
        ),
        failure_count=1,
    )

    report = ExecutionDetailReportBuilder().build(
        detail
    )

    assert (
        report.summary
        == (
            "Execution 5: Inspect failure "
            "[failed], 1 step(s), 1 failure(s)."
        )
    )
    assert (
        "error=invalid request"
        in report.step_lines[0]
    )
    assert (
        "step_failed"
        in report.timeline_lines[0]
    )
