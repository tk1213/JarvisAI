from __future__ import annotations

from datetime import UTC, datetime

from jarvis.planner.journal import (
    ExecutionEvent,
    ExecutionEventType,
)
from jarvis.planner.resilience_observer import ResilienceObserver


def make_event(
    sequence: int,
    event_type: ExecutionEventType,
    *,
    capability: str | None = None,
    details: dict | None = None,
) -> ExecutionEvent:
    return ExecutionEvent(
        sequence=sequence,
        event_type=event_type,
        timestamp=datetime.now(UTC),
        capability=capability,
        details=details or {},
    )


def main() -> None:
    observer = ResilienceObserver()

    events = [
        make_event(
            1,
            ExecutionEventType.PLAN_STARTED,
        ),
        make_event(
            2,
            ExecutionEventType.STEP_STARTED,
            capability="system.ping",
        ),
        make_event(
            3,
            ExecutionEventType.STEP_RETRYING,
            capability="system.ping",
        ),
        make_event(
            4,
            ExecutionEventType.STEP_COMPLETED,
            capability="system.ping",
        ),
        make_event(
            5,
            ExecutionEventType.PLAN_COMPLETED,
        ),
    ]

    for item in events:
        observer.observe(
            item
        )

    snapshot = observer.metrics.snapshot()

    print(
        "Sprint 3.4 Resilience Metrics"
    )
    print(
        "-" * 60
    )
    print(
        f"Plans started: {snapshot.plans_started}"
    )
    print(
        f"Plans completed: {snapshot.plans_completed}"
    )
    print(
        f"Steps started: {snapshot.steps_started}"
    )
    print(
        f"Steps completed: {snapshot.steps_completed}"
    )
    print(
        f"Retries: {snapshot.retries}"
    )

    if snapshot.plans_completed != 1:
        raise RuntimeError(
            "Resilience metrics gate failed."
        )

    if snapshot.retries != 1:
        raise RuntimeError(
            "Retry metric was not recorded."
        )

    print(
        "Resilience metrics gate: PASS"
    )


if __name__ == "__main__":
    main()
