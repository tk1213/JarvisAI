from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from jarvis.planner.executor import PlanExecutionResult
from jarvis.planner.models import PlanStepStatus
from jarvis.planner.risk import PlanRiskLevel, PlanRiskPolicy


class CompensationStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    REQUIRES_REVIEW = "requires_review"


@dataclass(slots=True, frozen=True)
class CompensationCandidate:
    step_index: int
    capability: str
    arguments: dict[str, Any] = field(
        default_factory=dict
    )
    output: Any = None


@dataclass(slots=True, frozen=True)
class CompensationPlan:
    status: CompensationStatus
    candidates: tuple[CompensationCandidate, ...] = ()
    reason: str = ""

    @property
    def requires_review(self) -> bool:
        return (
            self.status
            is CompensationStatus.REQUIRES_REVIEW
        )


class CompensationPlanner:
    def build(
        self,
        execution: PlanExecutionResult,
    ) -> CompensationPlan:
        if execution.success:
            return CompensationPlan(
                status=CompensationStatus.NOT_REQUIRED,
                reason=(
                    "Plan completed successfully; "
                    "compensation is not required."
                ),
            )

        completed_results = {
            result.step_index: result
            for result in execution.step_results
            if result.status is PlanStepStatus.COMPLETED
        }

        candidates: list[CompensationCandidate] = []

        for step in reversed(
            execution.plan.steps
        ):
            result = completed_results.get(
                step.index
            )

            if result is None:
                continue

            if (
                PlanRiskPolicy.classify(
                    step.capability
                )
                is not PlanRiskLevel.SIDE_EFFECT
            ):
                continue

            candidates.append(
                CompensationCandidate(
                    step_index=step.index,
                    capability=step.capability,
                    arguments=dict(
                        step.arguments
                    ),
                    output=result.output,
                )
            )

        if not candidates:
            return CompensationPlan(
                status=CompensationStatus.NOT_REQUIRED,
                reason=(
                    "The failed plan has no completed "
                    "side-effect steps to review."
                ),
            )

        return CompensationPlan(
            status=CompensationStatus.REQUIRES_REVIEW,
            candidates=tuple(
                candidates
            ),
            reason=(
                "One or more side-effect steps completed "
                "before the plan failed. Manual or "
                "policy-approved compensation review is "
                "required."
            ),
        )
