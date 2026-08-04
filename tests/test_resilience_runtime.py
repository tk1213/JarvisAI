from datetime import UTC, datetime

from jarvis.planner.executor import PlanExecutionResult
from jarvis.planner.journal import (
    ExecutionEvent,
    ExecutionEventType,
)
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.resilience_runtime import (
    ResilienceRuntime,
)


def make_execution(
    events: tuple[ExecutionEvent, ...],
) -> PlanExecutionResult:
    return PlanExecutionResult(
        plan=Plan(
            goal="test",
            steps=[
                PlanStep(
                    index=1,
                    capability="system.ping",
                )
            ],
            status=PlanStatus.COMPLETED,
        ),
        journal_events=events,
    )


def test_runtime_observes_execution_journal() -> None:
    runtime = ResilienceRuntime()

    execution = make_execution(
        (
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
        )
    )

    runtime.observe_execution(
        execution
    )

    snapshot = runtime.snapshot()

    assert snapshot.healthy is True
    assert snapshot.metrics.plans_started == 1
    assert snapshot.metrics.plans_completed == 1
    assert snapshot.summary == "resilience healthy"


def test_runtime_marks_rejection_as_degraded() -> None:
    runtime = ResilienceRuntime()

    execution = make_execution(
        (
            ExecutionEvent(
                sequence=1,
                event_type=ExecutionEventType.STEP_FAILED,
                timestamp=datetime.now(UTC),
                capability="system.ping",
                details={
                    "phase": "circuit_breaker",
                    "error": (
                        "capability circuit breaker is open"
                    ),
                },
            ),
        )
    )

    runtime.observe_execution(
        execution
    )

    snapshot = runtime.snapshot()

    assert snapshot.healthy is False
    assert snapshot.metrics.circuit_rejections == 1
    assert snapshot.summary == "resilience degraded"
