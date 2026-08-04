from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(slots=True)
class ResilienceMetrics:
    plans_started: int = 0
    plans_completed: int = 0
    plans_failed: int = 0
    steps_started: int = 0
    steps_completed: int = 0
    steps_failed: int = 0
    retries: int = 0
    timeouts: int = 0
    circuit_rejections: int = 0
    bulkhead_rejections: int = 0
    capability_failures: dict[str, int] = field(
        default_factory=dict
    )

    _NON_NEGATIVE_FIELDS: ClassVar[tuple[str, ...]] = (
        "plans_started",
        "plans_completed",
        "plans_failed",
        "steps_started",
        "steps_completed",
        "steps_failed",
        "retries",
        "timeouts",
        "circuit_rejections",
        "bulkhead_rejections",
    )

    def increment_capability_failure(
        self,
        capability: str,
    ) -> None:
        key = capability.strip()

        if not key:
            raise ValueError(
                "Capability cannot be empty."
            )

        self.capability_failures[key] = (
            self.capability_failures.get(
                key,
                0,
            )
            + 1
        )

    def snapshot(
        self,
    ) -> ResilienceMetricsSnapshot:
        return ResilienceMetricsSnapshot(
            plans_started=self.plans_started,
            plans_completed=self.plans_completed,
            plans_failed=self.plans_failed,
            steps_started=self.steps_started,
            steps_completed=self.steps_completed,
            steps_failed=self.steps_failed,
            retries=self.retries,
            timeouts=self.timeouts,
            circuit_rejections=self.circuit_rejections,
            bulkhead_rejections=self.bulkhead_rejections,
            capability_failures=dict(
                self.capability_failures
            ),
        )


@dataclass(slots=True, frozen=True)
class ResilienceMetricsSnapshot:
    plans_started: int
    plans_completed: int
    plans_failed: int
    steps_started: int
    steps_completed: int
    steps_failed: int
    retries: int
    timeouts: int
    circuit_rejections: int
    bulkhead_rejections: int
    capability_failures: dict[str, int]
