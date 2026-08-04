from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryRecord,
)


@dataclass(slots=True, frozen=True)
class AIPlanMemoryReport:
    summary: str
    lines: tuple[str, ...]


class AIPlanMemoryReportBuilder:
    def build(
        self,
        records: tuple[
            AIPlanMemoryRecord,
            ...
        ],
    ) -> AIPlanMemoryReport:
        successful = sum(
            record.success
            for record in records
        )

        summary = (
            "AI plan memory: "
            f"{len(records)} record(s), "
            f"{successful} successful, "
            f"{len(records) - successful} failed."
        )

        lines = tuple(
            (
                f"{index}. "
                f"{record.created_at.isoformat()} "
                f"goal={record.goal!r}, "
                f"success={record.success}, "
                f"decision={record.reflection_decision}, "
                f"capabilities="
                f"{','.join(record.capabilities) or 'none'}"
            )
            for index, record in enumerate(
                records,
                start=1,
            )
        )

        if not lines:
            lines = (
                "No AI plan memory records are available.",
            )

        return AIPlanMemoryReport(
            summary=summary,
            lines=lines,
        )
