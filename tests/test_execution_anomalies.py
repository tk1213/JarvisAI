from __future__ import annotations

import pytest

from jarvis.planner.capability_reliability import (
    CapabilityReliability,
    CapabilityReliabilitySummary,
)
from jarvis.planner.execution_anomalies import (
    ExecutionAnomalyService,
    ExecutionAnomalySeverity,
)
from jarvis.planner.execution_health import (
    ExecutionHealthLevel,
)
from jarvis.planner.execution_health_trends import (
    ExecutionHealthTrend,
    ExecutionHealthWindow,
)
from jarvis.planner.execution_statistics import (
    ExecutionStatistics,
)


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


class FakeTrendService:
    def __init__(
        self,
        trend: ExecutionHealthTrend,
    ) -> None:
        self.trend = trend

    async def summarize(
        self,
        *,
        window_size: int = 20,
    ) -> ExecutionHealthTrend:
        del window_size
        return self.trend


def make_service(
    *,
    success_rate: float,
    timed_out_steps: int,
    trend_direction: str,
    capability_success_rate: float,
) -> ExecutionAnomalyService:
    total = 10
    completed = round(
        success_rate * total
    )

    capability_executions = 4
    capability_failures = round(
        (
            1.0
            - capability_success_rate
        )
        * capability_executions
    )

    statistics = ExecutionStatistics(
        total=total,
        completed=completed,
        failed=total - completed,
        retried_steps=1,
        timed_out_steps=timed_out_steps,
        capability_counts={
            "system.health": capability_executions,
        },
        capability_failure_counts={
            "system.health": capability_failures,
        },
    )

    reliability = CapabilityReliabilitySummary(
        total_capabilities=1,
        capabilities=(
            CapabilityReliability(
                capability="system.health",
                executions=capability_executions,
                failures=capability_failures,
                retries=1,
                timeouts=timed_out_steps,
            ),
        ),
    )

    trend = ExecutionHealthTrend(
        current=ExecutionHealthWindow(
            size=5,
            completed=4,
            failed=1,
            retries=1,
            timeouts=timed_out_steps,
        ),
        previous=ExecutionHealthWindow(
            size=5,
            completed=5,
            failed=0,
            retries=0,
            timeouts=0,
        ),
        direction=trend_direction,
        level=ExecutionHealthLevel.DEGRADED,
        reason="test",
    )

    return ExecutionAnomalyService(
        FakeStatisticsService(
            statistics
        ),  # type: ignore[arg-type]
        FakeReliabilityService(
            reliability
        ),  # type: ignore[arg-type]
        FakeTrendService(
            trend
        ),  # type: ignore[arg-type]
    )


@pytest.mark.asyncio
async def test_detects_critical_reliability_anomalies() -> None:
    service = make_service(
        success_rate=0.4,
        timed_out_steps=3,
        trend_direction="worsening",
        capability_success_rate=0.25,
    )

    summary = await service.detect()

    assert summary.has_anomalies is True
    assert summary.critical >= 2
    assert summary.warnings >= 1

    codes = {
        anomaly.code
        for anomaly in summary.anomalies
    }

    assert "low_success_rate" in codes
    assert "repeated_timeouts" in codes
    assert "worsening_execution_trend" in codes
    assert "unreliable_capability" in codes


@pytest.mark.asyncio
async def test_detects_degraded_anomalies() -> None:
    service = make_service(
        success_rate=0.7,
        timed_out_steps=1,
        trend_direction="stable",
        capability_success_rate=0.75,
    )

    summary = await service.detect()

    assert summary.critical == 0
    assert summary.warnings >= 2

    severities = {
        anomaly.severity
        for anomaly in summary.anomalies
    }

    assert ExecutionAnomalySeverity.WARNING in severities


@pytest.mark.asyncio
async def test_rejects_invalid_limits() -> None:
    service = make_service(
        success_rate=1.0,
        timed_out_steps=0,
        trend_direction="stable",
        capability_success_rate=1.0,
    )

    with pytest.raises(
        ValueError,
        match="limit",
    ):
        await service.detect(
            limit=0
        )

    with pytest.raises(
        ValueError,
        match="trend_window_size",
    ):
        await service.detect(
            trend_window_size=0
        )
