from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BackoffPolicy:
    base_delay_seconds: float = 0.25
    multiplier: float = 2.0
    max_delay_seconds: float = 2.0

    def __post_init__(self) -> None:
        if self.base_delay_seconds < 0:
            raise ValueError(
                "base_delay_seconds cannot be negative."
            )

        if self.multiplier < 1:
            raise ValueError(
                "multiplier must be at least 1."
            )

        if self.max_delay_seconds < 0:
            raise ValueError(
                "max_delay_seconds cannot be negative."
            )

    def delay_for_retry(
        self,
        *,
        attempt: int,
    ) -> float:
        if attempt < 1:
            raise ValueError(
                "attempt must be at least 1."
            )

        delay = (
            self.base_delay_seconds
            * (
                self.multiplier
                ** (
                    attempt - 1
                )
            )
        )

        return min(
            delay,
            self.max_delay_seconds,
        )
