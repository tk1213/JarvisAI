from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from jarvis.services.capability import CapabilityRequest
from jarvis.services.capability_router import CapabilityRouter


@dataclass(slots=True)
class PlanStepResult:
    step_index: int
    capability: str
    success: bool
    output: Any = None
    error: str | None = None


@dataclass(slots=True)
class PlanExecutionResult:
    success: bool
    plan: Plan
    step_results: list[PlanStepResult] = field(
        default_factory=list
    )

    @property
    def completed_steps(self) -> int:
        return sum(
            result.success
            for result in self.step_results
        )


class PlanExecutor:
    def __init__(
        self,
        router: CapabilityRouter,
    ) -> None:
        self._router = router

    async def execute(
        self,
        plan: Plan,
    ) -> PlanExecutionResult:
        if plan.status is not PlanStatus.READY:
            raise ValueError(
                "Plan must be in READY status before execution."
            )

        plan.status = PlanStatus.RUNNING

        results: list[PlanStepResult] = []

        for step in plan.steps:
            result = await self._execute_step(
                step
            )

            results.append(
                result
            )

            if not result.success:
                plan.status = PlanStatus.FAILED

                self._skip_remaining_steps(
                    plan,
                    after_index=step.index,
                )

                return PlanExecutionResult(
                    success=False,
                    plan=plan,
                    step_results=results,
                )

        plan.status = PlanStatus.COMPLETED

        return PlanExecutionResult(
            success=True,
            plan=plan,
            step_results=results,
        )

    async def _execute_step(
        self,
        step: PlanStep,
    ) -> PlanStepResult:
        step.status = PlanStepStatus.RUNNING

        request = CapabilityRequest(
            capability=step.capability,
            arguments=dict(
                step.arguments
            ),
        )

        try:
            output = await self._router.execute_request(
                request
            )

        except Exception as exc:  # noqa: BLE001
            step.status = PlanStepStatus.FAILED

            return PlanStepResult(
                step_index=step.index,
                capability=step.capability,
                success=False,
                error=str(
                    exc
                ),
            )

        step.status = PlanStepStatus.COMPLETED

        return PlanStepResult(
            step_index=step.index,
            capability=step.capability,
            success=True,
            output=output,
        )

    @staticmethod
    def _skip_remaining_steps(
        plan: Plan,
        *,
        after_index: int,
    ) -> None:
        for step in plan.steps:
            if (
                step.index > after_index
                and step.status is PlanStepStatus.PENDING
            ):
                step.status = PlanStepStatus.SKIPPED
