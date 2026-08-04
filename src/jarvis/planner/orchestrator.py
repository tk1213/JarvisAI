from __future__ import annotations

from dataclasses import dataclass

from jarvis.planner.ai_generator import AIPlanGenerator
from jarvis.planner.execution_policy import ExecutionDecision, ExecutionPolicy
from jarvis.planner.executor import PlanExecutionResult, PlanExecutor
from jarvis.planner.models import Plan
from jarvis.planner.service import PlannerService


@dataclass(slots=True)
class PlanPreview:
    plan: Plan
    decision: ExecutionDecision

    @property
    def requires_confirmation(self) -> bool:
        return self.decision.requires_confirmation


class PlannerOrchestrator:
    def __init__(
        self,
        *,
        generator: AIPlanGenerator,
        planner: PlannerService,
        executor: PlanExecutor,
        execution_policy: ExecutionPolicy | None = None,
    ) -> None:
        self._generator = generator
        self._planner = planner
        self._executor = executor
        self._execution_policy = (
            execution_policy
            if execution_policy is not None
            else ExecutionPolicy()
        )
        self._pending_plan: Plan | None = None

    @property
    def has_pending_plan(self) -> bool:
        return self._pending_plan is not None

    async def prepare(
        self,
        text: str,
    ) -> PlanPreview | None:
        plan = await self._generator.generate(text)

        if plan is None:
            self._pending_plan = None
            return None

        self._planner.validate_plan(plan)

        decision = self._execution_policy.evaluate(plan)

        self._pending_plan = (
            plan
            if decision.requires_confirmation
            else None
        )

        return PlanPreview(
            plan=plan,
            decision=decision,
        )

    async def execute_preview(
        self,
        preview: PlanPreview,
    ) -> PlanExecutionResult:
        if preview.requires_confirmation:
            raise PermissionError(
                "Plan requires confirmation before execution."
            )

        return await self._executor.execute(preview.plan)

    async def confirm_pending(
        self,
    ) -> PlanExecutionResult:
        plan = self._pending_plan

        if plan is None:
            raise RuntimeError(
                "There is no pending plan to confirm."
            )

        self._pending_plan = None
        return await self._executor.execute(plan)

    def cancel_pending(self) -> bool:
        if self._pending_plan is None:
            return False

        self._pending_plan = None
        return True
