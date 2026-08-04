from __future__ import annotations

import asyncio
from typing import Any

import pytest

from jarvis.planner.deadline import PlanDeadlinePolicy
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from jarvis.planner.timeout import ExecutionTimeoutPolicy


class SlowRouter:
    def __init__(self) -> None:
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        del request
        self.calls += 1
        await asyncio.sleep(0.05)
        return {"ok": True}


@pytest.mark.asyncio
async def test_plan_deadline_stops_execution() -> None:
    router = SlowRouter()

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        timeout_policy=ExecutionTimeoutPolicy(
            step_timeout_seconds=1.0
        ),
        deadline_policy=PlanDeadlinePolicy(
            plan_timeout_seconds=0.01
        ),
    )

    plan = Plan(
        goal="Deadline test",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            ),
            PlanStep(
                index=2,
                capability="system.version",
            ),
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(plan)

    assert result.success is False
    assert plan.status is PlanStatus.FAILED
    assert router.calls == 1
    assert (
        result.step_results[0].status
        is PlanStepStatus.FAILED
    )
    assert (
        "deadline exceeded"
        in result.step_results[0].error
    )
    assert (
        plan.steps[1].status
        is PlanStepStatus.SKIPPED
    )
