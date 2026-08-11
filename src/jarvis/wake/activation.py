from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WakeActivationStatus(StrEnum):
    DETECTED = "detected"
    CANCELLED = "cancelled"
    CLOSED = "closed"


@dataclass(slots=True, frozen=True)
class WakeActivationResult:
    status: WakeActivationStatus
    score: float | None = None

    @property
    def detected(self) -> bool:
        return self.status is WakeActivationStatus.DETECTED


class WakeActivationPolicy:
    """Pure wake activation threshold contract."""

    def __init__(
        self,
        *,
        threshold: float,
    ) -> None:
        if not 0.0 < threshold <= 1.0:
            raise ValueError(
                "Wake word threshold must be between 0 and 1."
            )

        self._threshold = threshold

    @property
    def threshold(self) -> float:
        return self._threshold

    def evaluate(
        self,
        score: float,
    ) -> WakeActivationResult:
        if not 0.0 <= score <= 1.0:
            raise ValueError(
                "Wake word score must be between 0 and 1."
            )

        if score >= self._threshold:
            return WakeActivationResult(
                status=WakeActivationStatus.DETECTED,
                score=score,
            )

        return WakeActivationResult(
            status=WakeActivationStatus.CANCELLED,
            score=score,
        )
