from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_incident_grouping import (
    ExecutionIncidentGroupingSummary,
)
from jarvis.planner.execution_incident_timeline import (
    ExecutionIncidentTimeline,
)


@dataclass(slots=True, frozen=True)
class ExecutionIncidentDashboardSnapshot:
    total_incidents: int
    total_groups: int
    active_fingerprints: tuple[str, ...]
    latest_severity: str
    latest_incident_id: str | None
    oldest_first_seen: str | None
    newest_last_seen: str | None


class ExecutionIncidentDashboardService:
    def build(
        self,
        *,
        grouping: ExecutionIncidentGroupingSummary,
        timelines: list[ExecutionIncidentTimeline],
    ) -> ExecutionIncidentDashboardSnapshot:
        fingerprints = tuple(
            sorted(
                {
                    group.fingerprint
                    for group in grouping.groups
                }
            )
        )

        latest_timeline = (
            max(
                timelines,
                key=lambda timeline: timeline.last_seen,
            )
            if timelines
            else None
        )

        oldest_first_seen = (
            min(
                timeline.first_seen
                for timeline in timelines
            ).isoformat()
            if timelines
            else None
        )

        newest_last_seen = (
            max(
                timeline.last_seen
                for timeline in timelines
            ).isoformat()
            if timelines
            else None
        )

        latest_incident_id = (
            latest_timeline.entries[-1].incident_id
            if (
                latest_timeline is not None
                and latest_timeline.entries
            )
            else None
        )

        latest_severity = (
            latest_timeline.latest_severity
            if latest_timeline is not None
            else "none"
        )

        return ExecutionIncidentDashboardSnapshot(
            total_incidents=grouping.total_incidents,
            total_groups=grouping.total_groups,
            active_fingerprints=fingerprints,
            latest_severity=latest_severity,
            latest_incident_id=latest_incident_id,
            oldest_first_seen=oldest_first_seen,
            newest_last_seen=newest_last_seen,
        )
