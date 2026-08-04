from datetime import UTC, datetime

from jarvis.planner.execution_record import PlanExecutionRecordBuilder
from jarvis.planner.executor import (
    PlanExecutionResult,
    PlanStepResult,
)
from jarvis.planner.journal import (
    ExecutionEvent,
    ExecutionEventType,
)
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)


def test_record_builder_captures_execution_result() -> None:
    plan = Plan(
        goal="Ping Jarvis",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
                status=PlanStepStatus.COMPLETED,
            )
        ],
        status=PlanStatus.COMPLETED,
    )

    execution = PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="system.ping",
                status=PlanStepStatus.COMPLETED,
                output={
                    "status": "ok",
                },
                attempts=2,
            )
        ],
        journal_events=(
            ExecutionEvent(
                sequence=1,
                event_type=ExecutionEventType.PLAN_STARTED,
                timestamp=datetime.now(UTC),
            ),
            ExecutionEvent(
                sequence=2,
                event_type=ExecutionEventType.PLAN_COMPLETED,
                timestamp=datetime.now(UTC),
            ),
        ),
    )

    record = PlanExecutionRecordBuilder().build(
        execution
    )

    assert record.goal == "Ping Jarvis"
    assert record.plan_status == "completed"
    assert record.success is True
    assert record.completed_steps == 1
    assert record.steps[0].attempts == 2
    assert record.steps[0].output == {
        "status": "ok",
    }
    assert len(
        record.events
    ) == 2
