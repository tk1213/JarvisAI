from __future__ import annotations

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


def main() -> None:
    runtime = ResilienceRuntime()

    execution = PlanExecutionResult(
        plan=Plan(
            goal="Runtime resilience snapshot demo",
            steps=[
                PlanStep(
                    index=1,
                    capability="system.ping",
                )
            ],
            status=PlanStatus.COMPLETED,
        ),
        journal_events=(
            ExecutionEvent(
                sequence=1,
                event_type=ExecutionEventType.PLAN_STARTED,
                timestamp=datetime.now(UTC),
            ),
            ExecutionEvent(
                sequence=2,
                event_type=ExecutionEventType.STEP_STARTED,
                timestamp=datetime.now(UTC),
                capability="system.ping",
                step_index=1,
                attempt=1,
            ),
            ExecutionEvent(
                sequence=3,
                event_type=ExecutionEventType.STEP_COMPLETED,
                timestamp=datetime.now(UTC),
                capability="system.ping",
                step_index=1,
                attempt=1,
            ),
            ExecutionEvent(
                sequence=4,
                event_type=ExecutionEventType.PLAN_COMPLETED,
                timestamp=datetime.now(UTC),
            ),
        ),
    )

    runtime.observe_execution(
        execution
    )

    snapshot = runtime.snapshot()

    print(
        "Sprint 3.4 Resilience Runtime"
    )
    print(
        "-" * 60
    )
    print(
        f"Healthy: {snapshot.healthy}"
    )
    print(
        f"Summary: {snapshot.summary}"
    )
    print(
        f"Plans started: {snapshot.metrics.plans_started}"
    )
    print(
        f"Plans completed: {snapshot.metrics.plans_completed}"
    )
    print(
        f"Steps completed: {snapshot.metrics.steps_completed}"
    )

    if not snapshot.healthy:
        raise RuntimeError(
            "Resilience runtime gate failed."
        )

    if snapshot.metrics.plans_started != 1:
        raise RuntimeError(
            "Plan-start metric is incorrect."
        )

    if snapshot.metrics.plans_completed != 1:
        raise RuntimeError(
            "Plan-completed metric is incorrect."
        )

    if snapshot.metrics.steps_completed != 1:
        raise RuntimeError(
            "Step-completed metric is incorrect."
        )

    print(
        "Resilience runtime gate: PASS"
    )


if __name__ == "__main__":
    main()
