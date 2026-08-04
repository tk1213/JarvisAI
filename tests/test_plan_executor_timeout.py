from __future__ import annotations

import asyncio
from typing import Any

import pytest

from jarvis.planner.backoff import BackoffPolicy
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from jarvis.planner.retry import RetryPolicy
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
async def test_read_only_timeout_can_retry() -> None:
    router = SlowRouter()

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=2
        ),
        backoff_policy=BackoffPolicy(
            base_delay_seconds=0,
            multiplier=1,
            max_delay_seconds=0,
        ),
        timeout_policy=ExecutionTimeoutPolicy(
            step_timeout_seconds=0.01
        ),
    )

    plan = Plan(
        goal="Timeout ping",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
            )
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(plan)

    assert result.success is False
    assert router.calls == 2
    assert result.step_results[0].attempts == 2
    assert (
        result.step_results[0].status
        is PlanStepStatus.FAILED
    )
    assert "timed out" in result.step_results[0].error


@pytest.mark.asyncio
async def test_side_effect_timeout_is_not_retried() -> None:
    router = SlowRouter()

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=3
        ),
        timeout_policy=ExecutionTimeoutPolicy(
            step_timeout_seconds=0.01
        ),
    )

    plan = Plan(
        goal="Timeout side effect",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
            )
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(plan)

    assert result.success is False
    assert router.calls == 1
    assert result.step_results[0].attempts == 1
