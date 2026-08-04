from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_health import (
    ExecutionHealthSnapshot,
)


@dataclass(slots=True, frozen=True)
class ExecutionHealthReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionHealthReportBuilder:
    def build(
        self,
        snapshot: ExecutionHealthSnapshot,
    ) -> ExecutionHealthReport:
        summary = (
            "Execution health: "
            f"{snapshot.level.value}, "
            f"executions={snapshot.total_executions}, "
            f"success_rate={snapshot.success_rate:.1%}."
        )

        lines = [
            (
                "Retried steps: "
                f"{snapshot.retried_steps}"
            ),
            (
                "Timed out steps: "
                f"{snapshot.timed_out_steps}"
            ),
            (
                "Reason: "
                f"{snapshot.reason}"
            ),
        ]

        if snapshot.unreliable_capabilities:
            lines.append(
                "Unreliable capabilities: "
                + ", ".join(
                    snapshot.unreliable_capabilities
                )
            )

        return ExecutionHealthReport(
            summary=summary,
            lines=tuple(
                lines
            ),
        )
