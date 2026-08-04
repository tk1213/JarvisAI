from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.ai_plan_execution import (
    AIPlanExecutionResult,
)


@dataclass(slots=True, frozen=True)
class AIPlanExecutionReport:
    summary: str
    lines: tuple[str, ...]


class AIPlanExecutionReportBuilder:
    def build(
        self,
        result: AIPlanExecutionResult,
    ) -> AIPlanExecutionReport:
        plan = result.execution.plan

        summary = (
            "AI plan execution: "
            f"goal={plan.goal}, "
            f"status={plan.status.value}, "
            f"completed_steps={result.completed_steps}/"
            f"{len(plan.steps)}."
        )

        lines = tuple(
            self._step_line(
                step_result.step_index,
                step_result.capability,
                step_result.status.value,
                step_result.attempts,
                step_result.error,
            )
            for step_result in result.execution.step_results
        )

        if not lines:
            lines = (
                "No plan steps were executed.",
            )

        return AIPlanExecutionReport(
            summary=summary,
            lines=lines,
        )

    @staticmethod
    def _step_line(
        step_index: int,
        capability: str,
        status: str,
        attempts: int,
        error: str | None,
    ) -> str:
        error_text = (
            ""
            if error is None
            else f", error={error}"
        )

        return (
            f"{step_index}. "
            f"{capability}: "
            f"status={status}, "
            f"attempts={attempts}"
            f"{error_text}"
        )
