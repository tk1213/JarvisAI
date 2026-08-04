from __future__ import annotations

import pytest

from jarvis.planner.ai_plan_adapter import AIPlanAdapter
from jarvis.planner.ai_plan_execution import (
    AIPlanExecutionService,
)
from jarvis.planner.ai_plan_parser import AIPlanParser
from jarvis.planner.ai_plan_pipeline import AIPlanPipeline
from jarvis.planner.ai_plan_validation import AIPlanValidator
from jarvis.planner.executor import (
    PlanExecutionResult,
    PlanStepResult,
)
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStepStatus,
)
from jarvis.planner.service import PlannerService
from jarvis.services.capability import CapabilityDefinition
from jarvis.services.capability_registry import CapabilityRegistry


class FakeExecutor:
    def __init__(
        self,
        *,
        fail: bool = False,
    ) -> None:
        self.fail = fail
        self.received_plan: Plan | None = None

    async def execute(
        self,
        plan: Plan,
    ) -> PlanExecutionResult:
        self.received_plan = plan

        if self.fail:
            plan.status = PlanStatus.FAILED
            step = plan.steps[0]
            step.status = PlanStepStatus.FAILED

            return PlanExecutionResult(
                plan=plan,
                step_results=[
                    PlanStepResult(
                        step_index=step.index,
                        capability=step.capability,
                        status=PlanStepStatus.FAILED,
                        error="simulated failure",
                    )
                ],
            )

        results: list[PlanStepResult] = []

        for step in plan.steps:
            step.status = PlanStepStatus.COMPLETED
            results.append(
                PlanStepResult(
                    step_index=step.index,
                    capability=step.capability,
                    status=PlanStepStatus.COMPLETED,
                    output={
                        "status": "ok",
                    },
                )
            )

        plan.status = PlanStatus.COMPLETED

        return PlanExecutionResult(
            plan=plan,
            step_results=results,
        )


def make_service(
    executor: FakeExecutor,
) -> AIPlanExecutionService:
    registry = CapabilityRegistry(
        [
            CapabilityDefinition(
                name="system.ping",
            ),
            CapabilityDefinition(
                name="system.health",
            ),
        ]
    )

    pipeline = AIPlanPipeline(
        parser=AIPlanParser(),
        adapter=AIPlanAdapter(
            validator=AIPlanValidator(
                registry
            ),
            planner=PlannerService(
                registry
            ),
        ),
    )

    return AIPlanExecutionService(
        pipeline=pipeline,
        executor=executor,
    )


@pytest.mark.asyncio
async def test_execution_service_builds_and_executes_plan() -> None:
    executor = FakeExecutor()
    service = make_service(
        executor
    )

    result = await service.execute(
        {
            "goal": "Check Jarvis",
            "steps": [
                {
                    "capability": "system.ping",
                    "arguments": {},
                },
                {
                    "capability": "system.health",
                    "arguments": {},
                },
            ],
        }
    )

    assert result.success is True
    assert result.completed_steps == 2
    assert executor.received_plan is not None
    assert executor.received_plan.goal == "Check Jarvis"


@pytest.mark.asyncio
async def test_execution_service_preserves_failed_result() -> None:
    service = make_service(
        FakeExecutor(
            fail=True
        )
    )

    result = await service.execute(
        {
            "goal": "Check Jarvis",
            "steps": [
                {
                    "capability": "system.ping",
                    "arguments": {},
                }
            ],
        }
    )

    assert result.success is False
    assert result.completed_steps == 0
    assert (
        result.execution.step_results[0].error
        == "simulated failure"
    )


@pytest.mark.asyncio
async def test_execution_service_rejects_unknown_capability() -> None:
    service = make_service(
        FakeExecutor()
    )

    with pytest.raises(
        ValueError,
        match="unknown capability",
    ):
        await service.execute(
            {
                "goal": "Unknown",
                "steps": [
                    {
                        "capability": "system.unknown",
                        "arguments": {},
                    }
                ],
            }
        )
