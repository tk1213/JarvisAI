from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from time import monotonic


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass(slots=True, frozen=True)
class CircuitBreakerPolicy:
    failure_threshold: int = 3
    recovery_timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        if self.failure_threshold <= 0:
            raise ValueError(
                "failure_threshold must be greater than 0."
            )

        if self.recovery_timeout_seconds <= 0:
            raise ValueError(
                "recovery_timeout_seconds must be greater than 0."
            )


@dataclass(slots=True)
class _Circuit:
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    opened_at: float | None = None


class CircuitBreaker:
    def __init__(
        self,
        policy: CircuitBreakerPolicy | None = None,
    ) -> None:
        self._policy = (
            policy
            if policy is not None
            else CircuitBreakerPolicy()
        )
        self._circuits: dict[str, _Circuit] = {}

    def state_for(
        self,
        capability: str,
    ) -> CircuitState:
        circuit = self._get(
            capability
        )

        if (
            circuit.state is CircuitState.OPEN
            and circuit.opened_at is not None
            and monotonic() - circuit.opened_at
            >= self._policy.recovery_timeout_seconds
        ):
            circuit.state = CircuitState.HALF_OPEN

        return circuit.state

    def allow_request(
        self,
        capability: str,
    ) -> bool:
        return (
            self.state_for(capability)
            is not CircuitState.OPEN
        )

    def record_success(
        self,
        capability: str,
    ) -> None:
        circuit = self._get(
            capability
        )
        circuit.state = CircuitState.CLOSED
        circuit.failures = 0
        circuit.opened_at = None

    def record_failure(
        self,
        capability: str,
    ) -> None:
        circuit = self._get(
            capability
        )

        if circuit.state is CircuitState.HALF_OPEN:
            self._open(
                circuit
            )
            return

        circuit.failures += 1

        if (
            circuit.failures
            >= self._policy.failure_threshold
        ):
            self._open(
                circuit
            )

    def _get(
        self,
        capability: str,
    ) -> _Circuit:
        key = capability.strip()

        if not key:
            raise ValueError(
                "Capability cannot be empty."
            )

        return self._circuits.setdefault(
            key,
            _Circuit(),
        )

    @staticmethod
    def _open(
        circuit: _Circuit,
    ) -> None:
        circuit.state = CircuitState.OPEN
        circuit.opened_at = monotonic()
