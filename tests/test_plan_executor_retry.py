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
from jarvis.planner.retry import RetryPolicy


class FlakyRouter:
    def __init__(
        self,
        *,
        failures_before_success: int,
    ) -> None:
        self.failures_before_success = (
            failures_before_success
        )
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        del request

        self.calls += 1

        if self.calls <= self.failures_before_success:
            raise RuntimeError(
                f"temporary failure {self.calls}"
            )

        return {
            "ok": True,
        }


@pytest.mark.asyncio
async def test_executor_retries_transient_read_only_failure() -> None:
    router = FlakyRouter(
        failures_before_success=1
    )

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=2
        ),
    )

    plan = Plan(
        goal="Retry once",
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

    assert result.success is True
    assert router.calls == 2
    assert result.step_results[0].attempts == 2
    assert result.step_results[0].success is True


@pytest.mark.asyncio
async def test_executor_fails_after_read_only_retry_limit() -> None:
    router = FlakyRouter(
        failures_before_success=10
    )

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=3
        ),
    )

    plan = Plan(
        goal="Fail after retries",
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

    result = await executor.execute(
        plan
    )

    assert result.success is False
    assert router.calls == 3
    assert result.step_results[0].attempts == 3
    assert (
        result.step_results[0].status
        is PlanStepStatus.FAILED
    )
    assert (
        plan.steps[1].status
        is PlanStepStatus.SKIPPED
    )


@pytest.mark.asyncio
async def test_side_effect_failure_is_not_retried() -> None:
    router = FlakyRouter(
        failures_before_success=10
    )

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=3
        ),
    )

    plan = Plan(
        goal="Do not retry side effect",
        steps=[
            PlanStep(
                index=1,
                capability="smart_home.turn_off",
            )
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(
        plan
    )

    assert result.success is False
    assert router.calls == 1
    assert result.step_results[0].attempts == 1


@pytest.mark.asyncio
async def test_reference_resolution_errors_are_not_retried() -> None:
    router = FlakyRouter(
        failures_before_success=0
    )

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=3
        ),
    )

    plan = Plan(
        goal="Bad reference",
        steps=[
            PlanStep(
                index=1,
                capability="system.ping",
                arguments={
                    "value": {
                        "$step": "99.missing",
                    }
                },
            )
        ],
        status=PlanStatus.READY,
    )

    result = await executor.execute(
        plan
    )

    assert result.success is False
    assert router.calls == 0
    assert result.step_results[0].attempts == 1
