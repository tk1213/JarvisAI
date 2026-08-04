from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_statistics import (
    ExecutionStatistics,
)


@dataclass(slots=True, frozen=True)
class ExecutionStatisticsReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionStatisticsReportBuilder:
    def build(
        self,
        statistics: ExecutionStatistics,
    ) -> ExecutionStatisticsReport:
        summary = (
            "Execution statistics: "
            f"{statistics.total} record(s), "
            f"{statistics.completed} completed, "
            f"{statistics.failed} failed, "
            f"success_rate={statistics.success_rate:.1%}."
        )

        lines: list[str] = [
            (
                "Retried steps: "
                f"{statistics.retried_steps}"
            ),
            (
                "Timed out steps: "
                f"{statistics.timed_out_steps}"
            ),
        ]

        for capability in sorted(
            statistics.capability_counts
        ):
            total = statistics.capability_counts[
                capability
            ]
            failures = (
                statistics.capability_failure_counts.get(
                    capability,
                    0,
                )
            )

            lines.append(
                f"{capability}: "
                f"steps={total}, "
                f"failures={failures}"
            )

        return ExecutionStatisticsReport(
            summary=summary,
            lines=tuple(
                lines
            ),
        )
