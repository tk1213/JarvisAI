from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from jarvis.planner.capability_reliability import (
    CapabilityReliabilityService,
)
from jarvis.planner.execution_health_trends import (
    ExecutionHealthTrendService,
)
from jarvis.planner.execution_statistics import (
    ExecutionStatisticsService,
)


class ExecutionAnomalySeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(slots=True, frozen=True)
class ExecutionAnomaly:
    code: str
    severity: ExecutionAnomalySeverity
    message: str
    capability: str | None = None


@dataclass(slots=True, frozen=True)
class ExecutionAnomalySummary:
    total: int
    critical: int
    warnings: int
    anomalies: tuple[
        ExecutionAnomaly,
        ...
    ]

    @property
    def has_anomalies(self) -> bool:
        return self.total > 0


class ExecutionAnomalyService:
    def __init__(
        self,
        statistics: ExecutionStatisticsService,
        reliability: CapabilityReliabilityService,
        trends: ExecutionHealthTrendService,
    ) -> None:
        self._statistics = statistics
        self._reliability = reliability
        self._trends = trends

    async def detect(
        self,
        *,
        limit: int = 100,
        trend_window_size: int = 20,
    ) -> ExecutionAnomalySummary:
        if limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        if trend_window_size < 1:
            raise ValueError(
                "trend_window_size must be at least 1."
            )

        statistics = await self._statistics.summarize(
            limit=limit
        )
        reliability = await self._reliability.summarize(
            limit=limit
        )
        trend = await self._trends.summarize(
            window_size=trend_window_size
        )

        anomalies: list[
            ExecutionAnomaly
        ] = []

        if statistics.total == 0:
            anomalies.append(
                ExecutionAnomaly(
                    code="no_execution_history",
                    severity=ExecutionAnomalySeverity.INFO,
                    message=(
                        "No persisted execution history is "
                        "available for anomaly analysis."
                    ),
                )
            )

        elif statistics.success_rate < 0.5:
            anomalies.append(
                ExecutionAnomaly(
                    code="low_success_rate",
                    severity=ExecutionAnomalySeverity.CRITICAL,
                    message=(
                        "Recent execution success rate is "
                        f"{statistics.success_rate:.1%}."
                    ),
                )
            )

        elif statistics.success_rate < 0.8:
            anomalies.append(
                ExecutionAnomaly(
                    code="degraded_success_rate",
                    severity=ExecutionAnomalySeverity.WARNING,
                    message=(
                        "Recent execution success rate is "
                        f"{statistics.success_rate:.1%}."
                    ),
                )
            )

        if statistics.timed_out_steps >= 3:
            anomalies.append(
                ExecutionAnomaly(
                    code="repeated_timeouts",
                    severity=ExecutionAnomalySeverity.CRITICAL,
                    message=(
                        "Multiple execution timeouts were "
                        "detected in recent history."
                    ),
                )
            )

        elif statistics.timed_out_steps > 0:
            anomalies.append(
                ExecutionAnomaly(
                    code="execution_timeout",
                    severity=ExecutionAnomalySeverity.WARNING,
                    message=(
                        "At least one execution timeout was "
                        "detected in recent history."
                    ),
                )
            )

        if trend.direction == "worsening":
            anomalies.append(
                ExecutionAnomaly(
                    code="worsening_execution_trend",
                    severity=ExecutionAnomalySeverity.WARNING,
                    message=(
                        "Execution reliability is worsening "
                        "relative to the previous window."
                    ),
                )
            )

        for item in reliability.capabilities:
            if (
                item.executions >= 3
                and item.success_rate < 0.5
            ):
                anomalies.append(
                    ExecutionAnomaly(
                        code="unreliable_capability",
                        severity=ExecutionAnomalySeverity.CRITICAL,
                        capability=item.capability,
                        message=(
                            f"{item.capability} has a recent "
                            f"success rate of {item.success_rate:.1%}."
                        ),
                    )
                )

            elif (
                item.executions >= 3
                and item.success_rate < 0.8
            ):
                anomalies.append(
                    ExecutionAnomaly(
                        code="degraded_capability",
                        severity=ExecutionAnomalySeverity.WARNING,
                        capability=item.capability,
                        message=(
                            f"{item.capability} has a recent "
                            f"success rate of {item.success_rate:.1%}."
                        ),
                    )
                )

        critical = sum(
            anomaly.severity
            is ExecutionAnomalySeverity.CRITICAL
            for anomaly in anomalies
        )

        warnings = sum(
            anomaly.severity
            is ExecutionAnomalySeverity.WARNING
            for anomaly in anomalies
        )

        return ExecutionAnomalySummary(
            total=len(
                anomalies
            ),
            critical=critical,
            warnings=warnings,
            anomalies=tuple(
                anomalies
            ),
        )
