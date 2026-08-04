from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.execution_incident_correlation import (
    ExecutionIncidentCorrelation,
)


@dataclass(slots=True, frozen=True)
class ExecutionIncidentGroup:
    fingerprint: str
    incident_ids: tuple[str, ...]
    severities: tuple[str, ...]
    anomaly_codes: tuple[str, ...]
    capabilities: tuple[str, ...]
    occurrence_count: int


@dataclass(slots=True, frozen=True)
class ExecutionIncidentGroupingSummary:
    total_incidents: int
    total_groups: int
    groups: tuple[
        ExecutionIncidentGroup,
        ...
    ]


class ExecutionIncidentGroupingService:
    def group(
        self,
        correlations: list[
            ExecutionIncidentCorrelation
        ],
    ) -> ExecutionIncidentGroupingSummary:
        grouped: dict[
            str,
            list[ExecutionIncidentCorrelation],
        ] = {}

        for correlation in correlations:
            grouped.setdefault(
                correlation.fingerprint,
                [],
            ).append(
                correlation
            )

        groups = tuple(
            self._build_group(
                fingerprint=fingerprint,
                correlations=items,
            )
            for fingerprint, items in sorted(
                grouped.items()
            )
        )

        return ExecutionIncidentGroupingSummary(
            total_incidents=len(
                correlations
            ),
            total_groups=len(
                groups
            ),
            groups=groups,
        )

    @staticmethod
    def _build_group(
        *,
        fingerprint: str,
        correlations: list[
            ExecutionIncidentCorrelation
        ],
    ) -> ExecutionIncidentGroup:
        incident_ids = tuple(
            sorted(
                {
                    correlation.incident_id
                    for correlation in correlations
                }
            )
        )

        severities = tuple(
            sorted(
                {
                    correlation.severity
                    for correlation in correlations
                }
            )
        )

        anomaly_codes = tuple(
            sorted(
                {
                    code
                    for correlation in correlations
                    for code in correlation.anomaly_codes
                }
            )
        )

        capabilities = tuple(
            sorted(
                {
                    capability
                    for correlation in correlations
                    for capability in correlation.capabilities
                }
            )
        )

        return ExecutionIncidentGroup(
            fingerprint=fingerprint,
            incident_ids=incident_ids,
            severities=severities,
            anomaly_codes=anomaly_codes,
            capabilities=capabilities,
            occurrence_count=len(
                correlations
            ),
        )
