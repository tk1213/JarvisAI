from __future__ import annotations

from typing import Any

import pytest

from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)


class StubRouter:
    def __init__(self) -> None:
        self.requests: list[Any] = []

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.requests.append(request)

        if request.capability == "device.resolve":
            return {
                "device": {
                    "id": "plug-001",
                    "name": "Smart Plug 1",
                }
            }

        if request.capability == "device.status":
            return {
                "device_id": request.arguments["device_id"],
                "power": False,
            }

        raise RuntimeError(
            f"Unexpected capability: {request.capability}"
        )


@pytest.mark.asyncio
async def test_executor_passes_previous_output_to_next_step() -> None:
    router = StubRouter()
    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Resolve device and check status",
        steps=[
            PlanStep(
                index=1,
                capability="device.resolve",
                arguments={
                    "device_query": "Smart Plug 1",
                },
            ),
            PlanStep(
                index=2,
                capability="device.status",
                arguments={
                    "device_id": {
                        "$step": "1.device.id",
                    }
                },
            ),
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(plan)

    assert result.success is True
    assert result.completed_steps == 2
    assert plan.status is PlanStatus.COMPLETED
    assert router.requests[1].arguments == {
        "device_id": "plug-001",
    }
    assert result.step_results[1].output == {
        "device_id": "plug-001",
        "power": False,
    }


@pytest.mark.asyncio
async def test_reference_failure_stops_plan() -> None:
    router = StubRouter()
    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Invalid data dependency",
        steps=[
            PlanStep(
                index=1,
                capability="device.resolve",
                arguments={
                    "device_query": "Smart Plug 1",
                },
            ),
            PlanStep(
                index=2,
                capability="device.status",
                arguments={
                    "device_id": {
                        "$step": "1.device.missing",
                    }
                },
            ),
            PlanStep(
                index=3,
                capability="device.status",
                arguments={
                    "device_id": "plug-001",
                },
            ),
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(plan)

    assert result.success is False
    assert plan.status is PlanStatus.FAILED
    assert plan.steps[1].status is PlanStepStatus.FAILED
    assert plan.steps[2].status is PlanStepStatus.SKIPPED
    assert len(router.requests) == 1
    assert result.step_results[1].error is not None


@pytest.mark.asyncio
async def test_plan_must_be_ready() -> None:
    router = StubRouter()
    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Check status",
        steps=[
            PlanStep(
                index=1,
                capability="device.status",
                arguments={
                    "device_id": "plug-001",
                },
            )
        ],
        status=PlanStatus.DRAFT,
    )

    with pytest.raises(
        ValueError,
        match="READY",
    ):
        await executor.execute(plan)
