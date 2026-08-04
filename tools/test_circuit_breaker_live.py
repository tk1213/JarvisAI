from __future__ import annotations

import asyncio
from typing import Any

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


class DemoFailingRouter:
    def __init__(self) -> None:
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls += 1

        print(
            f"Router call {self.calls}: "
            f"{request.capability}"
        )

        raise RuntimeError(
            "invalid request"
        )


async def main() -> None:
    router = DemoFailingRouter()
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
        goal="Open circuit",
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
        goal="Verify fail fast",
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

    print()
    print(
        "Sprint 3.4 Circuit Breaker"
    )
    print(
        "-" * 60
    )
    print(
        f"First plan: {first_result.plan.status.value}"
    )
    print(
        f"Second plan: {second_result.plan.status.value}"
    )
    print(
        f"Router calls: {router.calls}"
    )
    print(
        "Second error: "
        f"{second_result.step_results[0].error}"
    )

    if router.calls != 1:
        raise RuntimeError(
            "Open circuit did not fail fast."
        )

    print(
        "Circuit breaker gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
