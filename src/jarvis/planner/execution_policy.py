from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from jarvis.planner.models import Plan
from jarvis.planner.risk import PlanRiskLevel, PlanRiskPolicy


class ExecutionRoute(StrEnum):
    READ_ONLY = "read_only"
    CONFIRMATION_REQUIRED = "confirmation_required"


@dataclass(slots=True, frozen=True)
class ExecutionDecision:
    route: ExecutionRoute
    side_effect_steps: tuple[int, ...]

    @property
    def requires_confirmation(self) -> bool:
        return self.route is ExecutionRoute.CONFIRMATION_REQUIRED


class ExecutionPolicy:
    def __init__(
        self,
        *,
        risk_policy: PlanRiskPolicy | None = None,
    ) -> None:
        self._risk_policy = (
            risk_policy
            if risk_policy is not None
            else PlanRiskPolicy()
        )

    def evaluate(
        self,
        plan: Plan,
    ) -> ExecutionDecision:
        side_effect_steps = tuple(
            step.index
            for step in plan.steps
            if (
                self._risk_policy.classify(step.capability)
                is PlanRiskLevel.SIDE_EFFECT
            )
        )

        if side_effect_steps:
            return ExecutionDecision(
                route=ExecutionRoute.CONFIRMATION_REQUIRED,
                side_effect_steps=side_effect_steps,
            )

        return ExecutionDecision(
            route=ExecutionRoute.READ_ONLY,
            side_effect_steps=(),
        )
