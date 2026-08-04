from __future__ import annotations

import asyncio
from typing import Any

from jarvis.planner.backoff import BackoffPolicy
from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.retry import RetryPolicy
from jarvis.planner.timeout import ExecutionTimeoutPolicy


class DemoSlowRouter:
    def __init__(self) -> None:
        self.calls = 0

    async def execute_request(
        self,
        request,
    ) -> Any:
        self.calls += 1

        print(
            f"Attempt {self.calls}: "
            f"{request.capability}"
        )

        await asyncio.sleep(
            0.05
        )

        return {
            "status": "late",
        }


async def main() -> None:
    router = DemoSlowRouter()

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
        goal="Demonstrate execution timeout",
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

    print()
    print(
        "Sprint 3.4 Execution Timeout"
    )
    print(
        "-" * 60
    )
    print(
        f"Plan status: {result.plan.status.value}"
    )
    print(
        f"Attempts: {result.step_results[0].attempts}"
    )
    print(
        f"Error: {result.step_results[0].error}"
    )

    if result.success:
        raise RuntimeError(
            "Timeout gate unexpectedly succeeded."
        )

    if router.calls != 2:
        raise RuntimeError(
            "Read-only timeout retry count is incorrect."
        )

    print(
        "Execution timeout gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
