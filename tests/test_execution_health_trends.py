from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jarvis.planner.execution_health import ExecutionHealthLevel
from jarvis.planner.execution_health_trends import (
    ExecutionHealthTrendService,
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
        limit: int = 40,
    ) -> list[PlanExecutionRecord]:
        return self.records[:limit]


def make_record(
    *,
    success: bool,
    attempts: int = 1,
    error: str | None = None,
) -> PlanExecutionRecord:
    return PlanExecutionRecord(
        goal="trend",
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
async def test_trend_detects_improvement() -> None:
    current = [
        make_record(
            success=True
        )
        for _ in range(4)
    ] + [
        make_record(
            success=False
        )
    ]

    previous = [
        make_record(
            success=True
        )
        for _ in range(2)
    ] + [
        make_record(
            success=False
        )
        for _ in range(3)
    ]

    service = ExecutionHealthTrendService(
        FakePersistence(
            current + previous
        )  # type: ignore[arg-type]
    )

    trend = await service.summarize(
        window_size=5
    )

    assert trend.direction == "improving"
    assert trend.current.success_rate == pytest.approx(
        0.8
    )


@pytest.mark.asyncio
async def test_trend_detects_worsening() -> None:
    current = [
        make_record(
            success=True
        )
        for _ in range(2)
    ] + [
        make_record(
            success=False
        )
        for _ in range(3)
    ]

    previous = [
        make_record(
            success=True
        )
        for _ in range(5)
    ]

    service = ExecutionHealthTrendService(
        FakePersistence(
            current + previous
        )  # type: ignore[arg-type]
    )

    trend = await service.summarize(
        window_size=5
    )

    assert trend.direction == "worsening"
    assert trend.level is ExecutionHealthLevel.UNHEALTHY


@pytest.mark.asyncio
async def test_trend_is_unknown_without_previous_window() -> None:
    service = ExecutionHealthTrendService(
        FakePersistence(
            [
                make_record(
                    success=True
                )
            ]
        )  # type: ignore[arg-type]
    )

    trend = await service.summarize(
        window_size=5
    )

    assert trend.direction == "unknown"
    assert trend.current.size == 1
    assert trend.previous.size == 0


@pytest.mark.asyncio
async def test_trend_rejects_invalid_window_size() -> None:
    service = ExecutionHealthTrendService(
        FakePersistence(
            []
        )  # type: ignore[arg-type]
    )

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        await service.summarize(
            window_size=0
        )
