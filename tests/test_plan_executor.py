from __future__ import annotations

import asyncio
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
    def __init__(
        self,
        *,
        outputs: dict[str, Any] | None = None,
        failures: set[str] | None = None,
    ) -> None:
        self.outputs = outputs or {}
        self.failures = failures or set()
        self.calls: list[str] = []

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls.append(
            request.capability
        )

        if request.capability in self.failures:
            raise RuntimeError(
                f"failed: {request.capability}"
            )

        return self.outputs.get(
            request.capability,
            {
                "capability": request.capability,
                "arguments": request.arguments,
            },
        )


def make_plan() -> Plan:
    return Plan(
        goal="Turn off bedroom light and check status",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
                arguments={
                    "device": "bedroom light",
                },
            ),
            PlanStep(
                index=2,
                capability="smart_home.status",
                arguments={
                    "device": "bedroom light",
                },
            ),
        ],
        status=PlanStatus.READY,
    )


@pytest.mark.asyncio
async def test_execute_plan_successfully() -> None:
    router = StubRouter(
        outputs={
            "smart_home.turn_off": True,
            "smart_home.status": {
                "power": False,
            },
        }
    )

    executor = PlanExecutor(
        router,  # type: ignore[arg-type]
    )

    plan = make_plan()

    result = await executor.execute(
        plan
    )

    assert result.success is True
    assert result.plan.status is PlanStatus.COMPLETED
    assert result.completed_steps == 2
    assert router.calls == [
        "smart_home.turn_off",
        "smart_home.status",
    ]
    assert all(
        step.status is PlanStepStatus.COMPLETED
        for step in plan.steps
    )


@pytest.mark.asyncio
async def test_execution_stops_on_failure() -> None:
    router = StubRouter(
        failures={
            "smart_home.turn_off",
        }
    )

    executor = PlanExecutor(
        router,  # type: ignore[arg-type]
    )

    plan = make_plan()

    result = await executor.execute(
        plan
    )

    assert result.success is False
    assert result.plan.status is PlanStatus.FAILED
    assert result.completed_steps == 0

    assert (
        plan.steps[0].status
        is PlanStepStatus.FAILED
    )
    assert (
        plan.steps[1].status
        is PlanStepStatus.SKIPPED
    )

    assert router.calls == [
        "smart_home.turn_off",
    ]


@pytest.mark.asyncio
async def test_step_result_contains_output() -> None:
    router = StubRouter(
        outputs={
            "system.ping": {
                "status": "ok",
            }
        }
    )

    executor = PlanExecutor(
        router,  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Check system",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            )
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(
        plan
    )

    assert result.step_results[0].output == {
        "status": "ok",
    }


@pytest.mark.asyncio
async def test_plan_must_be_ready() -> None:
    router = StubRouter()

    executor = PlanExecutor(
        router,  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Check system",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            )
        ],
        status=PlanStatus.DRAFT,
    )

    with pytest.raises(
        ValueError,
        match="READY",
    ):
        await executor.execute(
            plan
        )


@pytest.mark.asyncio
async def test_failure_result_contains_error() -> None:
    router = StubRouter(
        failures={
            "system.ping",
        }
    )

    executor = PlanExecutor(
        router,  # type: ignore[arg-type]
    )

    plan = Plan(
        goal="Check system",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            )
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(
        plan
    )

    assert result.step_results[0].success is False
    assert (
        result.step_results[0].error
        == "failed: system.ping"
    )

@pytest.mark.asyncio
async def test_cancellation_finalizes_active_and_pending_step_states() -> None:
    entered = asyncio.Event()

    class BlockingRouter:
        async def execute_request(
            self,
            request,
        ) -> Any:
            del request
            entered.set()
            await asyncio.Future()

    executor = PlanExecutor(
        BlockingRouter(),  # type: ignore[arg-type]
    )

    plan = make_plan()

    task = asyncio.create_task(
        executor.execute(
            plan
        )
    )

    await entered.wait()

    assert plan.status is PlanStatus.RUNNING
    assert (
        plan.steps[0].status
        is PlanStepStatus.RUNNING
    )
    assert (
        plan.steps[1].status
        is PlanStepStatus.PENDING
    )

    task.cancel()

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await task

    assert plan.status is PlanStatus.CANCELLED
    assert (
        plan.steps[0].status
        is PlanStepStatus.FAILED
    )
    assert (
        plan.steps[1].status
        is PlanStepStatus.SKIPPED
    )