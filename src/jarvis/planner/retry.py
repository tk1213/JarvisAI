from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from jarvis.planner.failures import (
    FailureClassification,
    FailureKind,
)
from jarvis.planner.risk import (
    PlanRiskLevel,
    PlanRiskPolicy,
)


class RetryDecision(StrEnum):
    RETRY = "retry"
    FAIL = "fail"


@dataclass(slots=True, frozen=True)
class RetryPolicy:
    max_attempts: int = 2

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError(
                "max_attempts must be at least 1."
            )

    def decide(
        self,
        *,
        attempt: int,
    ) -> RetryDecision:
        if attempt < 1:
            raise ValueError(
                "attempt must be at least 1."
            )

        if attempt < self.max_attempts:
            return RetryDecision.RETRY

        return RetryDecision.FAIL

    def decide_for_capability(
        self,
        *,
        capability: str,
        attempt: int,
        classification: FailureClassification | None = None,
    ) -> RetryDecision:
        if (
            PlanRiskPolicy.classify(
                capability
            )
            is PlanRiskLevel.SIDE_EFFECT
        ):
            return RetryDecision.FAIL

        if classification is not None:
            if (
                classification.kind
                is FailureKind.PERMANENT
            ):
                return RetryDecision.FAIL

            if (
                classification.kind
                is FailureKind.UNKNOWN
            ):
                return RetryDecision.FAIL

        return self.decide(
            attempt=attempt
        )
