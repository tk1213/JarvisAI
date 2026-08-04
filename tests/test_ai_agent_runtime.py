from __future__ import annotations

from dataclasses import dataclass

import pytest

from jarvis.agent.runtime import (
    AIAgentRunStatus,
    AIAgentRuntime,
)
from jarvis.planner.ai_plan_memory import (
    AIPlanMemoryStore,
)
from jarvis.planner.ai_plan_reflection import (
    AIPlanReflectionService,
)
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


@dataclass
class FakeOrchestrator:
    preview: PlanPreview | None
    execution: PlanExecutionResult | None = None
    pending_cancelled: bool = False

    async def prepare(
        self,
        text: str,
    ) -> PlanPreview | None:
        del text
        return self.preview

    async def execute_preview(
        self,
        preview: PlanPreview,
    ) -> PlanExecutionResult:
        del preview

        if self.execution is None:
            raise RuntimeError(
                "Missing fake execution."
            )

        return self.execution

    async def confirm_pending(
        self,
    ) -> PlanExecutionResult:
        if self.execution is None:
            raise RuntimeError(
                "Missing fake execution."
            )

        return self.execution

    def cancel_pending(
        self,
    ) -> bool:
        self.pending_cancelled = True
        return True


def make_plan(
    *,
    status: PlanStatus = PlanStatus.READY,
) -> Plan:
    return Plan(
        goal="Check Jarvis",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
                arguments={},
                description="Execute system.ping",
                status=(
                    PlanStepStatus.PENDING
                    if status is PlanStatus.READY
                    else PlanStepStatus.COMPLETED
                ),
            )
        ],
        status=status,
    )


def make_execution() -> PlanExecutionResult:
    plan = make_plan(
        status=PlanStatus.COMPLETED
    )

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


def make_runtime(
    orchestrator: FakeOrchestrator,
) -> AIAgentRuntime:
    return AIAgentRuntime(
        orchestrator=orchestrator,  # type: ignore[arg-type]
        reflection=AIPlanReflectionService(),
        memory=AIPlanMemoryStore(),
    )


@pytest.mark.asyncio
async def test_runtime_handles_no_plan() -> None:
    result = await make_runtime(
        FakeOrchestrator(
            preview=None
        )
    ).run(
        "hello"
    )

    assert result.status is AIAgentRunStatus.NO_PLAN
    assert result.execution is None


@pytest.mark.asyncio
async def test_runtime_stops_for_confirmation() -> None:
    preview = PlanPreview(
        plan=make_plan(),
        decision=ExecutionDecision(
            route=ExecutionRoute.CONFIRMATION_REQUIRED,
            side_effect_steps=(
                1,
            ),
        ),
    )

    result = await make_runtime(
        FakeOrchestrator(
            preview=preview
        )
    ).run(
        "turn on light"
    )

    assert (
        result.status
        is AIAgentRunStatus.CONFIRMATION_REQUIRED
    )
    assert result.requires_confirmation is True
    assert result.execution is None


@pytest.mark.asyncio
async def test_runtime_executes_reflects_and_remembers() -> None:
    preview = PlanPreview(
        plan=make_plan(),
        decision=ExecutionDecision(
            route=ExecutionRoute.READ_ONLY,
            side_effect_steps=(),
        ),
    )

    runtime = make_runtime(
        FakeOrchestrator(
            preview=preview,
            execution=make_execution(),
        )
    )

    result = await runtime.run(
        "check Jarvis"
    )

    assert result.status is AIAgentRunStatus.COMPLETED
    assert result.success is True
    assert result.reflection is not None
    assert result.memory_record is not None
    assert result.memory_record.goal == "Check Jarvis"