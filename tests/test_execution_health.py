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
from jarvis.planner.execution_statistics import ExecutionStatistics


class FakeStatisticsService:
    def __init__(
        self,
        statistics: ExecutionStatistics,
    ) -> None:
        self.statistics = statistics

    async def summarize(
        self,
        *,
        limit: int = 100,
    ) -> ExecutionStatistics:
        del limit
        return self.statistics


class FakeReliabilityService:
    def __init__(
        self,
        reliability: CapabilityReliabilitySummary,
    ) -> None:
        self.reliability = reliability

    async def summarize(
        self,
        *,
        limit: int = 100,
    ) -> CapabilityReliabilitySummary:
        del limit
        return self.reliability


def make_service(
    statistics: ExecutionStatistics,
    reliability: CapabilityReliabilitySummary,
) -> ExecutionHealthService:
    return ExecutionHealthService(
        FakeStatisticsService(
            statistics
        ),  # type: ignore[arg-type]
        FakeReliabilityService(
            reliability
        ),  # type: ignore[arg-type]
    )


@pytest.mark.asyncio
async def test_health_is_unknown_without_history() -> None:
    service = make_service(
        ExecutionStatistics(
            total=0,
            completed=0,
            failed=0,
            retried_steps=0,
            timed_out_steps=0,
            capability_counts={},
            capability_failure_counts={},
        ),
        CapabilityReliabilitySummary(
            total_capabilities=0,
            capabilities=(),
        ),
    )

    snapshot = await service.check()

    assert snapshot.level is ExecutionHealthLevel.UNKNOWN
    assert snapshot.total_executions == 0


@pytest.mark.asyncio
async def test_health_is_healthy_for_reliable_history() -> None:
    service = make_service(
        ExecutionStatistics(
            total=10,
            completed=9,
            failed=1,
            retried_steps=1,
            timed_out_steps=0,
            capability_counts={
                "system.ping": 10,
            },
            capability_failure_counts={
                "system.ping": 1,
            },
        ),
        CapabilityReliabilitySummary(
            total_capabilities=1,
            capabilities=(
                CapabilityReliability(
                    capability="system.ping",
                    executions=10,
                    failures=1,
                    retries=1,
                    timeouts=0,
                ),
            ),
        ),
    )

    snapshot = await service.check()

    assert snapshot.level is ExecutionHealthLevel.HEALTHY
    assert snapshot.success_rate == pytest.approx(
        0.9
    )


@pytest.mark.asyncio
async def test_health_is_degraded_for_timeouts() -> None:
    service = make_service(
        ExecutionStatistics(
            total=10,
            completed=8,
            failed=2,
            retried_steps=2,
            timed_out_steps=1,
            capability_counts={
                "system.health": 10,
            },
            capability_failure_counts={
                "system.health": 2,
            },
        ),
        CapabilityReliabilitySummary(
            total_capabilities=1,
            capabilities=(
                CapabilityReliability(
                    capability="system.health",
                    executions=10,
                    failures=2,
                    retries=2,
                    timeouts=1,
                ),
            ),
        ),
    )

    snapshot = await service.check()

    assert snapshot.level is ExecutionHealthLevel.DEGRADED


@pytest.mark.asyncio
async def test_health_is_unhealthy_for_unreliable_capability() -> None:
    service = make_service(
        ExecutionStatistics(
            total=5,
            completed=3,
            failed=2,
            retried_steps=1,
            timed_out_steps=0,
            capability_counts={
                "system.health": 3,
                "system.ping": 2,
            },
            capability_failure_counts={
                "system.health": 2,
            },
        ),
        CapabilityReliabilitySummary(
            total_capabilities=2,
            capabilities=(
                CapabilityReliability(
                    capability="system.health",
                    executions=3,
                    failures=2,
                    retries=1,
                    timeouts=0,
                ),
                CapabilityReliability(
                    capability="system.ping",
                    executions=2,
                    failures=0,
                    retries=0,
                    timeouts=0,
                ),
            ),
        ),
    )

    snapshot = await service.check()

    assert snapshot.level is ExecutionHealthLevel.UNHEALTHY
    assert snapshot.unreliable_capabilities == (
        "system.health",
    )


@pytest.mark.asyncio
async def test_health_rejects_invalid_limit() -> None:
    service = make_service(
        ExecutionStatistics(
            total=0,
            completed=0,
            failed=0,
            retried_steps=0,
            timed_out_steps=0,
            capability_counts={},
            capability_failure_counts={},
        ),
        CapabilityReliabilitySummary(
            total_capabilities=0,
            capabilities=(),
        ),
    )

    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        await service.check(
            limit=0
        )
