from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HealthState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(slots=True)
class HealthCheckResult:
    name: str
    state: HealthState
    reason: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    critical: bool = True

    @property
    def passed(self) -> bool:
        return self.state is HealthState.HEALTHY

    @property
    def available(self) -> bool:
        return self.state is not HealthState.UNAVAILABLE

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "passed": self.passed,
            "available": self.available,
            "reason": self.reason,
            "details": dict(self.details),
            "critical": self.critical,
        }
