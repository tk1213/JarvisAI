from __future__ import annotations

from jarvis.planner.journal import (
    ExecutionEvent,
    ExecutionEventType,
)
from jarvis.planner.resilience_metrics import ResilienceMetrics


class ResilienceObserver:
    def __init__(
        self,
        metrics: ResilienceMetrics | None = None,
    ) -> None:
        self.metrics = (
            metrics
            if metrics is not None
            else ResilienceMetrics()
        )

    def observe(
        self,
        event: ExecutionEvent,
    ) -> None:
        if event.event_type is ExecutionEventType.PLAN_STARTED:
            self.metrics.plans_started += 1
            return

        if event.event_type is ExecutionEventType.PLAN_COMPLETED:
            self.metrics.plans_completed += 1
            return

        if event.event_type is ExecutionEventType.PLAN_FAILED:
            self.metrics.plans_failed += 1
            return

        if event.event_type is ExecutionEventType.STEP_STARTED:
            self.metrics.steps_started += 1
            return

        if event.event_type is ExecutionEventType.STEP_COMPLETED:
            self.metrics.steps_completed += 1
            return

        if event.event_type is ExecutionEventType.STEP_RETRYING:
            self.metrics.retries += 1
            return

        if event.event_type is ExecutionEventType.STEP_FAILED:
            self.metrics.steps_failed += 1

            phase = str(
                event.details.get(
                    "phase",
                    "",
                )
            )

            error = str(
                event.details.get(
                    "error",
                    "",
                )
            )

            if "timed out" in error:
                self.metrics.timeouts += 1

            if phase == "circuit_breaker":
                self.metrics.circuit_rejections += 1

            if phase == "bulkhead":
                self.metrics.bulkhead_rejections += 1

            if event.capability:
                self.metrics.increment_capability_failure(
                    event.capability
                )
