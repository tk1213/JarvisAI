from __future__ import annotations

from dataclasses import dataclass

import pytest

from jarvis.agent.replanning import AIAgentReplanPolicy
from jarvis.agent.runtime import AIAgentRunStatus, AIAgentRuntime
from jarvis.planner.ai_plan_memory import AIPlanMemoryStore
from jarvis.planner.ai_plan_reflection import AIPlanReflectionService
from jarvis.planner.execution_policy import (
    ExecutionDecision,
    ExecutionRoute,
)
from jarvis.planner.executor import (
    PlanExecutionResult,
    PlanStepResult,
)
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from jarvis.planner.orchestrator import PlanPreview


def make_plan(
    *,
    status: PlanStatus,
) -> Plan:
    return Plan(
        goal="Check Jarvis",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
                status=(
                    PlanStepStatus.PENDING
                    if status is PlanStatus.READY
                    else PlanStepStatus.FAILED
                ),
            )
        ],
        status=status,
    )


def transient_failure() -> PlanExecutionResult:
    plan = make_plan(
        status=PlanStatus.FAILED
    )

    return PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="system.ping",
                status=PlanStepStatus.FAILED,
                error="Capability temporarily unavailable.",
            )
        ],
    )


def success_execution() -> PlanExecutionResult:
    plan = make_plan(
        status=PlanStatus.COMPLETED
    )
    plan.steps[0].status = PlanStepStatus.COMPLETED

    return PlanExecutionResult(
        plan=plan,
        step_results=[
            PlanStepResult(
                step_index=1,
                capability="system.ping",
                status=PlanStepStatus.COMPLETED,
                output={
                    "status": "ok",
                },
            )
        ],
    )


@dataclass
class ReplanningOrchestrator:
    executions: list[PlanExecutionResult]

    def __post_init__(self) -> None:
        self.prepare_calls: list[str] = []
        self.execute_calls = 0
        self.has_pending_plan = False

    async def prepare(
        self,
        text: str,
    ) -> PlanPreview:
        self.prepare_calls.append(
            text
        )

        return PlanPreview(
            plan=make_plan(
                status=PlanStatus.READY
            ),
            decision=ExecutionDecision(
                route=ExecutionRoute.READ_ONLY,
                side_effect_steps=(),
            ),
        )

    async def execute_preview(
        self,
        preview: PlanPreview,
    ) -> PlanExecutionResult:
        del preview

        result = self.executions[
            self.execute_calls
        ]
        self.execute_calls += 1

        return result

    def cancel_pending(
        self,
    ) -> bool:
        return False


@pytest.mark.asyncio
async def test_runtime_replans_once_after_transient_failure() -> None:
    orchestrator = ReplanningOrchestrator(
        executions=[
            transient_failure(),
            success_execution(),
        ]
    )

    runtime = AIAgentRuntime(
        orchestrator=orchestrator,  # type: ignore[arg-type]
        reflection=AIPlanReflectionService(),
        memory=AIPlanMemoryStore(),
        replan_policy=AIAgentReplanPolicy(
            max_replans=1
        ),
    )

    result = await runtime.run(
        "Check Jarvis"
    )

    assert result.status is AIAgentRunStatus.COMPLETED
    assert result.success is True
    assert result.replan_attempts == 1
    assert orchestrator.execute_calls == 2
    assert len(
        orchestrator.prepare_calls
    ) == 2
    assert "Agent retry context" in orchestrator.prepare_calls[1]


@pytest.mark.asyncio
async def test_runtime_stops_after_replan_limit() -> None:
    orchestrator = ReplanningOrchestrator(
        executions=[
            transient_failure(),
            transient_failure(),
        ]
    )

    runtime = AIAgentRuntime(
        orchestrator=orchestrator,  # type: ignore[arg-type]
        reflection=AIPlanReflectionService(),
        memory=AIPlanMemoryStore(),
        replan_policy=AIAgentReplanPolicy(
            max_replans=1
        ),
    )

    result = await runtime.run(
        "Check Jarvis"
    )

    assert result.success is False
    assert result.replan_attempts == 1
    assert orchestrator.execute_calls == 2
