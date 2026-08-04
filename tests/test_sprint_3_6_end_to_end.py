from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.planner.execution_detail import ExecutionDetailService
from jarvis.planner.execution_diagnostics import (
    ExecutionDiagnosticsService,
)
from jarvis.planner.execution_history import ExecutionHistoryService
from jarvis.planner.execution_persistence import (
    ExecutionPersistenceService,
)
from jarvis.planner.execution_query import ExecutionQuery
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)


class FakeRepository:
    def __init__(
        self,
        records: list[PlanExecutionRecord],
    ) -> None:
        self.records = records

    async def startup(self) -> None:
        pass

    async def save(
        self,
        record: PlanExecutionRecord,
    ) -> int:
        self.records.append(
            record
        )
        return len(
            self.records
        )

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        if record_id < 1:
            return None

        index = record_id - 1

        if index >= len(
            self.records
        ):
            return None

        return self.records[
            index
        ]

    async def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> list[PlanExecutionRecord]:
        return list(
            reversed(
                self.records
            )
        )[:limit]


def make_record(
    *,
    goal: str,
    status: str,
    capability: str,
    attempts: int = 1,
    error: str | None = None,
) -> PlanExecutionRecord:
    success = status == "completed"

    return PlanExecutionRecord(
        goal=goal,
        plan_status=status,
        success=success,
        completed_steps=(
            1
            if success
            else 0
        ),
        steps=(
            StepExecutionRecord(
                step_index=1,
                capability=capability,
                status=(
                    "completed"
                    if success
                    else "failed"
                ),
                attempts=attempts,
                error=error,
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
            ExecutionEventRecord(
                sequence=2,
                event_type=(
                    "plan_completed"
                    if success
                    else "step_failed"
                ),
                timestamp=datetime.now(UTC),
                step_index=(
                    None
                    if success
                    else 1
                ),
                capability=(
                    None
                    if success
                    else capability
                ),
                attempt=(
                    None
                    if success
                    else attempts
                ),
                details=(
                    {}
                    if error is None
                    else {
                        "error": error,
                    }
                ),
            ),
        ),
    )


@pytest.mark.asyncio
async def test_query_detail_and_diagnostics_work_together() -> None:
    repository = FakeRepository(
        [
            make_record(
                goal="Healthy ping",
                status="completed",
                capability="system.ping",
            ),
            make_record(
                goal="Timed out health",
                status="failed",
                capability="system.health",
                attempts=2,
                error="capability execution timed out",
            ),
        ]
    )

    persistence = ExecutionPersistenceService(
        repository  # type: ignore[arg-type]
    )

    history = ExecutionHistoryService(
        persistence
    )

    failed = await history.query(
        ExecutionQuery(
            limit=10,
            status="failed",
        )
    )

    assert failed.total == 1
    assert failed.records[0].goal == "Timed out health"

    detail_service = ExecutionDetailService(
        persistence
    )

    detail = await detail_service.get(
        2
    )

    assert detail is not None
    assert detail.plan_status == "failed"
    assert detail.failure_count == 1

    diagnostics_service = ExecutionDiagnosticsService(
        detail_service
    )

    diagnostics = await diagnostics_service.diagnose(
        2
    )

    assert diagnostics is not None
    assert diagnostics.failed_steps == (
        "system.health",
    )
    assert diagnostics.retry_steps == (
        "system.health",
    )
    assert diagnostics.timeout_steps == (
        "system.health",
    )
