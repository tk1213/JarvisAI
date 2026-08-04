from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from jarvis.planner.compensation import (
    CompensationCandidate,
    CompensationPlan,
)


class RecoveryDecisionType(StrEnum):
    NONE = "none"
    MANUAL_REVIEW = "manual_review"


@dataclass(slots=True, frozen=True)
class RecoveryDecision:
    decision: RecoveryDecisionType
    candidates: tuple[CompensationCandidate, ...]
    reason: str

    @property
    def requires_manual_review(self) -> bool:
        return self.decision is RecoveryDecisionType.MANUAL_REVIEW


class RecoveryPolicy:
    """
    Conservative recovery policy.

    Jarvis never auto-executes inverse actions in this pack.
    Completed side-effect steps require explicit manual review.
    """

    def decide(
        self,
        compensation: CompensationPlan,
    ) -> RecoveryDecision:
        if not compensation.requires_review:
            return RecoveryDecision(
                decision=RecoveryDecisionType.NONE,
                candidates=(),
                reason=compensation.reason,
            )

        return RecoveryDecision(
            decision=RecoveryDecisionType.MANUAL_REVIEW,
            candidates=compensation.candidates,
            reason=(
                "Completed side-effect steps require explicit "
                "review before any compensation action."
            ),
        )
