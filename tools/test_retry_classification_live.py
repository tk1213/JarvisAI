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


class DemoRouter:
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

        if self.calls == 1:
            raise RuntimeError(
                "temporary connection unavailable"
            )

        return {
            "status": "ok",
        }


async def main() -> None:
    router = DemoRouter()

    executor = PlanExecutor(
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

    plan = Plan(
        goal="Demonstrate classified retry",
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
        "Sprint 3.3 Retry Classification"
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
        f"Output: {result.step_results[0].output!r}"
    )

    if not result.success:
        raise RuntimeError(
            "Retry classification gate failed."
        )

    print(
        "Retry classification gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
