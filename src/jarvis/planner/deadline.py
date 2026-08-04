from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PlanDeadlinePolicy:
    plan_timeout_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.plan_timeout_seconds <= 0:
            raise ValueError(
                "plan_timeout_seconds must be greater than 0."
            )
