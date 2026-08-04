from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_record import PlanExecutionRecord


@dataclass(slots=True, frozen=True)
class ExecutionStepDetail:
    step_index: int
    capability: str
    status: str
    attempts: int
    output: Any = None
    error: str | None = None


@dataclass(slots=True, frozen=True)
class ExecutionTimelineEntry:
    sequence: int
    event_type: str
    timestamp: str
    step_index: int | None
    capability: str | None
    attempt: int | None
    details: dict[str, Any]


@dataclass(slots=True, frozen=True)
class ExecutionDetail:
    record_id: int
    goal: str
    plan_status: str
    success: bool
    completed_steps: int
    steps: tuple[ExecutionStepDetail, ...]
    timeline: tuple[ExecutionTimelineEntry, ...]
    failure_count: int

    @property
    def has_failures(self) -> bool:
        return self.failure_count > 0


class ExecutionDetailService:
    def __init__(
        self,
        persistence: ExecutionPersistenceService,
    ) -> None:
        self._persistence = persistence

    async def get(
        self,
        record_id: int,
    ) -> ExecutionDetail | None:
        if record_id < 1:
            raise ValueError(
                "record_id must be at least 1."
            )

        record = await self._persistence.get(
            record_id
        )

        if record is None:
            return None

        return self._build_detail(
            record_id=record_id,
            record=record,
        )

    @staticmethod
    def _build_detail(
        *,
        record_id: int,
        record: PlanExecutionRecord,
    ) -> ExecutionDetail:
        steps = tuple(
            ExecutionStepDetail(
                step_index=step.step_index,
                capability=step.capability,
                status=step.status,
                attempts=step.attempts,
                output=step.output,
                error=step.error,
            )
            for step in record.steps
        )

        timeline = tuple(
            ExecutionTimelineEntry(
                sequence=event.sequence,
                event_type=event.event_type,
                timestamp=event.timestamp.isoformat(),
                step_index=event.step_index,
                capability=event.capability,
                attempt=event.attempt,
                details=dict(
                    event.details
                ),
            )
            for event in record.events
        )

        failure_count = sum(
            step.status == "failed"
            for step in record.steps
        )

        return ExecutionDetail(
            record_id=record_id,
            goal=record.goal,
            plan_status=record.plan_status,
            success=record.success,
            completed_steps=record.completed_steps,
            steps=steps,
            timeline=timeline,
            failure_count=failure_count,
        )
