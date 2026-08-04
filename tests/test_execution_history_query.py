from datetime import UTC, datetime

import pytest

from jarvis.planner.execution_history import ExecutionHistoryService
from jarvis.planner.execution_query import ExecutionQuery
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)


class FakePersistence:
    def __init__(
        self,
        records: list[PlanExecutionRecord],
    ) -> None:
        self.records = records

    async def list_recent(
        self,
        *,
        limit: int = 20,
    ) -> list[PlanExecutionRecord]:
        return self.records[:limit]

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        del record_id
        return None


def make_record(
    *,
    goal: str,
    status: str,
    capability: str,
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
async def test_query_filters_by_status() -> None:
    service = ExecutionHistoryService(
        FakePersistence(
            [
                make_record(
                    goal="Completed",
                    status="completed",
                    capability="system.ping",
                ),
                make_record(
                    goal="Failed",
                    status="failed",
                    capability="system.version",
                ),
            ]
        )  # type: ignore[arg-type]
    )

    result = await service.query(
        ExecutionQuery(
            limit=10,
            status="failed",
        )
    )

    assert result.total == 1
    assert result.completed == 0
    assert result.failed == 1
    assert result.records[0].goal == "Failed"


@pytest.mark.asyncio
async def test_query_filters_by_capability() -> None:
    service = ExecutionHistoryService(
        FakePersistence(
            [
                make_record(
                    goal="Ping",
                    status="completed",
                    capability="system.ping",
                ),
                make_record(
                    goal="Version",
                    status="completed",
                    capability="system.version",
                ),
            ]
        )  # type: ignore[arg-type]
    )

    result = await service.query(
        ExecutionQuery(
            limit=10,
            capability="system.version",
        )
    )

    assert result.total == 1
    assert result.records[0].goal == "Version"


@pytest.mark.asyncio
async def test_query_combines_filters() -> None:
    service = ExecutionHistoryService(
        FakePersistence(
            [
                make_record(
                    goal="Ping OK",
                    status="completed",
                    capability="system.ping",
                ),
                make_record(
                    goal="Ping failed",
                    status="failed",
                    capability="system.ping",
                ),
                make_record(
                    goal="Version failed",
                    status="failed",
                    capability="system.version",
                ),
            ]
        )  # type: ignore[arg-type]
    )

    result = await service.query(
        ExecutionQuery(
            limit=10,
            status="failed",
            capability="system.ping",
        )
    )

    assert result.total == 1
    assert result.records[0].goal == "Ping failed"
