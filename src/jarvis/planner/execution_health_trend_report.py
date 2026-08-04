from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_health_trends import (
    ExecutionHealthTrend,
)


@dataclass(slots=True, frozen=True)
class ExecutionHealthTrendReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionHealthTrendReportBuilder:
    def build(
        self,
        trend: ExecutionHealthTrend,
    ) -> ExecutionHealthTrendReport:
        summary = (
            "Execution health trend: "
            f"{trend.direction}, "
            f"level={trend.level.value}, "
            f"current_success_rate="
            f"{trend.current.success_rate:.1%}."
        )

        lines = (
            (
                "Current window: "
                f"size={trend.current.size}, "
                f"completed={trend.current.completed}, "
                f"failed={trend.current.failed}, "
                f"retries={trend.current.retries}, "
                f"timeouts={trend.current.timeouts}"
            ),
            (
                "Previous window: "
                f"size={trend.previous.size}, "
                f"completed={trend.previous.completed}, "
                f"failed={trend.previous.failed}, "
                f"retries={trend.previous.retries}, "
                f"timeouts={trend.previous.timeouts}"
            ),
            (
                "Reason: "
                f"{trend.reason}"
            ),
        )

        return ExecutionHealthTrendReport(
            summary=summary,
            lines=lines,
        )
