from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from jarvis.planner.resilience_metrics import (
    ResilienceMetricsSnapshot,
)
from jarvis.planner.resilience_observer import (
    ResilienceObserver,
)

if TYPE_CHECKING:
    from jarvis.planner.executor import PlanExecutionResult
    from jarvis.planner.journal import ExecutionEvent


@dataclass(slots=True, frozen=True)
class ResilienceHealthSnapshot:
    healthy: bool
    metrics: ResilienceMetricsSnapshot
    summary: str


class ResilienceRuntime:
    def __init__(
        self,
        observer: ResilienceObserver | None = None,
    ) -> None:
        self._observer = (
            observer
            if observer is not None
            else ResilienceObserver()
        )

    def observe_event(
        self,
        event: ExecutionEvent,
    ) -> None:
        self._observer.observe(
            event
        )

    def observe_execution(
        self,
        execution: PlanExecutionResult,
    ) -> None:
        for event in execution.journal_events:
            self.observe_event(
                event
            )

    def snapshot(
        self,
    ) -> ResilienceHealthSnapshot:
        metrics = self._observer.metrics.snapshot()

        healthy = (
            metrics.circuit_rejections == 0
            and metrics.bulkhead_rejections == 0
        )

        summary = (
            "resilience healthy"
            if healthy
            else "resilience degraded"
        )

        return ResilienceHealthSnapshot(
            healthy=healthy,
            metrics=metrics,
            summary=summary,
        )


resilience_runtime = ResilienceRuntime()
