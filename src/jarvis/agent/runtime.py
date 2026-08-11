from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from jarvis.agent.memory import AIAgentMemoryLifecycle
from jarvis.agent.planning_context import AIAgentPlanningContextBuilder
from jarvis.agent.replanning import AIAgentReplanPolicy
from jarvis.planner.ai_plan_adapter import AIPlanAdaptationResult
from jarvis.planner.ai_plan_contract import (
    AIPlanDraft,
    AIPlanStepDraft,
)
from jarvis.planner.ai_plan_execution import AIPlanExecutionResult
from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryRecord,
    AIPlanMemoryStore,
)
from jarvis.planner.ai_plan_pipeline import AIPlanPipelineResult
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionResult,
    AIPlanReflectionService,
)
from jarvis.planner.ai_plan_validation import AIPlanValidationResult
from jarvis.planner.executor import PlanExecutionResult
from jarvis.planner.orchestrator import (
    PlannerOrchestrator,
    PlanPreview,
)


class AIAgentRunStatus(StrEnum):
    NO_PLAN = "no_plan"
    CONFIRMATION_REQUIRED = "confirmation_required"
    COMPLETED = "completed"


@dataclass(slots=True, frozen=True)
class AIAgentRunResult:
    status: AIAgentRunStatus
    preview: PlanPreview | None
    execution: PlanExecutionResult | None
    reflection: AIPlanReflectionResult | None
    memory_record: AIPlanMemoryRecord | None
    replan_attempts: int = 0

    @property
    def requires_confirmation(self) -> bool:
        return (
            self.status
            is AIAgentRunStatus.CONFIRMATION_REQUIRED
        )

    @property
    def success(self) -> bool:
        return (
            self.execution is not None
            and self.execution.success
        )


class AIAgentRuntime:
    def __init__(
        self,
        *,
        orchestrator: PlannerOrchestrator,
        reflection: AIPlanReflectionService,
        memory: AIPlanMemoryStore,
        memory_lifecycle: AIAgentMemoryLifecycle | None = None,
        planning_context: AIAgentPlanningContextBuilder | None = None,
        replan_policy: AIAgentReplanPolicy | None = None,
    ) -> None:
        self._orchestrator = orchestrator
        self._reflection = reflection
        self._memory = memory
        self._memory_lifecycle = (
            memory_lifecycle
            if memory_lifecycle is not None
            else AIAgentMemoryLifecycle(
                memory
            )
        )
        self._planning_context = (
            planning_context
            if planning_context is not None
            else AIAgentPlanningContextBuilder(
                self._memory_lifecycle
            )
        )
        self._last_result: AIAgentRunResult | None = None

        self._replan_policy = (
            replan_policy
            if replan_policy is not None
            else AIAgentReplanPolicy()
        )

    @property
    def has_pending_plan(self) -> bool:
        return self._orchestrator.has_pending_plan

    @property
    def memory_lifecycle(self) -> AIAgentMemoryLifecycle:
        return self._memory_lifecycle

    @property
    def last_result(self) -> AIAgentRunResult | None:
        return self._last_result

    async def run(
        self,
        text: str,
    ) -> AIAgentRunResult:
        original_text = text
        replan_attempts = 0

        planning_context = self._planning_context.build()

        planner_text = original_text

        if planning_context.available:
            planner_text = (
                f"{original_text}\n\n"
                f"{planning_context.text}"
            )

        while True:
            preview = await self._orchestrator.prepare(
                planner_text
            )

            if preview is None:
                return self._remember_last_result(
                    AIAgentRunResult(
                        status=AIAgentRunStatus.NO_PLAN,
                    preview=None,
                    execution=None,
                    reflection=None,
                    memory_record=None,
                        replan_attempts=replan_attempts,
                    )
                )

            if preview.requires_confirmation:
                return self._remember_last_result(
                    AIAgentRunResult(
                        status=AIAgentRunStatus.CONFIRMATION_REQUIRED,
                    preview=preview,
                    execution=None,
                    reflection=None,
                    memory_record=None,
                        replan_attempts=replan_attempts,
                    )
                )

            execution = await self._orchestrator.execute_preview(
                preview
            )

            completed = await self._complete_execution(
                execution=execution,
                source=(
                    "ai_agent_runtime"
                    if replan_attempts == 0
                    else "ai_agent_runtime_replanned"
                ),
                preview=preview,
                replan_attempts=replan_attempts,
            )

            reflection = completed.reflection

            if reflection is None:
                return self._remember_last_result(
                    completed
                )

            if not self._replan_policy.should_replan(
                reflection=reflection,
                attempts=replan_attempts,
            ):
                return self._remember_last_result(
                    completed
                )

            replan_attempts += 1

            planner_text = self._replan_policy.build_retry_text(
                original_text=original_text,
                reflection=reflection,
                attempt=replan_attempts,
            )

    async def confirm_pending(
        self,
    ) -> AIAgentRunResult:
        execution = await self._orchestrator.confirm_pending()

        return self._remember_last_result(
            await self._complete_execution(
                execution=execution,
                source="ai_agent_runtime_confirmed",
                preview=None,
            )
        )

    def cancel_pending(
        self,
    ) -> bool:
        return self._orchestrator.cancel_pending()

    def _remember_last_result(
        self,
        result: AIAgentRunResult,
    ) -> AIAgentRunResult:
        self._last_result = result
        return result

    async def _complete_execution(
        self,
        *,
        execution: PlanExecutionResult,
        source: str,
        preview: PlanPreview | None,
        replan_attempts: int = 0,
    ) -> AIAgentRunResult:
        wrapped_execution = self._wrap_execution(
            execution
        )

        reflection = self._reflection.reflect(
            wrapped_execution
        )

        memory_record = (
            await self._memory_lifecycle.remember_execution_durable(
                execution=wrapped_execution,
                reflection=reflection,
                source=source,
            )
        )

        return AIAgentRunResult(
            status=AIAgentRunStatus.COMPLETED,
            preview=preview,
            execution=execution,
            reflection=reflection,
            memory_record=memory_record,
            replan_attempts=replan_attempts,
        )

    @staticmethod
    def _wrap_execution(
        execution: PlanExecutionResult,
    ) -> AIPlanExecutionResult:
        plan = execution.plan

        draft = AIPlanDraft(
            goal=plan.goal,
            steps=tuple(
                AIPlanStepDraft(
                    capability=step.capability,
                    arguments=dict(
                        step.arguments
                    ),
                    description=step.description,
                )
                for step in plan.steps
            ),
            reasoning_summary=(
                "Generated by the existing JarvisAI "
                "AIPlanGenerator and PlannerOrchestrator."
            ),
        )

        validation = AIPlanValidationResult(
            valid=True,
            issues=(),
        )

        adaptation = AIPlanAdaptationResult(
            plan=plan,
            validation=validation,
        )

        pipeline = AIPlanPipelineResult(
            draft=draft,
            adaptation=adaptation,
        )

        return AIPlanExecutionResult(
            pipeline=pipeline,
            execution=execution,
        )
