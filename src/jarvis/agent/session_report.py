from __future__ import annotations

from dataclasses import dataclass

from jarvis.agent.session import AIAgentSessionSnapshot


@dataclass(slots=True, frozen=True)
class AIAgentSessionReport:
    summary: str
    lines: tuple[str, ...]


class AIAgentSessionReportBuilder:
    def build(
        self,
        snapshot: AIAgentSessionSnapshot,
    ) -> AIAgentSessionReport:
        summary = (
            "AI agent session: "
            f"pending_plan={snapshot.has_pending_plan}, "
            f"memory_records={snapshot.memory_records}."
        )

        lines = (
            (
                "Latest goal: "
                f"{snapshot.latest_goal or 'none'}"
            ),
            (
                "Latest success: "
                + (
                    "none"
                    if snapshot.latest_success is None
                    else str(
                        snapshot.latest_success
                    )
                )
            ),
            (
                "Snapshot time: "
                f"{snapshot.created_at.isoformat()}"
            ),
        )

        return AIAgentSessionReport(
            summary=summary,
            lines=lines,
        )
