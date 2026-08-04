from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from jarvis.planner.capability_reliability import (
    CapabilityReliabilityService,
    CapabilityReliabilitySummary,
)
from jarvis.planner.execution_statistics import (
    ExecutionStatistics,
    ExecutionStatisticsService,
)


class ExecutionHealthLevel(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class ExecutionHealthSnapshot:
    level: ExecutionHealthLevel
    total_executions: int
    success_rate: float
    retried_steps: int
    timed_out_steps: int
    unreliable_capabilities: tuple[str, ...]
    reason: str


class ExecutionHealthService:
    def __init__(
        self,
        statistics: ExecutionStatisticsService,
        reliability: CapabilityReliabilityService,
    ) -> None:
        self._statistics = statistics
        self._reliability = reliability

    async def check(
        self,
        *,
        limit: int = 100,
    ) -> ExecutionHealthSnapshot:
        if limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        statistics = await self._statistics.summarize(
            limit=limit
        )

        reliability = await self._reliability.summarize(
            limit=limit
        )

        return self._classify(
            statistics=statistics,
            reliability=reliability,
        )

    @staticmethod
    def _classify(
        *,
        statistics: ExecutionStatistics,
        reliability: CapabilityReliabilitySummary,
    ) -> ExecutionHealthSnapshot:
        if statistics.total == 0:
            return ExecutionHealthSnapshot(
                level=ExecutionHealthLevel.UNKNOWN,
                total_executions=0,
                success_rate=0.0,
                retried_steps=0,
                timed_out_steps=0,
                unreliable_capabilities=(),
                reason="No persisted execution history is available.",
            )

        unreliable = tuple(
            item.capability
            for item in reliability.capabilities
            if (
                item.executions >= 2
                and item.success_rate < 0.5
            )
        )

        if (
            statistics.success_rate < 0.5
            or statistics.timed_out_steps >= 3
            or unreliable
        ):
            level = ExecutionHealthLevel.UNHEALTHY
            reason = (
                "Execution reliability is below the healthy threshold."
            )

        elif (
            statistics.success_rate < 0.8
            or statistics.retried_steps >= 3
            or statistics.timed_out_steps > 0
        ):
            level = ExecutionHealthLevel.DEGRADED
            reason = (
                "Execution reliability shows elevated retries, "
                "timeouts, or failures."
            )

        else:
            level = ExecutionHealthLevel.HEALTHY
            reason = (
                "Recent execution reliability is within healthy limits."
            )

        return ExecutionHealthSnapshot(
            level=level,
            total_executions=statistics.total,
            success_rate=statistics.success_rate,
            retried_steps=statistics.retried_steps,
            timed_out_steps=statistics.timed_out_steps,
            unreliable_capabilities=unreliable,
            reason=reason,
        )
