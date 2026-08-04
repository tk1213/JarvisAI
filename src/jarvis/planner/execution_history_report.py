from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_history import (
    ExecutionHistorySummary,
)


@dataclass(slots=True, frozen=True)
class ExecutionHistoryReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionHistoryReportBuilder:
    def build(
        self,
        history: ExecutionHistorySummary,
    ) -> ExecutionHistoryReport:
        summary = (
            "Execution history: "
            f"{history.total} record(s), "
            f"{history.completed} completed, "
            f"{history.failed} failed."
        )

        lines = tuple(
            (
                f"{index}. "
                f"{record.goal} "
                f"[{record.plan_status}] "
                f"steps={len(record.steps)} "
                f"events={len(record.events)}"
            )
            for index, record in enumerate(
                history.records,
                start=1,
            )
        )

        return ExecutionHistoryReport(
            summary=summary,
            lines=lines,
        )
