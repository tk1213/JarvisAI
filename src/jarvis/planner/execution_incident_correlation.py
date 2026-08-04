from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from jarvis.planner.execution_incidents import ExecutionIncident


@dataclass(slots=True, frozen=True)
class ExecutionIncidentCorrelation:
    fingerprint: str
    incident_id: str
    severity: str
    anomaly_codes: tuple[str, ...]
    capabilities: tuple[str, ...]
    correlation_key: str


class ExecutionIncidentCorrelationService:
    def correlate(
        self,
        incident: ExecutionIncident,
    ) -> ExecutionIncidentCorrelation:
        anomaly_codes = tuple(
            sorted(
                set(
                    incident.anomaly_codes
                )
            )
        )

        capabilities = tuple(
            sorted(
                set(
                    incident.capabilities
                )
            )
        )

        correlation_key = self._correlation_key(
            anomaly_codes=anomaly_codes,
            capabilities=capabilities,
        )

        fingerprint = sha256(
            correlation_key.encode(
                "utf-8"
            )
        ).hexdigest()[:16]

        return ExecutionIncidentCorrelation(
            fingerprint=fingerprint,
            incident_id=incident.incident_id,
            severity=incident.severity.value,
            anomaly_codes=anomaly_codes,
            capabilities=capabilities,
            correlation_key=correlation_key,
        )

    @staticmethod
    def _correlation_key(
        *,
        anomaly_codes: tuple[str, ...],
        capabilities: tuple[str, ...],
    ) -> str:
        anomaly_part = (
            ",".join(
                anomaly_codes
            )
            or "none"
        )

        capability_part = (
            ",".join(
                capabilities
            )
            or "none"
        )

        return (
            f"anomalies={anomaly_part}"
            f"|capabilities={capability_part}"
        )
