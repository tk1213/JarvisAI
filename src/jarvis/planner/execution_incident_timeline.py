from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import pairwise
from statistics import mean

from jarvis.planner.execution_incidents import ExecutionIncident


@dataclass(slots=True, frozen=True)
class ExecutionIncidentTimelineEntry:
    incident_id: str
    severity: str
    title: str
    occurred_at: datetime


@dataclass(slots=True, frozen=True)
class ExecutionIncidentTimeline:
    fingerprint: str
    occurrence_count: int
    first_seen: datetime
    last_seen: datetime
    latest_severity: str
    average_interval_seconds: float | None
    age_seconds: float
    seconds_since_last: float
    entries: tuple[ExecutionIncidentTimelineEntry, ...]


class ExecutionIncidentTimelineService:
    def build(
        self,
        *,
        fingerprint: str,
        incidents: list[ExecutionIncident],
        now: datetime | None = None,
    ) -> ExecutionIncidentTimeline | None:
        normalized_fingerprint = fingerprint.strip()

        if not normalized_fingerprint:
            raise ValueError(
                "fingerprint cannot be empty."
            )

        if not incidents:
            return None

        normalized_now = (
            now
            if now is not None
            else datetime.now(UTC)
        )

        if normalized_now.tzinfo is None:
            raise ValueError(
                "now must be timezone-aware."
            )

        ordered = sorted(
            incidents,
            key=lambda incident: incident.created_at,
        )

        first_seen = ordered[0].created_at
        last_seen = ordered[-1].created_at

        intervals = [
            (
                current.created_at
                - previous.created_at
            ).total_seconds()
            for previous, current in pairwise(
                ordered
            )
        ]

        average_interval_seconds = (
            mean(intervals)
            if intervals
            else None
        )

        age_seconds = max(
            0.0,
            (
                normalized_now
                - first_seen
            ).total_seconds(),
        )

        seconds_since_last = max(
            0.0,
            (
                normalized_now
                - last_seen
            ).total_seconds(),
        )

        entries = tuple(
            ExecutionIncidentTimelineEntry(
                incident_id=incident.incident_id,
                severity=incident.severity.value,
                title=incident.title,
                occurred_at=incident.created_at,
            )
            for incident in ordered
        )

        return ExecutionIncidentTimeline(
            fingerprint=normalized_fingerprint,
            occurrence_count=len(
                entries
            ),
            first_seen=first_seen,
            last_seen=last_seen,
            latest_severity=ordered[-1].severity.value,
            average_interval_seconds=average_interval_seconds,
            age_seconds=age_seconds,
            seconds_since_last=seconds_since_last,
            entries=entries,
        )