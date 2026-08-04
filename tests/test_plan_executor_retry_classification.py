from __future__ import annotations

from typing import Any

import pytest

from jarvis.planner.backoff import BackoffPolicy
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.retry import RetryPolicy


class MessageRouter:
    def __init__(
        self,
        messages: list[str],
    ) -> None:
        self._messages = list(
            messages
        )
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        del request

        self.calls += 1

        if self._messages:
            raise RuntimeError(
                self._messages.pop(0)
            )

        return {
            "ok": True,
        }


def make_executor(
    router: MessageRouter,
) -> PlanExecutor:
    return PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=3
        ),
        backoff_policy=BackoffPolicy(
            base_delay_seconds=0,
            multiplier=1,
            max_delay_seconds=0,
        ),
    )


@pytest.mark.asyncio
async def test_transient_read_only_failure_retries() -> None:
    router = MessageRouter(
        [
            "temporary connection unavailable",
        ]
    )

    executor = make_executor(
        router
    )

    plan = Plan(
        goal="Retry transient failure",
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


@pytest.mark.asyncio
async def test_permanent_read_only_failure_does_not_retry() -> None:
    router = MessageRouter(
        [
            "invalid request",
        ]
    )

    executor = make_executor(
        router
    )

    plan = Plan(
        goal="Permanent failure",
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

    assert result.success is False
    assert router.calls == 1
    assert result.step_results[0].attempts == 1


@pytest.mark.asyncio
async def test_unknown_failure_does_not_retry() -> None:
    router = MessageRouter(
        [
            "mysterious failure",
        ]
    )

    executor = make_executor(
        router
    )

    plan = Plan(
        goal="Unknown failure",
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

    assert result.success is False
    assert router.calls == 1
    assert result.step_results[0].attempts == 1
