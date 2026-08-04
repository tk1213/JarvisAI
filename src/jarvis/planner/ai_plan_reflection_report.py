from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionResult,
)


@dataclass(slots=True, frozen=True)
class AIPlanReflectionReport:
    summary: str
    lines: tuple[str, ...]


class AIPlanReflectionReportBuilder:
    def build(
        self,
        reflection: AIPlanReflectionResult,
    ) -> AIPlanReflectionReport:
        summary = (
            "AI plan reflection: "
            f"decision={reflection.decision.value}, "
            f"success={reflection.success}, "
            f"completed_steps={reflection.completed_steps}, "
            f"failed_steps={reflection.failed_steps}."
        )

        lines = tuple(
            self._line(
                finding.code,
                finding.message,
                finding.step_index,
                finding.capability,
            )
            for finding in reflection.findings
        )

        return AIPlanReflectionReport(
            summary=summary,
            lines=lines,
        )

    @staticmethod
    def _line(
        code: str,
        message: str,
        step_index: int | None,
        capability: str | None,
    ) -> str:
        location = ""

        if step_index is not None:
            location += f" step={step_index}"

        if capability is not None:
            location += f" capability={capability}"

        return (
            f"{code}:{location} {message}"
        ).strip()
