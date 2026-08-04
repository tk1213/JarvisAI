from __future__ import annotations

from typing import Any

import pytest

from jarvis.planner.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerPolicy,
)
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)


class FailingRouter:
    def __init__(self) -> None:
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        del request
        self.calls += 1
        raise RuntimeError(
            "invalid request"
        )


@pytest.mark.asyncio
async def test_open_circuit_blocks_later_execution() -> None:
    router = FailingRouter()
    breaker = CircuitBreaker(
        CircuitBreakerPolicy(
            failure_threshold=1,
            recovery_timeout_seconds=60,
        )
    )

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        circuit_breaker=breaker,
    )

    first = Plan(
        goal="First failure",
        steps=[
            PlanStep(
                index=1,
                capability="system.version",
            )
        ],
        status=PlanStatus.READY,
    )

    first_result = await executor.execute(
        first
    )

    second = Plan(
        goal="Blocked by circuit",
        steps=[
            PlanStep(
                index=1,
                capability="system.version",
            )
        ],
        status=PlanStatus.READY,
    )

    second_result = await executor.execute(
        second
    )

    assert first_result.success is False
    assert second_result.success is False
    assert router.calls == 1
    assert (
        second_result.step_results[0].error
        == "capability circuit breaker is open"
    )
