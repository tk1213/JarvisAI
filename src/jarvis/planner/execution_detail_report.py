from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_detail import ExecutionDetail


@dataclass(slots=True, frozen=True)
class ExecutionDetailReport:
    summary: str
    step_lines: tuple[str, ...]
    timeline_lines: tuple[str, ...]


class ExecutionDetailReportBuilder:
    def build(
        self,
        detail: ExecutionDetail,
    ) -> ExecutionDetailReport:
        summary = (
            f"Execution {detail.record_id}: "
            f"{detail.goal} "
            f"[{detail.plan_status}], "
            f"{len(detail.steps)} step(s), "
            f"{detail.failure_count} failure(s)."
        )

        step_lines = tuple(
            self._step_line(
                detail=detail,
                index=index,
            )
            for index in range(
                len(detail.steps)
            )
        )

        timeline_lines = tuple(
            (
                f"{event.sequence}. "
                f"{event.event_type} "
                f"step={event.step_index} "
                f"capability={event.capability} "
                f"attempt={event.attempt}"
            )
            for event in detail.timeline
        )

        return ExecutionDetailReport(
            summary=summary,
            step_lines=step_lines,
            timeline_lines=timeline_lines,
        )

    @staticmethod
    def _step_line(
        *,
        detail: ExecutionDetail,
        index: int,
    ) -> str:
        step = detail.steps[
            index
        ]

        line = (
            f"{step.step_index}. "
            f"{step.capability} "
            f"[{step.status}] "
            f"attempts={step.attempts}"
        )

        if step.error:
            line += (
                f" error={step.error}"
            )

        return line
