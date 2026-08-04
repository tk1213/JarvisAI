from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FailureKind(StrEnum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class FailureClassification:
    kind: FailureKind
    reason: str


class FailureClassifier:
    _TRANSIENT_MARKERS = (
        "temporar",
        "timeout",
        "timed out",
        "connection",
        "unavailable",
        "rate limit",
        "try again",
    )

    _PERMANENT_MARKERS = (
        "invalid",
        "not allowed",
        "permission",
        "unauthorized",
        "forbidden",
        "not found",
        "unsupported",
        "bad request",
    )

    def classify(
        self,
        error: Exception,
    ) -> FailureClassification:
        message = str(
            error
        ).strip()

        normalized = message.casefold()

        if any(
            marker in normalized
            for marker in self._PERMANENT_MARKERS
        ):
            return FailureClassification(
                kind=FailureKind.PERMANENT,
                reason=message or error.__class__.__name__,
            )

        if any(
            marker in normalized
            for marker in self._TRANSIENT_MARKERS
        ):
            return FailureClassification(
                kind=FailureKind.TRANSIENT,
                reason=message or error.__class__.__name__,
            )

        return FailureClassification(
            kind=FailureKind.UNKNOWN,
            reason=message or error.__class__.__name__,
        )
