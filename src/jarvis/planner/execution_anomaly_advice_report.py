from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_anomaly_advice import (
    ExecutionAnomalyAdviceSummary,
)


@dataclass(slots=True, frozen=True)
class ExecutionAnomalyAdviceReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionAnomalyAdviceReportBuilder:
    def build(
        self,
        advice: ExecutionAnomalyAdviceSummary,
    ) -> ExecutionAnomalyAdviceReport:
        summary = (
            "Execution anomaly advice: "
            f"{advice.total} recommendation(s)."
        )

        lines = tuple(
            self._line(
                item.priority,
                item.anomaly_code,
                item.capability,
                item.recommendation,
            )
            for item in advice.advice
        )

        if not lines:
            lines = (
                "No anomaly recommendations are currently needed.",
            )

        return ExecutionAnomalyAdviceReport(
            summary=summary,
            lines=lines,
        )

    @staticmethod
    def _line(
        priority: int,
        anomaly_code: str,
        capability: str | None,
        recommendation: str,
    ) -> str:
        capability_text = (
            ""
            if capability is None
            else f" [{capability}]"
        )

        return (
            f"{priority}. "
            f"{anomaly_code}"
            f"{capability_text}: "
            f"{recommendation}"
        )
