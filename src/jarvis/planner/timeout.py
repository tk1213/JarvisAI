from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ExecutionTimeoutPolicy:
    step_timeout_seconds: float = 15.0

    def __post_init__(self) -> None:
        if self.step_timeout_seconds <= 0:
            raise ValueError(
                "step_timeout_seconds must be greater than 0."
            )
