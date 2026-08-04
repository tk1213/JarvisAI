from datetime import UTC, datetime

from jarvis.planner.execution_incident_correlation import (
    ExecutionIncidentCorrelationService,
)
from jarvis.planner.execution_incidents import (
    ExecutionIncident,
    ExecutionIncidentSeverity,
)


def make_incident(
    *,
    incident_id: str,
    anomaly_codes: tuple[str, ...],
    capabilities: tuple[str, ...],
) -> ExecutionIncident:
    return ExecutionIncident(
        incident_id=incident_id,
        severity=ExecutionIncidentSeverity.HIGH,
        title="Execution incident",
        summary="Incident summary.",
        anomaly_codes=anomaly_codes,
        capabilities=capabilities,
        created_at=datetime.now(UTC),
    )


def test_correlation_is_stable_for_same_incident_shape() -> None:
    service = ExecutionIncidentCorrelationService()

    first = service.correlate(
        make_incident(
            incident_id="execution-1",
            anomaly_codes=(
                "execution_timeout",
                "unreliable_capability",
            ),
            capabilities=(
                "system.health",
            ),
        )
    )

    second = service.correlate(
        make_incident(
            incident_id="execution-2",
            anomaly_codes=(
                "unreliable_capability",
                "execution_timeout",
            ),
            capabilities=(
                "system.health",
            ),
        )
    )

    assert first.fingerprint == second.fingerprint
    assert first.correlation_key == second.correlation_key


def test_correlation_changes_for_different_capability() -> None:
    service = ExecutionIncidentCorrelationService()

    first = service.correlate(
        make_incident(
            incident_id="execution-1",
            anomaly_codes=(
                "execution_timeout",
            ),
            capabilities=(
                "system.health",
            ),
        )
    )

    second = service.correlate(
        make_incident(
            incident_id="execution-2",
            anomaly_codes=(
                "execution_timeout",
            ),
            capabilities=(
                "system.ping",
            ),
        )
    )

    assert first.fingerprint != second.fingerprint


def test_correlation_deduplicates_values() -> None:
    correlation = ExecutionIncidentCorrelationService().correlate(
        make_incident(
            incident_id="execution-1",
            anomaly_codes=(
                "execution_timeout",
                "execution_timeout",
            ),
            capabilities=(
                "system.health",
                "system.health",
            ),
        )
    )

    assert correlation.anomaly_codes == (
        "execution_timeout",
    )
    assert correlation.capabilities == (
        "system.health",
    )
