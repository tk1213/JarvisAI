from datetime import UTC, datetime

from jarvis.planner.journal import (
    ExecutionEvent,
    ExecutionEventType,
)
from jarvis.planner.resilience_observer import ResilienceObserver


def event(
    event_type: ExecutionEventType,
    *,
    capability: str | None = None,
    details: dict | None = None,
) -> ExecutionEvent:
    return ExecutionEvent(
        sequence=1,
        event_type=event_type,
        timestamp=datetime.now(UTC),
        capability=capability,
        details=details or {},
    )


def test_observer_counts_lifecycle_events() -> None:
    observer = ResilienceObserver()

    observer.observe(
        event(
            ExecutionEventType.PLAN_STARTED
        )
    )
    observer.observe(
        event(
            ExecutionEventType.STEP_STARTED
        )
    )
    observer.observe(
        event(
            ExecutionEventType.STEP_RETRYING
        )
    )
    observer.observe(
        event(
            ExecutionEventType.STEP_COMPLETED
        )
    )
    observer.observe(
        event(
            ExecutionEventType.PLAN_COMPLETED
        )
    )

    snapshot = observer.metrics.snapshot()

    assert snapshot.plans_started == 1
    assert snapshot.plans_completed == 1
    assert snapshot.steps_started == 1
    assert snapshot.steps_completed == 1
    assert snapshot.retries == 1


def test_observer_classifies_rejections_and_timeouts() -> None:
    observer = ResilienceObserver()

    observer.observe(
        event(
            ExecutionEventType.STEP_FAILED,
            capability="system.ping",
            details={
                "phase": "circuit_breaker",
                "error": (
                    "capability circuit breaker is open"
                ),
            },
        )
    )

    observer.observe(
        event(
            ExecutionEventType.STEP_FAILED,
            capability="system.ping",
            details={
                "phase": "bulkhead",
                "error": (
                    "capability concurrency limit reached"
                ),
            },
        )
    )

    observer.observe(
        event(
            ExecutionEventType.STEP_FAILED,
            capability="system.ping",
            details={
                "phase": "capability_execution",
                "error": (
                    "capability execution timed out"
                ),
            },
        )
    )

    snapshot = observer.metrics.snapshot()

    assert snapshot.steps_failed == 3
    assert snapshot.circuit_rejections == 1
    assert snapshot.bulkhead_rejections == 1
    assert snapshot.timeouts == 1
    assert snapshot.capability_failures == {
        "system.ping": 3,
    }
