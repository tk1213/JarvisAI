from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_incident_grouping import (
    ExecutionIncidentGroupingSummary,
)


@dataclass(slots=True, frozen=True)
class ExecutionIncidentGroupingReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionIncidentGroupingReportBuilder:
    def build(
        self,
        grouping: ExecutionIncidentGroupingSummary,
    ) -> ExecutionIncidentGroupingReport:
        summary = (
            "Execution incident grouping: "
            f"{grouping.total_incidents} incident(s), "
            f"{grouping.total_groups} group(s)."
        )

        lines = tuple(
            (
                f"{group.fingerprint}: "
                f"occurrences={group.occurrence_count}, "
                f"incidents={','.join(group.incident_ids)}, "
                f"severities={','.join(group.severities)}, "
                f"capabilities="
                f"{','.join(group.capabilities) or 'none'}"
            )
            for group in grouping.groups
        )

        if not lines:
            lines = (
                "No execution incidents are available for grouping.",
            )

        return ExecutionIncidentGroupingReport(
            summary=summary,
            lines=lines,
        )
