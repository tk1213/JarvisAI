from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)
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


class FakeRepository:
    def __init__(self) -> None:
        self.started = False
        self.saved: list[PlanExecutionRecord] = []
        self.records: dict[int, PlanExecutionRecord] = {}

    async def startup(self) -> None:
        self.started = True

    async def save(
        self,
        record: PlanExecutionRecord,
    ) -> int:
        record_id = len(self.saved) + 1
        self.saved.append(
            record
        )
        self.records[
            record_id
        ] = record
        return record_id

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        return self.records.get(
            record_id
        )

    async def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> list[PlanExecutionRecord]:
        return list(
            reversed(
                self.saved
            )
        )[:limit]


def make_execution() -> PlanExecutionResult:
    plan = Plan(
        goal="Persist me",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
                status=PlanStepStatus.COMPLETED,
            )
        ],
        status=PlanStatus.COMPLETED,
    )

    return PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="system.ping",
                status=PlanStepStatus.COMPLETED,
                output={
                    "status": "ok",
                },
                attempts=1,
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


@pytest.mark.asyncio
async def test_service_starts_repository() -> None:
    repository = FakeRepository()

    service = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    await service.startup()

    assert repository.started is True


@pytest.mark.asyncio
async def test_service_persists_execution() -> None:
    repository = FakeRepository()

    service = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    record_id = await service.persist_execution(
        make_execution()
    )

    assert record_id == 1
    assert len(
        repository.saved
    ) == 1
    assert (
        repository.saved[0].goal
        == "Persist me"
    )


@pytest.mark.asyncio
async def test_service_reads_recent_records() -> None:
    repository = FakeRepository()

    repository.saved = [
        PlanExecutionRecord(
            goal="First",
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
        ),
        PlanExecutionRecord(
            goal="Second",
            plan_status="completed",
            success=True,
            completed_steps=1,
            steps=(
                StepExecutionRecord(
                    step_index=1,
                    capability="system.version",
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
        ),
    ]

    service = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    recent = await service.list_recent(
        limit=1
    )

    assert len(
        recent
    ) == 1
    assert recent[0].goal == "Second"
