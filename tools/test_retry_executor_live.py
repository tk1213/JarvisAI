from __future__ import annotations

import asyncio
from typing import Any

from jarvis.planner.executor import PlanExecutor
from jarvis.planner.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from jarvis.planner.retry import RetryPolicy


class DemoFlakyRouter:
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
                "simulated temporary failure"
            )

        return {
            "status": "ok",
        }


async def main() -> None:
    router = DemoFlakyRouter()

    executor = PlanExecutor(
        router=router,  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            max_attempts=2
        ),
    )

    plan = Plan(
        goal="Demonstrate safe retry recovery",
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
        "Sprint 3.3 Safe Retry Executor"
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
            "Safe retry executor gate failed."
        )

    if result.step_results[0].attempts != 2:
        raise RuntimeError(
            "Safe retry executor did not retry "
            "the read-only capability exactly once."
        )

    print(
        "Safe retry executor gate: PASS"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )
