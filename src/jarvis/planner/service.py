from __future__ import annotations

from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_registry import CapabilityRegistry


class PlannerService:
    def __init__(
        self,
        registry: CapabilityRegistry,
    ) -> None:
        self._registry = registry

    def create_plan(
        self,
        *,
        goal: str,
        requests: list[CapabilityRequest],
    ) -> Plan:
        normalized_goal = goal.strip()

        if not normalized_goal:
            raise ValueError(
                "Planner goal cannot be empty."
            )

        if not requests:
            raise ValueError(
                "Planner requires at least one capability request."
            )

        steps: list[PlanStep] = []

        for index, request in enumerate(
            requests,
            start=1,
        ):
            self._validate_request(
                request
            )

            steps.append(
                PlanStep(
                    index=index,
                    capability=request.capability,
                    arguments=dict(
                        request.arguments
                    ),
                    description=(
                        f"Execute {request.capability}"
                    ),
                )
            )

        return Plan(
            goal=normalized_goal,
            steps=steps,
            status=PlanStatus.READY,
        )

    def create_single_step_plan(
        self,
        *,
        goal: str,
        request: CapabilityRequest,
    ) -> Plan:
        return self.create_plan(
            goal=goal,
            requests=[
                request
            ],
        )

    def validate_plan(
        self,
        plan: Plan,
    ) -> None:
        for step in plan.steps:
            if not self._registry.is_allowed(
                step.capability
            ):
                raise PermissionError(
                    "Capability is not allowed: "
                    f"{step.capability}"
                )

    def _validate_request(
        self,
        request: CapabilityRequest,
    ) -> None:
        if not self._registry.is_allowed(
            request.capability
        ):
            raise PermissionError(
                "Capability is not allowed: "
                f"{request.capability}"
            )
