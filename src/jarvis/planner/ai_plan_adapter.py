from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.ai_plan_contract import AIPlanDraft
from jarvis.planner.ai_plan_validation import (
    AIPlanValidationResult,
    AIPlanValidator,
)
from jarvis.planner.models import Plan
from jarvis.planner.service import PlannerService
from jarvis.services.capability import CapabilityRequest


class AIPlanAdaptationError(ValueError):
    pass


@dataclass(slots=True, frozen=True)
class AIPlanAdaptationResult:
    plan: Plan
    validation: AIPlanValidationResult


class AIPlanAdapter:
    def __init__(
        self,
        *,
        validator: AIPlanValidator,
        planner: PlannerService,
    ) -> None:
        self._validator = validator
        self._planner = planner

    def adapt(
        self,
        draft: AIPlanDraft,
    ) -> AIPlanAdaptationResult:
        validation = self._validator.validate(
            draft
        )

        if not validation.valid:
            messages = "; ".join(
                issue.message
                for issue in validation.issues
            )

            raise AIPlanAdaptationError(
                "AI plan validation failed: "
                f"{messages}"
            )

        requests = [
            CapabilityRequest(
                capability=step.capability,
                arguments=dict(
                    step.arguments
                ),
            )
            for step in draft.steps
        ]

        plan = self._planner.create_plan(
            goal=draft.goal,
            requests=requests,
        )

        return AIPlanAdaptationResult(
            plan=plan,
            validation=validation,
        )