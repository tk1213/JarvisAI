from __future__ import annotations

import pytest

from jarvis.planner.capability_reliability import (
    CapabilityReliability,
    CapabilityReliabilitySummary,
)
from jarvis.planner.execution_health import (
    ExecutionHealthLevel,
    ExecutionHealthService,
)
from jarvis.planner.execution_health_trends import (
    ExecutionHealthTrendService,
)
from jarvis.planner.execution_statistics import (
    ExecutionStatistics,
)


class FakeStatisticsService:
    async def summarize(
        self,
        *,
        limit: int = 100,
    ) -> ExecutionStatistics:
        del limit

        return ExecutionStatistics(
            total=10,
            completed=8,
            failed=2,
            retried_steps=2,
            timed_out_steps=1,
            capability_counts={
                "system.health": 5,
                "system.ping": 5,
            },
            capability_failure_counts={
                "system.health": 2,
            },
        )


class FakeReliabilityService:
    async def summarize(
        self,
        *,
        limit: int = 100,
    ) -> CapabilityReliabilitySummary:
        del limit

        return CapabilityReliabilitySummary(
            total_capabilities=2,
            capabilities=(
                CapabilityReliability(
                    capability="system.health",
                    executions=5,
                    failures=2,
                    retries=2,
                    timeouts=1,
                ),
                CapabilityReliability(
                    capability="system.ping",
                    executions=5,
                    failures=0,
                    retries=0,
                    timeouts=0,
                ),
            ),
        )


class EmptyPersistence:
    async def list_recent(
        self,
        *,
        limit: int = 40,
    ):
        del limit
        return []


@pytest.mark.asyncio
async def test_execution_health_and_trend_contracts() -> None:
    health_service = ExecutionHealthService(
        FakeStatisticsService(),  # type: ignore[arg-type]
        FakeReliabilityService(),  # type: ignore[arg-type]
    )

    snapshot = await health_service.check(
        limit=10
    )

    assert snapshot.level is ExecutionHealthLevel.DEGRADED
    assert snapshot.total_executions == 10
    assert snapshot.success_rate == pytest.approx(
        0.8
    )
    assert snapshot.timed_out_steps == 1

    trend_service = ExecutionHealthTrendService(
        EmptyPersistence()  # type: ignore[arg-type]
    )

    trend = await trend_service.summarize(
        window_size=5
    )

    assert trend.level is ExecutionHealthLevel.UNKNOWN
    assert trend.direction == "unknown"
