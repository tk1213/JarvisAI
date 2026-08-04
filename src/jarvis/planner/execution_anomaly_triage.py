from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_anomalies import (
    ExecutionAnomaly,
    ExecutionAnomalySeverity,
    ExecutionAnomalySummary,
)

_SEVERITY_RANK = {
    ExecutionAnomalySeverity.CRITICAL: 3,
    ExecutionAnomalySeverity.WARNING: 2,
    ExecutionAnomalySeverity.INFO: 1,
}


@dataclass(slots=True, frozen=True)
class ExecutionAnomalyTriageItem:
    priority: int
    anomaly: ExecutionAnomaly


@dataclass(slots=True, frozen=True)
class ExecutionAnomalyTriage:
    total: int
    highest_severity: ExecutionAnomalySeverity | None
    items: tuple[
        ExecutionAnomalyTriageItem,
        ...
    ]


class ExecutionAnomalyTriageService:
    def prioritize(
        self,
        summary: ExecutionAnomalySummary,
    ) -> ExecutionAnomalyTriage:
        ordered = sorted(
            summary.anomalies,
            key=self._sort_key,
        )

        items = tuple(
            ExecutionAnomalyTriageItem(
                priority=index,
                anomaly=anomaly,
            )
            for index, anomaly in enumerate(
                ordered,
                start=1,
            )
        )

        highest_severity = (
            ordered[0].severity
            if ordered
            else None
        )

        return ExecutionAnomalyTriage(
            total=len(
                items
            ),
            highest_severity=highest_severity,
            items=items,
        )

    @staticmethod
    def _sort_key(
        anomaly: ExecutionAnomaly,
    ) -> tuple[
        int,
        str,
        str,
    ]:
        return (
            -_SEVERITY_RANK[
                anomaly.severity
            ],
            anomaly.capability or "",
            anomaly.code,
        )
