from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_anomaly_triage import (
    ExecutionAnomalyTriage,
)


@dataclass(slots=True, frozen=True)
class ExecutionAnomalyTriageReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionAnomalyTriageReportBuilder:
    def build(
        self,
        triage: ExecutionAnomalyTriage,
    ) -> ExecutionAnomalyTriageReport:
        highest = (
            "none"
            if triage.highest_severity is None
            else triage.highest_severity.value
        )

        summary = (
            "Execution anomaly triage: "
            f"{triage.total} item(s), "
            f"highest_severity={highest}."
        )

        lines = tuple(
            self._line(
                item.priority,
                item.anomaly,
            )
            for item in triage.items
        )

        if not lines:
            lines = (
                "No anomalies require triage.",
            )

        return ExecutionAnomalyTriageReport(
            summary=summary,
            lines=lines,
        )

    @staticmethod
    def _line(
        priority: int,
        anomaly,
    ) -> str:
        capability = (
            ""
            if anomaly.capability is None
            else f" [{anomaly.capability}]"
        )

        return (
            f"{priority}. "
            f"{anomaly.severity.value}: "
            f"{anomaly.code}"
            f"{capability} - "
            f"{anomaly.message}"
        )
