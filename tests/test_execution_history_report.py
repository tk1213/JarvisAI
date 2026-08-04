from datetime import UTC, datetime

from jarvis.planner.execution_history import (
    ExecutionHistorySummary,
)
from jarvis.planner.execution_history_report import (
    ExecutionHistoryReportBuilder,
)
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)


def test_report_formats_summary_and_records() -> None:
    record = PlanExecutionRecord(
        goal="Ping Jarvis",
        plan_status="completed",
        success=True,
        completed_steps=1,
        steps=(
            StepExecutionRecord(
                step_index=1,
                capability="system.ping",
                status="completed",
                attempts=1,
            ),
        ),
        events=(
            ExecutionEventRecord(
                sequence=1,
                event_type="plan_started",
                timestamp=datetime.now(UTC),
                step_index=None,
                capability=None,
                attempt=None,
                details={},
            ),
        ),
    )

    history = ExecutionHistorySummary(
        total=1,
        completed=1,
        failed=0,
        records=(
            record,
        ),
    )

    report = ExecutionHistoryReportBuilder().build(
        history
    )

    assert (
        report.summary
        == (
            "Execution history: 1 record(s), "
            "1 completed, 0 failed."
        )
    )

    assert (
        "Ping Jarvis [completed]"
        in report.lines[0]
    )
