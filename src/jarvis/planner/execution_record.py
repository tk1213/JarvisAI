from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from jarvis.planner.executor import PlanExecutionResult
from jarvis.planner.journal import ExecutionEvent


@dataclass(slots=True, frozen=True)
class StepExecutionRecord:
    step_index: int
    capability: str
    status: str
    attempts: int
    output: Any = None
    error: str | None = None


@dataclass(slots=True, frozen=True)
class ExecutionEventRecord:
    sequence: int
    event_type: str
    timestamp: datetime
    step_index: int | None
    capability: str | None
    attempt: int | None
    details: dict[str, Any]


@dataclass(slots=True, frozen=True)
class PlanExecutionRecord:
    goal: str
    plan_status: str
    success: bool
    completed_steps: int
    steps: tuple[StepExecutionRecord, ...]
    events: tuple[ExecutionEventRecord, ...]


class PlanExecutionRecordBuilder:
    def build(
        self,
        execution: PlanExecutionResult,
    ) -> PlanExecutionRecord:
        return PlanExecutionRecord(
            goal=execution.plan.goal,
            plan_status=execution.plan.status.value,
            success=execution.success,
            completed_steps=execution.completed_steps,
            steps=tuple(
                StepExecutionRecord(
                    step_index=result.step_index,
                    capability=result.capability,
                    status=result.status.value,
                    attempts=result.attempts,
                    output=result.output,
                    error=result.error,
                )
                for result in execution.step_results
            ),
            events=tuple(
                self._event_record(
                    event
                )
                for event in execution.journal_events
            ),
        )

    @staticmethod
    def _event_record(
        event: ExecutionEvent,
    ) -> ExecutionEventRecord:
        return ExecutionEventRecord(
            sequence=event.sequence,
            event_type=event.event_type.value,
            timestamp=event.timestamp,
            step_index=event.step_index,
            capability=event.capability,
            attempt=event.attempt,
            details=dict(
                event.details
            ),
        )
