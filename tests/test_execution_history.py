from datetime import UTC, datetime

import pytest

from jarvis.planner.execution_history import (
    ExecutionHistoryService,
)
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
async def test_history_summary_counts_success_and_failure() -> None:
    persistence = FakePersistence(
        [
            make_record(
                goal="First",
                success=True,
            ),
            make_record(
                goal="Second",
                success=False,
            ),
        ]
    )

    service = ExecutionHistoryService(
        persistence  # type: ignore[arg-type]
    )

    history = await service.recent(
        limit=10
    )

    assert history.total == 2
    assert history.completed == 1
    assert history.failed == 1


@pytest.mark.asyncio
async def test_history_get_returns_record() -> None:
    record = make_record(
        goal="First",
        success=True,
    )

    service = ExecutionHistoryService(
        FakePersistence(
            [
                record,
            ]
        )  # type: ignore[arg-type]
    )

    loaded = await service.get(
        1
    )

    assert loaded is record


@pytest.mark.asyncio
async def test_history_rejects_invalid_limit() -> None:
    service = ExecutionHistoryService(
        FakePersistence(
            []
        )  # type: ignore[arg-type]
    )

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        await service.recent(
            limit=0
        )
