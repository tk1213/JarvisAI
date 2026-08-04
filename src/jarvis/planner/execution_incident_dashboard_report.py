from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_incident_dashboard import (
    ExecutionIncidentDashboardSnapshot,
)


@dataclass(slots=True, frozen=True)
class ExecutionIncidentDashboardReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionIncidentDashboardReportBuilder:
    def build(
        self,
        snapshot: ExecutionIncidentDashboardSnapshot,
    ) -> ExecutionIncidentDashboardReport:
        summary = (
            "Execution incident dashboard: "
            f"{snapshot.total_incidents} incident(s), "
            f"{snapshot.total_groups} group(s), "
            f"latest_severity={snapshot.latest_severity}."
        )

        lines = (
            (
                "Active fingerprints: "
                + (
                    ", ".join(
                        snapshot.active_fingerprints
                    )
                    if snapshot.active_fingerprints
                    else "none"
                )
            ),
            (
                "Latest incident ID: "
                f"{snapshot.latest_incident_id or 'none'}"
            ),
            (
                "Oldest first seen: "
                f"{snapshot.oldest_first_seen or 'none'}"
            ),
            (
                "Newest last seen: "
                f"{snapshot.newest_last_seen or 'none'}"
            ),
        )

        return ExecutionIncidentDashboardReport(
            summary=summary,
            lines=lines,
        )
