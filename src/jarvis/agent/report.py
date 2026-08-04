from __future__ import annotations

from dataclasses import dataclass

from jarvis.agent.runtime import AIAgentRunResult


@dataclass(slots=True, frozen=True)
class AIAgentRunReport:
    summary: str
    lines: tuple[str, ...]


class AIAgentRunReportBuilder:
    def build(
        self,
        result: AIAgentRunResult,
    ) -> AIAgentRunReport:
        summary = (
            "AI agent run: "
            f"status={result.status.value}, "
            f"success={result.success}, "
            f"requires_confirmation="
            f"{result.requires_confirmation}."
        )

        lines: list[str] = []

        if result.preview is not None:
            lines.append(
                
                    "Plan: "
                    f"goal={result.preview.plan.goal}, "
                    f"steps={len(result.preview.plan.steps)}"
                
            )

        if result.execution is not None:
            lines.append(
                
                    "Execution: "
                    f"status={result.execution.plan.status.value}, "
                    f"completed_steps="
                    f"{result.execution.completed_steps}"
                
            )

        if result.reflection is not None:
            lines.append(
                
                    "Reflection: "
                    f"decision="
                    f"{result.reflection.decision.value}"
                
            )

        if result.memory_record is not None:
            lines.append(
                
                    "Memory: "
                    f"goal={result.memory_record.goal!r}, "
                    f"success={result.memory_record.success}"
                
            )

        if not lines:
            lines.append(
                "No executable AI plan was produced."
            )

        return AIAgentRunReport(
            summary=summary,
            lines=tuple(
                lines
            ),
        )
