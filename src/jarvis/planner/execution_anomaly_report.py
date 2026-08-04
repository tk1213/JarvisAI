from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_anomalies import (
    ExecutionAnomalySummary,
)


@dataclass(slots=True, frozen=True)
class ExecutionAnomalyReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionAnomalyReportBuilder:
    def build(
        self,
        anomalies: ExecutionAnomalySummary,
    ) -> ExecutionAnomalyReport:
        summary = (
            "Execution anomalies: "
            f"{anomalies.total} detected, "
            f"{anomalies.critical} critical, "
            f"{anomalies.warnings} warning(s)."
        )

        lines = tuple(
            self._line(
                anomaly
            )
            for anomaly in anomalies.anomalies
        )

        if not lines:
            lines = (
                "No execution anomalies detected.",
            )

        return ExecutionAnomalyReport(
            summary=summary,
            lines=lines,
        )

    @staticmethod
    def _line(
        anomaly,
    ) -> str:
        capability = (
            ""
            if anomaly.capability is None
            else f" [{anomaly.capability}]"
        )

        return (
            f"{anomaly.severity.value}: "
            f"{anomaly.code}"
            f"{capability} - "
            f"{anomaly.message}"
        )
