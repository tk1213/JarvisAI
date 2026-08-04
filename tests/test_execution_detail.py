from datetime import UTC, datetime

import pytest

from jarvis.planner.execution_detail import ExecutionDetailService
from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)


class FakePersistence:
    def __init__(
        self,
        record: PlanExecutionRecord | None,
    ) -> None:
        self.record = record

    async def get(
        self,
        record_id: int,
    ) -> PlanExecutionRecord | None:
        del record_id
        return self.record


def make_record() -> PlanExecutionRecord:
    return PlanExecutionRecord(
        goal="Inspect failure",
        plan_status="failed",
        success=False,
        completed_steps=1,
        steps=(
            StepExecutionRecord(
                step_index=1,
                capability="system.ping",
                status="completed",
                attempts=1,
                output={
                    "status": "ok",
                },
            ),
            StepExecutionRecord(
                step_index=2,
                capability="system.version",
                status="failed",
                attempts=1,
                error="invalid request",
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
                event_type="step_failed",
                timestamp=datetime.now(UTC),
                step_index=2,
                capability="system.version",
                attempt=1,
                details={
                    "error": "invalid request",
                },
            ),
        ),
    )


@pytest.mark.asyncio
async def test_detail_builds_steps_and_timeline() -> None:
    service = ExecutionDetailService(
        FakePersistence(
            make_record()
        )  # type: ignore[arg-type]
    )

    detail = await service.get(
        7
    )

    assert detail is not None
    assert detail.record_id == 7
    assert detail.goal == "Inspect failure"
    assert detail.plan_status == "failed"
    assert detail.success is False
    assert detail.completed_steps == 1
    assert len(
        detail.steps
    ) == 2
    assert len(
        detail.timeline
    ) == 2
    assert detail.failure_count == 1
    assert detail.has_failures is True
    assert (
        detail.steps[1].error
        == "invalid request"
    )


@pytest.mark.asyncio
async def test_detail_returns_none_for_missing_record() -> None:
    service = ExecutionDetailService(
        FakePersistence(
            None
        )  # type: ignore[arg-type]
    )

    assert await service.get(
        99
    ) is None


@pytest.mark.asyncio
async def test_detail_rejects_invalid_record_id() -> None:
    service = ExecutionDetailService(
        FakePersistence(
            None
        )  # type: ignore[arg-type]
    )

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        await service.get(
            0
        )
