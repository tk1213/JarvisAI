from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_incidents import (
    ExecutionIncident,
)


@dataclass(slots=True, frozen=True)
class ExecutionIncidentReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionIncidentReportBuilder:
    def build(
        self,
        incident: ExecutionIncident,
    ) -> ExecutionIncidentReport:
        summary = (
            f"{incident.incident_id}: "
            f"{incident.title} "
            f"[{incident.severity.value}]"
        )

        lines = (
            incident.summary,
            (
                "Anomaly codes: "
                + ", ".join(
                    incident.anomaly_codes
                )
            ),
            (
                "Capabilities: "
                + (
                    ", ".join(
                        incident.capabilities
                    )
                    if incident.capabilities
                    else "none"
                )
            ),
            (
                "Created at: "
                f"{incident.created_at.isoformat()}"
            ),
        )

        return ExecutionIncidentReport(
            summary=summary,
            lines=lines,
        )
