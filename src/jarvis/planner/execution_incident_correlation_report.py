from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_incident_correlation import (
    ExecutionIncidentCorrelation,
)


@dataclass(slots=True, frozen=True)
class ExecutionIncidentCorrelationReport:
    summary: str
    lines: tuple[str, ...]


class ExecutionIncidentCorrelationReportBuilder:
    def build(
        self,
        correlation: ExecutionIncidentCorrelation,
    ) -> ExecutionIncidentCorrelationReport:
        summary = (
            "Execution incident correlation: "
            f"fingerprint={correlation.fingerprint}, "
            f"severity={correlation.severity}."
        )

        lines = (
            (
                "Incident ID: "
                f"{correlation.incident_id}"
            ),
            (
                "Anomaly codes: "
                + (
                    ", ".join(
                        correlation.anomaly_codes
                    )
                    if correlation.anomaly_codes
                    else "none"
                )
            ),
            (
                "Capabilities: "
                + (
                    ", ".join(
                        correlation.capabilities
                    )
                    if correlation.capabilities
                    else "none"
                )
            ),
            (
                "Correlation key: "
                f"{correlation.correlation_key}"
            ),
        )

        return ExecutionIncidentCorrelationReport(
            summary=summary,
            lines=lines,
        )
