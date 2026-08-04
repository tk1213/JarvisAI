from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_incident_timeline import (
    ExecutionIncidentTimeline,
)


@dataclass(slots=True, frozen=True)
class ExecutionIncidentTimelineReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionIncidentTimelineReportBuilder:
    def build(
        self,
        timeline: ExecutionIncidentTimeline,
    ) -> ExecutionIncidentTimelineReport:
        average_interval = (
            "n/a"
            if timeline.average_interval_seconds is None
            else self._duration(
                timeline.average_interval_seconds
            )
        )

        summary = (
            "Execution incident timeline: "
            f"fingerprint={timeline.fingerprint}, "
            f"occurrences={timeline.occurrence_count}, "
            f"latest_severity={timeline.latest_severity}."
        )

        lines = (
            (
                "First seen: "
                f"{timeline.first_seen.isoformat()}"
            ),
            (
                "Last seen: "
                f"{timeline.last_seen.isoformat()}"
            ),
            (
                "Average interval: "
                f"{average_interval}"
            ),
            (
                "Incident age: "
                f"{self._duration(timeline.age_seconds)}"
            ),
            (
                "Time since last incident: "
                f"{self._duration(timeline.seconds_since_last)}"
            ),
            *(
                (
                    f"{index}. "
                    f"{entry.occurred_at.isoformat()} "
                    f"[{entry.severity}] "
                    f"{entry.incident_id} - "
                    f"{entry.title}"
                )
                for index, entry in enumerate(
                    timeline.entries,
                    start=1,
                )
            ),
        )

        return ExecutionIncidentTimelineReport(
            summary=summary,
            lines=lines,
        )

    @staticmethod
    def _duration(
        seconds: float,
    ) -> str:
        if seconds < 60:
            return f"{seconds:.1f}s"

        minutes = seconds / 60

        if minutes < 60:
            return f"{minutes:.1f}m"

        hours = minutes / 60

        if hours < 24:
            return f"{hours:.1f}h"

        days = hours / 24
        return f"{days:.1f}d"
