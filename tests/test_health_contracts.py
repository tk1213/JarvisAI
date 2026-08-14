from __future__ import annotations

from jarvis.main import _doctor_status_label
from jarvis.services.health_contracts import (
    HealthCheckResult,
    HealthState,
)


def test_health_state_values_are_stable() -> None:
    assert HealthState.HEALTHY.value == "healthy"
    assert HealthState.DEGRADED.value == "degraded"
    assert HealthState.UNAVAILABLE.value == "unavailable"


def test_healthy_result_passes() -> None:
    result = HealthCheckResult(
        name="database",
        state=HealthState.HEALTHY,
    )

    assert result.passed is True
    assert result.available is True


def test_degraded_result_does_not_pass_but_is_available() -> None:
    result = HealthCheckResult(
        name="audio",
        state=HealthState.DEGRADED,
        reason="Output device is unavailable.",
    )

    assert result.passed is False
    assert result.available is True


def test_unavailable_result_does_not_pass() -> None:
    result = HealthCheckResult(
        name="tuya",
        state=HealthState.UNAVAILABLE,
        reason="Credentials are missing.",
    )

    assert result.passed is False
    assert result.available is False


def test_result_defaults_are_safe() -> None:
    result = HealthCheckResult(
        name="database",
        state=HealthState.HEALTHY,
    )

    assert result.reason is None
    assert result.details == {}
    assert result.critical is True


def test_result_details_are_independent() -> None:
    first = HealthCheckResult(
        name="first",
        state=HealthState.HEALTHY,
    )
    second = HealthCheckResult(
        name="second",
        state=HealthState.HEALTHY,
    )

    first.details["value"] = 1

    assert second.details == {}


def test_result_serializes_to_diagnostic_dict() -> None:
    result = HealthCheckResult(
        name="database",
        state=HealthState.DEGRADED,
        reason="Slow response.",
        details={
            "latency_ms": 250,
        },
        critical=False,
    )

    assert result.to_dict() == {
        "name": "database",
        "state": "degraded",
        "passed": False,
        "available": True,
        "reason": "Slow response.",
        "details": {
            "latency_ms": 250,
        },
        "critical": False,
    }


def test_doctor_status_label_for_healthy() -> None:
    assert _doctor_status_label(HealthState.HEALTHY) == "PASS"


def test_doctor_status_label_for_degraded() -> None:
    assert _doctor_status_label(HealthState.DEGRADED) == "WARN"


def test_doctor_status_label_for_unavailable() -> None:
    assert _doctor_status_label(HealthState.UNAVAILABLE) == "FAIL"
