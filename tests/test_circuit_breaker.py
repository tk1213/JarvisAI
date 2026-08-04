from jarvis.planner.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerPolicy,
    CircuitState,
)


def test_circuit_opens_after_threshold() -> None:
    breaker = CircuitBreaker(
        CircuitBreakerPolicy(
            failure_threshold=2,
            recovery_timeout_seconds=60,
        )
    )

    breaker.record_failure(
        "system.ping"
    )
    assert (
        breaker.state_for("system.ping")
        is CircuitState.CLOSED
    )

    breaker.record_failure(
        "system.ping"
    )
    assert (
        breaker.state_for("system.ping")
        is CircuitState.OPEN
    )
    assert (
        breaker.allow_request("system.ping")
        is False
    )


def test_success_resets_failure_count() -> None:
    breaker = CircuitBreaker(
        CircuitBreakerPolicy(
            failure_threshold=2,
            recovery_timeout_seconds=60,
        )
    )

    breaker.record_failure(
        "system.ping"
    )
    breaker.record_success(
        "system.ping"
    )
    breaker.record_failure(
        "system.ping"
    )

    assert (
        breaker.state_for("system.ping")
        is CircuitState.CLOSED
    )
