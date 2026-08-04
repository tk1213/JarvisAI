from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.compensation import (
    CompensationPlan,
    CompensationPlanner,
)
from jarvis.planner.executor import PlanExecutionResult
from jarvis.planner.recovery_policy import (
    RecoveryDecision,
    RecoveryPolicy,
)


@dataclass(slots=True, frozen=True)
class RecoveryAssessment:
    execution: PlanExecutionResult
    compensation: CompensationPlan
    decision: RecoveryDecision

    @property
    def requires_compensation_review(self) -> bool:
        return self.decision.requires_manual_review


class RecoveryPlanner:
    def __init__(
        self,
        compensation_planner: CompensationPlanner | None = None,
        recovery_policy: RecoveryPolicy | None = None,
    ) -> None:
        self._compensation_planner = (
            compensation_planner
            if compensation_planner is not None
            else CompensationPlanner()
        )
        self._recovery_policy = (
            recovery_policy
            if recovery_policy is not None
            else RecoveryPolicy()
        )

    def assess(
        self,
        execution: PlanExecutionResult,
    ) -> RecoveryAssessment:
        compensation = self._compensation_planner.build(
            execution
        )

        decision = self._recovery_policy.decide(
            compensation
        )

        return RecoveryAssessment(
            execution=execution,
            compensation=compensation,
            decision=decision,
        )
