from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from jarvis.planner.execution_anomalies import (
    ExecutionAnomaly,
    ExecutionAnomalySeverity,
    ExecutionAnomalySummary,
)
from jarvis.planner.execution_anomaly_triage import (
    ExecutionAnomalyTriageService,
)


class ExecutionIncidentSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True, frozen=True)
class ExecutionIncident:
    incident_id: str
    severity: ExecutionIncidentSeverity
    title: str
    summary: str
    anomaly_codes: tuple[str, ...]
    capabilities: tuple[str, ...]
    created_at: datetime


class ExecutionIncidentService:
    def __init__(
        self,
        triage: ExecutionAnomalyTriageService | None = None,
    ) -> None:
        self._triage = (
            triage
            if triage is not None
            else ExecutionAnomalyTriageService()
        )

    def build(
        self,
        anomalies: ExecutionAnomalySummary,
    ) -> ExecutionIncident | None:
        if not anomalies.anomalies:
            return None

        triage = self._triage.prioritize(
            anomalies
        )

        ordered = tuple(
            item.anomaly
            for item in triage.items
        )

        severity = self._severity(
            ordered
        )

        codes = tuple(
            anomaly.code
            for anomaly in ordered
        )

        capabilities = tuple(
            sorted(
                {
                    anomaly.capability
                    for anomaly in ordered
                    if anomaly.capability is not None
                }
            )
        )

        created_at = datetime.now(UTC)

        incident_id = (
            "execution-"
            + created_at.strftime(
                "%Y%m%dT%H%M%SZ"
            )
        )

        title = self._title(
            severity=severity,
            anomalies=ordered,
        )

        summary = (
            f"{len(ordered)} execution anomaly item(s) "
            f"detected; severity={severity.value}."
        )

        return ExecutionIncident(
            incident_id=incident_id,
            severity=severity,
            title=title,
            summary=summary,
            anomaly_codes=codes,
            capabilities=capabilities,
            created_at=created_at,
        )

    @staticmethod
    def _severity(
        anomalies: tuple[
            ExecutionAnomaly,
            ...
        ],
    ) -> ExecutionIncidentSeverity:
        critical = sum(
            anomaly.severity
            is ExecutionAnomalySeverity.CRITICAL
            for anomaly in anomalies
        )

        warnings = sum(
            anomaly.severity
            is ExecutionAnomalySeverity.WARNING
            for anomaly in anomalies
        )

        if critical >= 2:
            return ExecutionIncidentSeverity.CRITICAL

        if critical == 1:
            return ExecutionIncidentSeverity.HIGH

        if warnings >= 2:
            return ExecutionIncidentSeverity.MEDIUM

        return ExecutionIncidentSeverity.LOW

    @staticmethod
    def _title(
        *,
        severity: ExecutionIncidentSeverity,
        anomalies: tuple[
            ExecutionAnomaly,
            ...
        ],
    ) -> str:
        first = anomalies[0]

        if first.capability is not None:
            return (
                f"Execution incident: {first.capability}"
            )

        return (
            "Execution incident: "
            f"{first.code} ({severity.value})"
        )
