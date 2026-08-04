from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.planner.execution_history import ExecutionHistoryService
from jarvis.planner.execution_history_report import (
    ExecutionHistoryReportBuilder,
)
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)


class FakeRepository:
    def __init__(self) -> None:
        self.started = False
        self.records: list[PlanExecutionRecord] = []

    async def startup(self) -> None:
        self.started = True

    async def save(
        self,
        record: PlanExecutionRecord,
    ) -> int:
        self.records.append(record)
        return len(self.records)

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        if record_id < 1 or record_id > len(self.records):
            return None

        return self.records[record_id - 1]

    async def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> list[PlanExecutionRecord]:
        return list(
            reversed(self.records)
        )[:limit]


def make_record(
    *,
    goal: str,
    success: bool,
) -> PlanExecutionRecord:
    return PlanExecutionRecord(
        goal=goal,
        plan_status=(
            "completed"
            if success
            else "failed"
        ),
        success=success,
        completed_steps=(
            1
            if success
            else 0
        ),
        steps=(
            StepExecutionRecord(
                step_index=1,
                capability="system.ping",
                status=(
                    "completed"
                    if success
                    else "failed"
                ),
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
    )


@pytest.mark.asyncio
async def test_persistence_history_and_reporting_work_together() -> None:
    repository = FakeRepository()

    persistence = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    await persistence.startup()

    await repository.save(
        make_record(
            goal="Completed execution",
            success=True,
        )
    )

    await repository.save(
        make_record(
            goal="Failed execution",
            success=False,
        )
    )

    history_service = ExecutionHistoryService(
        persistence
    )

    history = await history_service.recent(
        limit=10
    )

    report = ExecutionHistoryReportBuilder().build(
        history
    )

    assert repository.started is True
    assert history.total == 2
    assert history.completed == 1
    assert history.failed == 1
    assert (
        "2 record(s), 1 completed, 1 failed"
        in report.summary
    )
    assert (
        "Failed execution [failed]"
        in report.lines[0]
    )
    assert (
        "Completed execution [completed]"
        in report.lines[1]
    )
