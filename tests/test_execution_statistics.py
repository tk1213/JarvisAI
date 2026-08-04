from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.planner.execution_record import (
    ExecutionEventRecord,
    PlanExecutionRecord,
    StepExecutionRecord,
)
from jarvis.planner.execution_statistics import (
    ExecutionStatisticsService,
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
        limit: int = 100,
    ) -> list[PlanExecutionRecord]:
        return self.records[:limit]


def make_record(
    *,
    goal: str,
    success: bool,
    capability: str,
    attempts: int = 1,
    error: str | None = None,
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
        ),
    )


@pytest.mark.asyncio
async def test_statistics_summarize_records() -> None:
    service = ExecutionStatisticsService(
        FakePersistence(
            [
                make_record(
                    goal="Ping OK",
                    success=True,
                    capability="system.ping",
                    attempts=2,
                ),
                make_record(
                    goal="Health timeout",
                    success=False,
                    capability="system.health",
                    attempts=2,
                    error="capability execution timed out",
                ),
                make_record(
                    goal="Version OK",
                    success=True,
                    capability="system.version",
                ),
            ]
        )  # type: ignore[arg-type]
    )

    statistics = await service.summarize(
        limit=10
    )

    assert statistics.total == 3
    assert statistics.completed == 2
    assert statistics.failed == 1
    assert statistics.success_rate == pytest.approx(
        2 / 3
    )
    assert statistics.retried_steps == 2
    assert statistics.timed_out_steps == 1
    assert statistics.capability_counts == {
        "system.ping": 1,
        "system.health": 1,
        "system.version": 1,
    }
    assert statistics.capability_failure_counts == {
        "system.health": 1,
    }


@pytest.mark.asyncio
async def test_statistics_empty_history() -> None:
    service = ExecutionStatisticsService(
        FakePersistence(
            []
        )  # type: ignore[arg-type]
    )

    statistics = await service.summarize()

    assert statistics.total == 0
    assert statistics.success_rate == 0.0
    assert statistics.capability_counts == {}


@pytest.mark.asyncio
async def test_statistics_reject_invalid_limit() -> None:
    service = ExecutionStatisticsService(
        FakePersistence(
            []
        )  # type: ignore[arg-type]
    )

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        await service.summarize(
            limit=0
        )
